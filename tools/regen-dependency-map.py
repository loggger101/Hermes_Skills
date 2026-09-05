#!/usr/bin/env python3
"""Regenerate DEPENDENCY.md from live related_skills frontmatter (same format as repo convention)."""
import datetime, re, sys
from pathlib import Path
try:
    import yaml
except ImportError:
    print("pyyaml missing", file=sys.stderr); sys.exit(2)

REPO = Path(__file__).resolve().parents[1]
# NOTE: unlike tools/audit-skills.py, this map INCLUDES profiles-export/ (the second-brain
# view spans all profile skill copies) but dedupes by name — top-level wins over exports.
SKIP_PARTS = (".git/", ".hermes/", "memories/")

skills = {}  # name -> {"path": rel, "related": [..]}
for p in REPO.rglob("SKILL.md"):
    ps = str(p).replace("\\", "/")
    if any(s in ps for s in SKIP_PARTS):
        continue
    text = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    fm = yaml.safe_load(m.group(1)) if m else {}
    name = fm.get("name", p.parent.name)
    meta = (fm.get("metadata") or {}).get("hermes") or {}
    related = [r for r in (meta.get("related_skills") or [])]
    entry = {"path": str(p.relative_to(REPO)).replace("\\", "/"), "related": related}
    if name not in skills:
        skills[name] = entry
    elif "profiles-export/" not in ps and "profiles-export/" in skills[name]["path"]:
        skills[name] = entry  # prefer top-level copy over profile export

names = set(skills)
inbound = {n: [] for n in names}
total_refs = 0
for name, info in sorted(skills.items()):
    total_refs += len(info["related"])
    for r in info["related"]:
        if r in inbound and r != name:
            inbound[r].append(name)

hubs = [(n, sorted(inbound[n])) for n in names if len(inbound[n]) >= 2]
hubs.sort(key=lambda x: (-len(x[1]), x[0]))
standalone = [n for n in sorted(names) if not skills[n]["related"] and not inbound[n]]

lines = []
lines.append("# Skill Dependency Map")
lines.append(f"This document maps the relationship network between all **{len(skills)} Hermes skills** in this repository. It is generated from the `related_skills` field in each skill's frontmatter.")
standalone_total_no_out = [n for n in names if not skills[n]["related"]]
lines.append(f"**Network stats:** {total_refs} `related_skills` cross-references across {len(skills)} skills ({len(standalone_total_no_out)} skills are standalone with no `related_skills` entries).")
lines.append("## Hub Skills (referenced by 2+ other skills)")
lines.append("These are the core skills that serve as building blocks, referenced by many other skills:")
lines.append("| Skill | Referenced By (count) | Referencing Skills |")
lines.append("|-------|-----------------------|---------------------|")
for n, refs in hubs:
    lines.append(f"| `{n}` | {len(refs)} | {', '.join(refs)} |")
lines.append("## Standalone Skills")
lines.append(f"The following {len(standalone)} skills have no `related_skills` entries of their own (they do not reference other skills). These are genuinely standalone — no other skill references them either:")
for n in standalone:
    lines.append(f"- `{n}`")
lines.append("## Related Skills Validation")
broken = [(s, r) for s, i in skills.items() for r in i["related"] if r not in names]
if broken:
    lines.append(f"WARNING — {len(broken)} unresolved references:")
    for s, r in sorted(set(broken)):
        lines.append(f"- `{s}` -> `{r}` (not found)")
else:
    lines.append(f"All {total_refs} `related_skills` references in the repository resolve to existing in-repo skills. Verified against {len(names)} unique skill names.")
lines.append("")
lines.append("---")
lines.append("")
today = datetime.date.today().isoformat()
lines.append(f"*Last generated: {today} from live frontmatter analysis of all {len(skills)} skills.*")

out = REPO / "DEPENDENCY.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote DEPENDENCY.md: {len(skills)} skills, {total_refs} xrefs, {len(hubs)} hubs, {len(standalone)} standalone, broken={len(broken)}")
