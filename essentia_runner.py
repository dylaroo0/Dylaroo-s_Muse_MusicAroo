"""
Essentia Runner Script
Runs Essentia audio analysis in WSL.
"""
import os
import subprocess
import logging
import json

# Configure logging
logging.basicConfig(
    filename='logs/essentia_runner.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_essentia(audio_path: str, output_path: str) -> dict:
    """
    Runs Essentia analysis on an audio file in WSL.

    Args:
        audio_path (str): Path to the input audio file.
        output_path (str): Path to save the analysis output.

    Returns:
        dict: Analysis results.
    """
    try:
        if not os.path.exists(audio_path):
            logging.error(f"Audio file not found: {audio_path}")
            return {"error": "Audio file not found"}

        # Convert Windows path to WSL path
        wsl_audio_path = audio_path.replace('\\', '/').replace('C:', '/mnt/c')
        wsl_output_path = output_path.replace('\\', '/').replace('C:', '/mnt/c')

        # Run Essentia command in WSL
        cmd = [
            "wsl",
            "python3", "-c",
            f"import essentia.standard as es; audio = es.MonoLoader(filename='{wsl_audio_path}')(); "
            f"bpm = es.RhythmExtractor2013()(audio)[0]; "
            f"with open('{wsl_output_path}', 'w') as f: f.write(str(bpm))"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logging.error(f"Essentia failed: {result.stderr}")
            return {"error": f"Essentia failed: {result.stderr}"}

        # Read the output
        with open(output_path, 'r') as f:
            bpm = float(f.read())

        logging.info(f"Essentia analysis completed: BPM = {bpm}")
        return {"status": "success", "bpm": bpm}

    except Exception as e:
        logging.error(f"Error in essentia_runner: {str(e)}")
        return {"error": str(e)}