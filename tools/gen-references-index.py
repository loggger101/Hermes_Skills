#!/usr/bin/env python3
"""Rebuild REFERENCES-INDEX.md from every skill's references/ directory.

The reference docs (verified API maps, gotchas tables, working snippets) live
inside each owning skill's references/ dir since the 2026-09-07 reorg — but a
flat index of them did not exist, so finding one required grepping every
skill or knowing its owner. This tool closes that gap:

    python tools/gen-references-index.py

Output format (one line per doc, grep-friendly):

    - `category/skill/references/file.md` — purpose _(owner skill)_

Purpose comes from the file's frontmatter `description:` field when present
(fallback: first markdown heading with leading # stripped). Nested subdirectories
under references/ are indexed too (e.g. references/layouts/bento-grid.md) — a flat
references/*.md glob silently hid 42 docs. Regenerate after adding/removing/renaming
any references/**/*.md. Stdlib only.
"""
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

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "REFERENCES-INDEX.md"
SKIP_TOP = {"profile", "profiles-export", "docs", "tools"}
MIN_REFS = 150  # write-guard floor


def purpose_of(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if m:
        fm = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', m.group(1), re.MULTILINE)
        if fm:
            return fm.group(1).strip()
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
        if s and not s.startswith("---"):
            break
    return "(no description)"


def main() -> None:
    docs = []  # (owner_skill, relpath, purpose)
    for p in sorted(REPO.rglob("references/**/*.md")):
        parts = p.relative_to(REPO).parts
        if len(parts) < 3 or parts[0] in SKIP_TOP:
            continue
        owner = "/".join(parts[:2])
        docs.append((owner, p.relative_to(REPO).as_posix(), purpose_of(p)))

    lines = [
        "# REFERENCES-INDEX",
        "",
        f"Flat index of all **{len(docs)} reference documents** in this second brain — one line each, grep-friendly.",
        "Format: `- `path` — purpose _(owner skill)_`. Regenerate with `python tools/gen-references-index.py`.",
        "",
    ]
    current = None
    for owner, rel, purp in docs:
        if owner != current:
            lines += [f"## {owner}", ""]
            current = owner
        # strip the frontmatter description's leading verb noise? no — keep verbatim.
        lines.append(f"- `{rel}` — {purp}")
    check = wants_check()
    emit(OUT, chr(10).join(lines) + chr(10),
         count=len(docs), floor=MIN_REFS, label="gen-references-index", check=check)
    if not check:
        print(f"REFERENCES-INDEX.md: {len(docs)} docs across "
              f"{len({o for o, _, _ in docs})} owning skills -> {OUT.name}")


if __name__ == "__main__":
    main()
