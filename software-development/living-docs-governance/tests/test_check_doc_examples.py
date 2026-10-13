"""scripts/check_doc_examples.py: matching docs pass, drift fails, and a run that checks
nothing is not a pass. Needs node on PATH (CI has it); without node the script exits 2
and these tests FAIL rather than skip."""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_doc_examples.py"


def check(tmp_path, markdown, *flags):
    doc = tmp_path / "doc.md"
    doc.write_text(markdown, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *flags, str(doc)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    return proc.returncode, proc.stdout


def block(*lines):
    return "```js\n" + "\n".join(lines) + "\n```\n"


def test_matching_examples_pass(tmp_path):
    md = block(
        "const xs = [3, 1, 2].sort();",
        "console.log(xs)  // [ 1, 2, 3 ]",
        "console.log('hi')  // \"hi\"",
    )
    rc, out = check(tmp_path, md, "--verbose")
    assert rc == 0, out
    assert "1 block(s) checked, 0 failing" in out


def test_wrong_comment_fails(tmp_path):
    rc, out = check(tmp_path, block("console.log(1 + 1)  // 3"))
    assert rc == 1 and "comment says '3' but printed '2'" in out


def test_missing_output_fails(tmp_path):
    md = block("if (false) console.log('never')  // never")
    rc, out = check(tmp_path, md)
    assert rc == 1 and "1 expected console.log value(s), program printed 0" in out


def test_crash_fails_unless_marked_throws(tmp_path):
    rc, out = check(tmp_path, block("console.log(1)  // 1", "null.x;"))
    assert rc == 1 and "block crashed" in out
    rc, out = check(tmp_path, block("// throws", "console.log(1)  // 1", "null.x;"))
    assert rc == 0, out


def test_throws_block_that_runs_clean_fails(tmp_path):
    """Round-257: a `// throws` promise the code no longer keeps used to pass."""
    rc, out = check(tmp_path, block("// throws", "console.log(1)  // 1"))
    assert rc == 1 and "marked // throws but ran without error" in out


def test_no_run_blocks_are_skipped(tmp_path):
    md = block("// no-run", "console.log(window.x)  // 1") + block("console.log(2)  // 2")
    rc, out = check(tmp_path, md)
    assert rc == 0 and "1 block(s) checked" in out


def test_nothing_checkable_is_not_a_pass(tmp_path):
    """Round-257: zero checked blocks used to print '0 failing' and exit 0."""
    md = "# Title\n\n" + block("let x = 1;") + "```python\nprint(1)  # 1\n```\n"
    rc, out = check(tmp_path, md)
    assert rc == 2 and "no checkable block" in out


def test_no_files_is_usage_error():
    proc = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, timeout=60)
    assert proc.returncode == 2 and proc.stdout.startswith("usage:")
