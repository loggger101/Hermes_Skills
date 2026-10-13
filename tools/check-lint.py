#!/usr/bin/env python3
"""Gate: the repo's Python is clean under `ruff check` and `ruff format --check`, and every
path ruff.toml names still exists.

Round-257. README promised the code was "kept clean under `ruff check`" and formatted with
`ruff format`; no gate or CI job ran either, and the tree had 16 lint errors and 10
unformatted files. ruff.toml also carried a per-file ignore for a file that had moved two
rounds earlier: ruff silently ignores a pattern that matches nothing, so the moved file's
four E402 findings were live while the config looked deliberate.

Checks:
  1  ruff check .            (rules pinned in ruff.toml [lint] select)
  2  ruff format --check .
  3  every ruff.toml extend-exclude entry and per-file-ignores key matches a tracked path
  4  extend-exclude == the bundled skills (profile/.bundled_manifest) that contain Python.
     Round-257 found two bundled skills missing, so `ruff format` rewrote their files.
  5  a non-excluded Python file that prints a non-ASCII string literal must switch stdout
     to UTF-8 (sys.stdout.reconfigure). On a cp1252 console or pipe, print('✓') raises
     UnicodeEncodeError, and evidence-store.py raised it AFTER saving: a successful add
     exited 1. Bundled skills are upstream's to fix and are counted, not failed.
  6  the installed ruff is the version pinned in requirements.txt, and ci.yml pins the same:
     an unpinned or drifted ruff changes rules and formatting with no code change.

ruff not installed is a FAIL with the install line, never a skip.

Usage:
    python tools/check-lint.py
    LINT_SCAN_ROOT=/tmp/fixture python tools/check-lint.py     # mutation self-test

Exit 0 = clean. Exit 1 = findings. Exit 2 = the check could not run.
"""

import ast
import fnmatch
import os
import re
import subprocess
import sys
from pathlib import Path

from _repo_files import repo_files

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

REPO = Path(os.environ.get("LINT_SCAN_ROOT") or Path(__file__).resolve().parents[1])
INSTALL = "pip install -r requirements.txt  (pins ruff)"


def ruff(*args):
    try:
        return subprocess.run(
            [sys.executable, "-m", "ruff", *args],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        raise SystemExit("[FATAL] ruff timed out after 300s")


def stale_config_paths(config, tracked):
    """ruff.toml paths that match no tracked file or directory."""
    stale = []
    dirs = {str(Path(t).parent.as_posix()) for t in tracked}
    for parent in list(dirs):
        p = Path(parent)
        while str(p) not in (".", ""):
            dirs.add(p.as_posix())
            p = p.parent
    universe = set(tracked) | dirs

    def matches(pattern):
        if pattern in universe:
            return True
        return any(
            fnmatch.fnmatch(t, pattern) or fnmatch.fnmatch(t, pattern + "/*") for t in tracked
        )

    for pat in config.get("extend-exclude", []):
        if not matches(pat):
            stale.append(f"extend-exclude {pat!r}")
    for pat in config.get("lint", {}).get("per-file-ignores", {}):
        if not matches(pat):
            stale.append(f"lint.per-file-ignores {pat!r}")
    return stale


def ruff_pins():
    """(requirements.txt pin, ci.yml pin); None where a file names no exact ruff pin."""
    out = []
    for rel in ("requirements.txt", ".github/workflows/ci.yml"):
        path = REPO / rel
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        m = re.search(r"\bruff==([0-9][0-9.]*[0-9])", text)
        out.append(m.group(1) if m else None)
    return tuple(out)


def bundled_dirs(tracked):
    """Repo dirs of the skills profile/.bundled_manifest names (by SKILL.md `name:`)."""
    manifest = REPO / "profile" / ".bundled_manifest"
    if not manifest.is_file():
        raise SystemExit(f"[FATAL] {manifest} missing: cannot tell which skills are bundled")
    names = {
        ln.split(":")[0] for ln in manifest.read_text(encoding="utf-8").splitlines() if ":" in ln
    }
    dirs = set()
    for f in tracked:
        if f.endswith("/SKILL.md"):
            text = (REPO / f).read_text(encoding="utf-8", errors="replace")
            m = re.search(r"^name:\s*['\"]?([^'\"\r\n]+)", text, re.M)
            if m and m.group(1).strip() in names:
                dirs.add(f.rsplit("/", 1)[0])
    return dirs


def unsafe_prints(source):
    """Lines of print()/.write()/SystemExit()/exit() calls whose string literals hold non-ASCII, in a file that
    never reconfigures its output encoding."""
    if "reconfigure(" in source or "PYTHONIOENCODING" in source:
        return []
    lines = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call):
            fn = node.func
            name = (
                fn.id
                if isinstance(fn, ast.Name)
                else fn.attr
                if isinstance(fn, ast.Attribute)
                else ""
            )
            if name in ("print", "write", "SystemExit", "exit") and any(
                isinstance(c, ast.Constant) and isinstance(c.value, str) and not c.value.isascii()
                for c in ast.walk(node)
            ):
                lines.append(node.lineno)
    return sorted(set(lines))


