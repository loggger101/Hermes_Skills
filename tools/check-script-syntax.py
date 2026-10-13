#!/usr/bin/env python3
"""Gate: every script the repo ships must at least parse.

Round-257. 126 scripts live inside skills; only the ones a test happens to import or run
were ever parsed by anything. ruff covers the repo's own Python but excludes the bundled
skills, and nothing at all parsed the shell, PowerShell or JavaScript files, so a syntax
error in a script no test touches shipped green.

Parsers, one per language (each file is parsed, never executed):
  .py               compile() under the running interpreter
  .js .cjs .mjs     node --check
  .sh               bash -n          (Git Bash on Windows, never the WSL launcher)
  .ps1              PowerShell's own parser (pwsh, else Windows PowerShell)

A missing parser is a FAIL, never a skip: an unparsed file is an unchecked file. The file
list is tools/_repo_files.py (tracked + untracked-not-ignored, so a local venv never counts),
and a scan below FLOOR fails, so an emptied or mis-rooted scan cannot pass.

Usage:
    python tools/check-script-syntax.py
    SCRIPT_SCAN_ROOT=/tmp/fixture python tools/check-script-syntax.py --floor 1   # self-test

Exit 0 = every script parses. Exit 1 = a script does not parse. Exit 2 = the check could
not run (not a git checkout, a parser missing, scan below the floor).
"""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

from _repo_files import repo_files

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

TOOLS = Path(__file__).resolve().parent
REPO = Path(os.environ.get("SCRIPT_SCAN_ROOT") or TOOLS.parent)
FLOOR = 100  # 183 code files on 2026-10-13; a scan finding fewer is mis-rooted
LANG = {
    ".py": "python",
    ".js": "node",
    ".cjs": "node",
    ".mjs": "node",
    ".sh": "bash",
    ".ps1": "powershell",
}

# PowerShell parses every path passed in PS_PARSE_PATHS (JSON list) and prints one
# 'path<TAB>line<TAB>message' row per error. Reading paths from an env var avoids quoting
# rules that differ between pwsh and Windows PowerShell 5.1.
PS_PARSER = r"""
$ErrorActionPreference = 'Stop'
$bad = 0
foreach ($p in (ConvertFrom-Json $env:PS_PARSE_PATHS)) {
    $tokens = $null; $errors = $null
    [void][System.Management.Automation.Language.Parser]::ParseFile($p, [ref]$tokens, [ref]$errors)
    foreach ($e in $errors) {
        $bad++
        [Console]::Out.WriteLine("$p`t$($e.Extent.StartLineNumber)`t$($e.Message)")
    }
}
if ($bad) { exit 1 }
exit 0
"""


def _runner_helpers():
    """run-skill-tests.py already knows how to find a real bash and a PowerShell."""
    path = TOOLS / "run-skill-tests.py"
    spec = importlib.util.spec_from_file_location("run_skill_tests", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod._bash, mod._powershell


def tracked_scripts(root):
    return [f for f in repo_files(root) if Path(f).suffix in LANG]


def check_python(root, rel):
    try:
        source = (root / rel).read_bytes()
        compile(source, rel, "exec", dont_inherit=True)
    except SyntaxError as e:
        return [f"{rel}:{e.lineno}: {e.msg}"]
    except (OSError, ValueError) as e:
        return [f"{rel}: unreadable ({type(e).__name__}: {e})"]
    return []


def check_each(cmd_for, root, files, tool):
    problems = []
    for rel in files:
        proc = subprocess.run(
            cmd_for(rel),
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode != 0:
            first = (proc.stderr or proc.stdout).strip().splitlines()
            problems.append(
                f"{rel}: {tool} exited {proc.returncode}: {first[0] if first else ''}"[:300]
            )
    return problems


def check_powershell(ps, root, files):
    env = dict(os.environ, PS_PARSE_PATHS=json.dumps([str(root / f) for f in files]))
    proc = subprocess.run(
        [ps, "-NoProfile", "-NonInteractive", "-Command", PS_PARSER],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    rows = [ln.split("\t") for ln in proc.stdout.splitlines() if ln.count("\t") == 2]
    problems = [f"{Path(p).relative_to(root).as_posix()}:{line}: {msg}" for p, line, msg in rows]
    if proc.returncode == 1 and problems:
        return problems
    if proc.returncode != 0:
        # The parser itself broke (bad host, blocked policy): nothing was checked.
        raise SystemExit(
            f"[FATAL] PowerShell parser run exited {proc.returncode}: "
            + (proc.stderr or proc.stdout).strip()[:300]
        )
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--floor", type=int, default=FLOOR)
    args = ap.parse_args()

    files = tracked_scripts(REPO)
    if len(files) < args.floor:
        print(f"[FATAL] scanned {len(files)} scripts, below the floor of {args.floor}: mis-rooted?")
        return 2
    by_lang = {}
    for f in files:
        by_lang.setdefault(LANG[Path(f).suffix], []).append(f)

    find_bash, find_ps = _runner_helpers()
    tools = {
        "node": __import__("shutil").which("node"),
        "bash": find_bash(),
        "powershell": find_ps(),
    }
    missing = [lang for lang in by_lang if lang != "python" and not tools[lang]]
    if missing:
        print(
            f"[FATAL] no parser for: {', '.join(missing)} -- install it; these files are unchecked"
        )
        return 2

    problems = []
    for rel in by_lang.get("python", []):
        problems += check_python(REPO, rel)
    if "node" in by_lang:
        problems += check_each(
            lambda f: [tools["node"], "--check", f], REPO, by_lang["node"], "node --check"
        )
    if "bash" in by_lang:
        problems += check_each(lambda f: [tools["bash"], "-n", f], REPO, by_lang["bash"], "bash -n")
    if "powershell" in by_lang:
        problems += check_powershell(tools["powershell"], REPO, by_lang["powershell"])

    counts = ", ".join(f"{len(v)} {k}" for k, v in sorted(by_lang.items()))
    if problems:
        for p in problems:
            print(f"BROKEN {p}")
        print(f"[FAIL] {len(problems)} parse error(s) in {len(files)} scripts ({counts})")
        return 1
    print(f"[OK] all {len(files)} scripts parse ({counts})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
