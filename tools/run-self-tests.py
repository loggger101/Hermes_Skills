#!/usr/bin/env python3
"""Discovery-based runner for the skill self-test harnesses (*_verify.py).

Why this exists: run-skill-tests.py runs every pytest suite under a <skill>/tests/
dir, but the repo's other fail-loud mechanism — standalone *verification* scripts
that re-execute documented behavior against concrete cases (e.g. polars-v2-verify,
cap_grid_verify, ssrf_guard_verify) — was only ever run by hand on one machine.
If an upstream API shifts (polars deprecates cut/qcut; duckdb changes a default),
nothing in CI would notice until someone happened to re-run locally. This runner
closes that gap with the same discovery philosophy as run-skill-tests.py:

  * every file matching *_verify.py or *-verify.py under any <skill>/scripts/ or
    <skill>/references/ dir (excluding .hermes/, docs/, profiles-export/) is a
    candidate harness;
  * each runs once with sys.executable, cwd = its own directory, and the result
    is classified:
        rc == 0                          -> PASS
        rc == 77 or ModuleNotFoundError  -> SKIP (missing optional dependency —
                                            e.g. polars/duckdb/pyomo not installed;
                                            a dedicated CI job installs them)
        any other non-zero               -> FAIL (a real regression, printed loud)
  * the manifest below is the single source of truth for what may auto-run:
    every discovered harness must appear in AUTO_RUN or EXCLUDED. A new verify
    script that lands unregistered makes this runner exit 1 until someone decides
    how it should be handled — fail-loud, same contract as run-skill-tests.py's
    empty-scan-is-FATAL rule and the index drift gates.

Exit code: number of failed harnesses (0 = all pass or skip). --list prints what
would run without executing anything. Extra path args override discovery for that
run only (used by tools/mutation-test-selftest-gate.py to test a mutated copy in
a temp dir — those paths bypass the manifest check deliberately, since they are
throwaway fixtures, not repo harnesses).

Usage:
    py tools/run-self-tests.py            # run every registered harness
    py tools/run-self-tests.py --list     # print discovery + classification
"""
import os
import re
import subprocess
import sys
from pathlib import Path

if sys.version_info < (3, 8):
    raise SystemExit(
        "[FATAL] run-self-tests.py needs Python 3.8+, got " + sys.version.split()[0]
    )
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

REPO = Path(__file__).resolve().parents[1]
PY = sys.executable or "python3"
TIMEOUT_S = 600  # big-data harness builds a 200k-row fixture; generous but bounded

# --------------------------------------------------------------------------- manifest
# Harnesses that are self-contained (no required CLI args, no live network I/O) and
# safe to auto-run in any environment. Missing *optional* deps classify as SKIP —
# the dedicated CI jobs install those deps so they actually execute there.
AUTO_RUN = {
    "data-science/algorithms-python-catalog/scripts/algorithms_verify.py",   # numpy only
    "data-science/space-data-pipelines/scripts/cap_grid_verify.py",         # stdlib only (lgrs-free port)
    "devops/rest-api-client/scripts/ssrf_guard_verify.py",                  # stdlib, no sockets opened
    "data-science/python-data-science/references/big-data-patterns-verify.py",  # duckdb/polars/pyarrow -> skip without them
    "data-science/python-data-science/references/polars-v2-verify.py",      # polars 2.0.x rc -> skip on stable/absent (rc 77)
    "data-science/optimization-modeling-pyomo/scripts/pyomo_patterns_verify.py",  # pyomo+highspy -> skip without them
}

# Discovered but deliberately NOT auto-run, each with the reason it must stay out:
EXCLUDED = {
    # probes a live external API on every run — nondeterministic in CI by design
    "data-science/space-data-pipelines/scripts/lps_projection_verify.py":
        "live lgrs-oracle comparison (network); keep manual / dedicated job only",
}

SKIP_RC = 77  # convention: harness exits this when its pinned env is not present


def discover() -> list[str]:
    """Every *verify*.py under a skill's scripts/ or references/, repo-relative posix.

    Naming is mixed in this repo (`algorithms_verify.py` vs `big-data-patterns-verify.py`) —
    both underscore and hyphen forms are matched; anything else (e.g. *_crosscheck.py)
    is out of scope by name, so it never needs a manifest entry.
    """
    found = []
    for pattern in ("*_verify.py", "*-verify.py"):
        for p in REPO.rglob(pattern):
            parts = p.relative_to(REPO).parts
            if any(part in (".git", ".hermes", "docs", "profiles-export") or part.startswith(".")
                   for part in parts):
                continue
            rel = "/".join(parts)
            # must live under a skill's scripts/ or references/ dir, not e.g. tools/
            if re.search(r"/(scripts|references)/[^/]+$", "/" + rel):
                found.append(rel.replace("\\", "/"))
    return sorted(set(found))


