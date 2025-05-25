#!/usr/bin/env python3
"""
check_imports.py

Ensure every plugin module in src/ imports `register_plugin`.
Skips src/plugin_registry.py and src/main.py itself.
"""

import os
import fnmatch
import sys
import re

# regex to match either import style anywhere in the file
IMPORT_RE = re.compile(
    r'^\s*from\s+(?:src\.)?plugin_registry\s+import\s+register_plugin',
    re.MULTILINE
)

def find_py_files(root_dir):
    for dirpath, _, files in os.walk(root_dir):
        for fname in fnmatch.filter(files, '*.py'):
            yield os.path.join(dirpath, fname)

def is_plugin_module(path):
    """
    Return True if this file declares a @register_plugin decorator.
    Skip plugin_registry.py and main.py.
    """
    base = os.path.basename(path)
    if base in ('plugin_registry.py', 'main.py'):
        return False
    try:
        text = open(path, 'r', encoding='utf-8').read()
    except Exception:
        return False
    return '@register_plugin' in text

def has_register_import(path):
    try:
        text = open(path, 'r', encoding='utf-8').read()
    except Exception:
        return False
    return bool(IMPORT_RE.search(text))

def main():
    root = 'src'
    missing = []

    for py in find_py_files(root):
        if not is_plugin_module(py):
            continue
        if not has_register_import(py):
            missing.append(py)

    if missing:
        print("❌ The following plugin modules are missing a `register_plugin` import:\n")
        for p in missing:
            print(f"  - {p}")
        sys.exit(1)
    else:
        print("✅ All plugin modules correctly import `register_plugin`.")

if __name__ == '__main__':
    main()
