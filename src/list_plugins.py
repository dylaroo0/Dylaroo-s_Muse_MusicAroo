#!/usr/bin/env python3
"""
List Plugins Utility
Lists all registered plugins in the pipeline.
"""
import logging
import sys
from plugin_registry import plugins

# ─── Logging Configuration ──────────────────────────────────────────────────
LOG_FILE = "logs/list_plugins.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("list_plugins")

def list_plugins() -> dict:
    """
    Lists all registered plugins.

    Returns:
        dict: Status and plugin details.
    """
    try:
        all_plugins = plugins()
        plugin_list = []
        for p in all_plugins:
            plugin_list.append({
                "name": p.name,
                "description": p.description,
                "input_type": p.input_type,
                "phase": p.phase,
                "requires": p.requires or []
            })

        logger.info(f"Listed {len(plugin_list)} plugins: {[p['name'] for p in plugin_list]}")
        print("🔌 Available plugins:")
        for idx, plugin in enumerate(plugin_list, start=1):
            reqs = ", ".join(plugin["requires"]) if plugin["requires"] else "None"
            print(f"  {idx}. {plugin['name']} (input: {plugin['input_type']}, phase: {plugin['phase']}, requires: {reqs})")
            print(f"     → {plugin['description']}")
        return {"status": "success", "plugins": plugin_list}

    except Exception as e:
        logger.error(f"Error listing plugins: {e}", exc_info=True)
        print(f"Error listing plugins: {e}", file=sys.stderr)
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    result = list_plugins()
    if result.get("status") != "success":
        sys.exit(1)
