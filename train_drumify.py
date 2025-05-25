"""
Train a transformer model for drum pattern generation using the E-GMD v1.0.0 dataset.
"""
import os
import glob
import pretty_midi
import numpy as np
from transformers import GPT2Config, GPT2LMHeadModel, Trainer, TrainingArguments
from torch.utils.data import Dataset
import torch

# Define a custom dataset for drum patterns
class DrumDataset(Dataset):
    def __init__(self, midi_files, max_length=128):
        self.midi_files = midi_files
        self.max_length = max_length
        self.vocab = {36: 1, 38: 2, 42: 3}  # Kick, Snare, Hi-Hat

    def __len__(self):
        return len(self.midi_files)

    def __getitem__(self, idx):
        midi_path = self.midi_files[idx]
        midi_data = pretty_midi.PrettyMIDI(midi_path)

        # Extract drum notes (simplified: kick, snare, hi-hat)
        sequence = []
        for instrument in midi_data.instruments:
            if not instrument.is_drum:
                continue
            for note in instrument.notes:
                if note.pitch in self.vocab:
                    # Quantize time to 16th notes
                    time_step = int(note.start * 16)
                    if time_step < self.max_length:
                        sequence.append((time_step, self.vocab[note.pitch]))

        # Create input sequence (time step, note type)
        input_ids = np.zeros(self.max_length, dtype=np.int64)
        for time_step, note_type in sequence:
            input_ids[time_step] = note_type

        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "labels": torch.tensor(input_ids, dtype=torch.long)
        }

# Load MIDI files from E-GMD v1.0.0 (recursively)
data_dir = "data/e-gmd"
midi_files = glob.glob(os.path.join(data_dir, "**/*.mid"), recursive=True)
if not midi_files:
    raise FileNotFoundError(f"No MIDI files found in {data_dir}")

# Create dataset
dataset = DrumDataset(midi_files)

# Define model configuration
config = GPT2Config(
    vocab_size=4,  # 0 (padding), 1 (kick), 2 (snare), 3 (hi-hat)
    n_positions=128,
    n_ctx=128,
    n_embd=256,
    n_layer=6,
    n_head=8
)
model = GPT2LMHeadModel(config)

# Define training arguments
training_args = TrainingArguments(
    output_dir="models/drumify",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    save_steps=1000,
    save_total_limit=2,
    logging_steps=500,
)

# Initialize trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)

# Train the model
trainer.train()

# Save the model
model.save_pretrained("models/drumify")