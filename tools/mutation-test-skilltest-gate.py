#!/usr/bin/env python3
"""Mutation self-test for run-skill-tests.py, the runner behind CI's skill-tests job.

Until this existed the runner had only ever been seen passing, and it had two silent
gaps nobody could observe from a green run: it did not know node / shell / PowerShell
suites existed (65 security-audit tests and both ast-grep smoke scripts never ran;
eight of those tests were failing), and a suite whose every test skipped counted as a
pass. This builds hermetic fixture trees in a temp dir (`--root` points discovery at
them; no repo file is touched) and asserts each verdict:

  S1  pytest suite, all pass                         -> PASS
  S2  pytest suite, one assertion fails              -> FAIL naming the test
  S3  pytest suite, every test skipped               -> FAIL (verified nothing)
  S4  pytest suite, file with zero tests             -> FAIL
  S5  pytest suite, import error at collection       -> FAIL
  S6  node --test suite, all pass                    -> PASS
  S7  node --test suite, one test fails              -> FAIL naming the test
  S8  node --test suite, every test skipped          -> FAIL
  S9  sh smoke, all PASS lines, exit 0               -> PASS
  S10 sh smoke, FAIL line, exit 1                    -> FAIL naming the check
  S11 sh smoke, exit 0 but prints no PASS lines      -> FAIL (proved nothing)
  S12 ps1 smoke, passes                              -> PASS, or FAIL saying no PowerShell
  S13 ps1 smoke, fails                               -> FAIL
  O1  test_*.py outside a tests/ dir                 -> orphan, FATAL
  O2  *.test.ts (no runner)                          -> orphan, FATAL
  E1  a root with no suites at all                   -> FATAL, exit 1
  C1  a root with only passing suites                -> exit 0, ALL N SUITES PASSED
  L1  --list on the real repo                        -> exit 0, no orphans

Exit code = number of failed checks (0 = runner proven fail-loud). Needs pytest and node
on PATH, like the CI job it guards; if either is missing the affected checks fail.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if sys.version_info < (3, 8):
    raise SystemExit("[FATAL] needs Python 3.8+")
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "tools" / "run-skill-tests.py"
HAS_PS = bool(shutil.which("pwsh") or shutil.which("powershell"))

PY_PASS = "def test_a():\n    assert 1 + 1 == 2\n\ndef test_b():\n    assert 'x'\n"
PY_FAIL = "def test_ok():\n    assert True\n\ndef test_broken_math():\n    assert 1 + 1 == 3\n"
PY_SKIP = "import pytest\n\n@pytest.mark.skip(reason='no env')\ndef test_a():\n    pass\n"
PY_EMPTY = "# a test module with no tests in it\nVALUE = 1\n"
PY_IMPORT_ERR = "import module_that_does_not_exist_xyz\n\ndef test_a():\n    pass\n"
NODE_PASS = 'const test = require("node:test");\nconst assert = require("node:assert");\ntest("adds", () => { assert.equal(1 + 1, 2); });\n'
NODE_FAIL = 'const test = require("node:test");\nconst assert = require("node:assert");\ntest("ok", () => {});\ntest("broken_node_math", () => { assert.equal(1 + 1, 3); });\n'
NODE_SKIP = 'const test = require("node:test");\ntest("skipped", { skip: true }, () => {});\n'
SH_PASS = 'echo "PASS: first"\necho "PASS: second"\n'
SH_FAIL = 'echo "PASS: first"\necho "FAIL: broken_sh_check" >&2\nexit 1\n'
SH_SILENT = "true\n"
PS_PASS = "Write-Host 'PASS: one'\nexit 0\n"
PS_FAIL = "Write-Host 'FAIL: broken_ps_check'\nexit 1\n"

# label -> (relative file, content)
SCENARIOS = {
    "S1": ("s1/tests/test_pass.py", PY_PASS),
    "S2": ("s2/tests/test_fail.py", PY_FAIL),
    "S3": ("s3/tests/test_skip.py", PY_SKIP),
    "S4": ("s4/tests/test_empty.py", PY_EMPTY),
    "S5": ("s5/tests/test_import.py", PY_IMPORT_ERR),
    "S6": ("s6/scripts/a.test.cjs", NODE_PASS),
    "S7": ("s7/scripts/a.test.cjs", NODE_FAIL),
    "S8": ("s8/scripts/a.test.cjs", NODE_SKIP),
    "S9": ("s9/tests/smoke.sh", SH_PASS),
    "S10": ("s10/tests/smoke.sh", SH_FAIL),
    "S11": ("s11/tests/smoke.sh", SH_SILENT),
    "S12": ("s12/tests/smoke.ps1", PS_PASS),
    "S13": ("s13/tests/smoke.ps1", PS_FAIL),
}
# label -> (suite label as the runner prints it, expected PASS?, needle the line/details must hold)
EXPECT = {
    "S1": ("s1/tests", True, "2 passed"),
    "S2": ("s2/tests", False, "test_broken_math"),
    "S3": ("s3/tests", False, "verified nothing"),
    "S4": ("s4/tests", False, "exit 5"),
    "S5": ("s5/tests", False, "module_that_does_not_exist_xyz"),
    "S6": ("s6/scripts [node]", True, "1 pass"),
    "S7": ("s7/scripts [node]", False, "broken_node_math"),
    "S8": ("s8/scripts [node]", False, "verified nothing"),
    "S9": ("s9/tests [sh]", True, "2 checks passed"),
    "S10": ("s10/tests [sh]", False, "broken_sh_check"),
    "S11": ("s11/tests [sh]", False, "proved nothing"),
    "S12": (
        "s12/tests [ps1]",
        HAS_PS,
        "1 checks passed" if HAS_PS else "neither pwsh nor powershell",
    ),
    "S13": (
        "s13/tests [ps1]",
        False,
        "broken_ps_check" if HAS_PS else "neither pwsh nor powershell",
    ),
}

failures = []


def build(root, labels, extra=()):
    for lab in labels:
        rel, content = SCENARIOS[lab]
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8", newline="\n")
    for rel, content in extra:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8", newline="\n")


def run(*args):
    return subprocess.run(
        [sys.executable, str(RUNNER), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
    )


def block_for(out, label):
    """The runner's result line for `label` plus its indented detail lines."""
    lines = out.splitlines()
    for i, ln in enumerate(lines):
        parts = ln.split(None, 1)
        if len(parts) == 2 and parts[0] in ("PASS", "FAIL") and parts[1].startswith(label + " "):
            block = [ln]
            for nxt in lines[i + 1 :]:
                if nxt.startswith("      ") or nxt.startswith("\t"):
                    block.append(nxt)
                else:
                    break
            return parts[0] == "PASS", "\n".join(block)
    return None, None


