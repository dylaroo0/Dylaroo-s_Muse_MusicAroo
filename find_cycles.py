# find_cycles.py

import importlib
import pkgutil
from src.plugin_registry import import_all, PLUGINS

def import_all_plugins():
    """
    Triggers every plugin module in src/ to load, so that
    all @register_plugin decorators run and populate PLUGINS.
    """
    import_all()

def build_dependency_graph():
    """
    Returns a dict mapping plugin names to the set of
    names they depend on.
    """
    graph = {}
    for plugin in PLUGINS:
        # each plugin should have .name and .requires attributes
        graph[plugin.name] = set(getattr(plugin, "requires", []))
    return graph

def detect_cycles(graph):
    """
    Runs a DFS on the graph to find all cycles.
    Returns a list of cycles, each represented as a list of plugin names.
    """
    cycles = []
    path = []
    visited = set()

    def dfs(node):
        if node in path:
            # found a cycle: slice out the repeating segment
            idx = path.index(node)
            cycles.append(path[idx:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        path.append(node)
        for dep in graph.get(node, []):
            dfs(dep)
        path.pop()

    for start in graph:
        dfs(start)
    return cycles

def main():
    import_all_plugins()
    graph = build_dependency_graph()
    cycles = detect_cycles(graph)

    if not cycles:
        print("✅ No dependency cycles found.")
        return

    print("🚨 Dependency cycles detected:")
    for cycle in cycles:
        print("    " + " -> ".join(cycle))

if __name__ == "__main__":
    main()
