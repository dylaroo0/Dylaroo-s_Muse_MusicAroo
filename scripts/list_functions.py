# list_functions.py
import os
import ast

def list_all_functions(root_dir: str):
    """
    Walks every .py file under root_dir,
    parses it, and prints out each function name.
    """
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if not fname.endswith('.py'):
                continue
            full_path = os.path.join(dirpath, fname)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=full_path)
            except Exception as e:
                print(f"⚠️  Could not parse {full_path}: {e}")
                continue

            funcs = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            print(f"\n🗂  {full_path}")
            if funcs:
                for fn in funcs:
                    print(f"   – {fn}")
            else:
                print("   (no functions found)")

if __name__ == '__main__':
    # Change 'src' below if your code lives elsewhere
    list_all_functions('src')
