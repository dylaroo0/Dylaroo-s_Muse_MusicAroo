"""
Audio Visualizer Plugin
Generates waveform visualizations for audio files.
"""
import os
import logging
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from typing import List, Dict
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/audio_visualizer.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="visualize_audio",
    description="Generates audio visualizations",
    input_type="wav",
    phase=1
)
def visualize_audio(audio_paths: List[str], output_dir: str, analysis_context: dict) -> List[Dict]:
    """
    Generates waveform visualizations for WAV files.

    Args:
        audio_paths (List[str]): List of WAV file paths.
        output_dir (str): Directory to save outputs.
        analysis_context (dict): Context from previous plugins.

    Returns:
        List[Dict]: Visualization results for each file.
    """
    results = []
    os.makedirs(output_dir, exist_ok=True)

    for audio_path in audio_paths:
        try:
            if not os.path.exists(audio_path):
                logging.error(f"Audio file not found: {audio_path}")
                results.append({"file": audio_path, "error": "File not found"})
                continue

            # Load audio
            audio, sr = sf.read(audio_path)
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)
            logging.info(f"Loaded audio for visualization: {audio_path}")

            # Generate waveform plot
            base = os.path.splitext(os.path.basename(audio_path))[0]
            output_path = os.path.join(output_dir, f"{base}_waveform.png")
            time = np.arange(len(audio)) / sr
            plt.figure(figsize=(10, 4))
            plt.plot(time, audio, color='blue')
            plt.title(f"Waveform of {base}")
            plt.xlabel("Time (s)")
            plt.ylabel("Amplitude")
            plt.savefig(output_path)
            plt.close()
            logging.info(f"Generated waveform visualization: {output_path}")

            result = {
                "file": audio_path,
                "visualization": output_path
            }
            results.append(result)

        except Exception as e:
            logging.error(f"Error visualizing audio {audio_path}: {str(e)}")
            results.append({"file": audio_path, "error": str(e)})

    return results