"""
List Stages Utility
Lists all phases and their associated plugins.
"""
import logging
from plugin_registry import PLUGINS

# Configure logging
logging.basicConfig(
    filename='logs/list_stages.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def list_stages() -> dict:
    """
    Lists all phases and their plugins.

    Returns:
        dict: Phases and their plugins.
    """
    try:
        stages = {}
        for plugin in PLUGINS:
            phase = plugin["phase"]
            if phase not in stages:
                stages[phase] = []
            stages[phase].append(plugin["name"])
        
        logging.info(f"Listed stages: {stages}")
        print("📋 Pipeline stages:")
        for phase in sorted(stages.keys()):
            print(f"  Phase {phase}: {', '.join(stages[phase])}")
        
        return {"status": "success", "stages": stages}
    except Exception as e:
        logging.error(f"Error listing stages: {str(e)}")
        return {"error": str(e)}