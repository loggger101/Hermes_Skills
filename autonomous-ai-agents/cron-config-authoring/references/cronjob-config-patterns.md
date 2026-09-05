---
name: cronjob-config-patterns
---

# Cronjob Configuration Patterns Reference

Session-specific patterns discovered while enhancing the Hermes_Skills repository's cronjob registry (`.hermes/cron/active/`).

## The structured skills object

Replace flat `skills: ["path", ...]` arrays with a structured object:

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

### Rationale for no_agent script jobs

When a cronjob config has `no_agent: true`, the cron system runs a Python script (e.g. `tools/audit-skills.py`) with no LLM invocation. The `skills` array is therefore **not** used to grant tool access — it documents which skill's standards and guardrails govern each aspect of the script:

| Skill | Governs |
|-------|---------|
| `cron-job-authoring` | Watchdog pattern, delivery discipline, approval-mode pitfalls |
| `verification-culture` | Audit-pass-as-gate standing rules |
| `hermes-agent-skill-authoring` | Frontmatter standards the script validates |

The `note` field is essential — without it, a future reader assumes skills grant tool access.

### Rationale for LLM-driven jobs

For `no_agent: false` jobs, skills ARE invoked as tools. The `phase` + `rationale` fields tell the agent:
- Which phase of the pipeline each skill covers
- Whether the skill is needed at all for this specific run (e.g. skip Linux-only skills)
- What would break if a skill were removed

Example from `aspirecures-weekly.json`: `evaluating-llms-harness` is annotated as "Linux-only deps (lm-eval/vllm)" with a suggestion to substitute `mattpocock-evidence-driven`'s lighter test gate on Windows.

## Threshold key alignment

**Problem discovered:** The sync-hermes-skills.json threshold block originally listed conceptual keys like `no_merge_conflicts` and `dependency_map_regenerated` that the sync script never output as booleans. These were silently never evaluated.

**Fix:** Every threshold key must match an actual field in the script's JSON output. Read the script's `main()` + output dict structure, then confirm each key is produced.

**Real bug found:** `audit-skills.py` line 308 used `{threshold}` (undefined variable) instead of `THRESHOLDS['temps_scripts']`. If the temps_scripts threshold were ever breached, the script would crash with `NameError`. Fixed.

## Skill reference path resolution

Skill refs in cronjob JSON use **repo-relative slash paths** (e.g. `research/arxiv`), NOT the `name` field from SKILL.md frontmatter.

### Windows gotcha

`os.path.relpath()` on Windows produces backslash-separated strings. Comparing `"research\\arxiv"` against `"research/arxiv"` with `in` silently returns False — no error, just mismatch.

**Fix:** Always normalize:
```python
def norm_path(p):
    return str(p).replace('\\', '/').replace('//', '/')
```

The `validate-skill-refs.py` script (at `.hermes/cron/validate-skill-refs.py`) implements this normalization and validates all 16 skill refs across 3 cronjob JSON files.

### Broken path found and fixed

`aspirecures-weekly.json` originally referenced `github/mattpocock-using-git-worktrees` — but that skill lives under `software-development/`, not `github/`. The directory didn't exist. Fixed to `software-development/mattpocock-using-git-worktrees`.

## Model pinning for drift-skip prevention

The cron scheduler auto-skips unpinned jobs when global inference config drifts between creation and fire. Both LLM-driven and no_agent jobs should pin `model` + `provider` explicitly.

In the sync-hermes-skills.json config, `model`/`provider` are set even though `no_agent=true` — this prevents confusion if the flag is later flipped to `false`.

## Approval mode for terminal-using jobs

All three cronjobs in this repo use `terminal` to invoke Python scripts or git commands. When `approvals.cron_mode: deny` (the default), dangerous patterns (`git push`, `rm`, etc.) are silently blocked. Set:

```bash
hermes config set approvals.cron_mode approve
```

Note: `execute_code` is **always** hard-blocked in cron context — cron jobs must use `terminal` instead.
