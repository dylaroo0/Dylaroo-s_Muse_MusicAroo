# src/plugin_registry.py

import os
import sys
import pkgutil
import importlib
from typing import Callable, Dict, List, Any

# ─── Global registry ──────────────────────────────────────────────────────────
PLUGINS: List[Dict[str, Any]] = []

def register_plugin(
    *,
    name: str,
    input_type: str,
    phase: int = 1,
    requires: List[str] = None
) -> Callable[[Callable], Callable]:
    """
    Decorator to register a plugin.

    :param name: Unique plugin name.
    :param input_type: Type of input this plugin consumes.
    :param phase: Execution phase (lower runs earlier).
    :param requires: List of other plugin names this one depends on.
    """
    requires = requires or []

    def decorator(fn: Callable) -> Callable:
        PLUGINS.append({
            "name": name,
            "input_type": input_type,
            "phase": phase,
            "requires": requires,
            "func": fn
        })
        return fn

    return decorator

def import_all(src_dir: str = "src") -> None:
    """
    Dynamically import every module under the given directory
    so that all @register_plugin decorators execute.

    :param src_dir: Filesystem path to your package directory.
    """
    # Ensure project root is on sys.path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Walk the package and import all modules
    pkg_name = os.path.basename(os.path.normpath(src_dir))
    for finder, module_name, is_pkg in pkgutil.walk_packages([src_dir], f"{pkg_name}."):
        try:
            importlib.import_module(module_name)
        except Exception:
            # Skip modules that fail to import
            continue

def import_all_from(src_dir: str) -> None:
    """
    Alias for import_all, for external scripts that expect import_all_from.
    """
    import_all(src_dir)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Plugin registry CLI")
    parser.add_argument(
        "--list", action="store_true",
        help="List all registered plugins after auto-import."
    )
    parser.add_argument(
        "src_dir", nargs="?", default="src",
        help="Directory to import modules from (default: src)."
    )
    args = parser.parse_args()

    import_all(args.src_dir)

    if args.list:
        if not PLUGINS:
            print("No plugins registered.")
        else:
            print("Registered plugins:")
            for p in PLUGINS:
                print(f"  - {p['name']} (phase {p['phase']}, input {p['input_type']})")
    else:
        parser.print_help()
