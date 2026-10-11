"""Shared helpers for the tooling's own unit tests (run by verify-all's 'tool unit tests' gate).

The tools have hyphenated file names, so they are loaded by path, fresh per test, which
keeps one test's monkeypatching of module globals from leaking into the next.
"""

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


def load_tool(rel_path, name=None):
    path = REPO / rel_path
    if not path.exists():
        raise FileNotFoundError(f"tool under test is missing: {path}")
    spec = importlib.util.spec_from_file_location(name or path.stem.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def load():
    return load_tool
