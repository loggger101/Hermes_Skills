# Hermes Skills Repository

A comprehensive collection of **127 Hermes Agent skills** compiled from all available profiles into a single, organized repository.

## Overview

This repository serves as a centralized database of all Hermes Agent skills, organized by category. Skills are reusable procedures and workflows that extend Hermes Agent's capabilities.

### Source Profiles

Skills were imported from three Hermes profiles:
1. **Default profile** (`~/.hermes/skills/`) — system-level skills
2. **the-skill-maker** (`~/.hermes/profiles/the-skill-maker/skills/`) — primary working profile
3. **the-memory-controller** (`~/.hermes/profiles/the-memory-controller/skills/`) — memory management profile

When a skill existed in multiple profiles, the version from the highest-priority profile was used.

> ⚠️ **Known remaining issues** — see [NOTES.md](./NOTES.md) for the full audit.

### Categories

| Category | Description | Skill Count |
||----------|-------------|-------------|
|| [apple/](./apple/) | Apple platform integrations | 4 |
|| [autonomous-ai-agents/](./autonomous-ai-agents/) | Multi-agent orchestration and delegation | 9 |
|| [creative/](./creative/) | Creative content generation and design | 18 |
|| [data-science/](./data-science/) | Data science workflows and tools | 6 |
|| [devops/](./devops/) | Infrastructure, containers, and deployment | 5 |
|| [doc-coauthoring/](./doc-coauthoring/) | Structured document co-authoring workflow | 1 |
|| [dogfood/](./dogfood/) | Exploratory QA and testing | 1 |
|| [email/](./email/) | Email management and triage | 2 |
|| [frontend-design/](./frontend-design/) | Visual design for AI-generated UI | 1 |
|| [github/](./github/) | GitHub workflow management | 11 |
|| [huggingface-trackio/](./huggingface-trackio/) | ML experiment tracking with Trackio | 1 |
|| [media/](./media/) | Media content generation | 3 |
|| [mlops/](./mlops/) | ML operations: evaluation, inference, models | 5 |
|| [note-taking/](./note-taking/) | Note-taking and knowledge management | 1 |
|| [productivity/](./productivity/) | Productivity and document management | 18 |
|| [research/](./research/) | Research and content discovery | 9 |
|| [security/](./security/) | Security review and auditing | 1 |
|| [smart-home/](./smart-home/) | Smart home device control | 1 |
|| [social-media/](./social-media/) | Social media content | 1 |
|| [software-development/](./software-development/) | Development tools and workflows | 28 |

**Total: 127 skills across 20 categories**

## Skill Structure

Each skill follows the standard Hermes skill format:

```
category/
├── skill-name/
│   ├── SKILL.md          # Main skill definition with frontmatter
│   ├── DESCRIPTION.md    # Category-level description (optional)
│   ├── references/        # Supporting reference docs
│   ├── scripts/           # Helper scripts
│   ├── tests/            # Test files
│   └── templates/         # Template files
```

### SKILL.md Format

Every skill has a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: skill-name
description: "Brief description of what the skill does."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [...]
    related_skills: [...]
