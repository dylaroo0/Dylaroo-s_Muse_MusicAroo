"""
Feature to Prompt Plugin
Converts j# src/style_generators.py
from typing import List, Dict
import pretty_midi

def generate_pattern(
    section: Dict, style: str="indie-rock", subdivisions:int=8
) -> List[pretty_midi.Note]:
    """
    Return a list of Note objects for this section:
      - style: "reggae", "indie-rock", "spoon-mode", etc.
      - subdivisions: 8 for 8ths, 12 for triplets, etc.
    """
    notes = []
    # TODO: switch on style to pick groove & fill logic
    return notes

def generate_fill(time: float, style: str) -> List[pretty_midi.Note]:
    """
    One-bar fill at `time` offset, based on style.
    """
    return []
Symbolic features into creative prompts for Magenta generation.
"""
import os
import logging
from typing import Dict
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/feature_to_prompt.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="feature_to_prompt",
    description="Converts jSymbolic features into prompts for generation",
    input_type="midi",
    phase=5,
    requires=["jsymbolic_bridge"]
)
def feature_to_prompt(midi_path: str, output_dir: str = "reports", analysis_context: dict = None) -> Dict:
    """
    Creates a generation prompt based on extracted symbolic features.

    Args:
        midi_path (str): Path to the MIDI file.
        output_dir (str): Directory to save the output prompt (JSON).
        analysis_context (dict): Context from previous plugins.

    Returns:
        Dict: Generated prompt.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)

        # Get jSymbolic analysis
        features = analysis_context.get("jsymbolic_bridge", {}).get(midi_path, {}).get("features", {})
        if not features:
            logging.warning(f"No jSymbolic features available for {midi_path}")
            return {"error": "No jSymbolic features found."}

        prompt = {}

        # Interpret features into prompt hints
        avg_interval = features.get("Average Melodic Interval", 2.0)
        rhythmic_var = features.get("Rhythmic Variability", 0.5)
        pitch_range = features.get("Range of Pitch Classes", 12)

        # Melody style
        if avg_interval < 3.0:
            prompt["melodic_motion"] = "stepwise"
        elif avg_interval < 6.0:
            prompt["melodic_motion"] = "moderate leaps"
        else:
            prompt["melodic_motion"] = "wide leaps"

        # Rhythmic style
        if rhythmic_var < 0.3:
            prompt["rhythm_feel"] = "steady/simple"
        elif rhythmic_var < 0.7:
            prompt["rhythm_feel"] = "groovy/syncopated"
        else:
            prompt["rhythm_feel"] = "complex/polyrhythmic"

        # Pitch range
        if pitch_range < 8:
            prompt["pitch_range"] = "narrow"
        elif pitch_range < 16:
            prompt["pitch_range"] = "medium"
        else:
            prompt["pitch_range"] = "wide"

        prompt["input_file"] = midi_path
        prompt["style_hint"] = "symbolic"  # Tag it came from analysis

        # Save prompt
        prompt_path = os.path.join(output_dir, f"{os.path.basename(midi_path)}_prompt.json")
        import json
        with open(prompt_path, "w") as f:
            json.dump(prompt, f, indent=2)

        logging.info(f"Prompt generated for {midi_path}: {prompt}")
        return {"file": midi_path, "prompt": prompt, "prompt_path": prompt_path}

    except Exception as e:
        logging.error(f"Error generating prompt for {midi_path}: {str(e)}")
        return {"file": midi_path, "error": str(e)}
