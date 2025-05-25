"""
Score Engraver Plugin
Generates sheet music (PDF, PNG) from MusicXML files using MuseScore in WSL.
"""
import os
import subprocess
import logging
from typing import Dict
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/score_engraver.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="engrave_score",
    description="Generates sheet music from MusicXML using MuseScore",
    input_type="musicxml",
    phase=4,
    requires=["convert_to_musicxml"]
)
def engrave_score(musicxml_path: str, output_dir: str = "reports/scores") -> Dict:
    """
    Generates sheet music from a MusicXML file using MuseScore in WSL.

    Args:
        musicxml_path (str): Path to the MusicXML file.
        output_dir (str): Directory to save PDF and PNG outputs.

    Returns:
        Dict: Sheet music paths or error message.
    """
    try:
        if not os.path.exists(musicxml_path):
            logging.error(f"MusicXML file not found: {musicxml_path}")
            return {"file": musicxml_path, "error": "File not found"}

        base = os.path.splitext(os.path.basename(musicxml_path))[0]
        pdf_path = os.path.join(output_dir, f"{base}.pdf")
        png_path = os.path.join(output_dir, f"{base}.png")
        os.makedirs(output_dir, exist_ok=True)

        # Convert Windows path to WSL path
        wsl_musicxml_path = f"/mnt/{musicxml_path[0].lower()}{musicxml_path[2:].replace('\\\\', '/').replace('\\', '/')}"
        wsl_pdf_path = f"/mnt/{pdf_path[0].lower()}{pdf_path[2:].replace('\\\\', '/').replace('\\', '/')}"
        wsl_png_path = f"/mnt/{png_path[0].lower()}{png_path[2:].replace('\\\\', '/').replace('\\', '/')}"

        # Check if MuseScore is available in WSL
        muse_check = subprocess.run(
            ["wsl", "musescore3", "--version"],
            capture_output=True,
            text=True
        )
        if muse_check.returncode != 0:
            logging.error("MuseScore not found in WSL")
            return {"file": musicxml_path, "error": "MuseScore not found in WSL"}

        # Run MuseScore to generate PDF
        subprocess.run(
            ["wsl", "musescore3", "-o", wsl_pdf_path, wsl_musicxml_path],
            check=True,
            capture_output=True,
            text=True
        )
        logging.info(f"Generated PDF for {musicxml_path}: {pdf_path}")

        # Run MuseScore to generate PNG
        subprocess.run(
            ["wsl", "musescore3", "-o", wsl_png_path, wsl_musicxml_path],
            check=True,
            capture_output=True,
            text=True
        )
        logging.info(f"Generated PNG for {musicxml_path}: {png_path}")

        return {
            "file": musicxml_path,
            "pdf_path": pdf_path,
            "png_path": png_path,
            "status": "engraving_completed"
        }

    except subprocess.CalledProcessError as e:
        logging.error(f"MuseScore failed for {musicxml_path}: {e.stderr}")
        return {"file": musicxml_path, "error": f"MuseScore failed: {e.stderr}"}
    except Exception as e:
        logging.error(f"Error engraving score for {musicxml_path}: {str(e)}")
        return {"file": musicxml_path, "error": str(e)}