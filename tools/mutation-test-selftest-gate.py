#!/usr/bin/env python3
"""Mutation self-test for tools/run-self-tests.py (the self-test harness gate).

Same philosophy as mutation-test-doc-gate.py / mutation-test-secret-gate.py: a gate
that cannot be proven to fail is worse than no gate. This one proves the runner's
classification logic catches every failure mode that matters, using throwaway
fixtures in a temp dir (explicit-path mode — never touches the repo tree):

  M1 PASS      trivial green fixture            -> ok=True , note starts 'PASS'
  M2 SKIP-rc77 fixture exits 77                 -> ok=True , note starts 'SKIP'
  M3 SKIP-dep  fixture raises ModuleNotFoundErr -> ok=True , note names the module
  M4 FAIL      fixture prints a failed check    -> ok=False, note carries rc + detail
  M5 drift     manifest_check() with an unregistered candidate returns a problem;
               exact match returns None (both directions asserted)

Exit 0 = every mutation caught. Exit 1 = the gate would have shipped blind.
"""
import importlib.util
import os
import sys
from pathlib import Path

if sys.version_info < (3, 8):
    raise SystemExit("[FATAL] needs Python 3.8+")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "tools" / "run-self-tests.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("run_self_tests", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # module-level code only defines constants/functions (no main run)
    return mod


def write_fixture(tmp: Path, name: str, body: str) -> Path:
    p = tmp / f"scripts_{name}.py"
    p.write_text(body, encoding="utf-8")
    return p


def main() -> int:
    import tempfile
    r = load_runner()
    failures = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        print(f"  {'ok' if cond else 'FAIL'} {name}" + (f"   [{detail}]" if not cond and detail else ""))
        if not cond:
            failures.append(name)

    with tempfile.TemporaryDirectory(prefix="selftest-gate-") as td:
        tmp = Path(td)

        # M1 — green fixture classifies PASS
        f1 = write_fixture(tmp, "pass", 'print("fixture ok")\n')
        label, ok, note = r.run_one(f1)
        check("M1 pass-fixture -> PASS", ok and note.startswith("PASS"), note[:120])

        # M2 — exit-77 fixture classifies SKIP (pinned-env-missing convention)
        f2 = write_fixture(tmp, "skiprc", 'import sys\nprint("SKIP - pinned env missing")\nraise SystemExit(77)\n')
        label, ok, note = r.run_one(f2)
        check("M2 rc-77 -> SKIP (not FAIL)", ok and note.startswith("SKIP"), f"ok={ok} {note[:100]}")

        # M3 — missing-import fixture classifies SKIP naming the module
        f3 = write_fixture(tmp, "skipdep", 'import this_module_definitely_does_not_exist_xyz\n')
        label, ok, note = r.run_one(f3)
        check("M3 ModuleNotFoundError -> SKIP names dep",
              ok and note.startswith("SKIP") and "this_module_definitely_does_not_exist_xyz" in note,
              f"ok={ok} {note[:100]}")

        # M4 — real failure classifies FAIL with rc + the failing line surfaced
        f4 = write_fixture(tmp, "fail", 'print("FAIL  some_check   [bad value]")\nraise SystemExit(2)\n')
        label, ok, note = r.run_one(f4)
        check("M4 failed-check -> FAIL with rc=2 + detail",
              (not ok) and "rc=2" in note and "some_check" in note, f"ok={ok} {note[:100]}")

    # M5 — manifest drift detection, both directions (pure function; no tree mutation needed)
    candidates = r.discover()  # live discovery == today's ground truth for this repo
    check("M5a exact-match candidate list -> no drift", r.manifest_check(candidates) is None,
          f"candidates={len(candidates)}")
    drifted = candidates + ["some-new-skill/scripts/brand_new_verify.py"]
    prob = r.manifest_check(drifted) or ""
    check("M5b unregistered harness -> drift problem names it",
          "unregistered" in prob and "brand_new_verify.py" in prob, prob[:120])
    stale_auto = [c for c in candidates if c != sorted(candidates)[0]]  # pretend one AUTO_RUN file vanished
    check("M5c missing AUTO_RUN file -> drift problem",
          (r.manifest_check(stale_auto) or "") != "", "expected a problem string")

    print()
    if failures:
        print(f"FAILED ({len(failures)}): {', '.join(failures)} — the self-test gate itself is blind to these modes.")
        return 1
    print("ALL MUTATIONS CAUGHT — run-self-tests.py classification verified fail-loud (PASS/SKIP-77/SKIP-dep/FAIL/drift).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
