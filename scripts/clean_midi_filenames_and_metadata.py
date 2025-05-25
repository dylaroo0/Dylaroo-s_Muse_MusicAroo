
import os
from pathlib import Path
from mido import MidiFile, MidiTrack, MetaMessage
import shutil
import re

# Input/output locations
input_dir = Path(r"C:/Users/12502/Documents/AI music assistant/data/midi")
output_dir = input_dir / "cleaned_stripped"
backup_dir = output_dir / "_backup_corrupt"

output_dir.mkdir(exist_ok=True)
backup_dir.mkdir(exist_ok=True)

# Function to clean filenames
def clean_filename(name):
    name = name.replace('&', 'and')
    name = re.sub(r"[()]", "", name)
    name = re.sub(r"[!@#$%^&*+={}\[\]|;:\"<>,.?]", "", name)
    name = re.sub(r"__+", "_", name)
    name = re.sub(r"_+", "_", name)
    name = name.strip("_")
    return name

# Function to clean metadata
def clean_metadata(msg):
    if msg.type in ("track_name", "text", "lyrics", "marker", "cue_marker"):
        if hasattr(msg, 'text') and isinstance(msg.text, str) and '&' in msg.text:
            msg.text = msg.text.replace('&', 'and')
    return msg

# Process all MIDI files
for mid_path in input_dir.rglob("*.mid"):
    new_name = clean_filename(mid_path.stem) + ".mid"
    output_path = output_dir / new_name

    try:
        mid = MidiFile(mid_path)
        for track in mid.tracks:
            for i, msg in enumerate(track):
                if msg.is_meta:
                    track[i] = clean_metadata(msg)
        mid.save(output_path)
        print(f"✔ Cleaned and renamed: {mid_path.name} -> {output_path.name}")
    except Exception as e:
        print(f"✖ Skipped (error): {mid_path.name} - {e}")
        shutil.copy(mid_path, backup_dir / mid_path.name)
