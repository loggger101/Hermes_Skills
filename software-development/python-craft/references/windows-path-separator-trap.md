---
name: windows-path-separator-trap
description: "Windows os.path.relpath yields backslashes; cross-platform path-string comparison fails silently."
---

# Windows Path Separator Trap (python-craft reference)

## Problem

On Windows, `os.path.relpath()` and `str(Path(...))` produce backslash-separated strings:

```
C:\Users\Loggg\repo\research\arxiv       ← from os.path.relpath
```

But cross-platform config strings (JSON skill refs, regex patterns, substring filters) use forward slashes:

```
research/arxiv                           ← from cronjob JSON skill id
```

A direct `in` comparison returns False — no error, just silent mismatch.

## Reproduction

```python
import os
rel = os.path.relpath(r"C:\Users\Loggg\repo\research\arxiv", r"C:\Users\Loggg\repo")
# On Windows: rel = "research\arxiv" (backslash)
# "research/arxiv" in rel  →  False  (silent! no error raised)
```

## Fix

Normalize backslashes to forward slashes before any substring/regex comparison:

```python
def norm_path(p):
    return str(p).replace('\\', '/').replace('//', '/')
```

Or prefer pathlib throughout and convert at comparison boundaries:

```python
from pathlib import Path
rel = str(Path('C:/repo/research/arxiv').relative_to('C:/repo')).replace('\\', '/')
```

## Session context

Encountered while writing `validate-skill-refs.py` to audit cronjob skill references in the Hermes_Skills repo. Without normalization, all 16 skill refs across 3 cronjob JSON files were falsely flagged as BROKEN. With normalization applied, all 16 resolved correctly against 127 valid skill directories.

## See also

- `python-craft` SKILL.md — Common Code Smells table entry: "Path comparison without normalization"
- `sync-hermes-skills.py` — already implements this normalization pattern (line 43)
- `audit-skills.py` — same normalization used for exclusion filtering (line 43)