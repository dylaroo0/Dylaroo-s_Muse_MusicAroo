# src/structure_analyzer.py
from typing import List, Dict

def analyze_structure(midi_path: str) -> List[Dict]:
    """
    Detect verse/chorus/bridge by simple repeated-chunk logic
    (or hook into music21/time-signature, onset clustering, etc.)
    Returns e.g.:
      [
        {"name":"verse",  "start":0.0,  "end":32.0},
        {"name":"chorus", "start":32.0, "end":64.0},
        ...
      ]
    """
    # TODO: music21 chordify + self-similarity segmentation
    return [{"name":"full","start":0.0,"end":float('inf')}]
