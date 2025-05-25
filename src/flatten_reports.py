import os
import logging
import json
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/flatten_reports.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main(reports: List[Dict[str, Any]], output_dir: str) -> Dict[str, Any]:
    try:
        logger.info("Flattening reports into a master report")
        
        # Flatten reports into a single master report
        master_report = {
            "audio_mastering": [],
            "audio_features": [],
            "generate_melody": []
        }
        
        for report in reports:
            if report["status"] == "success":
                plugin_name = report.get("plugin_name", "unknown")
                if plugin_name in master_report:
                    master_report[plugin_name].append(report)
                else:
                    logger.warning(f"Unknown plugin name in report: {plugin_name}")
        
        # Save the master report to JSON
        output_file = os.path.join(output_dir, "master_report.json")
        with open(output_file, 'w') as f:
            json.dump(master_report, f, indent=4)
        logger.info(f"Master report saved to {output_file}")
        
        return {
            "status": "success",
            "output_file": output_file,
            "master_report": master_report
        }
    
    except Exception as e:
        logger.error(f"Error flattening reports: {e}")
        return {"status": "error", "error": str(e)}