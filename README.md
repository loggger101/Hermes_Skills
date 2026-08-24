# Hermes Skills Repository

A comprehensive collection of **127 Hermes Agent skills** compiled from all available profiles into a single, organized repository.

## Overview

This repository serves as a centralized database of all Hermes Agent skills, organized by category. Skills are reusable procedures and workflows that extend Hermes Agent's capabilities.

### Source Profiles
Skills were imported from three Hermes profiles:
1. **Default profile** (`~/AppData/Local/hermes/skills/`) — system-level skills
2. **the-skill-maker** (`~/AppData/Local/hermes/profiles/the-skill-maker/skills/`) — primary working profile
3. **the-memory-controller** (`~/AppData/Local/hermes/profiles/the-memory-controller/skills/`) — memory management profile

When a skill existed in multiple profiles, the version from the highest-priority profile was used.

### Categories

| Category | Description | Skill Count |
|----------|-------------|-------------|
| [apple/](./apple/) | Apple platform integrations | 4 |
| [autonomous-ai-agents/](./autonomous-ai-agents/) | Multi-agent orchestration and delegation | 7 |
| [creative/](./creative/) | Creative content generation and design | 21 |
| [data-science/](./data-science/) | Data science workflows and tools | 6 |
| [devops/](./devops/) | Infrastructure, containers, and deployment | 5 |
| [dogfood/](./dogfood/) | Exploratory QA and testing | 1 |
| [doc-coauthoring/](./doc-coauthoring/) | Structured document co-authoring workflow | 1 |
| [email/](./email/) | Email management and triage | 2 |
| [frontend-design/](./frontend-design/) | Visual design for AI-generated UI | 1 |
| [github/](./github/) | GitHub workflow management | 7 |
| [huggingface-trackio/](./huggingface-trackio/) | ML experiment tracking with Trackio | 1 |
| [media/](./media/) | Media content generation | 3 |
| [mlops/](./mlops/) | ML operations: evaluation, inference, models | 6 |
| [note-taking/](./note-taking/) | Note-taking and knowledge management | 1 |
| [productivity/](./productivity/) | Productivity and document management | 18 |
| [research/](./research/) | Research and content discovery | 9 |
| [security/](./security/) | Security review and auditing | 1 |
| [smart-home/](./smart-home/) | Smart home device control | 1 |
| [social-media/](./social-media/) | Social media content | 1 |
| [software-development/](./software-development/) | Development tools and workflows | 16 |

**Total: 127 skills across 20 categories**

## Skill Structure

Each skill follows the standard Hermes skill format:

```
category/
├── skill-name/
│   ├── SKILL.md          # Main skill definition with frontmatter
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

## Pre-existing vs Imported Skills

This repository contains two types of skills:

1. **Imported skills** (98): Copied from Hermes profiles during import
2. **Pre-existing skills** (29): Originally populated in this repo by another agent, including:
   - 26 `mattpocock-*` opinionated coding methodology skills
   - 4 devops skills (`docker-containers`, `rest-api-client`, `sqlite-queries`, `ssh-remote`)
   - 3 top-level category skills (`doc-coauthoring`, `frontend-design`, `security/mattpocock-security-review`)
   - `autonomous-repo-cronjob`

## Verification

- ✅ No duplicate skill names across categories
- ✅ No duplicate content (verified via MD5 hash comparison)
- ✅ No content overlap between pre-existing and imported skills
- ✅ No empty skill directories
- ✅ All SKILL.md files have valid frontmatter with `name` and `description` fields

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
