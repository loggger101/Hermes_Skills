"""The repo's file list, shared by the gates that scan code (check-lint, check-script-syntax,
check-script-coverage).

Tracked files plus untracked files git does not ignore: what the next commit can contain.
Tracked-only made a new test invisible until it was staged, so the coverage gate called its
script untested; a plain directory walk would count a local venv or node_modules. A tracked
file deleted from the working tree is left out (it is not on disk to scan).
"""

import subprocess
from pathlib import Path


def repo_files(root):
    proc = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc.returncode != 0:
        raise SystemExit(f"[FATAL] git ls-files failed in {root}: {proc.stderr.strip()[:300]}")
    files = sorted({f for f in proc.stdout.split("\0") if f})
    return [f for f in files if (Path(root) / f).is_file()]
