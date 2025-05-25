import subprocess
import os
import json
from pathlib import Path
from src.plugin_registry import register_plugin

@register_plugin("essentia_analysis")
def essentia_bridge(wav_path: str) -> dict:
    """
    Runs Essentia Streaming Extractor (via WSL) on the given WAV file.
    Outputs a rich JSON dict of musical features, or skips if not supported.
    """

    # Convert Windows path to WSL format
    path = Path(wav_path).resolve()
    drive_letter = path.drive[0].lower()
    wsl_input = f"/mnt/{drive_letter}{str(path)[2:].replace('\\', '/')}"
    
    # Prepare output JSON path (same name but .json)
    out_json = path.with_suffix('.essentia.json')
    wsl_output = f"/mnt/{drive_letter}{str(out_json)[2:].replace('\\', '/')}"

    # WSL command
    cmd = [
        "wsl",
        "essentia_streaming_extractor_music",
        wsl_input,
        wsl_output
    ]

    print(f"🔍 Running Essentia on: {wav_path}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print("❌ Essentia error:", result.stderr.strip())
            return {}

        # Load JSON result
        if out_json.exists():
            with open(out_json, 'r') as f:
                data = json.load(f)
            return data
        else:
            print("❌ Output JSON not found.")
            return {}

    except FileNotFoundError:
        print("⚠️ WSL or Essentia not installed — skipping Essentia plugin.")
        return {}
    except subprocess.TimeoutExpired:
        print("⏱️ Essentia took too long — skippin
