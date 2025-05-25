# src/drummaroo_plugin.py
from __future__ import annotations
import os
import pretty_midi, numpy as np
from plugin_registry import register_plugin
from typing import Dict, Any

@register_plugin(
    name="drummaroo",
    description="DrummAroo stub (test-mode) generates a simple 4-bar kick pattern",
    input_type=["midi","wav"],
    phase=3
)
def drummaroo(
    input_path: str,
    output_dir: str = "reports",
    analysis_context: dict | None = None,
    test_mode: bool = True
) -> Dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)
    # stub: always 4 bars, kick on downbeat
    midi = pretty_midi.PrettyMIDI()
    drum = pretty_midi.Instrument(is_drum=True, program=0, name="DrummAroo Stub")
    for bar in range(4):
        onset = float(bar)
        note = pretty_midi.Note(velocity=100, pitch=36, start=onset, end=onset+0.1)
        drum.notes.append(note)
    midi.instruments.append(drum)
    out = os.path.join(output_dir, f"drummaroo_stub.mid")
    midi.write(out)
    return {"status":"success","output_file":out}
