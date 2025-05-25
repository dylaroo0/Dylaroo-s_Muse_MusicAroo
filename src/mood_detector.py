"""
Mood Detector Plugin
Detects the mood of MIDI files based on key and dynamics.
"""
import os
import logging
from typing import Dict
from music21 import converter
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/mood_detector.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="detect_mood",
    description="Detects the mood of MIDI files",
    input_type="midi",
    phase=6,
    requires=["analyze_midi"]
)
def detect_mood(midi_path: str, output_dir: str = "reports/moods", analysis_context: dict = None) -> Dict:
    """
    Detects the mood of a MIDI file based on key and dynamics.

    Args:
        midi_path (str): Path to the MIDI file.
        output_dir (str): Directory to save outputs.
        analysis_context (dict): Context from previous plugins.

    Returns:
        Dict: Mood detection results or error message.
    """
    try:
        if not os.path.exists(midi_path):
            logging.error(f"MIDI file not found: {midi_path}")
            return {"file": midi_path, "error": "File not found"}

        os.makedirs(output_dir, exist_ok=True)

        # Load MIDI analysis from context
        midi_analysis = next((r for r in analysis_context.get("analyze_midi", []) if r["file"] == midi_path), None)
        if not midi_analysis or "error" in midi_analysis:
            logging.warning(f"No MIDI analysis available for {midi_path}")
            return {"file": midi_path, "error": "MIDI analysis unavailable"}

        # Load MIDI
        score = converter.parse(midi_path)
        logging.info(f"Loaded MIDI for mood detection: {midi_path}")

        # Heuristic mood detection
        key_str = midi_analysis.get("key", "C major")
        velocities = [n.volume.velocity for n in score.parts[0].flat.notes if n.volume.velocity is not None]
        avg_velocity = sum(velocities) / len(velocities) if velocities else 60

        if "major" in key_str.lower() and avg_velocity > 80:
            mood = "happy"
        elif "minor" in key_str.lower() and avg_velocity < 60:
            mood = "sad"
        else:
            mood = "neutral"

        result = {
            "file": midi_path,
            "mood": mood,
            "confidence": 0.9  # Simulated confidence score
        }
        logging.info(f"Mood detection completed for {midi_path}: {result}")
        return result

    except Exception as e:
        logging.error(f"Error detecting mood for {midi_path}: {str(e)}")
        return {"file": midi_path, "error": str(e)}