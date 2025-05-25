"""
Harmony Generator Plugin
Augments or generates chord progressions for MIDI/audio inputs, respecting complex progressions.
"""
import os
import logging
import json
import random
from typing import List, Dict, Any
from plugin_registry import register_plugin
import pretty_midi
import music21

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
    description="Augments or generates chord progressions for MIDI/audio inputs",
    input_type="midi",
    phase=5,
    requires=["audio_analysis", "jsymbolic_bridge"]
)
def harmony_generator(midi_paths: List[str], output_dir: str = "reports", analysis_context: dict = None) -> List[Dict[str, Any]]:
    """
    Generates or augments chord progressions with subtle variations.

    Args:
        midi_paths (List[str]): List of MIDI file paths.
        output_dir (str): Directory to save MIDI and JSON reports.
        analysis_context (dict): Context with analysis features.

    Returns:
        List[Dict[str, Any]]: Results with progression options.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        logger.info("Starting harmony generation process")

        # Progression templates (optional, for generation)
        progression_templates = {
            "subtle": [[[60, 64, 67], [65, 69, 72], [62, 65, 69], [60, 64, 67]], ["I", "IV", "ii", "I"]],
            "folk": [[[60, 64, 67], [67, 71, 74], [62, 65, 69], [65, 69, 72]], ["I", "V", "ii", "IV"]]
        }

        results = []
        for midi_path in midi_paths:
            if not midi_path.lower().endswith(".mid"):
                logger.warning(f"Skipping non-MIDI file: {midi_path}")
                results.append({"status": "error", "file": midi_path, "error": "Not a MIDI file", "plugin_name": "harmony_generator"})
                continue

            try:
                # Load MIDI
                midi = pretty_midi.PrettyMIDI(midi_path)
                stream = music21.converter.parse(midi_path)

                # Extract features
                audio_features = analysis_context.get("audio_analysis", [{}])[0] if analysis_context else {}
                jsymbolic_features = analysis_context.get("jsymbolic_bridge", [{}])[0] if analysis_context else {}
                tempo = audio_features.get("tempo", 120)
                timbre = audio_features.get("timbre", {"spectral_centroid": 1500})
                swing = audio_features.get("swing", 0.5)
                mood = audio_features.get("mood", jsymbolic_features.get("mood", "moderate"))
                key = jsymbolic_features.get("key", audio_features.get("key", "C major"))
                rhythmic_complexity = jsymbolic_features.get("rhythmic_complexity", 0.5)

                # Analyze existing chords
                try:
                    chords = stream.chordify().flat.getElementsByClass("Chord")
                    existing_chords = [(c.pitches, c.offset) for c in chords]
                except:
                    existing_chords = []
                    logger.warning(f"No chords detected in {midi_path}, generating new progression")

                # Key analysis
                try:
                    key_obj = stream.analyze("key")
                    key = key_obj.tonic.name + (" minor" if key_obj.mode == "minor" else " major")
                except:
                    logger.warning(f"Key detection failed for {midi_path}, using {key}")

                key_root = music21.pitch.Pitch(key.split()[0]).midi
                is_minor = "minor" in key.lower()

                progression_options = []
                if existing_chords:
                    # Augment existing chords
                    for style in ["subtle"]:
                        option_midi = pretty_midi.PrettyMIDI()
                        chord_track = pretty_midi.Instrument(program=0, is_drum=False, name=f"Chords_{style}")
                        velocity = 60 if mood == "calm" else 70 if mood == "upbeat" else 65
                        velocity += 5 if timbre["spectral_centroid"] > 2000 else -5

                        for pitches, offset in existing_chords:
                            start_time = float(offset) * (60 / tempo)
                            for pitch in pitches:
                                midi_note = pitch.midi
                                chord_track.notes.append(
                                    pretty_midi.Note(
                                        velocity=velocity,
                                        pitch=midi_note,
                                        start=start_time,
                                        end=start_time + (60 / tempo)
                                    )
                                )

                        # Save MIDI
                        output_midi = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(midi_path))[0]}__harmony_{style}.mid")
                        option_midi.write(output_midi)
                        logger.info(f"Generated {style} harmony MIDI: {output_midi}")

                        progression_options.append({
                            "style": style,
                            "midi_file": output_midi,
                            "chords": ["Existing"] * len(existing_chords)
                        })
                else:
                    # Generate new progressions
                    for style, (template, chord_names) in progression_templates.items():
                        velocity = 60 if mood == "calm" else 70 if mood == "upbeat" else 65
                        velocity += 5 if timbre["spectral_centroid"] > 2000 else -5

                        transposed = []
                        for chord in template:
                            transposed_chord = [note + (key_root - 60) for note in chord]
                            if is_minor:
                                transposed_chord = [note - 1 if i == 1 else note for i, note in enumerate(transposed_chord)]
                            transposed.append(transposed_chord)

                        option_midi = pretty_midi.PrettyMIDI()
                        chord_track = pretty_midi.Instrument(program=0, is_drum=False, name=f"Chords_{style}")
                        beat_duration = 60 / tempo * 4
                        for i, chord in enumerate(transposed):
                            start_time = i * beat_duration
                            swing_offset = swing * 0.05 * rhythmic_complexity if i % 2 else 0
                            for note in chord:
                                chord_track.notes.append(
                                    pretty_midi.Note(
                                        velocity=velocity,
                                        pitch=note,
                                        start=start_time + swing_offset,
                                        end=start_time + beat_duration
                                    )
                                )
                        option_midi.instruments.append(chord_track)

                        output_midi = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(midi_path))[0]}__harmony_{style}.mid")
                        option_midi.write(output_midi)
                        logger.info(f"Generated {style} harmony MIDI: {output_midi}")

                        progression_options.append({
                            "style": style,
                            "midi_file": output_midi,
                            "chords": chord_names
                        })

                # Save JSON report
                result = {
                    "status": "success",
                    "file": midi_path,
                    "progression_options": progression_options,
                    "key": key,
                    "tempo": tempo,
                    "timbre": timbre,
                    "swing": swing,
                    "mood": mood,
                    "rhythmic_complexity": rhythmic_complexity,
                    "message": f"Generated/augmented harmony options for {midi_path}",
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