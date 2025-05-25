"""
Style Transfer Plugin
Applies style transformations to MIDI inputs for acoustic guitar songs.
"""
import os
import logging
import json
from typing import List, Dict, Any
from plugin_registry import register_plugin
import pretty_midi

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/style_transfer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@register_plugin(
    name="style_transfer",
    description="Applies style transformations to MIDI inputs for acoustic guitar songs",
    input_type="midi",
    phase=5,
    requires=["genre_classifier"]
)
def style_transfer(midi_paths: List[str], output_dir: str = "reports", analysis_context: dict = None) -> List[Dict[str, Any]]:
    """
    Applies a folk-style transformation to MIDI inputs.

    Args:
        midi_paths (List[str]): List of MIDI file paths (.mid).
        output_dir (str): Directory to save transformed MIDI and JSON reports.
        analysis_context (dict): Context from previous plugins (e.g., genre).

    Returns:
        List[Dict[str, Any]]: Results for each input file.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        logger.info("Starting style transfer process")

        results = []
        for midi_path in midi_paths:
            if not midi_path.lower().endswith(".mid"):
                logger.warning(f"Skipping non-MIDI file: {midi_path}")
                results.append({"status": "error", "file": midi_path, "error": "Not a MIDI file", "plugin_name": "style_transfer"})
                continue

            try:
                # Load MIDI file
                midi = pretty_midi.PrettyMIDI(midi_path)
                
                # Apply folk-style transformation
                genre = analysis_context.get("genre_classifier", [{}])[0].get("genre", "folk") if analysis_context else "folk"
                for instrument in midi.instruments:
                    if genre == "folk":
                        for note in instrument.notes:
                            note.velocity = min(note.velocity, 85)  # Softer for acoustic
                            note.start += (note.start % 0.1) * 0.03  # Subtle timing variation
                            note.end += (note.end % 0.1) * 0.03

                # Save transformed MIDI
                output_midi = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(midi_path))[0]}__style_transfer.mid")
                midi.write(output_midi)
                logger.info(f"Generated transformed MIDI: {output_midi}")

                # Save JSON report
                result = {
                    "status": "success",
                    "file": midi_path,
                    "output_midi": output_midi,
                    "applied_style": genre,
                    "message": f"Applied {genre} style to {midi_path}",
                    "plugin_name": "style_transfer"
                }
                output_json = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(midi_path))[0]}__style_transfer.json")
                with open(output_json, "w") as f:
                    json.dump(result, f, indent=4)
                results.append(result)
                logger.info(f"Style transfer completed for file: {midi_path}")

            except Exception as e:
                logger.error(f"Error processing {midi_path}: {str(e)}")
                results.append({"status": "error", "file": midi_path, "error": str(e), "plugin_name": "style_transfer"})

        return results

    except Exception as e:
        logger.error(f"Plugin style_transfer failed: {str(e)}")
        return [{"status": "error", "error": str(e), "plugin_name": "style_transfer"}]