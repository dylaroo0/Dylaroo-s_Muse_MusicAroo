"""
MusicXML Validator Plugin
Validates MusicXML files for correctness and compatibility.
"""
import os
import logging
from typing import Dict
import xml.etree.ElementTree as ET
from plugin_registry import register_plugin

# Configure logging
logging.basicConfig(
    filename='logs/musicxml_validator.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@register_plugin(
    name="validate_musicxml",
    description="Validates MusicXML files for correctness",
    input_type="musicxml",
    phase=4
)
def validate_musicxml(musicxml_path: str) -> Dict:
    """
    Validates a MusicXML file for correctness.

    Args:
        musicxml_path (str): Path to the MusicXML file.

    Returns:
        Dict: Validation results or error message.
    """
    try:
        if not os.path.exists(musicxml_path):
            logging.error(f"MusicXML file not found: {musicxml_path}")
            return {"file": musicxml_path, "error": "File not found"}

        # Parse MusicXML file
        tree = ET.parse(musicxml_path)
        root = tree.getroot()
        logging.info(f"Parsed MusicXML file: {musicxml_path}")

        # Check for required elements
        required_elements = ["score-partwise", "part-list", "part"]
        missing_elements = [elem for elem in required_elements if root.find(elem) is None]
        errors = []

        if missing_elements:
            errors.extend([f"Missing required element: {elem}" for elem in missing_elements])

        # Check for parts
        parts = root.findall("part")
        if not parts:
            errors.append("No parts found in MusicXML")

        # Check for measures in each part
        for part in parts:
            measures = part.findall("measure")
            if not measures:
                errors.append(f"No measures found in part {part.get('id', 'unknown')}")

        if errors:
            logging.warning(f"Validation failed for {musicxml_path}: {errors}")
            return {"file": musicxml_path, "status": "validation_failed", "errors": errors}

        logging.info(f"Validation passed for {musicxml_path}")
        return {"file": musicxml_path, "status": "validation_passed", "errors": []}

    except ET.ParseError as e:
        logging.error(f"XML parsing error for {musicxml_path}: {str(e)}")
        return {"file": musicxml_path, "status": "validation_failed", "errors": [f"XML parsing error: {str(e)}"]}
    except Exception as e:
        logging.error(f"Error validating MusicXML {musicxml_path}: {str(e)}")
        return {"file": musicxml_path, "status": "validation_failed", "errors": [str(e)]}