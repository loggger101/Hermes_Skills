#!/usr/bin/env python3
"""Gate: every script the repo ships is exercised by a test, or is in the untested ledger
with a reason, and the ledger only ever shrinks.

Round-257. 83 of the 126 scripts inside skills were referenced by no test, no *_verify.py
harness and no smoke script, and no gate noticed: a script could be added, or break, with
every check green. This gate makes that debt visible and stops it growing.

What counts
-----------
script  a tracked .py/.sh/.ps1/.js/.cjs/.mjs outside tools/ and .github/ that is not
        itself a test (conftest.py included: it is test plumbing).
test    a tracked file in a `tests` dir, test_*.py, *_test.py, *.test.{js,cjs,mjs},
        *_verify.py / *-verify.py, smoke*.sh/.ps1, or tools/mutation-test-*.py. Every
        one of these is run by a gate (run-skill-tests.py, run-self-tests.py, verify-all).
tested  a test in the script's own skill dir names it (file name, or stem as a word); or
        any test names its full repo path; or any test names its file name and no other
        script shares that name (tools/ tests often build paths with os.path.join).

Checks (each failure is reported; exit 1 if any)
  A  script untested and not in the ledger      -> write a test (or a ledger line + reason)
  B  ledger entry whose script is now tested    -> delete the line (the ratchet)
  C  ledger entry naming no tracked script      -> delete the line
  D  ledger entry without a reason
  E  ledger entry listed twice

Usage:
    python tools/check-script-coverage.py
    python tools/check-script-coverage.py --list-untested   # print what a ledger would need
    COVERAGE_SCAN_ROOT=/tmp/fixture python tools/check-script-coverage.py --floor 1

Exit 0 = honest. Exit 1 = a violation. Exit 2 = could not run (not a git checkout, no
ledger, scan below the floor).
"""

import argparse
import os
import re
import sys
from pathlib import Path, PurePosixPath

from _repo_files import repo_files

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

REPO = Path(os.environ.get("COVERAGE_SCAN_ROOT") or Path(__file__).resolve().parents[1])
LEDGER = "tools/untested-scripts.txt"
FLOOR = 60  # 126 scripts on 2026-10-13
CODE = {".py", ".sh", ".ps1", ".js", ".cjs", ".mjs"}


def is_test(rel):
    p = PurePosixPath(rel)
    n = p.name
    return (
        "tests" in p.parts[:-1]
        or (n.startswith("test_") and n.endswith(".py"))
        or n.endswith("_test.py")
        or n.endswith((".test.js", ".test.cjs", ".test.mjs"))
        or n.endswith(("_verify.py", "-verify.py"))
        or (n.startswith("smoke") and p.suffix in (".sh", ".ps1"))
        or (rel.startswith("tools/mutation-test-") and n.endswith(".py"))
    )


def skill_dir(rel):
    return "/".join(PurePosixPath(rel).parts[:2])


def classify(tracked):
    code = [f for f in tracked if PurePosixPath(f).suffix in CODE]
    tests = [f for f in code if is_test(f)]
    scripts = [
        f
        for f in code
        if f not in tests
        and not f.startswith(("tools/", ".github/"))
        and len(PurePosixPath(f).parts) > 1
        and PurePosixPath(f).name != "conftest.py"
    ]
    return sorted(scripts), sorted(tests)


def tested(scripts, tests, read):
    texts = {t: read(t) for t in tests}
    name_count = {}
    for s in scripts:
        name_count[PurePosixPath(s).name] = name_count.get(PurePosixPath(s).name, 0) + 1

    def bounded(token):
        # Bounded, not a substring: 'plugin.json' must not cover plugin.js, nor
        # 'pdf_watermark.py' cover _watermark.py (both were false 'tested' verdicts).
        return re.compile(rf"(?<![\w.-]){re.escape(token)}(?![\w-])")

    out = set()
    for s in scripts:
        p = PurePosixPath(s)
        name, stem, full = bounded(p.name), bounded(p.stem), bounded(s)
        own = [t for t in tests if skill_dir(t) == skill_dir(s)]
        unique = name_count[p.name] == 1
        if (
            any(name.search(texts[t]) or stem.search(texts[t]) for t in own)
            or any(full.search(texts[t]) for t in tests)
            or (unique and any(name.search(texts[t]) for t in tests))
        ):
            out.add(s)
    return out


def read_ledger(path):
    """[(lineno, script, reason)] from 'path  # reason' lines; blank/# lines skipped."""
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        script, _, reason = stripped.partition("#")
        rows.append((i, script.strip(), reason.strip()))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--floor", type=int, default=FLOOR)
    ap.add_argument("--list-untested", action="store_true")
    args = ap.parse_args()

    tracked = repo_files(REPO)
    scripts, tests = classify(tracked)
    if len(scripts) < args.floor:
        print(f"[FATAL] found {len(scripts)} scripts, below the floor of {args.floor}: mis-rooted?")
        return 2
    covered = tested(
        scripts, tests, lambda t: (REPO / t).read_text(encoding="utf-8", errors="replace")
    )
    untested = [s for s in scripts if s not in covered]

    if args.list_untested:
        for s in untested:
            print(s)
        return 0

    ledger_path = REPO / LEDGER
    if not ledger_path.is_file():
        print(f"[FATAL] {LEDGER} missing: every untested script would be unaccounted for")
        return 2
    rows = read_ledger(ledger_path)
    problems = []
    seen = {}
    for lineno, script, reason in rows:
        where = f"{LEDGER}:{lineno}"
        if script in seen:
            problems.append(f"E {where}: {script} already listed at line {seen[script]}")
            continue
        seen[script] = lineno
        if not reason:
            problems.append(f"D {where}: {script} has no reason after '#'")
        if script not in scripts:
            problems.append(f"C {where}: {script} is not a tracked script; delete the line")
        elif script in covered:
            problems.append(
                f"B {where}: {script} is tested now; delete the line (ledger only shrinks)"
            )
    for s in untested:
        if s not in seen:
            problems.append(f"A {s}: no test runs it; add one (or a reasoned line in {LEDGER})")

    if problems:
        for p in problems:
            print(f"ERROR {p}")
        print(f"[FAIL] {len(problems)} script-coverage violation(s)")
        return 1
    print(
        f"[OK] {len(scripts)} scripts: {len(covered)} tested, {len(untested)} in the untested "
        f"ledger with reasons"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