---
```

> **Note:** Some older imported skills use a simpler frontmatter style (e.g. `category:` and `tags:` as top-level keys instead of nested under `metadata.hermes`). All skills have been checked and normalized to the current standard format.

## Pre-existing vs Imported Skills

This repository contains two types of skills:

1. **Imported skills** (98): Copied from Hermes profiles during import
2. **Pre-existing skills** (29): Originally populated in this repo by a previous agent / imported from the live Hermes skill set, including:
   - 22 `mattpocock-*` opinionated coding methodology skills
   - 4 devops skills (`docker-containers`, `rest-api-client`, `sdlc-review`, `ssh-remote`)
   - 3 top-level category skills (`doc-coauthoring`, `frontend-design`, `mattpocock-security-review`)
   - `autonomous-repo-cronjob`

## Cron Job Authoring

Skills for writing self-contained, autonomous cronjob prompts that run without session context. The core pattern is documented in `autonomous-repo-cronjob` (for repo-automation tasks) and `cron-job-authoring` (for general scheduling).

### Core Skills

| Skill | Purpose | Key References |
|-------|---------|-----------------|
| [`autonomous-repo-cronjob`](./autonomous-ai-agents/autonomous-repo-cronjob/SKILL.md) | Write self-contained cronjob prompts for repos with existing CI pipelines. Embeds the repo's guardrails, dedup logic, and two-agent split (preparer + commit agent). | [prompt-template](./autonomous-ai-agents/autonomous-repo-cronjob/references/prompt-template.md), [drafting-guide](./autonomous-ai-agents/autonomous-repo-cronjob/references/drafting-guide.md), [agent-vs-script-checklist](./autonomous-ai-agents/autonomous-repo-cronjob/references/agent-vs-script-checklist.md), [two-agent-architecture](./autonomous-ai-agents/autonomous-repo-cronjob/references/two-agent-architecture.md) |
| [`cron-job-authoring`](./autonomous-ai-agents/cron-job-authoring/SKILL.md) | Author autonomous cron prompts with guardrails. Covers `cronjob()` tool usage, schedule formats, delivery targets, and self-contained prompt patterns. | — |
| [`product-price-monitor`](./productivity/product-price-monitor/SKILL.md) | Price/availability monitoring via cronjob ticks. Uses `cronjob(action="create")` with normalized price alerts. | — |
| [`competitor-news-monitor`](./research/competitor-news-monitor/SKILL.md) | Company-focused news tracking via cronjob. Loads `blogwatcher` and `parallel-cli` for enrichment. | — |
| [`apple-reminders`](./apple/apple-reminders/SKILL.md) | Scheduled reminder checks via cronjob. Loads `cron-job-authoring` for automation patterns. | — |
| [`findmy`](./apple/findmy/SKILL.md) | Ongoing AirTag/device tracking via cronjob. Loads `imessage` for notifications and `cron-job-authoring` for scheduling. | — |

### Related Skills (via `related_skills` or `skill_view` calls)

| Skill | Cronjob Connection |
|-------|--------------------|
| [`hermes-agent`](./autonomous-ai-agents/hermes-agent/SKILL.md) | References `autonomous-repo-cronjob` in related_skills |
| [`mattpocock-yeet`](./github/mattpocheck-yeet/SKILL.md) | References `autonomous-repo-cronjob` in related_skills |
| [`mattpocock-using-git-worktrees`](./software-development/mattpocock-using-git-worktrees/SKILL.md) | References `autonomous-repo-cronjob` in related_skills |

### Two-Agent Architecture (from AspireCURES pipeline)

The recommended pattern for repo-automation cronjobs uses a **two-agent split**:

1. **Preparer (cronjob)**: Collects data, applies Claude-curate logic, emits a JSON report. Embeds repo guardrails (append-only merge, date-churn signature, dedup keys, spend caps).
2. **Commit agent**: Consumes the report, merges changes, renders pages, validates against `lint-feed.pl`, commits, and pushes.

This split allows the cronjob to run fully autonomously (no user interaction) while a separate agent handles the repo-write phase that may need to surface edge cases to the user.

### Cron Job Tool API

```python
# Create a recurring job
cronjob(action='create',
  prompt=<self-contained prompt body>,
  schedule='17 13 * * 1',    # cron expression
  workdir=<repo_root>,
  skills=[...],
  deliver='origin',
  enabled_toolsets=['web', 'terminal', 'file', 'delegation'],
  continuity=True)          # carry state across runs

# One-shot
cronjob(action='create',
  prompt=<body>,
  schedule='2026-06-01T09:00:00',
  workdir=<repo_root>,
  deliver='origin')
```

## Verification

- ✅ No empty skill directories
- ✅ All SKILL.md files have valid frontmatter with `name` and `description` fields
- ✅ No duplicate skill names (resolved — `mattpocock-subagent-driven-development` duplicate removed)
- ✅ All `related_skills` references resolve to existing in-repo skills (9 broken + 147 self/missing fixed)
- ✅ All skills have complete frontmatter (`version`, `author`, `platforms`, `metadata.hermes`)
- ✅ All skill descriptions are ≤ 60 characters (hardline standard)
- ✅ All 127 descriptions end with a period
- ✅ All 127 descriptions are double-quoted YAML strings
- ✅ All 127 skills have either a "What This Skill Does" or "When to Use" section
- ✅ All section headers use standard capitalization (`## When to Use`, `## Pitfalls`, `## How to Run`, `## Quick Start`)
- ✅ All non-standard Pitfalls headers (`## Common Pitfalls`, `## Troubleshooting`) renamed to `## Pitfalls`
- ✅ No trailing whitespace in any file
- ✅ All files end with a trailing newline
- ✅ All YAML frontmatter parses without errors
- ✅ No CRLF line endings (all LF)
- ✅ No temp scripts remaining in repo root
- ✅ `related_skills` network: 287 cross-references across 114 skills (13 standalone skills with none)
- ✅ No duplicate content (verified via hash comparison)
- ✅ DEPENDENCY.md relationship mapping audited and updated
- ✅ Profile documentation transferred to `profile/` directory
- ✅ Cron Job Authoring section added to README with skill index + tool API reference

## Usage

Skills can be loaded in Hermes Agent using:

```bash
hermes skill load <category>/<skill-name>
```

Or programmatically:

```python
skill_view(name='<skill-name>')
```

## License

Individual skills carry their own license headers. Most are MIT licensed.