def manifest_check(candidates: list[str]) -> int | None:
    """Return a problem string, or None when discovery == manifest (no drift)."""
    unregistered = [c for c in candidates if c not in AUTO_RUN and c not in EXCLUDED]
    stale_auto = sorted(AUTO_RUN - set(candidates))
    stale_excl = sorted(EXCLUDED.keys() - set(candidates))
    problems = []
    if unregistered:
        problems.append("unregistered harness(es) — add to AUTO_RUN or EXCLUDED with a reason: "
                        + ", ".join(unregistered))
    if stale_auto:
        problems.append("AUTO_RUN lists files that no longer exist (rename/delete?): "
                        + ", ".join(stale_auto))
    if stale_excl:
        problems.append("EXCLUDED lists files that no longer exist: " + ", ".join(stale_excl))
    return "; ".join(problems) or None  # None = clean; a truthy string always means drift


def _label(target: Path) -> str:
    """Repo-relative posix path when inside the repo; name + parent dir otherwise."""
    try:
        return target.relative_to(REPO).as_posix()
    except ValueError:  # explicit-path fixture living outside the repo (temp dir)
        return f"{target.name}  [{target.parent.as_posix()}]"


def run_one(target: Path) -> tuple[str, bool, str]:
    """Run one harness; classify PASS / SKIP / FAIL. Returns (label, ok, note)."""
    label = _label(target)
    try:
        proc = subprocess.run(
            [PY, str(target)], cwd=str(target.parent),
            capture_output=True, text=True, timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return label, False, f"TIMEOUT after {TIMEOUT_S}s"
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")

    if proc.returncode == 0:
        tail = [l.strip() for l in out.splitlines() if l.strip()]
        return label, True, "PASS — " + (tail[-1][:120] if tail else "(silent)")
    missing_dep = (proc.returncode == SKIP_RC
                   or re.search(r"ModuleNotFoundError: No module named '([A-Za-z_][\w.]*)'", out) is not None)
    if missing_dep:
        m = re.search(r"No module named '([^']+)'", out)
        return label, True, f"SKIP — optional dep missing ({m.group(1) if m else 'env'})"
    # real failure: surface the failing line(s), capped so one harness can't flood CI
    bad = [l.strip() for l in out.splitlines()
           if re.search(r"\bFAIL|FAILED\b|Error|assert", l)]
    detail = "\n".join(f"      {l[:200]}" for l in bad[-15:]) or "      (no failure lines parsed — see CI log)"
    return label, False, f"rc={proc.returncode}\n{detail}"


def main(argv: list[str]) -> int:
    flags = [a for a in argv if a.startswith("--")]
    positions = [a for a in argv if not a.startswith("--")]
    explicit_mode = bool(positions) and "--list" not in flags

    if explicit_mode:
        # literal paths (used by tools/mutation-test-selftest-gate.py on throwaway
        # fixtures in a temp dir): run exactly what is given, no discovery, no manifest.
        targets = [Path(p).resolve() for p in positions]
        missing = [str(t) for t in targets if not t.exists()]
        if missing:
            print(f"[FATAL] explicit harness path(s) do not exist:\n  " + "\n  ".join(missing))
            return 1
    else:
        candidates = discover()
        drift = manifest_check(candidates)
        auto = sorted(set(AUTO_RUN) & set(candidates))

        if "--list" in flags:
            print(f"{len(candidates)} harness discovered; {len(auto)} auto-run, "
                  f"{len(EXCLUDED)} excluded:")
            for c in candidates:
                tag = ("AUTO-RUN" if c in AUTO_RUN else
                       ("EXCLUDE  " + EXCLUDED[c][:60] if c in EXCLUDED else
                        "!! UNREGISTERED"))
                print(f"  {tag:<12} {c}")
            if drift:
                print("\n[FATAL] manifest drift:\n  " + drift)
                return 1
            return 0

        # hard-fail BEFORE running anything — an unregistered harness must be a decision,
        # never a silent gap (same fail-loud contract as run-skill-tests.py's empty scan).
        if drift:
            print(f"[FATAL] manifest drift before any run:\n  {drift}")
            return 1

        targets = [REPO / c for c in auto]

    results = []
    for t in targets:  # both branches produce absolute Paths (discovery: REPO/c, explicit: resolved)
        label, ok, note = run_one(Path(t))
        results.append((label, ok, note))

    print("=== self-test harnesses ===" + ("  (explicit paths)" if explicit_mode else ""))
    width = max(len(r[0]) for r in results) if results else 20
    for label, ok, note in results:
        first_line = note.splitlines()[0]
        tag = "SKIP" if (ok and note.startswith("SKIP")) else ("PASS" if ok else "FAIL")
        print(f"  {tag:<5} {label.ljust(width)}  {first_line}")
        for extra in note.splitlines()[1:]:
            print(f"       {extra}")

    failed = [r[0] for r in results if not r[1]]
    skipped = sum(1 for _, ok, n in results if ok and n.startswith("SKIP"))
    passed = len(results) - len(failed) - skipped
    if failed:
        print(f"\n{len(failed)} FAILED / {passed} pass / {skipped} skip — see details above")
        return 1
    print(f"\nALL GREEN — {passed} pass, {skipped} skip (missing optional deps), 0 fail")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
