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
    is classified against that harness's manifest entry:
        rc == 0 with output              -> PASS
        rc == 0 printing nothing         -> FAIL (a harness whose checks never ran —
                                            e.g. a lost `if __name__` block — exits 0 too)
        ModuleNotFoundError for a module
          the entry DECLARES optional    -> SKIP (polars/duckdb/pyomo not installed;
                                            the dedicated CI job installs them)
        ModuleNotFoundError for any
          other module                   -> FAIL (a renamed sibling module or a new hard
                                            dependency is a regression, not a skip;
                                            before round-256 every missing module SKIPped)
        rc == 77 from an entry declared
          skip_rc_ok                     -> SKIP (pinned env absent, e.g. polars 2.0 rc)
        rc == 77 from any other harness  -> FAIL
        any other non-zero               -> FAIL (a real regression, printed loud)
  * --strict (the CI job that installs every optional dep): a SKIP from a harness
    marked ci_required is a FAIL — there the deps are present, so a skip means the
    install broke and the harness silently stopped running.
  * the manifest below is the single source of truth for what may auto-run:
    every discovered harness must appear in AUTO_RUN or EXCLUDED. A new verify
    script that lands unregistered makes this runner exit 1 until someone decides
    how it should be handled — fail-loud, same contract as run-skill-tests.py's
    empty-scan-is-FATAL rule and the index drift gates.

Exit code: 1 if any harness failed, 2 on a usage or manifest problem (0 = all pass or skip). --list prints what
would run without executing anything. Extra path args override discovery for that
run only (used by tools/mutation-test-selftest-gate.py to test a mutated copy in
a temp dir — those paths bypass the manifest check deliberately, since they are
throwaway fixtures, not repo harnesses).

Usage:
    py tools/run-self-tests.py            # run every registered harness
    py tools/run-self-tests.py --strict   # CI job with every optional dep installed
    py tools/run-self-tests.py --list     # print discovery + classification
