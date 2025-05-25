"""
Stem Separator Plugin
Separates WAV audio into stems using Demucs.
"""
import os
import logging
from typing import Dict
from demucs import separate
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/stem_separator.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="separate_stems",
    description="Separates WAV audio into stems using Demucs",
    input_type="wav",
    phase=3
)
def separate_stems(audio_path: str, output_dir: str = "reports/stems") -> Dict:
    """
    Separates WAV audio into stems using Demucs.

    Args:
        audio_path (str): Path to the WAV file.
        output_dir (str): Directory to save outputs.

    Returns:
        Dict: Stem separation results or error message.
    """
    try:
        if not os.path.exists(audio_path):
            logging.error(f"Audio file not found: {audio_path}")
            return {"file": audio_path, "error": "File not found"}

        base = os.path.splitext(os.path.basename(audio_path))[0]
        stem_dir = os.path.join(output_dir, base)
        os.makedirs(stem_dir, exist_ok=True)

        # Run Demucs to separate stems
        separate.main(["--out", stem_dir, audio_path])
        logging.info(f"Separated stems for {audio_path} into {stem_dir}")

        # Collect stem files
        stems = [os.path.join(stem_dir, f) for f in os.listdir(stem_dir) if f.endswith(".wav")]

        return {"file": audio_path, "stems": stems}

    except Exception as e:
        logging.error(f"Error separating stems for {audio_path}: {str(e)}")
        return {"file": audio_path, "error": str(e)}