#!/usr/bin/env python3
"""Mutation self-test for tools/run-self-tests.py (the self-test harness gate).

Same philosophy as mutation-test-doc-gate.py / mutation-test-secret-gate.py: a gate
that cannot be proven to fail is worse than no gate. This one proves the runner's
classification logic catches every failure mode that matters, using throwaway
fixtures in a temp dir (explicit-path mode — never touches the repo tree):

  M1  PASS      trivial green fixture                      -> ok=True , note starts 'PASS'
  M2a SKIP-rc77 exit 77 from an entry declared skip_rc_ok      -> ok=True , SKIP
  M2b rc77      exit 77 from an entry NOT declared            -> ok=False (no undeclared skips)
  M3a SKIP-dep  missing module the entry declares optional   -> ok=True , SKIP names it
  M3b dep       missing module the entry does NOT declare    -> ok=False, names it
                (a renamed sibling module used to SKIP green)
  M3c SKIP-dep  missing submodule of a declared package      -> ok=True (top-level match)
  M4  FAIL      fixture prints a failed check                -> ok=False, rc + detail
  M5  drift     manifest_check(): exact match -> None; unregistered / vanished -> problem
  M6  silent    rc 0 with no output at all                   -> ok=False
  M7a strict    declared skip on a ci_required entry          -> ok=False under --strict
  M7b strict    declared skip on a not-ci_required entry      -> still SKIP under --strict
  M8  flags     an unknown flag (a typo'd --strict)           -> exit 2, never a normal run

Exit 0 = every mutation caught. Exit 1 = the gate would have shipped blind.
"""

import importlib.util
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
        print(
            f"  {'ok' if cond else 'FAIL'} {name}"
            + (f"   [{detail}]" if not cond and detail else "")
        )
        if not cond:
            failures.append(name)

    with tempfile.TemporaryDirectory(prefix="selftest-gate-") as td:
        tmp = Path(td)

        # M1 — green fixture classifies PASS
        f1 = write_fixture(tmp, "pass", 'print("fixture ok")\n')
        label, ok, note = r.run_one(f1)
        check("M1 pass-fixture -> PASS", ok and note.startswith("PASS"), note[:120])

        H = r.Harness
        skip77 = H(skip_rc_ok=True)

        # M2 — exit 77 is a SKIP only for an entry declared skip_rc_ok
        f2 = write_fixture(
            tmp, "skiprc", 'import sys\nprint("SKIP - pinned env missing")\nraise SystemExit(77)\n'
        )
        label, ok, note = r.run_one(f2, skip77)
        check("M2a declared rc-77 -> SKIP", ok and note.startswith("SKIP"), f"ok={ok} {note[:100]}")
        label, ok, note = r.run_one(f2)
        check("M2b undeclared rc-77 -> FAIL", not ok and "rc=77" in note, f"ok={ok} {note[:100]}")

        # M3 — a missing module is a SKIP only when the entry declares it optional
        missing = "this_module_definitely_does_not_exist_xyz"
        f3 = write_fixture(tmp, "skipdep", f"import {missing}\n")
        label, ok, note = r.run_one(f3, H({missing}))
        check(
            "M3a declared missing dep -> SKIP names it",
            ok and note.startswith("SKIP") and missing in note,
            f"ok={ok} {note[:100]}",
        )
        label, ok, note = r.run_one(f3)
        check(
            "M3b undeclared missing module -> FAIL names it",
            (not ok) and missing in note and "not a declared optional dep" in note,
            f"ok={ok} {note[:120]}",
        )
        f3c = write_fixture(tmp, "skipsub", f"import {missing}.sub.module\n")
        label, ok, note = r.run_one(f3c, H({missing}))
        check(
            "M3c declared package's submodule -> SKIP", ok and note.startswith("SKIP"), note[:100]
        )

        # M6 — exit 0 that printed nothing proves nothing
        f6 = write_fixture(tmp, "silent", "x = 1\n")
        label, ok, note = r.run_one(f6)
        check(
            "M6 silent rc-0 -> FAIL", not ok and "printed nothing" in note, f"ok={ok} {note[:100]}"
        )

        # M7 — --strict: a ci_required harness may not skip; a not-ci_required one may
        label, ok, note = r.run_one(f3, H({missing}), strict=True)
        check("M7a strict + ci_required skip -> FAIL", not ok and "--strict" in note, note[:100])
        label, ok, note = r.run_one(f3, H({missing}, ci_required=False), strict=True)
        check(
            "M7b strict + not-ci_required skip -> SKIP", ok and note.startswith("SKIP"), note[:100]
        )

        # M4 — real failure classifies FAIL with rc + the failing line surfaced
        f4 = write_fixture(
            tmp, "fail", 'print("FAIL  some_check   [bad value]")\nraise SystemExit(2)\n'
        )
        label, ok, note = r.run_one(f4)
        check(
            "M4 failed-check -> FAIL with rc=2 + detail",
            (not ok) and "rc=2" in note and "some_check" in note,
            f"ok={ok} {note[:100]}",
        )

    # M5 — manifest drift detection, both directions (pure function; no tree mutation needed)
    candidates = r.discover()  # live discovery == today's ground truth for this repo
    check(
        "M5a exact-match candidate list -> no drift",
        r.manifest_check(candidates) is None,
        f"candidates={len(candidates)}",
    )
    drifted = candidates + ["some-new-skill/scripts/brand_new_verify.py"]
    prob = r.manifest_check(drifted) or ""
    check(
        "M5b unregistered harness -> drift problem names it",
        "unregistered" in prob and "brand_new_verify.py" in prob,
        prob[:120],
    )
    stale_auto = [
        c for c in candidates if c != sorted(candidates)[0]
    ]  # pretend one AUTO_RUN file vanished
    check(
        "M5c missing AUTO_RUN file -> drift problem",
        (r.manifest_check(stale_auto) or "") != "",
        "expected a problem string",
    )

    # M8 — a typo'd flag must stop the run, not silently run non-strict
    import subprocess

    proc = subprocess.run(
        [sys.executable, str(RUNNER), "--strcit"], capture_output=True, text=True, timeout=60
    )
    check(
        "M8 unknown flag -> exit 2",
        proc.returncode == 2,
        f"rc={proc.returncode} {proc.stdout[:100]}",
    )

    print()
    if failures:
        print(
            f"FAILED ({len(failures)}): {', '.join(failures)} — the self-test gate itself is blind to these modes."
        )
        return 1
    print(
        "ALL MUTATIONS CAUGHT — run-self-tests.py classification verified fail-loud "
        "(PASS/declared-SKIP/undeclared-FAIL/silent/strict/drift/flags)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
