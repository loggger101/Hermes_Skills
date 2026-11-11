# Frontmatter Audit Pattern

A comprehensive pattern for auditing YAML frontmatter across an entire skill library. This is the battle-tested script used in the 2026-08-24 standardization pass that audited 127 SKILL.md files.

## Core Validation Script

The minimal inline validator (from `hermes-agent-skill-authoring` SKILL.md, Verification Checklist):

```python
import yaml, re, pathlib
content = pathlib.Path("skills/<category>/<name>/SKILL.md").read_text()
assert content.startswith("---")
m = re.search(r'\n---\s*\n', content[3:])
fm = yaml.safe_load(content[3:m.start()+3])
assert "name" in fm and "description" in fm
assert len(fm["description"]) <= 60
fm["description"].endswith(".")
assert "platforms" in fm
assert len(content) <= 100_000
```

## Full Library Audit Script

For auditing an entire repository (127+ files), use this expanded pattern:

```python
import os, yaml, re
from collections import defaultdict

base = os.getcwd()
skills = {}
all_refs = defaultdict(list)

for root, dirs, files in os.walk(base):
    rel = os.path.relpath(root, base)
    parts = rel.split(os.sep)
    if '.git' in parts or 'profile' in parts:
        continue
    if 'SKILL.md' in files:
        path = os.path.join(root, 'SKILL.md')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if content.startswith('---'):
            fm_end = content.index('\n---', 4)
            data = yaml.safe_load(content[4:fm_end])
            if data and isinstance(data, dict) and 'name' in data:
                name = data['name']
                related = data.get('metadata', {}).get('hermes', {}).get('related_skills', [])
                skills[name] = related
                for ref in related:
                    all_refs[ref].append(name)

# Find broken refs
for ref in sorted(all_refs.keys()):
    if ref not in skills:
        print(f"BROKEN: {ref} -> {all_refs[ref]}")

# Find name/path mismatches
for name, info in skills.items():
    expected = info['path'].split(os.sep)[-1]
    if name != expected:
        print(f"MISMATCH: name='{name}' but path is '{expected}'")
```

## Key Checks to Run

1. **YAML parse validity** — `yaml.safe_load()` must not throw
2. **Required fields** — `name`, `description`, `version`, `author`, `platforms`
3. **Description ≤ 60 chars** — hardline standard, ends with period
4. **Frontmatter closing** — ends with `\n---\n` (blank line before closing `---`)
5. **`related_skills` resolution** — every entry must resolve to an in-repo skill name
6. **No self-references** — skill must not list itself in `related_skills`
7. **Name/path match** — `name:` must match the directory name
8. **Tag overlap detection** — flag skills sharing 2+ tags that don't cross-reference

## Fixing Frontmatter Blank Line

The closing `---` should always be preceded by a blank line:

```diff
    tags: [foo, bar]
- ---
+
+---
```

Script to fix:

```python
for root, dirs, files in os.walk(base):
    if 'SKILL.md' in files:
        path = os.path.join(root, 'SKILL.md')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if content.startswith('---'):
            fm_end = content.index('\n---', 4)
            fm_content = content[4:fm_end]
            if fm_content and not fm_content.endswith('\n'):
                content = content[:fm_end] + '\n' + content[fm_end:]
                with open(path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(content)
```

## Addendum 2026-11-11 - four rules this pattern did not check (added from upstream lint)

The script above validates shape (parses, required fields, length, `name:` == directory). Reading
`addyosmani/agent-skills/scripts/lib/skill-lint.js` showed four checks a shape-auditor misses; all four now
run in `tools/analyze-skill-routing.py`, and the rules are written up in
[routing-quality-harness.md](routing-quality-harness.md) with this corpus's measurements:

1. **Top-level frontmatter allowlist** - only `name, description, license, compatibility, metadata,
   allowed-tools`. Measured here 2026-11-11: `version`, `author` and `platforms` sit top-level on **all 255**
   skills (spec-illegal), while every Hermes-specific field (`tags`, `related_skills`) is already correctly
   nested under `metadata.hermes`. Portability work is therefore one mechanical key move, not a rewrite.
2. **Positive trigger clause in the description**, with all negated clauses stripped first - measured:
   **254/255** descriptions here state only what a skill does, never when to use it. See the harness note for
   why this repo keeps that convention and adopts trigger wording on touch rather than by mass rewrite.
3. **Supporting `.md` filenames kebab-case**, plus non-empty support directories - measured: 7 exceptions in
   this tree (`README.md`, `DESCRIPTION.md`, `PORT_NOTES.md`), all intentional repo conventions, and one empty
   `references/` dir worth a look when that skill is next touched.
4. **Body line budget** (500) as an activation-cost warning - measured: 21 of 255 exceed it here; the remedy is
   this repo's usual split into `references/*.md`.

Note also, for anyone porting these rules to a JS validator: upstream documents that stripping negations needs
a *separate* `/g` copy of the pattern, because a global regex carries `lastIndex` across `.test()` calls - reuse
silently under-strips and lets two-negation descriptions pass. Irrelevant in Python's `re.sub`.
