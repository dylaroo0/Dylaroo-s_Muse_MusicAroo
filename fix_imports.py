#!/usr/bin/env python3
import re
from pathlib import Path

# patterns → (regex, replacement)
PATTERNS = [
    (
        re.compile(r'from\s+src\.plugin_registry\s+import\s+(.+)'),
        r'from plugin_registry import \1'
    ),
    (
        re.compile(r'import\s+src\.plugin_registry'),
        'import plugin_registry'
    ),
]

root = Path(__file__).parent
for py in (root / "src").rglob("*.py"):
    text = py.read_text(encoding="utf-8")
    new_text = text
    for pat, repl in PATTERNS:
        new_text = pat.sub(repl, new_text)
    if new_text != text:
        py.write_text(new_text, encoding="utf-8")
        print(f"Patched imports in {py.relative_to(root)}")

print("✅ Done.")
