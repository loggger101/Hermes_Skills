---
name: cron-config-authoring
description: "Author cronjob JSON configs with structured skills."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cron, configuration, skills, thresholds, no-agent, model-pinning]
    related_skills: [cron-job-authoring, hermes-agent-skill-authoring]
---

# Cron Configuration Authoring

## What This Skill Does

Teaches how to structure `.hermes/cron/active/*.json` cronjob config files for reliability: the structured `skills` object pattern (with per-skill phase + rationale), threshold key alignment with script output, skill reference path resolution, model pinning for drift-skip prevention, and approval-mode configuration for terminal-using jobs.

## When to Use

- You are creating or editing a cronjob JSON config in `.hermes/cron/active/`
- You need to add skills to a no_agent script job (e.g. audit-skills.py, sync-hermes-skills.py)
- You are wiring up threshold checks against a script's JSON output
- You need to verify that skill references resolve to valid in-repo skill directories

## The Structured Skills Object

Replace flat `skills: ["path/to/skill", ...]` arrays with a structured object that documents why each skill is loaded:

```json
"skills": {
  "loaded": [
    {
      "id": "autonomous-ai-agents/cron-job-authoring",
      "name": "cron-job-authoring",
      "phase": "pre-audit (no_interaction guardrail construction)",
      "rationale": "Governs the autonomy framing..."
    }
  ],
  "note": "no_agent=true — skills loaded for documentation/standards reference, NOT for tool access."
}
```

### For no_agent script jobs

The script is pure Python — skills are NOT invoked as tools. Loading them documents which skill's authoring standards and guardrails govern each aspect of the script. The `note` field is critical: without it, a future reader may assume skills grant tool access.

### For LLM-driven jobs

Skills ARE invoked as tools. The phase + rationale mapping tells the agent which skills to prioritize and when, and surfaces dependency constraints (e.g. "Linux-only deps — skip on Windows").

## Threshold Key Alignment

**Every key in the `threshold` block must match an actual field in the script's JSON output** — not a conceptual check name.

### Good
```json
// script outputs: {"summary": {"broken_refs": 0, "yaml_errors": 0, ...}}
"threshold": {
  "broken_refs": 0,
  "yaml_errors": 0,
  "temps_scripts": 0
}
```

### Bad
```json
"threshold": {
  "no_broken_refs": true,           // never appears in script output
  "dependency_map_regenerated": true // conceptual, not a script field
}
```

**Symptom of mismatch:** `threshold_breached: false` even when the check failed — the key never matches any output field, so it's never evaluated.

**Verification:** Read the script's `main()` and output dict, then grep each threshold key to confirm the script produces it.

## Skill Reference Resolution

Skill refs in cronjob JSON use **repo-relative slash paths** (e.g. `research/arxiv`), NOT the `name` field from SKILL.md frontmatter.

### Windows path normalization

`os.path.relpath()` on Windows produces backslash-separated strings. Comparing these against forward-slash JSON refs silently fails. Always normalize:

```python
def norm_path(p):
    return str(p).replace('\\', '/').replace('//', '/')
```

Use `.hermes/cron/validate-skill-refs.py` to validate all refs before scheduling.

## Model Pinning (drift-skip prevention)

For `no_agent=False` jobs, always set `model` and `provider` explicitly. The scheduler auto-skips unpinned jobs when global inference config drifts.

For `no_agent=True` jobs, pinning is optional but recommended for documentation clarity.

## Approval Mode

For jobs that use `terminal` to invoke scripts, set `approvals.cron_mode: approve` in config.yaml:

```bash
hermes config set approvals.cron_mode approve
```

Note: `execute_code` is ALWAYS hard-blocked in cron context — use `terminal` instead.

## Validation

Run before scheduling:

```bash
python .hermes/cron/validate-skill-refs.py   # all skill refs resolve
python .hermes/cron/validate-cronjobs.py      # structural + threshold + no_agent consistency
python tools/audit-skills.py                  # repo audit passes
```

See also: references/cronjob-config-patterns.md

## Pitfalls

1. **Threshold keys that don't match script output.** If a threshold key like `no_merge_conflicts` or `dependency_map_regenerated` never appears in the script's JSON output, it is silently never evaluated — the job reports `threshold_breached: false` even when the conceptual check failed. Always match threshold keys to actual output field names. (See also: a related class of bug in `audit-skills.py` where `{threshold}` was used as an f-string variable but `threshold` was undefined — if the temps_scripts threshold had been breached, the script would have crashed with `NameError`. Fixed to `THRESHOLDS['temps_scripts']`.)
2. **Flat skills array gives no rationale.** A plain list of skill paths tells the agent *what* to load but not *why* or *when*. Use the structured `skills` object with `phase` + `rationale` so the agent can make decisions (e.g., skip a Linux-only skill on Windows).
3. **Forgetting the `note` on no_agent jobs.** Without `note: "no_agent=true — skills loaded for documentation..."`, future readers assume skills grant tool access and may be confused when `toolView` returns nothing.
4. **Not validating skill refs before scheduling.** A single broken path (e.g. `github/mattpocock-using-git-worktrees` when the skill lives under `software-development/`) fails silently at fire time. Always run the validator.
5. **JSON patch operations silently dropping fields.** When using find-and-replace to edit cronjob JSON, nested fields like `no_agent`, `enabled_toolsets`, or `continuity` can be accidentally swallowed if the old_string/new_string brackets overlap adjacent fields. Always validate with a schema checker (`python .hermes/cron/validate-cronjobs.py`) after ANY edit — don't rely on spot-checking. A missing `no_agent=true` on a script-only job causes the cron system to invoke the LLM instead, and a missing `enabled_toolsets` causes all tool calls to be rejected.
6. **Dry-run shows false deletions for sync-script jobs.** When a sync script does PULL-then-PUSH and you run `--dry-run`, the PULL step reports "Would copy" but doesn't actually copy files to local. The subsequent PUSH step then sees those files as missing locally and reports "Would delete (removed locally)." This is a **dry-run artifact**, not actual data loss — in a real run, the PULL copies files first, so PUSH won't delete them. Always interpret dry-run deletion reports with this pattern in mind; confirm against the actual script flow rather than trusting the output at face value.
