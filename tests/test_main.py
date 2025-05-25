import pytest
from src.main import resolve_execution_order

def test_resolve_execution_order_simple():
    plugins = [
        {"name": "a", "phase": 1, "requires": []},
        {"name": "b", "phase": 1, "requires": ["a"]},
        {"name": "c", "phase": 2, "requires": []}
    ]
    ordered = resolve_execution_order(plugins)
    names = [p["name"] for p in ordered]
    assert names == ["a", "b", "c"]

def test_resolve_execution_order_cycle():
    plugins = [
        {"name": "x", "phase": 1, "requires": ["y"]},
        {"name": "y", "phase": 1, "requires": ["x"]}
    ]
    with pytest.raises(RuntimeError):
        resolve_execution_order(plugins)
