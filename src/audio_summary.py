"""
Audio Summary Plugin
Summarizes analysis results from previous plugins.
"""
import os
import logging
from typing import List, Dict
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/audio_summary.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="generate_summary",
    description="Summarizes analysis results",
    input_type="wav",
    phase=1,
    requires=["analyze_wav", "analyze_features", "analyze_vocals", "analyze_roles", "extract_structure"]
)
def generate_summary(audio_paths: List[str], output_dir: str, analysis_context: dict) -> List[Dict]:
    """
    Summarizes analysis results from previous plugins.

    Args:
        audio_paths (List[str]): List of WAV file paths.
        output_dir (str): Directory to save outputs.
        analysis_context (dict): Context from previous plugins.

    Returns:
        List[Dict]: Summary results for each file.
    """
    results = []
    os.makedirs(output_dir, exist_ok=True)

    for audio_path in audio_paths:
        try:
            if not os.path.exists(audio_path):
                logging.error(f"Audio file not found: {audio_path}")
                results.append({"file": audio_path, "error": "File not found"})
                continue

            # Aggregate data from previous plugins
            waveform = next((r for r in analysis_context.get("analyze_wav", []) if r["file"] == audio_path), {})
            features = next((r for r in analysis_context.get("analyze_features", []) if r["file"] == audio_path), {})
            vocals = next((r for r in analysis_context.get("analyze_vocals", []) if r["file"] == audio_path), {})
            roles = next((r for r in analysis_context.get("analyze_roles", []) if r["file"] == audio_path), {})
            structure = next((r for r in analysis_context.get("extract_structure", []) if r["file"] == audio_path), {})

            # Check for errors
            errors = [r.get("error") for r in [waveform, features, vocals, roles, structure] if "error" in r]
            if errors:
                logging.warning(f"Errors in analysis for {audio_path}: {errors}")
                results.append({"file": audio_path, "error": "Incomplete analysis data"})
                continue

            # Generate summary
            summary = (
                f"Tempo: {features.get('bpm', 'Unknown')} BPM, "
                f"Spectral Centroid: {features.get('spectral_centroid', 'Unknown')} Hz, "
                f"Has Vocals: {vocals.get('has_vocals', 'Unknown')}, "
                f"Roles: {roles.get('roles', {})}, "
                f"Structure: {structure.get('segments', [])}"
            )

            result = {
                "file": audio_path,
                "summary": summary
            }
            logging.info(f"Summary generated for {audio_path}: {result}")
            results.append(result)

        except Exception as e:
            logging.error(f"Error generating summary for {audio_path}: {str(e)}")
            results.append({"file": audio_path, "error": str(e)})

    return results