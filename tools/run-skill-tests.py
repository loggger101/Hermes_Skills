#!/usr/bin/env python3
"""Discover and run every test suite that ships inside a skill, one command.

Why this exists: the first version of .github/workflows/ci.yml hardcoded five
suite paths in YAML (docx/pdf/powerpoint/xlsx/comfyui). Hardcoded lists drift —
the moment any new skill ships a tests/ dir it is silently absent from CI until
someone remembers to edit the workflow. Discovery removes that class of mistake.

Four suite kinds are discovered (outside profiles-export/, docs/, .hermes/, tools/,
node_modules/):

  pytest  every directory named `tests` holding a test_*.py / *_test.py file; its
          dir is pytest's working directory so conftest.py resolves as it does locally
  node    every directory holding *.test.js / *.test.cjs / *.test.mjs files, run with
          `node --test` (the security-audit validators shipped 65 such tests that no
          runner executed; 7 of them failed on Windows and nobody knew)
  sh      every *.sh inside a `tests` dir, run with bash (Git Bash on Windows, never
          the WSL launcher in System32)
  ps1     every *.ps1 inside a `tests` dir, run with pwsh, else Windows PowerShell

Every suite must PROVE it tested something, or it fails:

  * non-zero exit                        -> FAIL
  * no parseable summary / PASS lines    -> FAIL (the run cannot be shown to have tested)
  * zero passing tests (all skipped)     -> FAIL (a suite that skipped everything
                                            verified nothing; a partial skip is shown)
  * interpreter (node/bash/PowerShell) not found -> FAIL, never a quiet skip

And every test-shaped file must belong to a suite: a test_*.py outside a `tests` dir,
a *.test.ts nothing can run, a smoke script in an unexpected place — each is an
ORPHAN, and orphans are FATAL until someone moves the file or records why it is
exempt in ORPHAN_EXEMPT. That is how the security-audit and ast-grep suites sat
unexecuted: the runner simply did not know their shape existed.

An empty scan is FATAL too. Usage:
    py tools/run-skill-tests.py                 # run every discovered suite
    py tools/run-skill-tests.py --list          # print suites + orphans, run nothing
    py tools/run-skill-tests.py --root DIR      # discover under DIR (mutation fixtures)
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

if sys.version_info < (3, 8):
    raise SystemExit("[FATAL] run-skill-tests.py needs Python 3.8+, got " + sys.version.split()[0])
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

REPO = Path(__file__).resolve().parents[1]
PY = sys.executable or "python3"
# Decode child output as UTF-8 (and make children emit it); the Windows codepage cannot.
CHILD_IO = dict(encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
TIMEOUT_S = 900

# Historical snapshots and non-skill trees never contain skill suites. tools/ holds the
# gates' own unit tests, which verify-all runs as a gate of its own.
SKIP_DIRS = {".git", ".hermes", ".github", "profiles-export", "docs", "tools", "node_modules"}
NODE_TEST_SUFFIXES = (".test.js", ".test.cjs", ".test.mjs")

# Test-shaped files that deliberately belong to no suite, each with the reason.
# Repo-relative posix path -> reason. Empty today; an entry is a decision, not a default.
ORPHAN_EXEMPT = {}


class Suite:
    """One runnable suite: a directory plus the kind of runner that executes it."""

    def __init__(self, kind, directory, files, root):
        self.kind = kind
        self.dir = directory
        self.files = sorted(files)
        rel = directory.relative_to(root).as_posix()
        self.label = rel if kind == "pytest" else f"{rel} [{kind}]"
        # README key: the owning skill's dir name, plus the kind when it is not pytest
        # (ast-grep ships both an sh and a ps1 suite in one dir).
        owner = directory.parent.name if directory.name in ("tests", "scripts") else directory.name
        self.key = owner if kind == "pytest" else f"{owner}:{kind}"

    def __repr__(self):
        return f"Suite({self.label!r})"


def _skipped(rel_parts):
    return any(part in SKIP_DIRS or part == "__pycache__" for part in rel_parts)


def _walk(root):
    """Every file under root outside SKIP_DIRS, as (path, rel_parts)."""
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root).parts
        if _skipped(rel_dir):
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and d != "__pycache__"]
        for name in filenames:
            yield Path(dirpath) / name, rel_dir + (name,)


def _is_pytest_file(name):
    return name.endswith(".py") and (name.startswith("test_") or name.endswith("_test.py"))


def discover_suites(root=None):
    """Return every runnable Suite under the repo (or `root`), sorted by label."""
    root = Path(root or REPO)
    by_key = {}
    for path, parts in _walk(root):
        name, parent = path.name, path.parent
        kind = None
        if parent.name == "tests" and _is_pytest_file(name):
            kind = "pytest"
        elif name.endswith(NODE_TEST_SUFFIXES):
            kind = "node"
        elif parent.name == "tests" and name.endswith(".sh"):
            kind = "sh"
        elif parent.name == "tests" and name.endswith(".ps1"):
            kind = "ps1"
        if kind:
            by_key.setdefault((kind, parent), []).append(path)
    suites = [Suite(kind, d, files, root) for (kind, d), files in by_key.items()]
    return sorted(suites, key=lambda s: s.label)


def find_orphans(root=None, suites=None):
    """Test-shaped files that no suite will ever execute (repo-relative posix paths)."""
    root = Path(root or REPO)
    covered = {
        f for s in (suites if suites is not None else discover_suites(root)) for f in s.files
    }
    orphans = []
    for path, parts in _walk(root):
        name = path.name
        test_shaped = (
            _is_pytest_file(name)
            or re.search(r"\.test\.[a-z0-9]+$", name) is not None
            or re.search(r"(^|[-_])smoke([-_.]|$)", name) is not None
            or (path.parent.name == "tests" and name.endswith((".sh", ".ps1", ".bats")))
        )
        if not test_shaped or path in covered:
            continue
        rel = "/".join(parts)
        if rel not in ORPHAN_EXEMPT:
            orphans.append(rel)
    return sorted(orphans)


def count_tests(suite):
    """Static test count, the way a human reads 'comfyui 117': call sites, not runtime cases.

    pytest: `def test_*` definitions (parametrize expansions are not counted).
    node:   `test(` / `it(` call sites.
    sh/ps1: `pass ...` / `Pass ...` call sites (one per smoke check; a check with two
            alternative outcomes has two call sites).
    """
    n = 0
    for f in suite.files if suite.kind != "pytest" else sorted(suite.dir.rglob("*.py")):
        txt = f.read_text(encoding="utf-8", errors="replace")
        if suite.kind == "pytest":
            n += len(re.findall(r"^\s*def (test_\w+)", txt, re.M))
        elif suite.kind == "node":
            n += len(re.findall(r"^\s*(?:test|it)\(", txt, re.M))
        elif suite.kind == "sh":
            n += len(re.findall(r"^\s*pass \"", txt, re.M))
        else:
            n += len(re.findall(r"\bPass ['\"]", txt))
    return n


def _bash():
    """A real bash. On Windows System32\\bash.exe is the WSL launcher: a different OS
    with a different python3, so it is never accepted; Git Bash is found via git."""
    found = shutil.which("bash")
    if found and not (os.name == "nt" and "system32" in found.lower()):
        return found
    git = shutil.which("git")
    if git:
        for cand in (
            Path(git).parents[1] / "bin" / "bash.exe",
            Path(git).parents[1] / "usr" / "bin" / "bash.exe",
        ):
            if cand.exists():
                return str(cand)
    return None


def _powershell():
    return shutil.which("pwsh") or shutil.which("powershell")


def _counts(pattern, out):
    return {k: int(v) for v, k in re.findall(pattern, out)}


def _command(suite):
    """(argv, None) or (None, reason the suite cannot run here)."""
    if suite.kind == "pytest":
        # -rfEs, not -rs: any -r value REPLACES pytest's default 'fE', and without it the
        # FAILED/ERROR lines that name each broken test vanish (the mutation test caught it).
        return [PY, "-m", "pytest", "--tb=line", "-q", "-rfEs", "."], None
    if suite.kind == "node":
        node = shutil.which("node")
        if not node:
            return None, "node not found on PATH — cannot run this suite"
        return [node, "--test", *[f.name for f in suite.files]], None
    if suite.kind == "sh":
        bash = _bash()
        if not bash:
            return None, "no bash found (Git Bash on Windows) — cannot run this suite"
        return [bash, *[f.name for f in suite.files]], None
    ps = _powershell()
    if not ps:
        return None, "neither pwsh nor powershell found — cannot run this suite"
    if len(suite.files) != 1:
        return None, f"{len(suite.files)} .ps1 files in one tests dir; the runner runs one per dir"
    return [ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", suite.files[0].name], None


def classify(suite, rc, out):
    """Judge a finished run. Returns (ok, note); every PASS must show tests that passed."""
    fail_lines = []
    if suite.kind == "pytest":
        m = re.search(r"^(\d+ \w+(?:, \d+ \w+)*) in [\d.]+s", out, re.M)
        summary = m.group(1) if m else None
        c = _counts(r"(\d+) (\w+)", summary or "")
        passed, skipped = c.get("passed", 0), c.get("skipped", 0)
        fail_lines = [ln.strip() for ln in out.splitlines() if ln.startswith(("FAILED ", "ERROR "))]
        # A collection error's summary line is just 'ERROR test_x.py'; the cause (the
        # missing module, the syntax error) is only on pytest's 'E   ' detail lines.
        causes = []
        for ln in out.splitlines():
            if ln.startswith("E   ") and ln.strip() not in causes:
                causes.append(ln.strip())
        fail_lines += causes[:8]
        no_summary = "no pytest summary line — cannot show any test ran"
    elif suite.kind == "node":
        c = {
            k: int(v)
            for k, v in re.findall(r"^# (pass|fail|skipped|cancelled|todo) (\d+)\s*$", out, re.M)
        }
        summary = (
            ", ".join(f"{c[k]} {k}" for k in ("pass", "fail", "skipped") if k in c)
            if "pass" in c
            else None
        )
        passed, skipped = c.get("pass", 0), c.get("skipped", 0)
        fail_lines = [ln.strip() for ln in out.splitlines() if ln.startswith("not ok ")]
        no_summary = "no '# pass N' summary from node --test — cannot show any test ran"
    else:
        passed = len(re.findall(r"^PASS:", out, re.M))
        skipped = 0
        fail_lines = [ln.strip() for ln in out.splitlines() if ln.startswith("FAIL")]
        summary = f"{passed} checks passed" if passed else None
        no_summary = "no 'PASS:' lines — the smoke script proved nothing"

    note = summary or no_summary
    if rc != 0:
        if not fail_lines:
            tail = [ln.strip() for ln in out.splitlines() if ln.strip()][-3:]
            fail_lines = ["(no failure lines parsed; last output:)"] + tail
        return False, f"{note} (exit {rc})\n" + "\n".join(
            f"      {ln[:300]}" for ln in fail_lines[:25]
        )
    if summary is None:
        return False, no_summary
    if passed == 0:
        return False, f"{note} — 0 tests passed, so this suite verified nothing"
    if skipped:
        note += "  (skips listed by the suite: run it directly for reasons)"
    return True, note


def run_suite(suite):
    argv, why_not = _command(suite)
    if argv is None:
        return False, why_not
    try:
        proc = subprocess.run(
            argv, cwd=str(suite.dir), capture_output=True, timeout=TIMEOUT_S, **CHILD_IO
        )
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT after {TIMEOUT_S}s"
    except OSError as e:
        return False, f"could not start {argv[0]}: {e}"
    return classify(suite, proc.returncode, (proc.stdout or "") + "\n" + (proc.stderr or ""))


def main(argv):
    root = REPO
    if "--root" in argv:
        i = argv.index("--root")
        if i + 1 >= len(argv):
            print("[FATAL] --root needs a directory")
            return 2
        root = Path(argv[i + 1]).resolve()
        if not root.is_dir():
            print(f"[FATAL] --root {root} is not a directory")
            return 2
    suites = discover_suites(root)
    orphans = find_orphans(root, suites)

    if "--list" in argv:
        print(f"{len(suites)} suite(s) discovered:")
        for s in suites:
            print(f"  {s.label:<56} {count_tests(s):>4} tests  key={s.key}")
        if orphans:
            print(f"\n[FATAL] {len(orphans)} orphan test file(s) no runner executes:")
            for o in orphans:
                print(f"  {o}")
            return 1
        return 0

    if not suites:
        # An empty scan is FATAL, not a pass — the same rule as verify-all.py.
        print("[FATAL] no test suites discovered; repo layout changed?")
        return 1

    results = []
    for s in suites:
        try:
            ok, note = run_suite(s)
        except Exception as e:  # noqa: BLE001 — one broken suite must not mask the rest
            ok, note = False, f"runner crashed: {type(e).__name__}: {e}"[:200]
        results.append((s.label, ok, note))

    print("=== skill test suites ===")
    for label, ok, note in results:
        first, *rest = note.splitlines()
        print(f"  {'PASS' if ok else 'FAIL'}  {label:<56} {first}")
        for extra in rest:
            print(extra)
    if orphans:
        print(
            f"\n[FATAL] {len(orphans)} orphan test file(s) that no suite runs — move each "
            "into a suite shape or record why in ORPHAN_EXEMPT:"
        )
        for o in orphans:
            print(f"  {o}")
    failed = [r[0] for r in results if not r[1]]
    if failed or orphans:
        print(f"\n{len(failed)}/{len(results)} suite(s) FAILED, {len(orphans)} orphan(s)")
        return 1
    print(f"\nALL {len(results)} SUITES PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
