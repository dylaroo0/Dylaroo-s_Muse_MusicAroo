"""
Music Generator Plugin
Generates music from a prompt.
"""
import os
import logging
import music21
from typing import Dict
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/music_generator.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="music_generator",
    description="Generates music from a prompt",
    input_type="prompt",
    phase=5
)
def music_generator(prompt: Dict, output_dir: str = "reports", analysis_context: dict = None) -> Dict:
    """
    Generates a simple melody based on a prompt.

    Args:
        prompt (Dict): Prompt containing bars and optional input file.
        output_dir (str): Directory to save the output MIDI.
        analysis_context (dict): Context from previous plugins (not used here).

    Returns:
        Dict: Result of the generation process.
    """
    try:
        bars = prompt.get("bars", 4)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "generated_melody.mid")

        # Generate a simple melody
        stream = music21.stream.Stream()
        for _ in range(bars * 4):  # 4 notes per bar
            note = music21.note.Note("C4")
            note.duration.quarterLength = 1
            stream.append(note)

        # Save to MIDI
        stream.write('midi', fp=output_path)
        logging.info(f"Music generated: {output_path}")

        return {
            "status": "success",
            "output_file": output_path,
            "bars": bars
        }

    except Exception as e:
        logging.error(f"Error in music_generator: {str(e)}")
        return {"error": str(e)}