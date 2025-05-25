#!/usr/bin/env python3
"""
check_imports_minimal.py

Scan every .py under src/ and report which files do NOT have
the `register_plugin` import line in their first few lines.
"""

import os
import fnmatch
import sys
import re

# adjust this if you import from a different path
IMPORT_PATTERN = re.compile(r'^\s*from\s+(\S+\.)?plugin_registry\s+import\s+register_plugin')

def find_py_files(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for name in fnmatch.filter(filenames, '*.py'):
            yield os.path.join(dirpath, name)

def file_has_import(path, max_lines=5):
    """Return True if one of the first max_lines lines matches IMPORT_PATTERN."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for _ in range(max_lines):
                line = f.readline()
                if not line:
                    break
                if IMPORT_PATTERN.search(line):
                    return True
    except Exception as e:
        print(f"⚠️  Could not read {path}: {e}", file=sys.stderr)
    return False

def main():
    root = 'src'
    missing = []
    for path in find_py_files(root):
        if not file_has_import(path):
            missing.append(path)

    if missing:
        print("❌ The following files are missing the `register_plugin` import in the first few lines:\n")
        for p in missing:
            print(f"  - {p}")
        sys.exit(1)
    else:
        print("✅ All .py files under src/ have the `register_plugin` import near the top.")

if __name__ == '__main__':
    main()
