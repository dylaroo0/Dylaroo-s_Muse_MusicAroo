"""
Train a transformer model for drum-pattern generation on the
E-GMD v1.0.0 dataset, with an extra token that encodes each clip's genre.
"""
from __future__ import annotations
import argparse, os, csv, random, pathlib as pl
import numpy as np, torch, pretty_midi
from torch.utils.data import Dataset
from transformers import (
    GPT2Config,
    GPT2LMHeadModel,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
)

# -----------------------------------------------------------------------------
# 1.  CONFIGURATION
# -----------------------------------------------------------------------------
MAX_LEN   = 128                       # 128 × 1/16-note grid = 2 bars of 4/4
KICK, SNARE, HAT = 36, 38, 42         # GM pitches we keep
GENRES    = ["rock", "funk", "latin", "swing"]  # extend if you like
PAD_TOKEN = 0
NOTE_TOKENS = {KICK: 1, SNARE: 2, HAT: 3}       # will stay 1-3
GENRE_OFFSET = 10                                # genre tokens start at 10
GENRE_TOKENS = {g: GENRE_OFFSET + i for i, g in enumerate(GENRES)}
VOCAB_SIZE   = max(GENRE_TOKENS.values()) + 1    # +1 because 0 is padding

# -----------------------------------------------------------------------------
# 2.  DATASET
# -----------------------------------------------------------------------------
class DrumDataset(Dataset):
    """
    Converts a list of (midi_path, primary_genre) into transformer
    input/label pairs of fixed length MAX_LEN.
    """
    def __init__(self, items, max_len=MAX_LEN):
        self.items    = items
        self.max_len  = max_len

    def __len__(self): return len(self.items)

    def __getitem__(self, idx):
        midi_path, genre = self.items[idx]
        seq = np.zeros(self.max_len, dtype=np.int64)
        seq[0] = GENRE_TOKENS.get(genre, PAD_TOKEN)   # genre token at position 0

        pm = pretty_midi.PrettyMIDI(midi_path)
        for inst in pm.instruments:
            if not inst.is_drum:  # skip melodic tracks
                continue
            for n in inst.notes:
                if n.pitch not in NOTE_TOKENS:
                    continue
                step = int(n.start * 16) + 1          # +1 because 0 is genre
                if 1 <= step < self.max_len:
                    seq[step] = NOTE_TOKENS[n.pitch]

        return {"input_ids": torch.tensor(seq),
                "labels":    torch.tensor(seq)}

# -----------------------------------------------------------------------------
# 3.  DATA LOADING UTILITIES
# -----------------------------------------------------------------------------
def load_e_gmd(data_root: str) -> tuple[list, list, list]:
    """
    Reads e-gmd-v1.0.0.csv to gather (midi_path, genre) tuples and
    splits them into train/val/test lists.
    """
    csv_path = pl.Path(data_root) / "e-gmd-v1.0.0.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV metadata not found: {csv_path}")

    train, val, test = [], [], []
    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            midi_rel = row["midi_filename"]
            midi_abs = pl.Path(data_root) / midi_rel
            genre    = row["style"].split("/")[0].lower()
            item     = (str(midi_abs), genre)
            split    = row["split"].lower()  # 'train'/'validation'/'test'

            if split == "train":
                train.append(item)
            elif split == "validation":
                val.append(item)
            else:
                test.append(item)

    # Shuffle for good measure
    rng = random.Random(42)
    for lst in (train, val, test):
        rng.shuffle(lst)
    return train, val, test

# -----------------------------------------------------------------------------
# 4.  TRAINING SCRIPT
# -----------------------------------------------------------------------------
def main(args):
    print("⏳ Loading E-GMD metadata …")
    train_items, val_items, test_items = load_e_gmd(args.data_root)

    print(f"✓ {len(train_items):6} train  |  "
          f"{len(val_items):5} val  |  {len(test_items):5} test clips")

    train_ds = DrumDataset(train_items)
    val_ds   = DrumDataset(val_items)

    config = GPT2Config(
        vocab_size=VOCAB_SIZE,
        n_positions=MAX_LEN,
        n_ctx=MAX_LEN,
        n_embd=args.n_embd,
        n_layer=args.n_layer,
        n_head=args.n_head,
        bos_token_id=None,
        eos_token_id=None,
        pad_token_id=PAD_TOKEN,
    )
    model = GPT2LMHeadModel(config)

    collator = DataCollatorForLanguageModeling(
        tokenizer=None,               # we already supply tensors
        mlm=False,                    # no masked-LM loss
    )

    training_args = TrainingArguments(
        output_dir=args.out_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_steps=200,
        save_total_limit=3,
        fp16=torch.cuda.is_available(),   # mixed precision if GPU
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=collator,
    )

    print("🚀 Starting training …")
    trainer.train()
    print("✅ Training complete. Saving checkpoint …")
    model.save_pretrained(args.out_dir)
    print(f"📦 Model saved to {args.out_dir}")

# -----------------------------------------------------------------------------
# 5.  CLI ENTRY-POINT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root", default="data/midi/drums/clean/e-gmd-v1.0.0",
                        help="Path to the root of the un-zipped E-GMD folder")
    parser.add_argument("--out_dir",   default="models/drumify",
                        help="Where checkpoints and final model go")
    parser.add_argument("--epochs",    type=int, default=3)
    parser.add_argument("--batch",     type=int, default=16)
    parser.add_argument("--n_embd",    type=int, default=256)
    parser.add_argument("--n_layer",   type=int, default=8)
    parser.add_argument("--n_head",    type=int, default=8)
    args = parser.parse_args()

    main(args)
