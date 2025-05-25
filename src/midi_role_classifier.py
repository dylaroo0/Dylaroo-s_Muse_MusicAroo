"""
MIDI Role Classifier Plugin
Classifies MIDI tracks as melody, bass, drums, or chords.
"""
import os
import logging
from typing import Dict
from music21 import converter
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/midi_role_classifier.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="classify_midi_roles",
    description="Classifies MIDI tracks as melody, bass, drums, or chords",
    input_type="midi",
    phase=2
)
def classify_midi_roles(midi_path: str, output_dir=None, analysis_context=None) -> Dict:
    """
    Classifies MIDI tracks based on heuristics.

    Args:
        midi_path (str): Path to the MIDI file.
        output_dir (str, optional): Output directory (unused).
        analysis_context (dict, optional): Shared pipeline context.

    Returns:
        Dict: Role classification results or error message.
    """
    try:
        if not os.path.exists(midi_path):
            logging.error(f"MIDI file not found: {midi_path}")
            return {"file": midi_path, "error": "File not found"}

        # Load MIDI
        score = converter.parse(midi_path)
        logging.info(f"Loaded MIDI for role classification: {midi_path}")

        roles = {}
        for i, part in enumerate(score.parts):
            track_name = f"track{i+1}"
            notes = part.flat.notes
            if not notes:
                roles[track_name] = "unknown"
                continue

            # Compute average pitch
            pitches = [n.pitch.midi for n in notes if hasattr(n, 'pitch')]
            avg_pitch = sum(pitches) / len(pitches) if pitches else 0

            # Heuristic classification
            if part.hasElementOfClass('Percussion'):
                roles[track_name] = "drums"
            elif avg_pitch < 48:  # Low pitches
                roles[track_name] = "bass"
            elif len(notes) > 50 and avg_pitch > 60:  # High note density and pitch
                roles[track_name] = "melody"
            else:
                roles[track_name] = "chords"

        result = {
            "file": midi_path,
            "roles": roles
        }
        logging.info(f"Role classification completed for {midi_path}: {result}")

        # Update shared analysis_context if present
        if analysis_context is not None:
            analysis_context["midi_roles"] = roles

        return result

    except Exception as e:
        logging.error(f"Error classifying MIDI roles for {midi_path}: {str(e)}")
        return {"file": midi_path, "error": str(e)}
