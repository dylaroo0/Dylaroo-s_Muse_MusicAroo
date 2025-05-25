import os
import logging
import librosa
import numpy as np
from typing import Dict, Any
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/audio_features.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main(file_path: str, output_dir: str) -> Dict[str, Any]:
    try:
        logger.info(f"Extracting features from audio file: {file_path}")
        
        # Load audio
        audio, sr = librosa.load(file_path, sr=None, mono=True)
        
        # Extract features
        tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
        rms = np.mean(librosa.feature.rms(y=audio))
        
        # Prepare features dictionary
        features = {
            "tempo": float(tempo),
            "spectral_centroid": float(spectral_centroid),
            "rms": float(rms)
        }
        
        # Save features to JSON
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = os.path.join(output_dir, f"{base_name}_features.json")
        with open(output_file, 'w') as f:
            json.dump(features, f, indent=4)
        logger.info(f"Features saved to {output_file}")
        
        return {
            "status": "success",
            "input_file": file_path,
            "output_file": output_file,
            "features": features
        }
    
    except Exception as e:
        logger.error(f"Error extracting features from {file_path}: {e}")
        return {"status": "error", "error": str(e)}