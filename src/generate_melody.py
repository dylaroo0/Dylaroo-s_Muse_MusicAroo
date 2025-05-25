import os
import logging
import pretty_midi
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/generate_melody.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main(file_path: str, output_dir: str) -> Dict[str, Any]:
    try:
        logger.info(f"Generating melody from MIDI file: {file_path}")
        
        # Load MIDI file
        midi_data = pretty_midi.PrettyMIDI(file_path)
        
        # Find the track with the highest average pitch (likely the melody)
        max_avg_pitch = -float('inf')
        melody_track = None
        for instrument in midi_data.instruments:
            if instrument.is_drum:
                continue
            pitches = [note.pitch for note in instrument.notes]
            if pitches:
                avg_pitch = sum(pitches) / len(pitches)
                if avg_pitch > max_avg_pitch:
                    max_avg_pitch = avg_pitch
                    melody_track = instrument
        
        if not melody_track:
            raise ValueError("No suitable melody track found in MIDI file")
        
        # Transpose the melody up by 5 semitones
        for note in melody_track.notes:
            note.pitch += 5
        
        # Create a new MIDI file with only the transposed melody
        new_midi = pretty_midi.PrettyMIDI()
        new_midi.instruments.append(melody_track)
        
        # Save the new MIDI file
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = os.path.join(output_dir, f"generated_melody_{base_name}.mid")
        new_midi.write(output_file)
        logger.info(f"Generated melody saved to {output_file}")
        
        return {
            "status": "success",
            "input_file": file_path,
            "output_file": output_file
        }
    
    except Exception as e:
        logger.error(f"Error generating melody from {file_path}: {e}")
        return {"status": "error", "error": str(e)}