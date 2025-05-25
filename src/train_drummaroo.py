# src/train_drumify.py
"""
SuperDrummify – sequence-to-sequence drum-pattern trainer
--------------------------------------------------------
* Trains a transformer-based model on the E-GMD or any folder of MIDI grooves.
* Saves checkpoints + tensorboard logs under runs/<run_name>/.
* Designed to work with CPU or GPU, on Windows, macOS, Linux, or WSL.

USAGE (GPU example)
-------------------
python -m src.train_drumify \
    --midi_root data/midi/drums/clean/e-gmd-v1.0.0 \
    --run_name superdrummify_e_gmd \
    --epochs 80 \
    --batch 256 \
    --seq_len 256 \
    --lr 3e-4

After training, set the environment variable:
    set DRUMIFY_CHECKPOINT="runs/superdrummify_e_gmd/best.ckpt"
or move that file into models/drumify/ and the plugin will auto-find it.

Dependencies: torch, torch-text, pretty_midi, tqdm
"""

import argparse
import json
import os
from pathlib import Path
from typing import List

import pretty_midi as pm
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm


################################################################################
#                               DATASET                                         #
################################################################################

PAD, SOS, EOS = 0, 1, 2  # token ids reserved for padding / start / end


def midi_to_tokens(midi_path: Path, max_len: int) -> List[int]:
    """Convert a single-track drum MIDI into a flat token list (pitch + time)."""
    midi = pm.PrettyMIDI(str(midi_path))
    drum = next((i for i in midi.instruments if i.is_drum), None)
    if drum is None:
        return []
    events = []
    for note in drum.notes:
        token_time = int(note.start * 1000)  # ms → integer
        token_pitch = note.pitch
        events.append((token_time, token_pitch))
    # Sort by time then pitch
    events.sort()
    # Interleave [time, pitch] to a 1-D sequence
    seq = [SOS]
    for t, p in events:
        seq += [t, p]
        if len(seq) >= max_len - 1:
            break
    seq.append(EOS)
    return seq


class DrumDataset(Dataset):
    def __init__(self, midi_root: Path, max_len: int):
        self.files = list(Path(midi_root).rglob("*.mid*"))
        self.max_len = max_len

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        tokens = midi_to_tokens(self.files[idx], self.max_len)
        return torch.tensor(tokens, dtype=torch.long)


def collate(batch, pad_val: int = PAD):
    lens = [len(x) for x in batch]
    max_len = max(lens)
    padded = torch.full((len(batch), max_len), pad_val, dtype=torch.long)
    for i, seq in enumerate(batch):
        padded[i, : len(seq)] = seq
    return padded, torch.tensor(lens, dtype=torch.long)


################################################################################
#                               MODEL                                           #
################################################################################

class DrumTransformer(nn.Module):
    def __init__(self, vocab: int = 2048, d_model: int = 256, nhead: int = 8,
                 num_layers: int = 6, dim_feedforward: int = 512, dropout: float = 0.1):
        super().__init__()
        self.embed = nn.Embedding(vocab, d_model, padding_idx=PAD)
        self.pos = nn.Parameter(torch.randn(1, 4096, d_model) * 0.01)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model, nhead, dim_feedforward, dropout, batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        self.fc = nn.Linear(d_model, vocab)

    def forward(self, x):
        x = self.embed(x) + self.pos[:, : x.size(1)]
        h = self.encoder(x)
        return self.fc(h)


################################################################################
#                               TRAINING LOOP                                   #
################################################################################

def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    ds = DrumDataset(args.midi_root, args.seq_len)
    dl = DataLoader(ds, batch_size=args.batch, shuffle=True,
                    collate_fn=collate, num_workers=2)

    model = DrumTransformer().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    loss_fn = nn.CrossEntropyLoss(ignore_index=PAD)

    run_dir = Path("runs") / args.run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    writer = SummaryWriter(run_dir)

    global_step = 0
    best_loss = float("inf")
    for epoch in range(1, args.epochs + 1):
        model.train()
        pbar = tqdm(dl, desc=f"Epoch {epoch}/{args.epochs}")
        for x, lens in pbar:
            x = x.to(device)
            opt.zero_grad()
            logits = model(x[:, :-1])
            loss = loss_fn(logits.reshape(-1, logits.size(-1)),
                           x[:, 1:].reshape(-1))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()

            writer.add_scalar("train/loss", loss.item(), global_step)
            pbar.set_postfix(loss=f"{loss.item():.3f}")
            global_step += 1

        # simple val = one random batch (can add proper split later)
        model.eval()
        with torch.no_grad():
            x_val, _ = next(iter(dl))
            x_val = x_val.to(device)
            val_loss = loss_fn(
                model(x_val[:, :-1]).reshape(-1, logits.size(-1)),
                x_val[:, 1:].reshape(-1)
            ).item()
        writer.add_scalar("val/loss", val_loss, epoch)

        # checkpoint
        ckpt_path = run_dir / f"epoch{epoch:03d}.ckpt"
        torch.save(model.state_dict(), ckpt_path)
        if val_loss < best_loss:
            best_loss = val_loss
            torch.save(model.state_dict(), run_dir / "best.ckpt")

    # Save metadata for plugin
    meta = {
        "epochs": args.epochs,
        "batch": args.batch,
        "seq_len": args.seq_len,
        "best_val_loss": best_loss,
    }
    with open(run_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Training complete – best.ckpt saved to {run_dir}")


################################################################################
#                               CLI                                             #
################################################################################

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--midi_root", type=Path,
                    default=Path("data/midi/drums/clean/e-gmd-v1.0.0"),
                    help="Folder of training MIDI grooves")
    ap.add_argument("--run_name", type=str, default="superdrummify_run")
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--seq_len", type=int, default=256)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--cpu", action="store_true",
                    help="Force CPU even if GPU available")
    return ap.parse_args()


if __name__ == "__main__":
    train(parse_args())
