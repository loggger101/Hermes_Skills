# Script Path Resolution Pitfalls

## Problem: `parents[N]` indexing error

When a cron job invokes a Python script via `terminal`, the script must compute its
own `REPO_ROOT` from `__file__`. The `parents[N]` index depends on how many directories
deep the script lives in the repo.

### Example

For a script at `repo/tools/audit-skills.py`:

```python
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[1]  # ✅ correct: repo root
```

- `parents[0]` = `repo/tools/`
- `parents[1]` = `repo/` ← **correct**
- `parents[2]` = parent of `repo/` ← **WRONG** — scans unrelated directories

If you accidentally use `parents[2]`, the audit script scans the parent directory
(containing multiple sibling repos) instead of the repo itself, producing false
negatives when sibling repos are clean and false positives when they use different
formats.

### How to verify

```bash
# Before committing a script, verify REPO_ROOT:
python -c "from pathlib import Path; print(Path('tools/audit-skills.py').resolve().parents[1])"
# Should print: /path/to/Hermes_Skills
# NOT: /path/to/Documents/GitHub or any parent directory
```

### Sync script (correct)

`tools/sync-hermes-skills.py` correctly uses `parents[1]`:

```python
REPO_ROOT = Path(__file__).resolve().parents[1]  # ✅ repo root
```

## Problem: rglob() picks up sync output directories

Scripts that recursively search the repo root (e.g. `root.rglob("SKILL.md")`) will
find files in generated output directories:

- `profiles-export/` — copies of skills from local Hermes profiles (created by sync-hermes-skills.py)
- `memories-export/` — exported memory files (created by sync-hermes-skills.py)

These directories contain duplicates of source skill files with potentially older content.
The audit will report them as duplicate skills, broken refs, missing body sections, etc.

### Fix

In any `rglob()` loop, add exclusion checks:

```python
for path in root.rglob("SKILL.md"):
    path_str = str(path).replace("\\", "/")  # Normalize for Windows backslash paths
    if ".git/" in path_str or ".hermes/" in path_str:
        continue
    if "profiles-export/" in path_str or "memories-export/" in path_str:
        continue
    # ... process path
```

Also exclude these directories in `find_category_dirs` which uses `root.iterdir()`:

```python
# Skip dirs that are not skill categories:
# - .git, .hermes — internal/git directories
# - profiles-export, memories-export — sync script outputs
# - profile — profile state directory (config.yaml, PROFILE.md, etc.)
# - tools — utility scripts (audit-skills.py, sync-hermes-skills.py)
SKIP_DIRS = {".git", ".hermes", "profiles-export", "memories-export", "profile", "tools"}
for entry in sorted(root.iterdir()):
    if entry.is_dir() and entry.name not in SKIP_DIRS:
        ...
```

### Verify exclusions work

```bash
# The audit script should report the same skill count with or without
# profiles-export/ and memories-export/ present:
python tools/audit-skills.py
# Check that repo_root in the output points to Hermes_Skills, not a parent dir
```

## Problem: Model references must be updated across all config files

When a cron job's model changes (e.g. `claude-sonnet-4-20250514` → `qwen/qwen3.6-35b`),
the model string appears in multiple places that all need updating:

1. **Cron JSON config** — `"model"` and `"provider"` fields in `.hermes/cron/active/*.json`
2. **Guardrails array** — text strings that mention the model pin for documentation
3. **README tables** — verification items that list the expected model
4. **NOTES.md** — any audit notes referencing model versions
5. **SKILL.md guardrails** — pitfall text mentioning the model

Always grep for the old model string after updating:
```bash
grep -rn "claude-sonnet-4-20250514" .hermes/cron/ README.md NOTES.md autonomous-ai-agents/cron-job-authoring/SKILL.md
```
This catches stale references that would otherwise cause drift between the documented
and actual model config.
