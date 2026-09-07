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
(fallback: first markdown heading with leading # stripped). Regenerate after
adding/removing/renaming any references/*.md. Stdlib only.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "REFERENCES-INDEX.md"
SKIP_TOP = {"profile", "profiles-export", "docs", "tools"}


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
    for p in sorted(REPO.rglob("references/*.md")):
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
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"REFERENCES-INDEX.md: {len(docs)} docs across "
          f"{len({o for o, _, _ in docs})} owning skills -> {OUT.name}")


if __name__ == "__main__":
    main()
