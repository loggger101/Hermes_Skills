"""scripts/scan_bypasses.py: every category fires on an added line, never on context or
removed lines, line numbers track the hunk, and non-diff input is not reported as clean."""

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "scan_bypasses.py"


def scan(diff):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=diff,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    assert proc.returncode == 0, "the scanner must always exit 0"
    hits = [ln.split("\t") for ln in proc.stdout.splitlines() if ln]
    return hits, proc.stderr


def one_file(added, path="src/app.py", start=10):
    body = "".join(f"+{line}\n" for line in added)
    return (
        f"diff --git a/{path} b/{path}\n--- a/{path}\n+++ b/{path}\n"
        f"@@ -{start},1 +{start},{len(added)} @@\n{body}"
    )


@pytest.mark.parametrize(
    "line, category",
    [
        ("x = 1  # noqa: E501", "suppression"),
        ("// eslint-disable-next-line", "suppression"),
        ("y = f()  # type: ignore", "suppression"),
        ("it.only('runs alone', () => {})", "test-dodge"),
        ("@pytest.mark.skip(reason='flaky')", "test-dodge"),
        ("git commit --no-verify", "hook-bypass"),
        ("requests.get(url, verify=False)", "tls-bypass"),
        ("const v = x as any;", "type-bypass"),
        ("except ValueError: pass", "error-swallow"),
        ("try { go() } catch (e) {}", "error-swallow"),
        ("<div dangerouslySetInnerHTML={h} />", "unsafe-html"),
        ("time.sleep(5)", "sync-hack"),
    ],
)
def test_each_category_fires(line, category):
    hits, err = scan(one_file([line]))
    assert [h[1] for h in hits] == [category]
    assert hits[0][0] == "src/app.py:10"
    assert "1 candidate(s) in 1 file(s)" in err


def test_line_numbers_follow_context_and_removed_lines():
    diff = (
        "--- a/m.py\n+++ b/m.py\n@@ -1,4 +1,4 @@\n"
        " keep = 1\n"
        "-old = 2  # noqa\n"  # removed: never a hit, does not advance the new-file line
        "+new = 2\n"
        " ctx = 3  # noqa\n"  # context: never a hit
        "+late = time.sleep(1)\n"
    )
    hits, _ = scan(diff)
    assert hits == [["m.py:4", "sync-hack", "late = time.sleep(1)"]]


def test_clean_diff_has_no_hits():
    hits, err = scan(one_file(["total = a + b", "return total"]))
    assert hits == [] and "0 candidate(s) in 1 file(s)" in err


@pytest.mark.parametrize("text", ["", "this is not a diff\n", "--- a/x\n+added # noqa\n"])
def test_non_diff_input_is_not_reported_clean(text):
    hits, err = scan(text)
    assert hits == [] and "not a unified diff, nothing scanned" in err
