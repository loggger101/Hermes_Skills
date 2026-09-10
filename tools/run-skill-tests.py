#!/usr/bin/env python3
"""Discover and run every pytest suite that ships inside a skill, one command.

Why this exists: the first version of .github/workflows/ci.yml hardcoded five
suite paths in YAML (docx/pdf/powerpoint/xlsx/comfyui). Hardcoded lists drift —
the moment any new skill ships a tests/ dir it is silently absent from CI until
someone remembers to edit the workflow. Discovery removes that class of mistake:

  * every directory named `tests` containing at least one test_*.py / *_test.py
    file anywhere in the repo (except profiles-export/, docs/, .hermes/) is a
    suite; its parent dir becomes pytest's working directory so conftest.py and
    relative imports resolve exactly as they do locally.

  * suites run sequentially, each with sys.executable -m pytest --tb=short -q,
    and the exit code is non-zero if ANY suite fails or errors — fail loud,
    same contract as verify-all.py (a quiet "clean" on a broken environment is
    worse than a red gate).

Usage:
    py tools/run-skill-tests.py            # run every discovered suite
    py tools/run-skill-tests.py --list     # print what would run, exit 0
"""
import re
import subprocess
import sys
from pathlib import Path

if sys.version_info < (3, 8):
    raise SystemExit(
        "[FATAL] run-skill-tests.py needs Python 3.8+, got " + sys.version.split()[0]
    )
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

REPO = Path(__file__).resolve().parents[1]
PY = sys.executable or "python3"

# Historical snapshots and non-skill trees never contain runnable suites.
SKIP_DIRS = {".git", ".hermes", ".github", "profiles-export", "docs"}


def discover_suites() -> list[tuple[str, Path]]:
    """Return [(label, tests_dir)] for every pytest suite in the repo."""
    suites = []
    for testfile in REPO.rglob("test_*.py"):
        rel_parts = testfile.relative_to(REPO).parts
        if any(part in SKIP_DIRS or part == "__pycache__" for part in rel_parts):
            continue
        tests_dir = testfile.parent
        # only count dirs actually named `tests` (convention: <skill>/tests/)
        if tests_dir.name != "tests":
            continue
        label = str(tests_dir.relative_to(REPO)).replace("\\", "/")
        suites.append((label, tests_dir))

    testfile2 = REPO.rglob("*_test.py")  # second convention; de-dupe by dir
    seen = {d for _, d in suites}
    for tf in testfile2:
        rel_parts = tf.relative_to(REPO).parts
        if any(part in SKIP_DIRS or part == "__pycache__" for part in rel_parts):
            continue
        tests_dir = tf.parent
        if tests_dir.name != "tests" or tests_dir in seen:
            continue
        suites.append((str(tests_dir.relative_to(REPO)).replace("\\", "/"), tests_dir))

    # de-dupe (a dir can match both globs) and sort for stable output
    unique = {}
    for label, d in suites:
        unique.setdefault(d, label)
    return sorted(((label, d) for d, label in unique.items()), key=lambda t: t[0])


def run_suite(label: str, tests_dir: Path) -> tuple[str, bool, str]:
    proc = subprocess.run(
        [PY, "-m", "pytest", "--tb=line", "-q", "."],
        cwd=str(tests_dir), capture_output=True, text=True, timeout=900,
    )
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    # pull the pytest short-summary line ("29 passed in 10.9s") — with -q it is
    # printed bare, without === separators; fall back to a failure count if present
    m = re.search(r"^(\d+ failed(?:, \d+ (?:passed|skipped|xfailed))?|\d+ passed(?:, \d+ skipped)?) in [\d.]+s", out, re.M)
    note = (m.group(1).strip()[:140] if m else "no summary line").replace("\n", " ")

    # Fail loud: on failure the runner must say WHICH tests failed — a bare
    # "1 failed" in CI forces a log dig every time. --tb=line gives one line per
    # FAILED test (file::test - reason); cap so one pathological suite can't flood.
    if proc.returncode != 0:
        failed_lines = [ln.strip() for ln in out.splitlines() if ln.startswith("FAILED ")]
        detail = "\n".join(f"      {ln[:300]}" for ln in failed_lines[:25]) or "      (no FAILED lines parsed — see CI log)"
        note += f"\n{detail}"
    return label, proc.returncode == 0, note


def main(argv: list[str]) -> int:
    suites = discover_suites()
    if "--list" in argv:
        print(f"{len(suites)} suite(s) discovered:")
        for label, _ in suites:
            print(f"  {label}")
        return 0

    if not suites:
        # An empty scan is FATAL, not a pass — the same rule as verify-all.py.
        print("[FATAL] no test suites discovered; repo layout changed?")
        return 1

    results = []
    for label, tests_dir in suites:
        try:
            ok, note = run_suite(label, tests_dir)[1:]
        except subprocess.TimeoutExpired:
            ok, note = False, "TIMEOUT after 900s"
        except Exception as e:  # noqa: BLE001 — one broken suite must not mask the rest
            ok, note = False, f"{type(e).__name__}: {e}"[:140]
        results.append((label, ok, note))

    print("=== skill test suites ===")
    for label, ok, note in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {label:<52} {note}")
    failed = [r[0] for r in results if not r[1]]
    if failed:
        print(f"\n{len(failed)}/{len(results)} suite(s) FAILED")
        return 1
    print(f"\nALL {len(results)} SUITES PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
