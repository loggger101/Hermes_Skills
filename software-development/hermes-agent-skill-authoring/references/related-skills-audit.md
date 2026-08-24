# Auditing and Fixing `related_skills` References

## Why This Matters

Broken `related_skills` references cause two failure modes:
1. **Routing failures** — when a skill tells the agent to "load `skill_view(name='X')`" but X doesn't exist, the agent wastes a turn and may produce wrong guidance.
2. **Decayed relationship graphs** — DEPENDENCY.md and internal cross-references become unreliable, degrading trust in the skill catalog.

## Common Breakage Patterns

### 1. Core-tool names used as skill references
Skills sometimes list Hermes core tools as `related_skills`:
- `clarify` → should be removed (it's a tool, not a skill)
- `delegate-task` → should be removed (it's `delegate_task`, a core tool)
- `skill-view` → should be replaced with `hermes-agent-skill-authoring`
- `web-extract` → should be removed (it's `web_extract`, a core tool)
- `duckduckgo-search` → should be removed (it's a tool, not a skill)
- `mcporter` → check if this maps to an actual skill name

**Fix:** Remove core-tool names from `related_skills`. If the skill genuinely depends on that tool's capability, mention it in the body (Prerequisites, How to Run) instead.

### 2. Shortened skill names
Skills sometimes use a shortened form instead of the full skill name:
- `subagent-driven-development` → should be `mattpocock-subagent-driven-development`

**Fix:** Replace with the full, exact skill name. When in doubt, search for the skill: `search_files(pattern='<name>', target='files', path='.')`.

### 3. Non-existent skills
Skills sometimes reference skills that never existed or were renamed:
- `concept-diagrams` → no skill with this name exists
- `stable-diffusion` → no skill with this name exists (the actual skill is `comfyui`)

**Fix:** Either create the missing skill, or redirect to the closest existing equivalent.

### 4. Stale references after skill re-organization
When a skill moves categories or gets renamed, old references aren't always updated. This is especially common with `mattpocock-*` skills that migrated from `autonomous-ai-agents/` to `software-development/`.

## How to Audit Systematically

Use this Python script to scan all SKILL.md files:

```python
import os, yaml
from collections import defaultdict

base = "."
skills = set()
all_refs = defaultdict(list)

for root, dirs, files in os.walk(base):
    if '.git' in root.split(os.sep):
        continue
    if 'SKILL.md' in files:
        path = os.path.join(root, 'SKILL.md')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if content.startswith('---'):
            fm_end = content.index('\n---', 4)
            data = yaml.safe_load(content[4:fm_end])
            if data and 'name' in data:
                skills.add(data['name'])
                meta = data.get('metadata', {}).get('hermes', {})
                related = meta.get('related_skills', []) if isinstance(meta, dict) else []
                if not related and 'related_skills' in data:
                    related = data.get('related_skills', [])
                for r in related:
                    all_refs[r].append(data['name'])

# Find broken refs
for ref in sorted(all_refs.keys()):
    if ref not in skills:
        print(f"BROKEN: {ref} -> {all_refs[ref]}")
```

### 5. Missing related_skills (not broken, just absent)

Many skills simply have no `related_skills` field at all, or have an empty list, even though they clearly reference other skills via `skill_view(name='...')` calls in their body text, or share tags with peer skills. This is not a correctness bug but a discoverability gap.

**Detection methods:**

1. **skill_view() call analysis** — parse the body text for `skill_view(name='X')` calls and check if X is in `related_skills`. If not, it should be added:
   ```python
   import re
   sv_matches = re.findall(r"skill_view\s*\(\s*(?:name\s*=\s*)?['\"]([^'\"]+)['\"]", body)
   ```

2. **Tag overlap analysis** — skills sharing 2+ tags in `metadata.hermes.tags` should be cross-referenced:
   ```python
   my_tags = set(skill_a['tags'])
   other_tags = set(skill_b['tags'])
   if len(my_tags & other_tags) >= 2:
       # skill_a should reference skill_b in related_skills
   ```

3. **Category proximity** — skills in the same category directory that are thematically related (e.g., all `apple/*` system-integration skills) should cross-reference each other.

**Fix:** Add missing skills to `related_skills` as a YAML list inline:
```yaml
    related_skills: [skill-a, skill-b, skill-c]
```
Or as a block list for long lists:
```yaml
    related_skills:
      - skill-a
      - skill-b
```

**Self-reference trap:** When auto-adding, never add a skill's own name to its `related_skills`. Filter with: `if ref != current_skill_name`.

### 6. Malformed YAML in related_skills

When generating `related_skills` programmatically, a common error is producing `[item1], [item2], [item3]]` instead of `[item1, item2, item3]`. This causes YAML parse errors.

**Detection:** The audit script will catch this as a YAML parse error. Visually, look for nested brackets or stray commas in the `related_skills` line.

**Fix:** Remove extra brackets:
```diff
-    related_skills: [apple-notes], [findmy], [imessage]]
+    related_skills: [apple-notes, findmy, imessage]
```

## Duplicate Skill Names

A duplicate name means two SKILL.md files share the same `name:` field but live in different directories. Fix by:
1. Comparing the two files to determine which is more complete.
2. Keeping the more complete version (usually the one in the category that better matches the skill's domain).
3. Deleting the older/duplicated directory.
4. Updating any directory-level references (e.g., in `mattpocock-subagent-driven-development`'s case, the `software-development/` copy is more complete and should be kept).
