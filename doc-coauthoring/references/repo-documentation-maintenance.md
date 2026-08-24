# Maintaining Repo Documentation (README, DEPENDENCY, NOTES)

## When to Update

Update repo-level documentation (`README.md`, `DEPENDENCY.md`, `NOTES.md`) whenever the skill set changes:
- After adding/removing/reorganizing skills
- After changing `related_skills` metadata in any SKILL.md
- After renaming skills or merging duplicates
- After structural changes to the repo

## README.md

The README contains a category count table. Keep it accurate by regenerating counts from disk:

```bash
find C:/path/to/Hermes_Skills -name "SKILL.md" -not -path '*/.git/*' | \
  xargs -I{} dirname {} | xargs -I{} dirname {} | \
  xargs basename | sort | uniq -c | sort -rn
```

Or use the Python audit script in `_audit_repo.py`.

**Key things to verify:**
1. Category counts match actual SKILL.md files per top-level directory
2. Total count matches `find ... | wc -l`
3. The "Pre-existing vs Imported" split is correct (audit each skill's origin)
4. Verification claims are honest (use ✅/⚠️/❌ with specific notes)

## DEPENDENCY.md

This maps `related_skills` cross-references. It degrades quickly — any skill that changes its `related_skills` or any skill that gets renamed/deleted breaks the graph.

**Regenerate by:**
1. Parse every SKILL.md's frontmatter for `metadata.hermes.related_skills`
2. Build a reverse map: target → list of referrers
3. Identify hub skills (referenced by ≥2 others)
4. Flag broken refs (targets not in the skill name set)
5. Rebuild the hub table, broken refs table, skill chains, and category relationships

**Don't trust the git history** — commits may have changed metadata without updating DEPENDENCY.md.

## NOTES.md

This file tracks known data-quality issues that need human review:
- Duplicate skill names
- Broken `related_skills` references
- Incomplete frontmatter (missing version/author/platforms)
- Missing "What This Skill Does" sections
- Stale documentation claims

Update NOTES.md whenever you discover an issue during work, and add a verification status row for any check that doesn't pass.