def check(name, cond, detail):
    if cond:
        print(f"  [OK] {name}")
    else:
        failures.append(f"{name}: {detail}")


with tempfile.TemporaryDirectory(prefix="skilltest-mut-") as tmp:
    root = Path(tmp)

    # S1-S13 in one fixture: one runner call, each verdict read from its own line.
    allroot = root / "all"
    build(allroot, list(SCENARIOS))
    r = run("--root", str(allroot))
    out = r.stdout + r.stderr
    check("mixed fixture exits 1", r.returncode == 1, f"rc={r.returncode}\n{out[-600:]}")
    for lab, (suite_label, want_pass, needle) in EXPECT.items():
        got, block = block_for(out, suite_label)
        if got is None:
            failures.append(f"{lab}: no result line for {suite_label!r}\n{out[-800:]}")
        elif got != want_pass:
            failures.append(f"{lab}: expected {'PASS' if want_pass else 'FAIL'}, got {block}")
        elif needle not in block:
            failures.append(f"{lab}: verdict right but {needle!r} missing from: {block}")
        else:
            print(f"  [OK] {lab} {suite_label} -> {'PASS' if got else 'FAIL'}")

    # C1: only passing suites -> exit 0 and the all-pass line.
    clean = root / "clean"
    build(clean, ["S1", "S6", "S9"])
    r = run("--root", str(clean))
    check(
        "C1 passing-only fixture exits 0",
        r.returncode == 0 and "ALL 3 SUITES PASSED" in r.stdout,
        f"rc={r.returncode}\n{(r.stdout + r.stderr)[-600:]}",
    )

    # O1/O2: a passing suite plus orphans -> FATAL listing each orphan, even though
    # every suite itself passed.
    orph = root / "orphans"
    build(
        orph,
        ["S1"],
        extra=[
            ("o1/scripts/test_stray.py", PY_PASS),
            ("o2/web/widget.test.ts", "test('x', () => {});\n"),
        ],
    )
    r = run("--root", str(orph))
    out = r.stdout + r.stderr
    check("O1/O2 orphans exit 1", r.returncode == 1, f"rc={r.returncode}\n{out[-600:]}")
    check("O1 test_*.py outside tests/ reported", "o1/scripts/test_stray.py" in out, out[-600:])
    check("O2 *.test.ts reported", "o2/web/widget.test.ts" in out, out[-600:])
    r = run("--root", str(orph), "--list")
    check(
        "O1 --list also fails on orphans",
        r.returncode == 1 and "orphan" in r.stdout,
        r.stdout[-400:],
    )

    # E1: nothing to run is FATAL, never a pass.
    empty = root / "empty"
    (empty / "some-skill").mkdir(parents=True)
    (empty / "some-skill" / "SKILL.md").write_text("---\nname: x\n---\n", encoding="utf-8")
    r = run("--root", str(empty))
    check(
        "E1 empty scan is FATAL",
        r.returncode == 1 and "[FATAL] no test suites" in r.stdout,
        f"rc={r.returncode}\n{r.stdout[-300:]}",
    )

# L1: the real repo has no orphan test files.
r = run("--list")
check("L1 real repo --list: no orphans", r.returncode == 0, (r.stdout + r.stderr)[-600:])

print()
if failures:
    print(f"FAILED ({len(failures)}):")
    for f in failures:
        print("  - " + f.replace("\n", "\n    "))
    sys.exit(len(failures))
print(
    "ALL CHECKS PASSED — run-skill-tests.py verified fail-loud (pytest/node/sh/ps1, orphans, empty scan)."
)
sys.exit(0)
