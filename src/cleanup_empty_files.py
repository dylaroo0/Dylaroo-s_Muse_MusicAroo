# ──────────────────────────────────────────────────────────────
# File: src/cleanup_empty_files.py
# Purpose: scan src/ for 0-byte or “placeholder” modules and
#          (1) print a colorized table,
#          (2) optionally delete or quarantine them.
# Usage:
#   python -m src.cleanup_empty_files           # dry-run
#   python -m src.cleanup_empty_files --delete  # actually remove
#   python -m src.cleanup_empty_files --quarantine bad/  # move to folder
# ──────────────────────────────────────────────────────────────
import argparse, os, re, shutil, textwrap
from pathlib import Path

PLACEHOLDER_PATTERNS = [
    re.compile(r"^\s*$"),                                 # empty file
    re.compile(r'""".*placeholder', re.I | re.S),         # triple-quoted placeholder
    re.compile(r"#\s*TODO[: ]?placeholder", re.I),        # comment placeholder
]

def looks_like_placeholder(text: str) -> bool:
    return any(p.search(text) for p in PLACEHOLDER_PATTERNS)

def scan_src(src_dir: Path):
    suspects = []
    for py in src_dir.glob("*.py"):
        if py.name in {"__init__.py", "cleanup_empty_files.py"}:
            continue
        try:
            txt = py.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if looks_like_placeholder(txt):
            suspects.append(py)
    return suspects

def main():
    ap = argparse.ArgumentParser(
        description="Find and optionally delete placeholder .py files."
    )
    ap.add_argument("--delete", action="store_true",
                    help="Delete the suspects permanently.")
    ap.add_argument("--quarantine", type=str, metavar="FOLDER",
                    help="Move suspects into FOLDER instead of deleting.")
    args = ap.parse_args()

    src_dir = Path(__file__).parent
    suspects = scan_src(src_dir)

    if not suspects:
        print("✨  No placeholder files detected. Clean as a whistle!")
        return

    print("\n⚠️  Placeholder / empty modules found:\n")
    for py in suspects:
        print(f" • {py.relative_to(src_dir)}")
    print()

    if args.delete:
        for py in suspects:
            py.unlink(missing_ok=True)
        print("🗑  Deleted them all. Your importer will be silent now.")
    elif args.quarantine:
        qdir = Path(args.quarantine)
        qdir.mkdir(parents=True, exist_ok=True)
        for py in suspects:
            shutil.move(str(py), qdir / py.name)
        print(f"🚚  Moved {len(suspects)} files into {qdir}")
    else:
        msg = textwrap.dedent(
            """
            Nothing changed (dry-run).
            Re-run with:
              --delete        to remove them
              --quarantine X  to move them into folder X
            """
        )
        print(msg.strip())

if __name__ == "__main__":
    main()
