---
description: Hermes Agent second brain — 145 skills across 20 categories, memories, cron configs.
---

# Hermes Skills Repository (Second Brain)

This repository is the **second brain** of its owner's Hermes Agent environment: a centralized collection of **145 verified, audit-passing skills**, persistent agent memories, and cronjob configuration — organized so that any agent can clone it and be productive in under a minute.

## Start here (cheapest → most thorough)
- **[AGENTS.md](./AGENTS.md)** — how agents should use this repo: lookup order, skill anatomy, hard conventions, maintenance rules. Read this first.
- **[SKILLS-INDEX.md](./SKILLS-INDEX.md)** — flat one-line-per-skill index of all 145 skills; `grep -i <term>` is the fastest way to find a capability.
- **[DEPENDENCY.md](./DEPENDENCY.md)** — relationship map: hub skills, standalone skills, full cross-reference validation.
- **[README.md](./README.md)** — human-facing overview with the full catalog and verification status.

## Organization

Skills are organized into 20 categories (each has a `DESCRIPTION.md`):

| Category | Focus |
|----------|-------|
| [apple/](./apple/) | Apple platform integrations (macOS, iOS) |
| [autonomous-ai-agents/](./autonomous-ai-agents/) | Multi-agent orchestration, cronjob patterns |
| [creative/](./creative/) | Creative content generation, design, media, diagrams |
| [data-science/](./data-science/) | Data science workflows, Python, SQL, orbital mechanics, space pipelines |
| [devops/](./devops/) | Docker, REST APIs, SSH, SQLite |
| [doc-coauthoring/](./doc-coauthoring/) | Structured documentation co-authoring |
| [dogfood/](./dogfood/) | Exploratory QA and adversarial UX testing |
| [email/](./email/) | Email management and triage |
| [frontend-design/](./frontend-design/) | Visual design for AI-generated UI + Python reactive-UI builders (NiceGUI) |
| [github/](./github/) | GitHub workflows, PR review, issues, CI, issue-triage state machine |
| [huggingface-trackio/](./huggingface-trackio/) | ML experiment tracking |
| [media/](./media/) | GIF search, audio analysis, YouTube content |
| [mlops/](./mlops/) | Evaluation harnesses, HuggingFace Hub, vLLM, W&B |
| [note-taking/](./note-taking/) | Obsidian vault integration |
| [productivity/](./productivity/) | Documents, spreadsheets, meetings, calendars, website audits |
| [research/](./research/) | Paper writing pipeline, citation verification, monitoring |
| [security/](./security/) | Code security review |
| [smart-home/](./smart-home/) | Philips Hue control |
| [social-media/](./social-media/) | X/Twitter via xurl CLI |
| [software-development/](./software-development/) | TDD, spec-driven dev, debugging, planning (grilling/wayfinder), Python, Node |

Non-skill content: [`memories/`](./memories/) (the agent's persistent notes + user profile — the "brain" part) and [`profile/`](./profile/) (a reference snapshot of one live Hermes profile). See each directory's `DESCRIPTION.md`.

## Structure

```
category/
├── SKILL.md          # Skill definition (frontmatter + body; required sections enforced by audit)
├── DESCRIPTION.md    # Category description
├── references/       # Supporting reference docs (loaded on demand)
├── scripts/          # Helper scripts
└── templates/        # Template files
```

## Tooling (`tools/`)

- **`audit-skills.py`** — validates all skills against repo conventions; exit 0 = clean. Run before committing any skill change.
- **`gen-skills-index.py`** — rebuilds `SKILLS-INDEX.md` from live frontmatter (stdlib-only).
- **`regen-dependency-map.py`** — rebuilds `DEPENDENCY.md` from live frontmatter (safe standalone; the sync script's built-in generator can hang on import interactively).
- **`sync-hermes-skills.py`** — full bidirectional GitHub↔local-Hermes sync, run weekly by cron. Has `--dry-run`. Do not run casually: its delete phase removes repo files that no longer exist locally.

## Getting Started

```bash
# Find a capability (cheapest path)
grep -i "delta-v" SKILLS-INDEX.md

# Load a skill in Hermes
hermes skill load <category>/<skill-name>

# View a skill's details
skill_view(name='<skill-name>')

# Run the audit / regenerate generated docs
python tools/audit-skills.py
python tools/gen-skills-index.py && python tools/regen-dependency-map.py
```

## Maintenance rules (summary)

Never break the audit; keep `description` ≤59 chars; regenerate DEPENDENCY.md + SKILLS-INDEX.md after frontmatter changes; log significant changes in [NOTES.md](./NOTES.md); commit author for automation is `hermes-cronbot <cronbot@hermes.local>`; never commit credentials. Full detail in [AGENTS.md](./AGENTS.md).
