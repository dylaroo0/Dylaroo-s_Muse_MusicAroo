"""
MIDI Visualizer Plugin
Generates piano-roll visualizations for MIDI files.
"""
import os
import logging
import pretty_midi
import matplotlib.pyplot as plt
from typing import Dict
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/midi_visualizer.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="visualize_midi",
    description="Generates piano-roll visualizations for MIDI files",
    input_type="midi",
    phase=2
)
def visualize_midi(midi_path: str, output_dir: str = "reports/visualizations") -> Dict:
    """
    Generates piano-roll visualizations for MIDI files.

    Args:
        midi_path (str): Path to the MIDI file.
        output_dir (str): Directory to save outputs.

    Returns:
        Dict: Visualization results or error message.
    """
    try:
        if not os.path.exists(midi_path):
            logging.error(f"MIDI file not found: {midi_path}")
            return {"file": midi_path, "error": "File not found"}

        base = os.path.splitext(os.path.basename(midi_path))[0]
        output_path = os.path.join(output_dir, f"{base}_pianoroll.png")
        os.makedirs(output_dir, exist_ok=True)

        # Load MIDI
        midi_data = pretty_midi.PrettyMIDI(midi_path)
        logging.info(f"Loaded MIDI for visualization: {midi_path}")

        # Generate piano roll
        piano_roll = midi_data.get_piano_roll(fs=100)
        plt.figure(figsize=(12, 6))
        plt.imshow(piano_roll, aspect='auto', origin='lower', cmap='viridis')
        plt.title(f"Piano Roll of {base}")
        plt.xlabel("Time (ticks)")
        plt.ylabel("Pitch")
        plt.colorbar(label='Velocity')
        plt.savefig(output_path)
        plt.close()
        logging.info(f"Generated piano-roll visualization: {output_path}")

        return {"file": midi_path, "visualization": output_path}

    except Exception as e:
        logging.error(f"Error visualizing MIDI {midi_path}: {str(e)}")
        return {"file": midi_path, "error": str(e)}