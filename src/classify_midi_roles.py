"""
Classify MIDI Roles Plugin
Assigns musical roles (melody, bass, harmony, percussion) to each track in a MIDI file.
Returns a dictionary of {track_name: role}.
"""

import os
import pretty_midi
import logging
from plugin_registry import register_plugin

logging.basicConfig(
    filename='logs/classify_midi_roles.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="classify_midi_roles",
    description="Assigns musical roles (melody, bass, harmony, percussion) to each track in a MIDI file",
    input_type="midi",
    phase=2
)
def classify_midi_roles(midi_path, output_dir=None, analysis_context=None):
    try:
        if not os.path.exists(midi_path):
            logging.error(f"MIDI file not found: {midi_path}")
            return {"status": "error", "error": "File not found"}
        
        midi_data = pretty_midi.PrettyMIDI(midi_path)
        roles = {}
        for idx, inst in enumerate(midi_data.instruments):
            name = inst.name if inst.name else f"Track {idx+1}"
            # Guess role
            if inst.is_drum:
                role = "percussion"
            else:
                program = inst.program
                # General MIDI program numbers:
                # 32-39 = Bass
                # 0-7 = Piano (likely harmony)
                # 40-47 = Strings (harmony/melody)
                # 56-63 = Brass (harmony/melody)
                # 64-71 = Reed (melody/harmony)
                if 32 <= program <= 39:
                    role = "bass"
                elif 0 <= program <= 7:
                    role = "harmony"
                elif 40 <= program <= 71:
                    role = "melody"
                else:
                    role = "unknown"
            roles[name] = role
        
        logging.info(f"Roles for {midi_path}: {roles}")

        result = {
            "status": "success",
            "file": midi_path,
            "roles": roles
        }

        if analysis_context is not None:
            analysis_context["midi_roles"] = roles

        return result

    except Exception as e:
        logging.error(f"Error classifying roles in {midi_path}: {e}")
        return {"status": "error", "error": str(e)}
