# Cronjob Registry for Hermes Skills Repository

This directory contains cronjob definitions that use skills from this repository.
Each file is a self-contained cronjob prompt body that can be loaded via:

```python
cronjob(action='create', prompt=<prompt body>, schedule='...')
```

## Structure

```
.hermes/cron/
├── README.md              # This file
├── templates/
│   ├── repo-automation.py # Two-agent split pattern (preparer + commit)
│   └── skill-watchdog.py  # Simple watchdog pattern
├── active/
│   ├── aspirecures-weekly.json  # Example: research pipeline
│   ├── skill-audit.json         # Example: weekly skill audit
│   └── sync-hermes-skills.json  # Bidirectional sync: repo ↔ local Hermes env
└── archive/
    └── old-jobs/        # Deprecated cronjobs kept for reference
```

## Writing a Cronjob Prompt

Every cronjob prompt must be **self-contained** — it cannot rely on session context.
See:
- [`cron-job-authoring` skill](../../autonomous-ai-agents/cron-job-authoring/SKILL.md)
- [`autonomous-repo-cronjob` skill](../../autonomous-ai-agents/autonomous-repo-cronjob/SKILL.md)
- [No-interaction guardrail template](../../autonomous-ai-agents/cron-job-authoring/references/guardrail-template.md)
- [Delivery discipline guide](../../autonomous-ai-agents/cron-job-authoring/references/delivery-discipline.md)

## Active Cronjobs

| Job | Schedule | Skills Used | Purpose |
||-----|----------|-------------|---------|
|| [`aspirecures-weekly.json`](./active/aspirecures-weekly.json) | Weekly Mon 1 PM ET | 9 skills (research, mlops, github) | Research pipeline: collect→curate→render→commit disease pages (two-agent split) |
|| [`skill-audit.json`](./active/skill-audit.json) | Weekly Sun 3 AM | 4 skills (cron-job-authoring, skill-authoring, verification) | Self-audit: YAML validation, broken refs, description lengths, line endings |
|| [`sync-hermes-skills.json`](./active/sync-hermes-skills.json) | Weekly Sun 2 AM | 4 skills (cron-job-authoring, hermes-agent, skill-authoring, verification) | Bidirectional sync: pull upstream → sync skills/memories/profiles ↔ local → commit → push → audit |

## Active Cronjobs Detail

### aspirecures-weekly.json
|- **Architecture:** Two-agent split (preparer + commit agent). Preparer collects candidates from Europe PMC + PubMed + ClinicalTrials.gov + ISRCTN, applies the Claude curation gate (strict relevance + credibility + patient-appropriateness + confidence threshold + 65-95 word summary), emits a JSON report. Commit agent consumes the report, merges into data/research/*.json, runs the full render pipeline (render.pl → render-ads.pl → gen-sitemap.pl → schema.pl → dedash.pl → gen-feeds.pl), validates with lint-feed.pl + verify.sh, then commits + pushes.
|- **Schedule:** Weekly Monday at 1 PM ET (cron: `0 13 * * 1`)
|- **Skills:** 9 skills across research, MLOps, and software-development categories
|- **Embedded prompt body:** Full self-contained prompt with repo context, two-mode split (maintenance-only vs full), data file shape (field-by-field), date-churn signature algorithm (C8), candidate gates (structural + curation), dedup keys, country normalization map, render pipeline order, lint-feed.pl validation matrix, failure modes & responses, and phased instructions (9 phases)
|- **Guardrails:** Append-only merge, date-churn prevention (signature excludes `generated` + `trials[].countries`), dedup by PMID+DOI+title, safe-fail per entity, spend caps (max_tokens_per_run=300000, max_curations_per_run=200), country normalization, maintenance-only passes always run even without curation
|- **Key guardrails:** 10 hard rules including no ANTHROPIC_API_KEY needed (agent IS the model), skip-and-record on missing credentials, signature taken BEFORE maintenance mutations (C8 fix), self-validation against lint-feed.pl before emitting
|- **Credential strategy:** Skip-and-record — Europe PMC and PubMed are free; ClinicalTrials.gov and ISRCTN are free; Embase and Web of Science need subscription keys but are silently skipped if absent
|- **Threshold:** git_push_success=true, lint_passed=true, no_fabricated_data=true, report_emitted=true
|- **Model:** primary=qwen/qwen3.6-35b (provider=qwen), fallback=poolside/laguna-s-2.1:free (provider=nous)
|- **Note:** The agent substitutes its own Claude judgments for the ANTHROPIC_API_KEY-gated curation step in fetch_curate.mjs. The preparer does NOT touch repo data files — it emits a JSON report that a separate commit agent consumes.

## Quick Start

```python
from hermes_tools import cronjob

# Load a prompt body from this directory
with open('.hermes/cron/templates/repo-automation.py') as f:
    prompt = f.read()

cronjob(
    action='create',
    prompt=prompt,
    schedule='0 9 * * 1',  # Weekly Monday at 9 AM
    workdir='.'
    skills=['autonomous-ai-agents/autonomous-repo-cronjob'],
    deliver='origin',
    continuity=True
)
```
