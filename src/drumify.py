"""
Drumify Plugin
Generates drum patterns from MIDI inputs using a trained transformer model.
Now with basic genre awareness.
"""
import os
import logging
import pretty_midi
import numpy as np
import torch
from transformers import GPT2LMHeadModel
from typing import Dict
from plugin_registry import register_plugin

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL_PATH = "models/drumify"                       # checkpoint folder
DEFAULT_TEMPO = 120
DEFAULT_ENERGY = 0.5
MAX_LENGTH = 128                                    # 128 × 1/16-note steps

# Map genre → MIDI drum pitches (GM)
GENRE_VOCAB = {
    "rock":  {1: 36, 2: 38, 3: 42},                # kick, snare, closed hat
    "funk":  {1: 36, 2: 38, 3: 42, 4: 46},         # add open hat
    "latin": {1: 36, 2: 38, 3: 42, 4: 39},         # add clap
    "swing": {1: 36, 2: 40, 3: 42},                # sidestick snare
    "default": {1: 36, 2: 38, 3: 42},              # fallback
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    filename="logs/drumify.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# ---------------------------------------------------------------------------
# Load model (once at import time)
# ---------------------------------------------------------------------------
try:
    MODEL = GPT2LMHeadModel.from_pretrained(MODEL_PATH)
    MODEL.eval()
    logging.info("Loaded Drumify transformer model.")
except Exception as e:
    MODEL = None
    logging.warning(
        f"Could not load Drumify model at '{MODEL_PATH}': {e}. Falling back to rule-based drums."
    )

# ---------------------------------------------------------------------------
# Helper: very lightweight genre guess if the caller provides none
# ---------------------------------------------------------------------------
def _heuristic_genre(jsym: Dict) -> str:
    """
    Derive a crude genre tag from a few jSymbolic features.
    Returns one of 'swing', 'funk', 'rock', 'latin' or 'default'.
    """
    swing_ratio = jsym.get("Average Swing Ratio", 0.0) or 0.0
    density     = jsym.get("Mean Note Duration", 0.0) or 0.0

    # These thresholds are just ballpark numbers—tweak as you like
    if swing_ratio > 1.25:
        return "swing"
    if density < 0.25:
        return "funk"   # lots of short notes
    if density > 0.75:
        return "latin"  # more sustained parts typical of bossa/samba comps
    return "rock"

# ---------------------------------------------------------------------------
# Plugin entry-point
# ---------------------------------------------------------------------------
@register_plugin(
    name="drumify",
    description="Generates drum patterns from MIDI inputs using a trained transformer model (genre-aware)",
    input_type="midi",
    phase=3,
    requires=["jsymbolic_bridge"],  # expects jSymbolic features in analysis_context
)
def drumify(
    midi_path: str,
    output_dir: str = "reports",
    analysis_context: dict = None,
) -> Dict:
    """
    Args
    ----
    midi_path        : Path to the input MIDI file (e.g. melody or bassline).
    output_dir       : Folder to save the generated drum MIDI.
    analysis_context : Dict carrying info from upstream plugins
                       (tempo, energy, jsymbolic_bridge, *genre* …).

    Returns
    -------
    Dict with status and metadata, or {'error': ...} on failure.
    """
    try:
        # -------------------------------------------------------------------
        # Sanity checks & MIDI load
        # -------------------------------------------------------------------
        if not os.path.exists(midi_path):
            msg = f"MIDI not found: {midi_path}"
            logging.error(msg)
            return {"error": msg}

        midi_in = pretty_midi.PrettyMIDI(midi_path)
        if not midi_in.instruments:
            msg = "No instruments in MIDI file"
            logging.error(msg)
            return {"error": msg}

        # -------------------------------------------------------------------
        # Extract onsets from *first* track (good enough for a seed)
        # -------------------------------------------------------------------
        onsets = [n.start for n in midi_in.instruments[0].notes]
        if not onsets:
            msg = "No notes detected"
            logging.error(msg)
            return {"error": msg}

        # -------------------------------------------------------------------
        # Context: tempo, energy, jSymbolic features, genre
        # -------------------------------------------------------------------
        tempo  = analysis_context.get("tempo", DEFAULT_TEMPO) if analysis_context else DEFAULT_TEMPO
        energy = analysis_context.get("energy", DEFAULT_ENERGY) if analysis_context else DEFAULT_ENERGY

        jsym = analysis_context.get("jsymbolic_bridge", {}).get("features", {}) if analysis_context else {}

        # Preferred: caller supplies a genre in analysis_context
        genre = analysis_context.get("genre") if analysis_context else None
        # Fallback: quick-and-dirty heuristic
        if genre is None:
            genre = _heuristic_genre(jsym)

        vocab = GENRE_VOCAB.get(genre, GENRE_VOCAB["default"])

        # Use rhythmic variability to control complexity
        variability = jsym.get("Variability of Note Duration", 0.5) or 0.5
        complexity_factor = np.clip(variability / 0.5, 0.5, 1.5)

        # -------------------------------------------------------------------
        # Encode onsets into transformer input (16th-note grid)
        # -------------------------------------------------------------------
        input_ids = np.zeros(MAX_LENGTH, dtype=np.int64)
        for o in onsets:
            step = int(o * 16)
            if step < MAX_LENGTH:
                input_ids[step] = 1  # just a seed flag

        # -------------------------------------------------------------------
        # Generate drum sequence
        # -------------------------------------------------------------------
        drum_midi = pretty_midi.PrettyMIDI()
        drum_track = pretty_midi.Instrument(program=0, is_drum=True, name=f"Drums ({genre})")

        if MODEL:
            inp = torch.tensor([input_ids], dtype=torch.long)
            with torch.no_grad():
                out = MODEL.generate(
                    inp,
                    max_length=MAX_LENGTH,
                    temperature=1.0 + energy * complexity_factor,
                    do_sample=True,
                )
            gen_ids = out[0].cpu().numpy()

            for t, token in enumerate(gen_ids):
                if token == 0:
                    continue
                onset = t / 16.0
                pitch = vocab.get(token, 36)  # default kick
                drum_track.notes.append(
                    pretty_midi.Note(
                        velocity=int(100 * energy),
                        pitch=pitch,
                        start=onset,
                        end=onset + 0.1,
                    )
                )
        else:
            # ----------------------------------------------------------------
            # Very simple fallback groove: kick on 1 & 3, snare on 2 & 4
            # ----------------------------------------------------------------
            beats = sorted(set(int(o * 2) for o in onsets))  # quarter-note grid
            for b in beats:
                sec = b * 0.5  # back to seconds (assuming 120 BPM)
                if b % 2 == 0:  # bars start at 0,2,4…
                    pitch = vocab.get(1, 36)  # kick
                else:
                    pitch = vocab.get(2, 38)  # snare
                drum_track.notes.append(
                    pretty_midi.Note(
                        velocity=int(100 * energy),
                        pitch=pitch,
                        start=sec,
                        end=sec + 0.1,
                    )
                )

        drum_midi.instruments.append(drum_track)

        # -------------------------------------------------------------------
        # Save & return
        # -------------------------------------------------------------------
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, f"drumify_{os.path.basename(midi_path)}")
        drum_midi.write(out_path)
        logging.info(f"Generated drums ({genre}) → {out_path}")

        return {
            "status": "success",
            "input_file": midi_path,
            "output_file": out_path,
            "tempo": tempo,
            "energy": energy,
            "genre": genre,
            "rhythmic_variability": variability,
        }

    except Exception as exc:
        logging.exception("Drumify failed")
        return {"error": str(exc)}
