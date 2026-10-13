#!/usr/bin/env python3
"""Mutation self-test for the three round-257 code gates: check-script-syntax.py,
check-script-coverage.py and check-lint.py.

Each gate runs against throwaway git repos: a clean control that must PASS, then one
planted defect per check that must FAIL with the defect named. A gate that cannot fail on
its own defect class is a false green waiting to happen, so every class is planted:

  syntax    a broken .py, .js, .sh and .ps1 (one language each), and a scan below the floor
  coverage  A untested script, B tested-but-listed, C phantom entry, D reasonless entry,
            E duplicate entry, a substring false positive ('pdf_fixture_mark.py' must not
            cover _fixture_mark.py), a missing ledger, and a scan below the floor
  lint      a ruff check finding, an unformatted file, a stale per-file-ignore, a bundled
            skill missing from extend-exclude, an extend-exclude that is not bundled, and a
            non-ASCII print without UTF-8 stdout (plus its fixed form and the bundled
            exemption, which must both stay clean), and a ruff pin that disagrees

Exit 0 = every gate proven fail-loud. Exit 1 = a check failed (never a count: it wraps).
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / "tools"
failures = []


def fixture(files):
    root = Path(tempfile.mkdtemp(prefix="script-gates-mut-"))
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8", newline="\n")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
    return root


def run(gate, env_var, files, *args):
    root = fixture(files)
    try:
        proc = subprocess.run(
            [sys.executable, str(TOOLS / gate), *args],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=dict(os.environ, **{env_var: str(root)}),
            timeout=300,
        )
        return proc.returncode, proc.stdout + proc.stderr
    finally:
        shutil.rmtree(root, ignore_errors=True)


def expect(name, result, rc, needle=None):
    got_rc, out = result
    ok = got_rc == rc and (needle is None or needle in out)
    print(
        f"  {'[OK]  ' if ok else '[FAIL]'} {name}: exit {got_rc}"
        + ("" if ok else f" (want {rc}, '{needle}')")
    )
    if not ok:
        failures.append(name)
        print("        " + out.strip().replace("\n", "\n        ")[:800])


# ------------------------------------------------------------------------------- syntax
SYNTAX_OK = {
    "s/a/good.py": "x = 1\n",
    "s/a/good.js": "const a = 1;\n",
    "s/a/good.sh": "echo hi\n",
    "s/a/good.ps1": "Write-Output 'hi'\n",
}
SYNTAX_BAD = {
    "python": ("s/a/bad.py", "def f(:\n"),
    "node": ("s/a/bad.js", "const = ;\n"),
    "bash": ("s/a/bad.sh", "if then fi\n"),
    "powershell": ("s/a/bad.ps1", "function f {\n"),
}


def syntax():
    print("check-script-syntax.py")
    expect(
        "clean control",
        run("check-script-syntax.py", "SCRIPT_SCAN_ROOT", SYNTAX_OK, "--floor", "1"),
        0,
    )
    for lang, (rel, src) in SYNTAX_BAD.items():
        files = dict(SYNTAX_OK, **{rel: src})
        res = run("check-script-syntax.py", "SCRIPT_SCAN_ROOT", files, "--floor", "1")
        expect(f"broken {lang}", res, 1, f"BROKEN {rel}")
    res = run("check-script-syntax.py", "SCRIPT_SCAN_ROOT", SYNTAX_OK, "--floor", "5")
    expect("scan below floor", res, 2, "below the floor")


# ----------------------------------------------------------------------------- coverage
LEDGER = "tools/untested-scripts.txt"
COV_OK = {
    "cat/sk/SKILL.md": "---\nname: sk\n---\n",
    "cat/sk/scripts/tool.py": "print(1)\n",
    "cat/sk/scripts/other.py": "print(2)\n",
    "cat/sk/tests/test_tool.py": "SCRIPT = 'scripts/tool.py'\n",
    LEDGER: "# header\ncat/sk/scripts/other.py  # backlog: not yet\n",
}


def cov(files, *args):
    return run("check-script-coverage.py", "COVERAGE_SCAN_ROOT", files, "--floor", "1", *args)


def coverage():
    print("check-script-coverage.py")
    expect("clean control", cov(COV_OK), 0, "2 scripts: 1 tested, 1 in the untested ledger")
    expect(
        "A untested and unlisted",
        cov(dict(COV_OK, **{LEDGER: "# empty\n"})),
        1,
        "A cat/sk/scripts/other.py",
    )
    expect(
        "B tested but listed",
        cov(dict(COV_OK, **{LEDGER: COV_OK[LEDGER] + "cat/sk/scripts/tool.py  # stale\n"})),
        1,
        "B tools/untested-scripts.txt:3: cat/sk/scripts/tool.py is tested now",
    )
    expect(
        "C phantom entry",
        cov(dict(COV_OK, **{LEDGER: COV_OK[LEDGER] + "cat/sk/scripts/gone.py  # x\n"})),
        1,
        "C tools/untested-scripts.txt:3: cat/sk/scripts/gone.py is not a tracked script",
    )
    expect(
        "D reasonless entry",
        cov(dict(COV_OK, **{LEDGER: "cat/sk/scripts/other.py\n"})),
        1,
        "D tools/untested-scripts.txt:1: cat/sk/scripts/other.py has no reason",
    )
    expect(
        "E duplicate entry",
        cov(dict(COV_OK, **{LEDGER: COV_OK[LEDGER] + "cat/sk/scripts/other.py  # again\n"})),
        1,
        "E tools/untested-scripts.txt:3",
    )
    sub = dict(
        COV_OK,
        **{
            "cat/sk/scripts/_fixture_mark.py": "print(3)\n",
            "cat/sk/tests/test_tool.py": "SCRIPT = 'scripts/tool.py'  # see pdf_fixture_mark.py\n",
        },
    )
    expect("substring is not coverage", cov(sub), 1, "A cat/sk/scripts/_fixture_mark.py")
    no_ledger = {k: v for k, v in COV_OK.items() if k != LEDGER}
    expect("missing ledger", cov(no_ledger), 2, "untested-scripts.txt missing")
    expect("scan below floor", cov(COV_OK, "--floor", "9"), 2, "below the floor")


# --------------------------------------------------------------------------------- lint
RUFF_TOML = """line-length = 100
extend-exclude = ["cat/bund"]

