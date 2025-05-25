"""
Audio Roles Plugin
Identifies instrument roles in audio (e.g., drums, bass).
"""
import os
import logging
import numpy as np
import librosa
from typing import List, Dict
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/audio_roles.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="analyze_roles",
    description="Identifies instrument roles",
    input_type="wav",
    phase=1,
    requires=["analyze_features"]
)
def analyze_roles(audio_paths: List[str], output_dir: str, analysis_context: dict) -> List[Dict]:
    """
    Identifies instrument roles based on spectral features.

    Args:
        audio_paths (List[str]): List of WAV file paths.
        output_dir (str): Directory to save outputs.
        analysis_context (dict): Context from previous plugins.

    Returns:
        List[Dict]: Role identification results for each file.
    """
    results = []
    os.makedirs(output_dir, exist_ok=True)

    for audio_path in audio_paths:
        try:
            if not os.path.exists(audio_path):
                logging.error(f"Audio file not found: {audio_path}")
                results.append({"file": audio_path, "error": "File not found"})
                continue

            # Retrieve features from context
            features = next((r for r in analysis_context.get("analyze_features", []) if r["file"] == audio_path), None)
            if not features or "error" in features:
                logging.warning(f"No valid features for {audio_path}")
                results.append({"file": audio_path, "error": "Feature analysis unavailable"})
                continue

            # Heuristic role detection based on spectral centroid and bpm
            spectral_centroid = features.get("spectral_centroid", 0)
            roles = {}
            roles["drums"] = features.get("bpm", 0) > 80  # High BPM suggests drums
            roles["bass"] = spectral_centroid < 500  # Low centroid suggests bass

            result = {
                "file": audio_path,
                "roles": roles
            }
            logging.info(f"Role analysis completed for {audio_path}: {result}")
            results.append(result)

        except Exception as e:
            logging.error(f"Error analyzing roles for {audio_path}: {str(e)}")
            results.append({"file": audio_path, "error": str(e)})

    return results