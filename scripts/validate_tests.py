import ast, os
from importlib import import_module

errors = []
for root, _, files in os.walk("tests"):
    for fn in files:
        if not fn.endswith(".py"):
            continue
        path = os.path.join(root, fn)
        tree = ast.parse(open(path, encoding="utf-8").read(), fn)
        for node in [n for n in tree.body if isinstance(n, ast.ImportFrom)]:
            mod = node.module  # e.g. "src.audio_features"
            for alias in node.names:
                name = alias.name  # e.g. "analyze_features"
                try:
                    m = import_module(mod)
                    if not hasattr(m, name):
                        errors.append(f"{fn}: {mod}.{name} not found")
                except ModuleNotFoundError:
                    errors.append(f"{fn}: module {mod} not found")
if errors:
    print("❌ Test import errors:")
    for e in errors:
        print("  ", e)
else:
    print("✅ All test imports match actual code.")
