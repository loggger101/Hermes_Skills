---
description: Hermes Agent skills repository — 127 skills across 20 categories.
---

# Hermes Skills Repository

This repository is a centralized database of **127 Hermes Agent skills** compiled from all available profiles into a single, organized collection. Skills are reusable procedures and workflows that extend Hermes Agent's capabilities.

## Organization

Skills are organized into 20 categories:

| Category | Focus |
|----------|-------|
| [apple/](./apple/) | Apple platform integrations (macOS, iOS) |
| [autonomous-ai-agents/](./autonomous-ai-agents/) | Multi-agent orchestration, cronjob patterns |
| [creative/](./creative/) | Creative content generation, design, media |
| [data-science/](./data-science/) | Data science workflows, Python, SQL, orbital mechanics |
| [devops/](./devops/) | Docker, REST APIs, SSH, SQLite |
| [doc-coauthoring/](./doc-coauthoring/) | Structured documentation co-authoring |
| [dogfood/](./dogfood/) | Exploratory QA and adversarial UX testing |
| [email/](./email/) | Email management and triage |
| [frontend-design/](./frontend-design/) | Visual design for AI-generated UI |
| [github/](./github/) | GitHub workflows, PR review, issues, CI |
| [huggingface-trackio/](./huggingface-trackio/) | ML experiment tracking |
| [media/](./media/) | GIF search, audio analysis, YouTube content |
| [mlops/](./mlops/) | Evaluation harnesses, HuggingFace Hub, vLLM, W&B |
| [note-taking/](./note-taking/) | Obsidian vault integration |
| [productivity/](./productivity/) | Documents, spreadsheets, meetings, calendars |
| [research/](./research/) | Paper writing pipeline, citation verification, monitoring |
| [security/](./security/) | Code security review |
| [smart-home/](./smart-home/) | Philips Hue control |
| [social-media/](./social-media/) | X/Twitter via xurl CLI |
| [software-development/](./software-development/) | TDD, spec-driven dev, debugging, Python, Node |

## Structure

```
category/
├── SKILL.md          # Skill definition (frontmatter + body)
├── DESCRIPTION.md    # Category description
├── references/       # Supporting reference docs
├── scripts/          # Helper scripts
├── tests/            # Test files
└── templates/        # Template files
```

## Tooling

- **`tools/audit-skills.py`** — Automated audit script that validates all skills
- **`.hermes/cron/`** — Cronjob registry with templates and active job definitions

## Getting Started

```bash
# Load a skill
hermes skill load <category>/<skill-name>

# View a skill's details
skill_view(name='<skill-name>')

# Run the audit
python3 tools/audit-skills.py
```

See the [README](./README.md) for the full skill catalog and the [DEPENDENCY.md](./DEPENDENCY.md) for the relationship map.
