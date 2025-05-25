# -*- coding: utf-8 -*-
"""
Audio Analysis Plugin
Extracts basic audio features from WAV files.
"""
import os
import logging
import json

import librosa
import numpy as np

from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/audio_analysis.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="audio_analysis",
    input_type="audio",
    description="Extracts basic audio features like RMS and spectral centroid from WAV files",
    phase=1
)
def audio_analysis(path: str, output_dir: str = "reports", analysis_context: dict = None) -> dict:
    """
    Extracts basic audio features like RMS and spectral centroid.
    
    Args:
        path (str): Path to the input WAV file.
        output_dir (str): Directory to save the output report.
        analysis_context (dict, optional): Context from previous plugins.
        
    Returns:
        dict: Analysis status and features.
    """
    try:
        if not os.path.exists(path):
            logging.error(f"Audio file not found: {path}")
            return {"status": "error", "error": "Audio file not found", "input": path}

        # Load audio, preserve native sample rate
        y, sr = librosa.load(path, sr=None)

        # Compute features
        rms_val = float(np.mean(librosa.feature.rms(y=y)))
        spec_cent = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))

        features = {
            "rms": round(rms_val, 6),
            "spectral_centroid": round(spec_cent, 6)
        }

        result = {
            "status": "success",
            "input_file": path,
            "features": features
        }

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        # Write per-file JSON report
        base = os.path.splitext(os.path.basename(path))[0]
        report_path = os.path.join(output_dir, f"audio_analysis_{base}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        logging.info(f"Audio features extracted for {path}: {features}")
        return result

    except Exception as e:
        logging.error(f"Error in audio_analysis for {path}: {e}", exc_info=True)
        return {"status": "error", "error": str(e), "input": path}
