"""
MIDI Exporter Plugin
Exports MIDI annotations to JAMS format.
"""
import os
import logging
import jams
from typing import Dict
from music21 import converter
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/midi_exporter.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="export_midi",
    description="Exports MIDI annotations to MusicXML and JAMS",
    input_type="midi",
    phase=2,
    requires=["analyze_midi"]
)
def export_midi(midi_path: str, output_dir: str = "reports/exports") -> Dict:
    """
    Exports MIDI annotations to JAMS format.

    Args:
        midi_path (str): Path to the MIDI file.
        output_dir (str): Directory to save outputs.
        analysis_context (dict): Context from previous plugins.

    Returns:
        Dict: Export results or error message.
    """
    try:
        if not os.path.exists(midi_path):
            logging.error(f"MIDI file not found: {midi_path}")
            return {"file": midi_path, "error": "File not found"}

        base = os.path.splitext(os.path.basename(midi_path))[0]
        jams_path = os.path.join(output_dir, f"{base}.jams")
        os.makedirs(output_dir, exist_ok=True)

        # Load MIDI
        score = converter.parse(midi_path)
        logging.info(f"Loaded MIDI for export: {midi_path}")

        # Create JAMS object
        jam = jams.JAMS()
        jam.file_metadata.duration = score.highestTime

        # Add annotations (e.g., chords from analysis)
        chord_anno = jam.annotations.add(namespace='chord')
        # Placeholder for chord data (could pull from analysis_context)
        for i in range(5):
            chord_anno.append(time=i*4, duration=4, value=f"C:{i+1}")

        # Save JAMS
        jam.save(jams_path)
        logging.info(f"Exported MIDI annotations to {jams_path}")

        return {"file": midi_path, "exported": jams_path}

    except Exception as e:
        logging.error(f"Error exporting MIDI {midi_path}: {str(e)}")
        return {"file": midi_path, "error": str(e)}