[lint]
select = ["E4", "E7", "E9", "F"]

[lint.per-file-ignores]
"cat/own/x.py" = ["E402"]
"""


def installed_ruff():
    out = subprocess.run(
        [sys.executable, "-m", "ruff", "--version"], capture_output=True, text=True
    ).stdout.split()
    if not out:
        raise SystemExit("[FATAL] ruff is not installed: pip install -r requirements.txt")
    return out[-1]


RUFF_VERSION = installed_ruff()
LINT_OK = {
    "requirements.txt": f"ruff=={RUFF_VERSION}\n",
    ".github/workflows/ci.yml": f'run: pip install "ruff=={RUFF_VERSION}"\n',
    "ruff.toml": RUFF_TOML,
    "profile/.bundled_manifest": "bund:0123\n",
    "cat/bund/SKILL.md": "---\nname: bund\n---\n",
    "cat/bund/s.py": 'print("✓ bundled: upstream to fix")\n',
    "cat/own/SKILL.md": "---\nname: own\n---\n",
    "cat/own/x.py": 'import sys\n\nsys.stdout.reconfigure(encoding="utf-8")\nprint("✓ ok")\n',
}


def lint(files):
    return run("check-lint.py", "LINT_SCAN_ROOT", files)


def lint_checks():
    print("check-lint.py")
    expect(
        "clean control (incl. bundled + reconfigured non-ASCII)",
        lint(LINT_OK),
        0,
        "1 bundled file(s) left to upstream",
    )
    expect("ruff check finding", lint(dict(LINT_OK, **{"cat/own/y.py": "import os\n"})), 1, "F401")
    expect("unformatted file", lint(dict(LINT_OK, **{"cat/own/y.py": "x=1\n"})), 1, "unformatted")
    stale = RUFF_TOML.replace('"cat/own/x.py"', '"cat/own/moved.py"')
    expect(
        "stale per-file-ignore",
        lint(dict(LINT_OK, **{"ruff.toml": stale})),
        1,
        "lint.per-file-ignores 'cat/own/moved.py'",
    )
    unlisted = dict(
        LINT_OK,
        **{
            "profile/.bundled_manifest": "bund:0123\nown:4567\n",
        },
    )
    expect(
        "bundled skill not excluded",
        lint(unlisted),
        1,
        "bundled skill cat/own has Python but is not in ruff.toml",
    )
    over = RUFF_TOML.replace(
        'extend-exclude = ["cat/bund"]', 'extend-exclude = ["cat/bund", "cat/own"]'
    )
    expect(
        "exclude that is not bundled",
        lint(dict(LINT_OK, **{"ruff.toml": over})),
        1,
        "'cat/own' is not a bundled skill",
    )
    drift = dict(LINT_OK, **{".github/workflows/ci.yml": 'run: pip install "ruff==0.0.1"\n'})
    expect("ruff pin drift", lint(drift), 1, "ruff versions disagree")
    unpinned = dict(LINT_OK, **{"requirements.txt": "ruff\n"})
    expect("ruff unpinned", lint(unpinned), 1, "ruff is not pinned")
    unsafe = dict(LINT_OK, **{"cat/own/y.py": 'print("→ done")\n'})
    expect(
        "non-ASCII print without UTF-8 stdout", lint(unsafe), 1, "cat/own/y.py:1: prints non-ASCII"
    )
    exits = dict(LINT_OK, **{"cat/own/y.py": 'raise SystemExit("usage — see docs")\n'})
    expect("non-ASCII SystemExit message", lint(exits), 1, "cat/own/y.py:1: prints non-ASCII")


def main():
    for tool in ("check-script-syntax.py", "check-script-coverage.py", "check-lint.py"):
        if not (TOOLS / tool).is_file():
            print(f"[FATAL] {tool} is missing: the gate this test proves is gone")
            return 1
    syntax()
    coverage()
    lint_checks()
    print()
    if failures:
        print(f"FAILED: {len(failures)} check(s): {', '.join(failures)}")
        return 1
    print("ALL CHECKS PASSED — script syntax, script coverage and lint gates verified fail-loud.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
