#!/usr/bin/env python3
"""Check that every skill pointer written in prose names a skill that exists.

audit-skills.py validates the `related_skills` frontmatter list, but nothing validated the
pointers written in running text, so three of them rotted unnoticed (round-64):
`use wiretext` (no such skill), `skill_view(name='web_extract')` (a tool, not a skill) and a
README Quick Start command with the wrong category directory.

Pointer forms checked, in every .md/.json/.py/.txt/.yml/.yaml/.sh/.ps1 file of the catalog:

  skill_view(name='x')  /  skill_view("x")      x must be a skill name (or a skill path)
  hermes skill load a/b                          a/b must be a real skill directory
  skill_manage("install", "x")                   x must be a skill name

A skill name is its frontmatter `name:` or its directory name. Placeholders are skipped:
anything with <, >, {, }, '...' or a ':' namespace (plugin:skill), and the literals in
PLACEHOLDERS. Not scanned: .git, profiles-export, memories, docs/archive, and this tool plus
its mutation test (their examples are deliberately wrong).

Usage:
    py tools/check-skill-pointers.py
Environment:
    SKILL_POINTER_SCAN_ROOT   scan this tree instead of the repo (the mutation test uses it)

Exit 0 = every pointer resolves. Exit 1 = at least one dangling pointer (listed with file:line).
"""

import os
import re
import sys
from pathlib import Path

if sys.version_info < (3, 8):
    raise SystemExit(
        "[FATAL] check-skill-pointers.py needs Python 3.8+, got "
        f"{sys.version.split()[0]} at {sys.executable or '<unknown interpreter>'}"
    )
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

REPO = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("SKILL_POINTER_SCAN_ROOT") or REPO)

SKIP_DIRS = {
    ".git",
    "profiles-export",
    "memories",
    "memories-export",
    "__pycache__",
    "node_modules",
}
SKIP_PREFIXES = ("docs/archive/",)
SKIP_FILES = {"tools/check-skill-pointers.py", "tools/mutation-test-pointer-gate.py"}
SUFFIXES = (".md", ".json", ".py", ".txt", ".yml", ".yaml", ".sh", ".ps1")
PLACEHOLDERS = {
    "xxx",
    "x",
    "name",
    "skill-name",
    "skill_name",
    "my-skill",
    "your-skill",
    "example-skill",
}

# an optional backslash before each quote lets the same patterns read pointers inside JSON strings
Q = r"""\\?["']"""
SKILL_VIEW = re.compile(rf"skill_view\(\s*(?:name\s*=\s*)?{Q}([^\"'\\]+){Q}")
SKILL_LOAD = re.compile(r"hermes skill load\s+([\w<{][\w./<>{}:-]*)")
SKILL_INSTALL = re.compile(rf"skill_manage\(\s*{Q}install{Q}\s*,\s*{Q}([^\"'\\]+){Q}")


def is_placeholder(target):
    return target.lower() in PLACEHOLDERS or any(c in target for c in "<>{}:") or "..." in target


def walk():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(SUFFIXES):
                continue
            path = Path(dirpath) / fn
            rel = path.relative_to(ROOT).as_posix()
            if rel in SKIP_FILES or rel.startswith(SKIP_PREFIXES):
                continue
            yield path, rel


def skill_index():
    dirs, names = set(), set()
    for path, rel in walk():
        if path.name != "SKILL.md":
            continue
        dirs.add(Path(rel).parent.as_posix())
        text = path.read_bytes().decode("utf-8", "replace")
        m = re.search(r"^name:\s*[\"']?([\w.-]+)", text, re.M)
        names.add(m.group(1) if m else path.parent.name)
        names.add(path.parent.name)
    return dirs, names


def main():
    dirs, names = skill_index()
    if len(names) < 3:
        print(f"[FATAL] found only {len(names)} skills under {ROOT} — wrong scan root?")
        return 1
    problems, checked, files = [], 0, set()
    for path, rel in walk():
        text = path.read_bytes().decode("utf-8", "replace")
        for kind, pattern in (
            ("skill_view", SKILL_VIEW),
            ("skill load", SKILL_LOAD),
            ("install", SKILL_INSTALL),
        ):
            for m in pattern.finditer(text):
                raw = m.group(1)
                target = raw.rstrip(".,;)")
                if is_placeholder(raw) or not target:
                    continue
                checked += 1
                files.add(rel)
                leaf = target.split("/")[-1]
                if kind == "skill load":
                    ok = target in dirs if "/" in target else target in names
                else:
                    ok = target in names or target in dirs or (("/" in target) and leaf in names)
                if not ok:
                    line = text.count("\n", 0, m.start()) + 1
                    why = "no such skill"
                    if kind == "skill load" and "/" in target and leaf in names:
                        why = "skill exists but not at that path"
                    problems.append(f"{rel}:{line}  {kind} -> {target}  ({why})")
    if problems:
        print(f"[BROKEN] {len(problems)} dangling skill pointer(s):")
        for p in problems:
            print("  " + p)
        return 1
    print(f"[OK] {checked} skill pointers in {len(files)} files all resolve ({len(names)} skills)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
