"""
Melody Predictor Plugin
Predicts melody continuations using a Markov chain model.
"""
import os
import logging
import random
from typing import Dict
from music21 import converter, stream, note
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/melody_predictor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="predict_melody",
    description="Predicts melody continuations using a Markov chain",
    input_type="midi",
    phase=6,
    requires=["analyze_midi"]
)
def predict_melody(midi_path: str, output_dir: str = "reports/predicted", analysis_context: dict = None) -> Dict:
    """
    Predicts a melody continuation using a Markov chain.

    Args:
        midi_path (str): Path to the input MIDI file.
        output_dir (str): Directory to save the predicted MIDI file.
        analysis_context (dict): Context from previous plugins.

    Returns:
        Dict: Predicted melody details or error message.
    """
    try:
        if not os.path.exists(midi_path):
            logging.error(f"MIDI file not found: {midi_path}")
            return {"file": midi_path, "error": "File not found"}

        os.makedirs(output_dir, exist_ok=True)

        # Load MIDI
        score = converter.parse(midi_path)
        logging.info(f"Loaded MIDI for melody prediction: {midi_path}")

        # Extract notes from the first part
        notes = score.parts[0].flat.notes
        pitch_sequence = [n.pitch.nameWithOctave for n in notes if hasattr(n, 'pitch')]

        # Build a simple Markov chain (first-order)
        transitions = {}
        for i in range(len(pitch_sequence) - 1):
            current = pitch_sequence[i]
            next_note = pitch_sequence[i + 1]
            if current not in transitions:
                transitions[current] = []
            transitions[current].append(next_note)

        # Predict continuation (10 notes)
        last_note = pitch_sequence[-1] if pitch_sequence else "C4"
        predicted_notes = []
        for _ in range(10):
            if last_note in transitions and transitions[last_note]:
                next_note = random.choice(transitions[last_note])
            else:
                next_note = "C4"  # Fallback
            predicted_notes.append(note.Note(next_note, quarterLength=1.0))
            last_note = next_note

        # Create a new stream with the predicted notes
        s = stream.Stream()
        s.extend(predicted_notes)
        logging.info(f"Predicted {len(predicted_notes)} notes for {midi_path}")

        # Save as MIDI
        base = os.path.splitext(os.path.basename(midi_path))[0]
        output_path = os.path.join(output_dir, f"{base}_predicted.mid")
        s.write('midi', output_path)
        logging.info(f"Saved predicted melody to {output_path}")

        return {
            "file": midi_path,
            "output_path": output_path,
            "predicted_notes": [str(n) for n in predicted_notes],
            "status": "prediction_completed"
        }

    except Exception as e:
        logging.error(f"Error predicting melody for {midi_path}: {str(e)}")
        return {"file": midi_path, "error": str(e)}