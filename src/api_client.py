# ────────────────────────────────────────────────────────────────
# File: src/api_client.py  (full replacement)
# ────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import logging
import os
import requests
import pathlib
from typing import Dict, Any, Optional

from plugin_registry import PLUGINS

logger = logging.getLogger(__name__)
API_BASE = os.getenv("AIMUSIC_API_URL", "http://127.0.0.1:8000")


def analyze_file(
    file_path: str,
    plugin_name: str,
    output_dir: str = "reports/tmp",
    analysis_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Call another registered plugin directly inside the same process."""
    plugin = next(p for p in PLUGINS if p.name == plugin_name)
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    return plugin.module(file_path, output_dir, analysis_context=analysis_context or {})


def request_analysis(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """POST to the FastAPI backend if running; otherwise fall back to local call."""
    url = f"{API_BASE.rstrip('/')}/{endpoint.lstrip('/')}"
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        logger.warning(f"API request failed ({exc}); using local plugin")
        plugin_name = endpoint.replace("-", "_")
        file_path = payload.get("file_path") or payload.get("input_file")
        return analyze_file(file_path, plugin_name)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("plugin")
    ap.add_argument("file")
    ap.add_argument("--out", default="reports/tmp")
    ns = ap.parse_args()

    result = analyze_file(ns.file, ns.plugin, ns.out)
    print(json.dumps(result, indent=2))
