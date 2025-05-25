"""
MusicXML Converter Plugin
Converts MIDI files to MusicXML format.
"""
import os
import logging
import music21
from typing import Dict
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/musicxml_converter.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="musicxml_converter",
    description="Converts MIDI files to MusicXML format",
    input_type="midi",
    phase=4
)
def musicxml_converter(midi_path: str, output_dir: str = "reports", analysis_context: dict = None) -> Dict:
    """
    Converts a MIDI file to MusicXML.

    Args:
        midi_path (str): Path to the input MIDI file.
        output_dir (str): Directory to save the output MusicXML.
        analysis_context (dict): Context from previous plugins (not used here).

    Returns:
        Dict: Result of the conversion process.
    """
    try:
        if not os.path.exists(midi_path):
            logging.error(f"MIDI file not found: {midi_path}")
            return {"error": "MIDI file not found"}

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"musicxml_{os.path.basename(midi_path)}.musicxml")

        # Convert MIDI to MusicXML
        stream = music21.converter.parse(midi_path)
        stream.write('musicxml', fp=output_path)

        logging.info(f"MIDI converted to MusicXML: {output_path}")
        return {
            "status": "success",
            "input_file": midi_path,
            "output_file": output_path
        }

    except Exception as e:
        logging.error(f"Error in musicxml_converter: {str(e)}")
        return {"error": str(e)}