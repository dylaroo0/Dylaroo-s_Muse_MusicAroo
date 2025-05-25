"""
Essentia Bridge Plugin
Runs Essentia analysis on WAV files via WSL.
"""
import subprocess
import json
import os
import logging
from typing import List, Dict
from plugin_registry import register_plugin

# Configure logging to match project directory
log_dir = "logs" if not os.getenv("DOCKER_ENV") else "/app/logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'essentia_bridge.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="essentia_analysis",
    description="Runs Essentia analysis on WAV files via WSL",
    input_type="wav",
    phase=1
)
def run_essentia_bridge(audio_paths: List[str], output_dir: str = "reports", analysis_context: dict = None) -> List[Dict]:
    """
    Runs Essentia analysis on a list of WAV files via WSL.

    Args:
        audio_paths (List[str]): List of paths to the WAV files.
        output_dir (str): Directory to save outputs.
        analysis_context (dict): Context from previous plugins.

    Returns:
        List[Dict]: Analysis results or error messages.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)

        # Validate files
        valid_paths = []
        for audio_path in audio_paths:
            if not os.path.exists(audio_path):
                logging.error(f"Audio file not found: {audio_path}")
                return [{"file": audio_path, "error": "File not found"}]
            valid_paths.append(audio_path)

        # Convert Windows paths to WSL paths
        wsl_audio_paths = [
            f"/mnt/{p[0].lower()}{p[2:].replace('\\\\', '/').replace('\\', '/')}"
            for p in valid_paths
        ]
        logging.info(f"Translated paths for WSL: {wsl_audio_paths}")

        # Determine runner script path
        # Local WSL: Use the project directory path
        # Docker: Use the /app/ directory
        wsl_runner_path = "/mnt/c/Users/12502/Documents/AI_music_assistant/essentia_runner.py" if not os.getenv("DOCKER_ENV") else "/app/essentia_runner.py"
        result = subprocess.run(
            ["wsl", "test", "-f", wsl_runner_path],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logging.error(f"Essentia runner script not found: {wsl_runner_path}")
            return [{"error": "Essentia runner script not found"}]

        # Run Essentia analysis (batch mode)
        cmd = ["wsl", "python3", wsl_runner_path] + wsl_audio_paths
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60 * len(audio_paths)  # Adjust timeout for batch
        )

        if result.returncode != 0:
            logging.error(f"Essentia analysis failed: {result.stderr}")
            return [{"error": result.stderr.strip()}]

        # Parse results
        analysis = json.loads(result.stdout.strip())
        logging.info(f"Essentia analysis completed: {analysis}")
        return analysis if isinstance(analysis, list) else [analysis]

    except subprocess.TimeoutExpired:
        logging.error(f"Essentia analysis timed out for {audio_paths}")
        return [{"error": "Analysis timed out"}]
    except Exception as e:
        logging.error(f"Error in Essentia bridge for {audio_paths}: {str(e)}")
        return [{"error": str(e)}]