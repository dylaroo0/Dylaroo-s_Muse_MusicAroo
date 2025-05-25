"""
Harmony Generator Plugin
Generates harmonic progressions for MIDI inputs, optimized for acoustic guitar songs.
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
        logging.FileHandler("logs/harmony_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@register_plugin(
    name="harmony_generator",
    description="Generates harmonic progressions for MIDI inputs, optimized for acoustic guitar songs",
    input_type="midi",
    phase=5,
    requires=["audio_analysis"]
)
def harmony_generator(midi_paths: List[str], output_dir: str = "reports", analysis_context: dict = None) -> List[Dict[str, Any]]:
    """
    Generates a chord progression (e.g., I-IV-V-I) for MIDI inputs.

    Args:
        midi_paths (List[str]): List of MIDI file paths (.mid).
        output_dir (str): Directory to save MIDI and JSON reports.
        analysis_context (dict): Context from previous plugins (e.g., key, tempo).

    Returns:
        List[Dict[str, Any]]: Results for each input file.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        logger.info("Starting harmony generation process")

        # Default chord progression: I-IV-V-I in C major
        chords = [
            [60, 64, 67],  # C major (C, E, G)
            [65, 69, 72],  # F major (F, A, C)
            [67, 71, 74],  # G major (G, B, D)
            [60, 64, 67]   # C major
        ]

        results = []
        for midi_path in midi_paths:
            if not midi_path.lower().endswith(".mid"):
                logger.warning(f"Skipping non-MIDI file: {midi_path}")
                results.append({"status": "error", "file": midi_path, "error": "Not a MIDI file", "plugin_name": "harmony_generator"})
                continue

            try:
                # Load MIDI file
                midi = pretty_midi.PrettyMIDI(midi_path)
                
                # Get key and tempo from analysis_context
                key = analysis_context.get("audio_analysis", [{}])[0].get("key", "C major") if analysis_context else "C major"
                tempo = analysis_context.get("audio_analysis", [{}])[0].get("tempo", 120) if analysis_context else 120

                # Create chord track
                chord_track = pretty_midi.Instrument(program=0, is_drum=False, name="Chords")
                beat_duration = 60 / tempo * 4  # Duration of one chord (4 beats)
                for i, chord in enumerate(chords):
                    start_time = i * beat_duration
                    for note in chord:
                        chord_track.notes.append(
                            pretty_midi.Note(
                                velocity=65,  # Soft for acoustic guitar
                                pitch=note,
                                start=start_time,
                                end=start_time + beat_duration
                            )
                        )
                midi.instruments.append(chord_track)

                # Save MIDI with chords
                output_midi = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(midi_path))[0]}__harmony_generator.mid")
                midi.write(output_midi)
                logger.info(f"Generated harmony MIDI: {output_midi}")

                # Save JSON report
                result = {
                    "status": "success",
                    "file": midi_path,
                    "output_midi": output_midi,
                    "chords": ["I", "IV", "V", "I"],
                    "key": key,
                    "tempo": tempo,
                    "message": f"Generated harmony for {midi_path}",
                    "plugin_name": "harmony_generator"
                }
                output_json = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(midi_path))[0]}__harmony_generator.json")
                with open(output_json, "w") as f:
                    json.dump(result, f, indent=4)
                results.append(result)
                logger.info(f"Harmony generation completed for file: {midi_path}")

            except Exception as e:
                logger.error(f"Error processing {midi_path}: {str(e)}")
                results.append({"status": "error", "file": midi_path, "error": str(e), "plugin_name": "harmony_generator"})

        return results

    except Exception as e:
        logger.error(f"Plugin harmony_generator failed: {str(e)}")
        return [{"status": "error", "error": str(e), "plugin_name": "harmony_generator"}]