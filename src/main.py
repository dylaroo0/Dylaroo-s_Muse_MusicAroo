# src/main.py
# -*- coding: utf-8 -*-
"""
main.py – pipeline orchestrator

* Auto-imports every .py in src/
* Executes plugins in phase order
* Passes analysis_context only if the target function accepts it
"""

from __future__ import annotations
import argparse
import importlib
import inspect
import logging
import os
import pkgutil
import sys
import pathlib
from typing import Dict, Any, List

# Logging -----------------------------------------------------------
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  |  %(levelname)-7s |  %(message)s",
    handlers=[
        logging.FileHandler("logs/main.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("main")

# Ensure src/ is on path so we can import plugin_registry
SRC_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

# Auto-import every module in src/ so that @register_plugin calls happen
def _import_all(src: pathlib.Path) -> None:
    for info in pkgutil.iter_modules([str(src)]):
        if info.name in {"main"} or info.name.startswith("_"):
            continue
        if info.name in sys.modules:
            continue
        try:
            importlib.import_module(info.name)
        except Exception as exc:
            logger.warning(f"⚠️  Skipped module {info.name}: {exc}")

_import_all(SRC_DIR)

# Import only the PLUGINS list from your registry
from plugin_registry import PLUGINS  # noqa: E402

# Helpers -----------------------------------------------------------
def _collect(dir_path: str, exts: tuple[str, ...]) -> List[str]:
    p = pathlib.Path(dir_path)
    if not p.exists():
        return []
    return [str(f) for f in p.iterdir() if f.is_file() and f.suffix.lower() in exts]

def _call_plugin(func, infile: str, out_dir: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke plugin, passing ctx only if signature includes it."""
    sig = inspect.signature(func)
    if "analysis_context" in sig.parameters:
        return func(infile, out_dir, analysis_context=ctx)
    else:
        return func(infile, out_dir)

def _handle(res: Dict[str, Any], name: str, infile: str,
            reports: List[Dict[str, Any]], ctx: Dict[str, Any]) -> None:
    res["plugin_name"] = name
    if res.get("status") == "success":
        reports.append(res)
        # merge any new context keys
        ctx.update({k: v for k, v in res.items()
                    if k not in {"status", "plugin_name"}})
        logger.info(f"✔ {name} succeeded on {infile}")
    else:
        logger.warning(f"✖ {name} failed on {infile}: {res.get('error')}")

# Pipeline ----------------------------------------------------------
def run_pipeline(audio_dir: str, midi_dir: str,
                 xml_dir: str, out_dir: str) -> Dict[str, Any]:
    logger.info("🚀  Pipeline started")
    os.makedirs(out_dir, exist_ok=True)

    audio_files = _collect(audio_dir, (".wav", ".flac", ".mp3"))
    midi_files  = _collect(midi_dir,  (".mid", ".midi"))
    xml_files   = _collect(xml_dir,   (".xml", ".musicxml"))

    # sort plugins by (phase, name)
    plugins = sorted(PLUGINS, key=lambda p: (p.phase, p.name.lower()))
    print("Loaded plugins:")
    for i, p in enumerate(plugins, 1):
        print(f"  {i:2}. {p.name.ljust(22)} phase {p.phase}")

    ctx: Dict[str, Any] = {}
    reports: List[Dict[str, Any]] = []

    for p in plugins:
        print(f"\nRunning plugin: {p.name}")
        logger.info(f"Running plugin: {p.name}")

        if p.input_type == "audio":
            for f in audio_files:
                _handle(_call_plugin(p.module, f, out_dir, ctx),
                        p.name, f, reports, ctx)
        elif p.input_type == "midi":
            for f in midi_files:
                _handle(_call_plugin(p.module, f, out_dir, ctx),
                        p.name, f, reports, ctx)
        elif p.input_type == "musicxml":
            for f in xml_files:
                _handle(_call_plugin(p.module, f, out_dir, ctx),
                        p.name, f, reports, ctx)
        elif p.input_type == "report":
            _handle(_call_plugin(p.module, reports, out_dir, ctx),
                    p.name, "<reports>", reports, ctx)

    logger.info("✅  Pipeline finished")
    print(f"\nAll done! Master report at {out_dir}/master_report.json")
    return {"status": "success", "reports": reports}

# CLI ----------------------------------------------------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="AI Music Assistant pipeline")
    ap.add_argument("--audio_dir",     required=True)
    ap.add_argument("--midi_dir",      required=True)
    ap.add_argument("--musicxml_dir",  required=True)
    ap.add_argument("--out_dir",       required=True)
    ns = ap.parse_args()

    run_pipeline(ns.audio_dir, ns.midi_dir, ns.musicxml_dir, ns.out_dir)
