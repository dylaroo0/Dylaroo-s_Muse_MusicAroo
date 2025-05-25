import os
import logging
from typing import Dict, Any
import soundfile as sf
import librosa
import numpy as np
from pedalboard import Pedalboard, Compressor, HighShelfFilter, Gain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/audio_mastering.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main(file_path: str, output_dir: str) -> Dict[str, Any]:
    try:
        logger.info(f"Processing audio file: {file_path}")
        
        # Load audio
        audio, sr = librosa.load(file_path, sr=None, mono=False)
        if len(audio.shape) == 1:
            audio = np.asfortranarray([audio, audio])
        
        logger.info(f"Input audio shape: {audio.shape}, dtype: {audio.dtype}, sample rate: {sr}")
        
        # Create a mastering chain with Pedalboard
        board = Pedalboard([
            Compressor(threshold_db=-20, ratio=4),
            HighShelfFilter(cutoff_frequency_hz=8000, gain_db=2),
            Gain(gain_db=3)
        ])
        mastered_audio = board(audio, sr)
        
        # Ensure the audio is in the correct format for soundfile
        mastered_audio = np.array(mastered_audio, dtype=np.float32)
        # Transpose from (channels, samples) to (samples, channels) for soundfile
        mastered_audio = mastered_audio.T
        
        logger.info(f"Mastered audio shape: {mastered_audio.shape}, dtype: {mastered_audio.dtype}")
        
        # Save the mastered audio
        output_file = os.path.join(output_dir, f"mastered_{os.path.basename(file_path)}")
        sf.write(output_file, mastered_audio, sr)
        logger.info(f"Mastered audio saved to {output_file}")
        
        return {
            "status": "success",
            "input_file": file_path,
            "output_file": output_file,
            "sample_rate": sr
        }
    
    except Exception as e:
        logger.error(f"Error processing audio file {file_path}: {e}")
        return {"status": "error", "error": str(e)}