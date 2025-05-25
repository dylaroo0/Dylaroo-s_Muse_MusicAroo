"""
MIDI Analysis Plugin
Extracts basic MIDI features like note onsets and durations.
"""
import os
import logging
import pretty_midi
from typing import Dict
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/midi_analysis.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="midi_analysis",
    description="Extracts basic MIDI features like note onsets and durations",
    input_type="midi",
    phase=2
)
def midi_analysis(midi_path: str, output_dir: str = "reports", analysis_context: dict = None) -> Dict:
    """
    Extracts MIDI features from a MIDI file.

    Args:
        midi_path (str): Path to the input MIDI file.
        output_dir (str): Directory to save the output report.
        analysis_context (dict): Context from previous plugins (not used here).

    Returns:
        Dict: Extracted MIDI features.
    """
    try:
        if not os.path.exists(midi_path):
            logging.error(f"MIDI file not found: {midi_path}")
            return {"error": "MIDI file not found"}

        # Load MIDI file
        midi_data = pretty_midi.PrettyMIDI(midi_path)
        if not midi_data.instruments:
            logging.error("No instruments found in MIDI file")
            return {"error": "No instruments found"}

        # Extract features
        notes = midi_data.instruments[0].notes  # First instrument
        onsets = [note.start for note in notes]
        durations = [note.end - note.start for note in notes]

        result = {
            "note_count": len(notes),
            "avg_onset": float(sum(onsets) / len(onsets)) if onsets else 0.0,
            "avg_duration": float(sum(durations) / len(durations)) if durations else 0.0
        }

        # Save to JSON
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"midi_analysis_{os.path.basename(midi_path)}.json")
        with open(output_path, 'w') as f:
            import json
            json.dump(result, f, indent=2)

        logging.info(f"MIDI features extracted: {result}")
        return {
            "status": "success",
            "input_file": midi_path,
            "output_path": output_path,
            "features": result
        }

    except Exception as e:
        logging.error(f"Error in midi_analysis: {str(e)}")
        return {"error": str(e)}