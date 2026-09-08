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


MIN_SKILLS = 100  # write-guard floor: fewer means the scan failed

def main():
    rows = collect()
    cats = sorted(set(r[0] for r in rows))
    missing_desc = [f"{c}/{n}" for c, n, d in rows if not d]

    lines = [
        "# SKILLS-INDEX",
        "",
        f"Flat index of all **{len(rows)} skills** in this second brain — one line each, grep-friendly.",
        "Format: `- \\`skill-name\\` — description _(category)_. Regenerate with `python tools/gen-skills-index.py`.",
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
        f"*{len(rows)} skills across {len(cats)} categories. Keep in sync when adding/removing/renaming skills (conventions: README 'Verification' section + tools/audit-skills.py).*",
    ]

    lines_out = [ln + chr(10) for ln in lines]
    check = wants_check()
    emit(REPO / "SKILLS-INDEX.md", "".join(lines_out),
         count=len(rows), floor=MIN_SKILLS, label="gen-skills-index", check=check)
    if not check:
        print(f"wrote SKILLS-INDEX.md: {len(rows)} skills, {len(cats)} categories")
    if missing_desc:
        print("WARNING — skills with empty description:", ", ".join(missing_desc), file=sys.stderr)

    write_category_descriptions(rows, cats)


def write_category_descriptions(rows, cats):
    """Regenerate each category's DESCRIPTION.md skill list from live frontmatter.

    The files claim '*Regenerated from live frontmatter*' but nothing actually wrote them —
    hand-edited copies drifted (broken links to nonexistent SKILL.md paths for nested or
    same-named skills). This makes the claim true: every run rewrites each category's list,
    preserving its existing YAML frontmatter and one-line blurb verbatim.

    Link targets are computed from where the skill ACTUALLY lives on disk:
      <cat>/<skill>/SKILL.md   -> ./<skill>/SKILL.md
      <cat>/<sub>/<skill>      -> ./<sub>/<skill>/SKILL.md   (e.g. mlops/evaluation/w-b)
    """
    check = wants_check()
    # map skill name -> its real dir relative to the category root
    by_cat = {}
    for p in REPO.rglob("SKILL.md"):
        ps = str(p).replace("\\", "/")
        if any(s in ps for s in SKIP_PARTS):
            continue
        parts = p.relative_to(REPO).parts          # (cat, [sub...], skilldir, SKILL.md) or (cat, SKILL.md)
        cat = parts[0]
        if len(parts) == 2:                        # top-level single-skill category: <cat>/SKILL.md
            by_cat.setdefault(cat, []).append((None, cat))
            continue
        name_dir = parts[-2]
        rel_skill_dir = "/".join(parts[1:-2])      # '' for flat, 'evaluation' etc. for nested
        by_cat.setdefault(cat, []).append((rel_skill_dir, name_dir))

    written = 0
    for cat in cats:
        catdir = REPO / cat
        if not catdir.is_dir():
            continue
        path = catdir / "DESCRIPTION.md"
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        fm_m = re.match(r"^---\n(.*?)\n---", existing, re.DOTALL)
        frontmatter = (fm_m.group(0).rstrip("\n") + "\n\n") if fm_m else f"---\ndescription: {cat}.\n---\n\n"

        # blurb: derived deterministically from the frontmatter description (the old
        # hand-typed body lines had drift — doubled periods, stale text). fm_desc + "."
        desc_m = re.search(r'^description:\s*"?([^"\n]+?)"?\s*$', fm_m.group(1), re.M) if fm_m else None
        blurb = (desc_m.group(1).strip().rstrip(".") + ".") if desc_m and desc_m.group(1).strip() else f"{cat}."

        items = sorted(by_cat.get(cat, []), key=lambda r: (r[0] or "", r[1].lower()))
        out = [frontmatter.rstrip("\n"), "", f"# {cat}", "", blurb, ""]
        for rel_skill_dir, name in items:
            if rel_skill_dir is None:              # top-level single-skill category
                target = "./SKILL.md"
            elif not rel_skill_dir:
                target = f"./{name}/SKILL.md"
            else:
                target = f"./{rel_skill_dir}/{name}/SKILL.md"
            # description from the live frontmatter rows (rows already carry it)
            desc = next((d for c2, n2, d in rows if c2 == cat and n2 == name), "")
            out.append(f"- [`{name}`]({target}) — {desc}")
        out += ["", "*Regenerated from live frontmatter — keep in sync with `tools/gen-skills-index.py`.*"]
        emit(path, chr(10).join(out) + chr(10), count=max(len(items), 1), floor=1,
             label=f"gen-skills-index ({cat}/DESCRIPTION.md)", check=check)
        written += 1
    if not check:
        print(f"wrote DESCRIPTION.md for {written} categories (skill lists now match disk)")


if __name__ == "__main__":
    main()