"""

import os
import re
import subprocess
import sys
from pathlib import Path

if sys.version_info < (3, 8):
    raise SystemExit("[FATAL] run-self-tests.py needs Python 3.8+, got " + sys.version.split()[0])
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

REPO = Path(__file__).resolve().parents[1]
PY = sys.executable or "python3"
# Decode child output as UTF-8 (and make children emit it); the Windows codepage cannot.
CHILD_IO = dict(encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
TIMEOUT_S = 600  # big-data harness builds a 200k-row fixture; generous but bounded


# --------------------------------------------------------------------------- manifest
class Harness:
    """How one harness may legitimately not run.

    optional     top-level module names whose absence is a SKIP (anything else missing
                 is a FAIL)
    skip_rc_ok   the harness may exit 77 to say its pinned environment is absent
    ci_required  under --strict (the CI job that installs selftest-requirements.txt)
                 a SKIP is a FAIL: there the deps exist, so a skip means it stopped running
    """

    def __init__(self, optional=(), skip_rc_ok=False, ci_required=True):
        self.optional = frozenset(optional)
        self.skip_rc_ok = skip_rc_ok
        self.ci_required = ci_required


STDLIB_ONLY = Harness()  # nothing may be missing, nothing may skip

# Harnesses that are self-contained (no required CLI args, no live network I/O) and
# safe to auto-run in any environment, each with what it may lack.
AUTO_RUN = {
    "data-science/algorithms-python-catalog/scripts/algorithms_verify.py": Harness({"numpy"}),
    "data-science/lunar-gis-projections/scripts/cap_grid_verify.py": STDLIB_ONLY,  # lgrs-free port
    "devops/rest-api-client/scripts/ssrf_guard_verify.py": STDLIB_ONLY,  # no sockets opened
    "web-development/web-perf-audit/scripts/perf_audit_verify.py": STDLIB_ONLY,  # temp-dir fixtures
    "data-science/polars-pipelines/references/big-data-patterns-verify.py": Harness(
        {"numpy", "pandas", "duckdb", "polars", "pyarrow"}
    ),
    # pins polars 2.0.x rc behavior: exits 77 on stable or absent polars, CI included
    "data-science/polars-pipelines/references/polars-v2-verify.py": Harness(
        {"polars", "pyarrow"}, skip_rc_ok=True, ci_required=False
    ),
    "data-science/optimization-modeling-pyomo/scripts/pyomo_patterns_verify.py": Harness(
        {"pyomo", "highspy"}
    ),
}

# Discovered but deliberately NOT auto-run, each with the reason it must stay out:
EXCLUDED = {
    # probes a live external API on every run — nondeterministic in CI by design
    "data-science/lunar-gis-projections/scripts/lps_projection_verify.py": "live lgrs-oracle comparison (network); keep manual / dedicated job only",
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
            if any(
                part in (".git", ".hermes", "docs", "profiles-export") or part.startswith(".")
                for part in parts
            ):
                continue
            rel = "/".join(parts)
            # must live under a skill's scripts/ or references/ dir, not e.g. tools/
            if re.search(r"/(scripts|references)/[^/]+$", "/" + rel):
                found.append(rel.replace("\\", "/"))
    return sorted(set(found))


def manifest_check(candidates: list[str]) -> int | None:
    """Return a problem string, or None when discovery == manifest (no drift)."""
    unregistered = [c for c in candidates if c not in AUTO_RUN and c not in EXCLUDED]
    stale_auto = sorted(AUTO_RUN.keys() - set(candidates))
    stale_excl = sorted(EXCLUDED.keys() - set(candidates))
    problems = []
    if unregistered:
        problems.append(
            "unregistered harness(es) — add to AUTO_RUN or EXCLUDED with a reason: "
            + ", ".join(unregistered)
        )
    if stale_auto:
        problems.append(
            "AUTO_RUN lists files that no longer exist (rename/delete?): " + ", ".join(stale_auto)
        )
    if stale_excl:
        problems.append("EXCLUDED lists files that no longer exist: " + ", ".join(stale_excl))
    return "; ".join(problems) or None  # None = clean; a truthy string always means drift


def _label(target: Path) -> str:
    """Repo-relative posix path when inside the repo; name + parent dir otherwise."""
    try:
        return target.relative_to(REPO).as_posix()
    except ValueError:  # explicit-path fixture living outside the repo (temp dir)
        return f"{target.name}  [{target.parent.as_posix()}]"


def run_one(target: Path, spec=STDLIB_ONLY, strict=False) -> tuple[str, bool, str]:
    """Run one harness; classify PASS / SKIP / FAIL against its manifest entry.

    Returns (label, ok, note); note starts with PASS / SKIP / a failure reason.
    """
    label = _label(target)
    try:
        proc = subprocess.run(
            [PY, str(target)],
            cwd=str(target.parent),
            capture_output=True,
            timeout=TIMEOUT_S,
            **CHILD_IO,
        )
    except subprocess.TimeoutExpired:
        return label, False, f"TIMEOUT after {TIMEOUT_S}s"
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")

    tail = [line.strip() for line in out.splitlines() if line.strip()]
    if proc.returncode == 0:
        if not tail:
            return label, False, "rc=0 but printed nothing — its checks may never have run"
        return label, True, "PASS — " + tail[-1][:120]

    skip_note = None
    if proc.returncode == SKIP_RC:
        if not spec.skip_rc_ok:
            return (
                label,
                False,
                (
                    f"rc=77 (skip) from a harness not declared skip_rc_ok — "
                    f"{tail[-1][:120] if tail else '(no output)'}"
                ),
            )
        skip_note = f"SKIP — pinned env absent: {tail[-1][:100] if tail else '(no output)'}"
    else:
        m = re.search(r"ModuleNotFoundError: No module named '([A-Za-z_][\w.]*)'", out)
        if m:
            top = m.group(1).split(".")[0]
            if top not in spec.optional:
                declared = ", ".join(sorted(spec.optional)) or "none"
                return (
                    label,
                    False,
                    (
                        f"rc={proc.returncode} — missing module {m.group(1)!r} is not a declared "
                        f"optional dep (declared: {declared}); a renamed sibling or a new hard "
                        "dependency is a regression, not a skip"
                    ),
                )
            skip_note = f"SKIP — optional dep missing ({m.group(1)})"
    if skip_note:
        if strict and spec.ci_required:
            return label, False, f"--strict: {skip_note[7:]} — this job installs it, so it must run"
        return label, True, skip_note
    # real failure: surface the failing line(s), capped so one harness can't flood CI
    bad = [
        line.strip()
        for line in out.splitlines()
        if re.search(r"\bFAIL|FAILED\b|Error|assert", line)
    ]
    detail = (
        "\n".join(f"      {line[:200]}" for line in bad[-15:])
        or "      (no failure lines parsed — see CI log)"
    )
    return label, False, f"rc={proc.returncode}\n{detail}"


def main(argv: list[str]) -> int:
    flags = [a for a in argv if a.startswith("--")]
    positions = [a for a in argv if not a.startswith("--")]
    explicit_mode = bool(positions) and "--list" not in flags
    strict = "--strict" in flags
    unknown = sorted(set(flags) - {"--list", "--strict"})
    if unknown:
        print(f"[FATAL] unknown flag(s): {', '.join(unknown)}")
        return 2

    if explicit_mode:
        # literal paths (used by tools/mutation-test-selftest-gate.py on throwaway
        # fixtures in a temp dir): run exactly what is given, no discovery, no manifest.
        targets = [Path(p).resolve() for p in positions]
        missing = [str(t) for t in targets if not t.exists()]
        if missing:
            print("[FATAL] explicit harness path(s) do not exist:\n  " + "\n  ".join(missing))
            return 1
    else:
        candidates = discover()
        drift = manifest_check(candidates)
        auto = sorted(set(AUTO_RUN) & set(candidates))

        if "--list" in flags:
            print(
                f"{len(candidates)} harness discovered; {len(auto)} auto-run, "
                f"{len(EXCLUDED)} excluded:"
            )
            for c in candidates:
                if c in AUTO_RUN:
                    h = AUTO_RUN[c]
                    tag = "AUTO-RUN"
                    extra = (
                        f"  optional={','.join(sorted(h.optional)) or '-'}"
                        f"{' rc77-ok' if h.skip_rc_ok else ''}"
                        f"{'' if h.ci_required else ' not-ci-required'}"
                    )
                elif c in EXCLUDED:
                    tag, extra = "EXCLUDE  " + EXCLUDED[c][:60], ""
                else:
                    tag, extra = "!! UNREGISTERED", ""
                print(f"  {tag:<12} {c}{extra}")
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

    if not targets:
        print("[FATAL] nothing to run: no registered harness was discovered")
        return 1
    results = []
    for (
        t
    ) in targets:  # both branches produce absolute Paths (discovery: REPO/c, explicit: resolved)
        rel = _label(Path(t))
        spec = AUTO_RUN.get(rel, STDLIB_ONLY)  # explicit fixture paths get the strictest entry
        label, ok, note = run_one(Path(t), spec, strict)
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
