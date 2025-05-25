"""
Audio to MIDI Plugin
Transcribes audio to MIDI using basic_pitch.
"""
import os
import logging
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
from typing import Dict
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/audio_to_midi.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="audio_to_midi",
    description="Transcribes audio to MIDI using basic_pitch",
    input_type="wav",
    phase=3
)
def audio_to_midi(audio_path: str, output_dir: str = "reports", analysis_context: dict = None) -> Dict:
    """
    Transcribes audio to MIDI.

    Args:
        audio_path (str): Path to the input WAV file.
        output_dir (str): Directory to save the output MIDI.
        analysis_context (dict): Context from previous plugins (not used here).

    Returns:
        Dict: Result of the transcription process.
    """
    try:
        if not os.path.exists(audio_path):
            logging.error(f"Audio file not found: {audio_path}")
            return {"error": "Audio file not found"}

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"transcribed_{os.path.basename(audio_path)}.mid")

        # Transcribe audio to MIDI
        midi_data, _, _ = predict(
            audio_path,
            model_path=ICASSP_2022_MODEL_PATH,
            onset_threshold=0.5,
            frame_threshold=0.3
        )

        # Save MIDI file
        midi_data.write(output_path)
        logging.info(f"Audio transcribed to MIDI: {output_path}")

        return {
            "status": "success",
            "input_file": audio_path,
            "output_file": output_path
        }

    except Exception as e:
        logging.error(f"Error in audio_to_midi: {str(e)}")
        return {"error": str(e)}