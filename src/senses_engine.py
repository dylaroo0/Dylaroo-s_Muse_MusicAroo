"""
Senses Plugin
Analyzes MIDI to create a musical 'sense profile' (smell, taste, touch, sight, hearing).
"""
import os
import logging
from typing import List, Dict
from music21 import converter, key, tempo, meter

from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/senses.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="analyze_senses",
    description="Generates a musical senses profile from MIDI",
    input_type="midi",
    phase=2,
    requires=["midi_analysis"]
)
def analyze_senses(midi_paths: List[str], output_dir: str = "reports", analysis_context: dict = None) -> List[Dict]:
    results = []
    os.makedirs(output_dir, exist_ok=True)

    for midi_path in midi_paths:
        try:
            if not os.path.exists(midi_path):
                logging.error(f"MIDI file not found: {midi_path}")
                results.append({"file": midi_path, "error": "File not found"})
                continue

            score = converter.parse(midi_path)

            # Default senses
            smell = "fresh"
            taste = "sweet"
            touch = "soft"
            sight = "bright"
            hearing = "steady"

            # Extract basic info
            tempo_indication = score.metronomeMarkBoundaries()
            tempos = [mm[2].number for mm in tempo_indication if mm[2]]
            avg_tempo = sum(tempos) / len(tempos) if tempos else 120

            key_signature = score.analyze('key')

            time_signatures = [n[2].ratioString for n in score.timeSignatureBoundaries() if n[2]]
            tsig_set = set(time_signatures)

            notes = score.flat.notes
            pitch_span = max([n.pitch.midi for n in notes]) - min([n.pitch.midi for n in notes]) if notes else 0

            # Smell (fresh/rotten/burning)
            if key_signature.mode == 'major' and avg_tempo > 100:
                smell = "fresh"
            elif key_signature.mode == 'minor' and avg_tempo > 130:
                smell = "burning"
            elif key_signature.mode == 'minor' and avg_tempo < 90:
                smell = "rotten"

            # Taste (sweet/sour)
            if "7/8" in tsig_set or "5/4" in tsig_set:
                taste = "sour"
            elif key_signature.mode == 'major':
                taste = "sweet"

            # Touch (soft/rough)
            if avg_tempo < 90:
                touch = "soft"
            elif avg_tempo > 150:
                touch = "rough"

            # Sight (bright/dark)
            if key_signature.mode == 'major':
                sight = "bright"
            else:
                sight = "dark"

            # Hearing (steady/chaotic)
            if len(tsig_set) > 2:
                hearing = "chaotic"

            senses_profile = {
                "file": midi_path,
                "smell": smell,
                "taste": taste,
                "touch": touch,
                "sight": sight,
                "hearing": hearing,
                "tempo": avg_tempo,
                "key": str(key_signature),
                "pitch_span": pitch_span
            }

            logging.info(f"Senses analysis complete for {midi_path}: {senses_profile}")
            results.append(senses_profile)

        except Exception as e:
            logging.error(f"Error analyzing senses for {midi_path}: {str(e)}")
            results.append({"file": midi_path, "error": str(e)})

    return results
