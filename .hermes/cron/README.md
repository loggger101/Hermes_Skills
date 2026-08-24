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
    workdir='/path/to/repo',
    skills=['autonomous-ai-agents/autonomous-repo-cronjob'],
    deliver='origin',
    continuity=True
)
```
