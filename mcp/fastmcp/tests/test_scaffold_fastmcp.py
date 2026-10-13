"""scripts/scaffold_fastmcp.py and the three templates it renders (api_wrapper, database_server,
file_processor): each renders to Python that parses and passes the exact server name to
FastMCP(), whatever characters the name holds. fastmcp itself is not needed: the generated
files are parsed, not run."""

import ast
import subprocess
import sys
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "scaffold_fastmcp.py"
TEMPLATES = ["api_wrapper", "database_server", "file_processor"]


def scaffold(*args):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    return proc.returncode, proc.stdout, proc.stderr


def server_name(path):
    """The string literal passed to FastMCP(...) in a generated file."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    calls = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "FastMCP"
    ]
    assert len(calls) == 1
    return ast.literal_eval(calls[0].args[0])


def test_list_names_every_template():
    rc, out, _ = scaffold("--list")
    assert rc == 0 and out.split() == TEMPLATES


@pytest.mark.parametrize("template", TEMPLATES)
@pytest.mark.parametrize(
    "name", ["Weather API", 'Bob\'s "quoted" server', "C:\\tools\\srv", "Café ☕"]
)
def test_every_template_renders_valid_python_with_the_exact_name(tmp_path, template, name):
    """A quote or backslash in the name used to be pasted raw, writing a broken file."""
    out = tmp_path / "server.py"
    rc, stdout, err = scaffold("--template", template, "--name", name, "--output", out)
    assert rc == 0, err
    assert stdout.startswith("Wrote") and server_name(out) == name


def test_refuses_to_overwrite_without_force(tmp_path):
    out = tmp_path / "s.py"
    out.write_text("keep me\n", encoding="utf-8")
    rc, _, err = scaffold("--template", "api_wrapper", "--name", "x", "--output", out)
    assert rc != 0 and "Refusing to overwrite" in err
    assert out.read_text(encoding="utf-8") == "keep me\n"
    rc, _, _ = scaffold("--template", "api_wrapper", "--name", "x", "--output", out, "--force")
    assert rc == 0 and server_name(out) == "x"


def test_unknown_template_writes_nothing(tmp_path):
    out = tmp_path / "new" / "dir" / "s.py"
    rc, _, err = scaffold("--template", "nope", "--name", "x", "--output", out)
    assert rc != 0 and "Unknown template 'nope'" in err
    assert not (tmp_path / "new").exists()  # the parent dir used to be created first


def test_missing_arguments_is_a_usage_error():
    rc, _, err = scaffold("--template", "api_wrapper")
    assert rc == 2 and "required unless --list" in err
