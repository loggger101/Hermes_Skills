# Building Repo-Health Audit Scripts for Hermes Skill Repositories

> **Use this pattern when:** You need to validate a large Hermes_Skills repo for consistency, broken cross-references, or style violations. Instead of manual `grep` loops, create a Python audit script and wire it to a cronjob.

## The Pattern

A self-contained Python script that:

1. **Discovers all SKILL.md files** recursively (skipping `.git/`, `.hermes/`)
2. **Parses YAML frontmatter** using regex + `yaml.safe_load`
3. **Runs a battery of checks**, each producing a list of issues
4. **Outputs JSON** suitable for cron delivery
5. **Exits 0/1** based on whether threshold breaches occurred

## Key Technique: Regex-Based Frontmatter Extraction

```python
import re, yaml

text = path.read_text(encoding="utf-8")
m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
if m:
    fm = yaml.safe_load(m.group(1))
```

The regex `^---\n(.*?)\n---` with `re.DOTALL` captures the YAML block reliably. This avoids needing a YAML library that understands Markdown — it's just extracting the delimited block, then YAML parsing the inner content.

## Key Technique: Alternative Header Recognition

Don't just check for `## What This Skill Does` — many skills use valid alternatives:

```python
has_wtd = (
    "## What This Skill Does" in body
    or "**What This Skill Does:**" in body
    or "## What's in this skill" in body
    or re.search(r"^##\s+(Overview|Creative Standard)\s*$", body, re.MULTILINE)
)
```

This eliminates false positives (70 → 0 in the Hermes_Skills repo) while still catching genuinely missing sections.

## Key Technique: Threshold-Based Exit Codes

```python
THRESHOLDS = {
    "broken_refs": 0,
    "yaml_errors": 0,
    "long_descriptions": 0,
    "temps_scripts": 0,
}
```

Only hard-block on actual failures (broken references, invalid YAML, missing scripts). Body-section checks are **informational** — they don't break the build if they're below a threshold. This prevents audit noise from blocking legitimate changes.

## Key Technique: Cross-Reference Validation

Check that every `skill_view("xxx")` call in body text has a corresponding entry in `related_skills`:

```python
sv_calls = re.findall(r'skill_view\(["\']([^"\']+)["\']\)', body)
for ref in sv_calls:
    short_name = ref.split("/")[-1] if "/" in ref else ref
    if short_name not in related:
        errors.append(f"skill_view('{ref}') called but '{short_name}' not in related_skills")
```

Also skip self-referential calls that load reference files (those use `file_path=` parameter):

```python
sv_calls_with_path = re.findall(
    r'skill_view\([^)]*file_path\s*=\s*["\']', body
)
```

## Key Technique: Cronjob Integration

Wire the script to a cronjob with `no_agent=true` so it runs as a pure script without LLM involvement:

```json
{
  "script": "tools/audit-skills.py",
  "no_agent": true,
  "schedule": "0 9 * * 1",
  "workdir": "."
}
```

The `no_agent=true` flag means the script's stdout is delivered verbatim — no LLM overhead, just the JSON report as a weekly health check.

## Pitfalls

1. **Checking `## What This Skill Does` literally** without recognizing alternative headers produces false positives. Accept equivalent alternatives.
2. **Treating informational issues as hard failures** blocks legitimate changes. Use thresholds — only crash on actual errors (broken refs, invalid YAML).
3. **Not skipping `.git/` and `.hermes/` in file discovery** causes false positives from internal files.
4. **Regex too loose** for frontmatter extraction can capture content beyond the frontmatter block. Use `^---\n` as the anchor and `(.*?)` non-greedy with `\n---` terminator.
5. **File path resolution for scripts** — scripts referenced in frontmatter `script:` field must be resolved relative to the skill directory, not repo root.
