# Section Header Standardization

## Standard Section Headers

The modern section order per `hermes-agent-skill-authoring` is:

```
## When to Use
## Prerequisites
## How to Run
## Quick Reference
## Procedure
## Pitfalls
## Verification
```

## Capitalization Rules

All section headers use **title case with lowercase prepositions**:

| Standard Form | Non-standard Forms to Fix |
|---|---|
| `## When to Use` | `## When to use`, `## When To Use`, `## When to Use This Skill`, `## When to Use Each` |
| `## What This Skill Does` | `## What This Skill Does:` (trailing colon) |
| `## Quick Reference` | (none known) |
| `## Quick Start` | `## Quick start` |
| `## Prerequisites` | (none known) |

### Detection

```bash
# Find lowercase "use" in section headers
grep -rn '## When to use' --include='SKILL.md' .

# Find capitalized "To" in section headers
grep -rn '## When To Use' --include='SKILL.md' .

# Find "Quick start" with lowercase 's'
grep -rn '## Quick start' --include='SKILL.md' .
```

### Bulk Fix Script

```python
#!/usr/bin/env python3
"""Fix section header capitalization across all skills."""
import os, re

base = os.getcwd()
fixes = {
    '## When to use': '## When to Use',
    '## When To Use': '## When to Use',
    '## Quick start': '## Quick Start',
}

for root, dirs, files in os.walk(base):
    if '.git' in root.split(os.sep) or 'profile' in root.split(os.sep):
        continue
    if 'SKILL.md' in files:
        path = os.path.join(root, 'SKILL.md')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        original = content
        for old, new in fixes.items():
            content = content.replace(old, new)
        if content != original:
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            print(f'Fixed: {os.path.relpath(path, base)}')
```

## Non-standard But Acceptable Headers

Some skills use descriptive subsections under standard headers (e.g., `## When to Use: CLI vs Web`). These are **acceptable** — they extend the standard header with a colon subtitle. The key requirement is that the base form matches the standard capitalization.

## False Positives to Ignore

- `# Title` (H1) — these are human-readable titles, not section headers. Capitalization should be sentence case or title case per the skill's style, not enforced to a specific pattern.
- `### H3` headers — these are subsections within a section and follow their own capitalization logic.
- Code-block content that starts with `#` — these are shell comments, not Markdown headers.