def main():
    try:
        import tomllib
    except ModuleNotFoundError:
        print("[FATAL] tomllib missing: check-lint.py needs Python 3.11+ to read ruff.toml")
        return 2
    version = ruff("--version")
    if version.returncode != 0:
        print(f"[FATAL] ruff is not installed for {sys.executable}: {INSTALL}")
        return 2
    cfg_path = REPO / "ruff.toml"
    if not cfg_path.is_file():
        print(f"[FATAL] {cfg_path} missing: the lint settings this gate enforces are gone")
        return 2
    config = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
    tracked = repo_files(REPO)

    problems = []
    check = ruff("check", ".", "--output-format", "concise")
    if check.returncode != 0:
        lines = [ln for ln in check.stdout.splitlines() if ln.strip()]
        problems += [f"ruff check: {ln}" for ln in lines[:40]]
        if not lines:
            problems.append(f"ruff check exited {check.returncode}: {check.stderr.strip()[:300]}")
    fmt = ruff("format", "--check", "--output-format", "concise", ".")
    if fmt.returncode != 0:
        lines = [ln for ln in fmt.stdout.splitlines() if "unformatted" in ln]
        problems += [f"ruff format: {ln}" for ln in lines]
        if not lines:
            problems.append(
                f"ruff format --check exited {fmt.returncode}: {(fmt.stderr or fmt.stdout).strip()[:300]}"
            )
    problems += [
        f"ruff.toml names a path that matches nothing: {s}"
        for s in stale_config_paths(config, tracked)
    ]

    installed = version.stdout.split()[-1] if version.stdout.split() else "?"
    req_pin, ci_pin = ruff_pins()
    if req_pin is None or ci_pin is None:
        problems.append(
            f"ruff is not pinned (ruff==X.Y.Z): requirements.txt={req_pin}, ci.yml={ci_pin}"
        )
    elif not req_pin == ci_pin == installed:
        problems.append(
            f"ruff versions disagree: installed {installed}, requirements.txt {req_pin}, "
            f"ci.yml {ci_pin} -- {INSTALL}"
        )

    excluded = set(config.get("extend-exclude", []))
    bundled = bundled_dirs(tracked)
    bundled_py = {
        d for d in bundled if any(f.startswith(d + "/") and f.endswith(".py") for f in tracked)
    }
    for d in sorted(bundled_py - excluded):
        problems.append(f"bundled skill {d} has Python but is not in ruff.toml extend-exclude")
    for d in sorted(excluded - bundled_py):
        problems.append(f"ruff.toml extend-exclude {d!r} is not a bundled skill with Python")

    upstream = 0
    for f in tracked:
        if not f.endswith(".py"):
            continue
        hits = unsafe_prints((REPO / f).read_text(encoding="utf-8", errors="replace"))
        if not hits:
            continue
        if any(f.startswith(d + "/") for d in excluded):
            upstream += 1
            continue
        problems.append(
            f"{f}:{hits[0]}: prints non-ASCII without sys.stdout.reconfigure(encoding='utf-8')"
            f" ({len(hits)} call(s))"
        )

    if problems:
        for p in problems:
            print(f"ERROR {p}")
        print(f"[FAIL] {len(problems)} lint problem(s) ({version.stdout.strip()})")
        return 1
    n_cfg = len(config.get("extend-exclude", [])) + len(
        config.get("lint", {}).get("per-file-ignores", {})
    )
    print(
        f"[OK] ruff check + format clean, {n_cfg} ruff.toml paths live, excludes == "
        f"{len(bundled_py)} bundled Python skills, UTF-8 output safe "
        f"({upstream} bundled file(s) left to upstream) ({version.stdout.strip()})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
