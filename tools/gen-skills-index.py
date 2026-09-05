#!/usr/bin/env python3
"""Regenerate SKILLS-INDEX.md from live skill frontmatter (flat, grep-friendly).

The index is the cheapest lookup path in this second brain: one `grep -i <term>`
instead of parsing 145+ YAML frontmatters. Run after adding/removing/renaming skills.

Usage: python tools/gen-skills-index.py
Stdlib only (no PyYAML needed — description/name are extracted with regex, which is
sufficient for the flat index; audit-skills.py does the strict validation).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKIP_PARTS = (".git/", ".hermes/", "profiles-export/", "memories-export/", "memories/")


def collect():
    rows = []
    for p in REPO.rglob("SKILL.md"):
        ps = str(p).replace("\\", "/")
        if any(s in ps for s in SKIP_PARTS):
            continue
        text = p.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        fm = m.group(1) if m else ""
        nm_m = re.search(r"^name:\s*(\S+)", fm, re.M)
        dm_m = re.search(r'^description:\s*"?([^"\n]+?)"?\s*$', fm, re.M)
        name = nm_m.group(1) if nm_m else p.parent.name
        desc = (dm_m.group(1).strip() if dm_m else "").rstrip(".")
        cat = str(p.relative_to(REPO)).replace("\\", "/").split("/")[0]
        rows.append((cat, name, desc))
    return sorted(rows, key=lambda r: (r[0], r[1].lower()))


def main():
    rows = collect()
    cats = sorted(set(r[0] for r in rows))
    missing_desc = [f"{c}/{n}" for c, n, d in rows if not d]

    lines = [
        "# SKILLS-INDEX",
        "",
        f"Flat index of all **{len(rows)} skills** in this second brain — one line each, grep-friendly.",
        "Format: `- \\`skill-name\\` — description _(category)_`. Regenerate with `python tools/gen-skills-index.py`.",
    ]
    cur = None
    for cat, name, desc in rows:
        if cat != cur:
            lines.append(f"\n## {cat}\n")
            cur = cat
        lines.append(f"- `{name}` — {desc} _({cat})_")
    lines += [
        "",
        "---",
        f"*{len(rows)} skills across {len(cats)} categories. Keep in sync when adding/removing/renaming skills (see AGENTS.md).*",
    ]

    out = REPO / "SKILLS-INDEX.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote SKILLS-INDEX.md: {len(rows)} skills, {len(cats)} categories")
    if missing_desc:
        print("WARNING — skills with empty description:", ", ".join(missing_desc), file=sys.stderr)


if __name__ == "__main__":
    main()
