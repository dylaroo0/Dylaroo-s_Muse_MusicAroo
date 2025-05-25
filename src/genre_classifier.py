"""
Genre Classifier Plugin
Classifies the genre of an audio file.
"""
import os
import logging
import librosa
import numpy as np
from typing import Dict
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/genre_classifier.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="genre_classifier",
    description="Classifies the genre of an audio file",
    input_type="wav",
    phase=6
)
def genre_classifier(audio_path: str, output_dir: str = "reports", analysis_context: dict = None) -> Dict:
    """
    Classifies the genre of an audio file (simplified).

    Args:
        audio_path (str): Path to the input WAV file.
        output_dir (str): Directory to save the output report.
        analysis_context (dict): Context from previous plugins.

    Returns:
        Dict: Genre classification result.
    """
    try:
        if not os.path.exists(audio_path):
            logging.error(f"Audio file not found: {audio_path}")
            return {"error": "Audio file not found"}

        # Load audio features from analysis_context if available
        features = analysis_context.get("audio_analysis", {}).get("features", {})
        if not features:
            y, sr = librosa.load(audio_path)
            features = {
                "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
            }

        # Simplified genre classification (placeholder)
        genre = "rock" if features["spectral_centroid"] > 3000 else "classical"

        # Save to JSON
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"genre_{os.path.basename(audio_path)}.json")
        result = {"genre": genre}
        with open(output_path, 'w') as f:
            import json
            json.dump(result, f, indent=2)

        logging.info(f"Genre classified: {genre}")
        return {
            "status": "success",
            "input_file": audio_path,
            "output_path": output_path,
            "genre": genre
        }

    except Exception as e:
        logging.error(f"Error in genre_classifier: {str(e)}")
        return {"error": str(e)}