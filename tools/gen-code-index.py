#!/usr/bin/env python3
"""Regenerate CODE-INDEX.md from live code files (flat, grep-friendly).

Companion to gen-skills-index.py: SKILLS-INDEX answers "which skill does X";
CODE-INDEX answers "where is the executable knowledge for X" — every script,
helper module, test, and template in the repo with its owning skill, language,
size, and a one-line purpose extracted from its docstring/header comment.

Usage: python tools/gen-code-index.py
Stdlib only (no PyYAML needed). Run after adding/removing/renaming code files.
"""
import os
import re
import sys
from pathlib import Path

# Import the sibling helper explicitly rather than relying on sys.path[0] being
# this script's directory -- that holds for `python tools/x.py` but not for runpy,
# exec, or an import from elsewhere.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _index_output import emit, wants_check

# ── Environment guard ───────────────────────────────────────────────────────
# A wrong interpreter must fail HERE, loudly — never half-run and report clean.
# On Windows, bare `python` / `python3` are usually Microsoft Store alias stubs
# that never execute the script at all; use `py` there (README → Verification).
if sys.version_info < (3, 8):
    raise SystemExit(
        "[FATAL] this tool needs Python 3.8+, got "
        f"{sys.version.split()[0]} at {sys.executable or '<unknown interpreter>'}"
    )
try:  # repo content is UTF-8; a cp1252 console must not abort an otherwise-clean run
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

REPO = Path(__file__).resolve().parents[1]
SKIP_PARTS = (".git", "profiles-export")
CODE_EXT = {".py": "python", ".sh": "bash", ".js": "javascript", ".mjs": "javascript"}


def first_summary(path: Path, lang: str) -> str:
    """First meaningful docstring line (python) or comment line (sh/js)."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return ""
    lines = text.splitlines()

    if lang == "python":
        # module docstring: first string literal after optional shebang/encoding/coding line
        for i, ln in enumerate(lines[:40]):
            s = ln.strip()
            if not s or s.startswith("#!") or s.startswith("# -*-"):
                continue
            m = re.match(r'^(?:from __future__ import .+|import \S+)$', s)
            if m:
                continue
            dm = re.match(r'^[rbfu]*"""(.*)$', s) or re.match(r"^[rbfu]*'''(.*)$", s)
            if dm and i < 5:
                return clean(dm.group(1))
            break
        # fallback: first comment line
    for ln in lines[:20]:
        s = ln.strip()
        if s.startswith("#") and not s.startswith("#!"):
            body = s.lstrip("#").strip()
            if body:
                return clean(body)
    return ""


def clean(s: str, limit: int = 110) -> str:
    s = re.sub(r"\s+", " ", s).strip().rstrip(".")
    # strip trailing quote residue from single-line docstrings
    s = s.rstrip('"""').rstrip("'''").strip()
    return (s[:limit] + "\u2026") if len(s) > limit else s


def owner_of(rel: str):
    """Nearest ancestor dir with a SKILL.md -> (skill_name, category_path); else ('repo tooling', top)."""
    parts = rel.split("/")[:-1]  # dirs containing the file
    for i in range(len(parts), -1, -1):
        cand = "/".join(parts[:i])
        if not cand:
            break
        skill_md = REPO / cand / "SKILL.md"
        if skill_md.exists():
            txt = skill_md.read_text(encoding="utf-8")
            m = re.match(r"^---\n(.*?)\n---", txt, re.DOTALL)
            nm = re.search(r"^name:\s*(\S+)", m.group(1), re.M) if m else None
            return (nm.group(1) if nm else cand, cand)
    top = parts[0] if parts else "(root)"
    return ("repo tooling", top)


def kind_of(rel: str) -> str:
    base = rel.split("/")[-1]
    dirs = set(rel.split("/"))
    if "tests" in dirs or base.startswith("test_") or base == "conftest.py":
        return "test"
    if base.startswith("_") or re.search(r"_common\.(py|js)$", base):
        return "shared helper"
    if "templates" in dirs:
        return "template"
    top = rel.split("/")[0]
    if top in ("tools", ".hermes"):
        return "repo tooling"
    return "script"


MIN_CODE_FILES = 50  # write-guard floor

def main():
    rows = []  # (owner_name, owner_path, kind, lang, lines, summary, rel)
    for dirpath, _, filenames in os.walk(REPO):
        parts = [p for p in Path(dirpath).parts]
        if any(s in parts for s in SKIP_PARTS):
            continue
        for f in sorted(filenames):
            ext = os.path.splitext(f)[1].lower()
            if ext not in CODE_EXT:
                continue
            full = Path(dirpath) / f
            rel = str(full.relative_to(REPO)).replace("\\", "/")
            lang = CODE_EXT[ext]
            n_lines = len(full.read_text(encoding="utf-8").splitlines())
            owner_name, owner_path = owner_of(rel)
            rows.append((owner_name, owner_path, kind_of(rel), lang, n_lines, first_summary(full, lang), rel))

    # group by owning skill path (repo tooling last); within a group: scripts before helpers/tests/templates
    groups = {}
    for r in rows:
        key = "(repo-level)" if r[0] == "repo tooling" else r[1]
        groups.setdefault(key, []).append(r)

    kind_rank = {"script": 0, "shared helper": 1, "template": 2, "test": 3, "repo tooling": 4}
    ordered_keys = sorted(k for k in groups if k != "(repo-level)") + (["(repo-level)"] if "(repo-level)" in groups else [])

    lines = [
        "# CODE-INDEX",
        "",
        f"Flat index of all **{len(rows)} code files** ({sum(r[4] for r in rows):,} lines total) in this second brain — one line each, grep-friendly.",
        "Format: `- `path` (kind, lang, N lines) — purpose _(owner)_`. Regenerate with `python tools/gen-code-index.py`.",
    ]
    for key in ordered_keys:
        title = key if key != "(repo-level)" else "Repo-level tooling (`tools/`, `.hermes/cron/`)"
        lines.append(f"\n## {title}\n")
        for owner_name, owner_path, kind, lang, n_lines, summary, rel in sorted(
            groups[key], key=lambda r: (kind_rank.get(r[2], 9), r[6])
        ):
            suffix = f" — {summary}" if summary else ""
            lines.append(f"- `{rel}` ({kind}, {lang}, {n_lines} lines){suffix}")

    n_scripts = sum(1 for r in rows if r[2] == "script")
    n_helpers = sum(1 for r in rows if r[2] == "shared helper")
    n_tests = sum(1 for r in rows if r[2] == "test")
    lines += [
        "",
        "---",
        f"*{len(rows)} code files: {n_scripts} scripts, {n_helpers} shared helpers, {n_tests} tests. Keep in sync when adding/removing/renaming code (conventions: README 'Verification' section + tools/audit-skills.py).*",
    ]

    check = wants_check()
    emit(REPO / "CODE-INDEX.md", chr(10).join(lines) + chr(10),
         count=len(rows), floor=MIN_CODE_FILES, label="gen-code-index", check=check)
    if not check:
        print(f"wrote CODE-INDEX.md: {len(rows)} code files, {sum(r[4] for r in rows):,} lines, {len(ordered_keys)} owner groups")


if __name__ == "__main__":
    main()
