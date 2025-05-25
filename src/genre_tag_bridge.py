"""
Genre Tag Bridge
Reads the genre/style label from an E-GMD (or similarly named) MIDI
and passes it downstream via `analysis_context["genre"]`.
"""
import os, csv, re, pretty_midi, logging
from typing import Dict
from plugin_registry import register_plugin

CSV_HINT = "e-gmd-v1.0.0.csv"          # adjust if you renamed it
CACHE: Dict[str, str] = {}             # speed-up

def _csv_lookup(midi_path: str) -> str:
    """Look up style in the E-GMD metadata CSV if it’s nearby."""
    root = midi_path.split("e-gmd-v1.0.0")[0] + "e-gmd-v1.0.0"
    csv_path = os.path.join(root, CSV_HINT)
    if not os.path.exists(csv_path):
        return ""
    if not CACHE:                        # first call → read once
        with open(csv_path, newline="") as f:
            for row in csv.DictReader(f):
                CACHE[row["midi_filename"]] = row["style"]
    key = os.path.relpath(midi_path, root).replace("\\", "/")
    return CACHE.get(key, "")

def _metadata_lookup(midi_path: str) -> str:
    """Extract style from the MIDI’s track-name or text events."""
    midi = pretty_midi.PrettyMIDI(midi_path)
    for t in midi.text_events + midi.lyrics:
        m = re.search(r"(rock|funk|latin|swing|hiphop|pop)", t.text, re.I)
        if m:
            return m.group(0).lower()
    return ""

@register_plugin(
    name="genre_tag_bridge",
    description="Adds 'genre' to analysis_context based on E-GMD filenames/metadata",
    input_type="midi",
    phase=2,                 # run right after jsymbolic_bridge
)
def genre_tag_bridge(midi_path: str,
                     analysis_context: dict | None = None,
                     **_) -> Dict:
    try:
        style = (_csv_lookup(midi_path) or _metadata_lookup(midi_path)).lower()
        if not style:
            # fallback: guess from the folder name (drummer#/rock_90bpm.mid)
            style = re.search(r"(rock|funk|latin|swing|hiphop|pop)",
                              midi_path, re.I)
            style = style.group(0).lower() if style else "unknown"

        if analysis_context is not None:
            analysis_context["genre"] = style      # <-- key line

        return {"status": "success", "genre": style}

    except Exception as e:
        logging.exception("genre_tag_bridge failed")
        return {"error": str(e)}
