# Hermes Skills Repository

A comprehensive collection of **202 Hermes Agent skills** across 23 categories — the second brain for its owner's Hermes Agent environment. See [DESCRIPTION.md](./DESCRIPTION.md) for the task-to-skill lookup ladder and [SKILLS-INDEX.md](./SKILLS-INDEX.md) for the full flat index.

## Table of Contents

- [Quick Start](#quick-start)
- [Overview](#overview)
- [Skills Index (flat, grep-friendly)](./SKILLS-INDEX.md)
- [Code Index (scripts/helpers/tests, flat)](./CODE-INDEX.md)
- [Skill Structure](#skill-structure)
- [Provenance](#provenance)
- [Cron Job Authoring](#cron-job-authoring)
- [Claude Code](#claude-code)
- [Tools](#tools)
- [Verification](#verification)
- [Usage](#usage)
- [License](#license)

## Quick Start

```bash
# Load a skill in Hermes
hermes skill load software-development/mattpocock-code-review

# Or load multiple skills for cronjob automation
hermes skill load autonomous-ai-agents/cron-job-authoring
hermes skill load github/mattpocock-yeet
hermes skill load software-development/mattpocock-using-git-worktrees

# View a skill's details
skill_view(name='cron-job-authoring')
```

**Looking for a specific capability?** Grep the flat index first — it's one line per skill and costs nothing:

```bash
grep -i "delta-v" SKILLS-INDEX.md   # or: nicegui, triage, diagram...
# Looking for runnable code (scripts/helpers/tests) instead?
grep -i "raster\|token bridge" CODE-INDEX.md
```

**New to the repo?** Start with the [Skill Structure](#skill-structure) and [Verification](#verification) sections below (they define every convention in this second brain), then the [Cron Job Authoring](#cron-job-authoring) section for the two-agent automation pattern, or browse the [Dependency Map](./DEPENDENCY.md) for skill relationships.

## Overview

This repository serves as a centralized database of all **202 Hermes Agent skills**, organized by category. Skills are reusable procedures and workflows that extend Hermes Agent's capabilities. All skills follow the standard `SKILL.md` format with consistent frontmatter, section headers, and `related_skills` cross-references (538 cross-references mapped across 202 skills — every skill is connected to at least one other). See [audit notes](docs/archive/audit-notes-skills-repo-pass.md) for the full audit details and [DEPENDENCY.md](./DEPENDENCY.md) for the full relationship map.

### Categories

| Category | Description | Skill Count |
|----------|-------------|-------------|
| [apple/](./apple/) | Apple platform integrations | 4 |
| [autonomous-ai-agents/](./autonomous-ai-agents/) | Multi-agent orchestration and delegation | 12 |
| [communication/](./communication/) | Decision-brief formats (1-3-1 rule) + mental-model latticeworks | 2 |
| [creative/](./creative/) | Creative content generation and design | 29 |
| [data-science/](./data-science/) | Data science workflows and tools | 15 |
| [devops/](./devops/) | Infrastructure, containers, and deployment + zero-install SSH tunnels (Pinggy) + system-design knowledge layer + live incident command | 11 |
| [doc-coauthoring/](./doc-coauthoring/) | Structured document co-authoring workflow | 1 |
| [dogfood/](./dogfood/) | Exploratory QA and testing | 1 |
| [email/](./email/) | Email management and triage | 2 |
| [frontend-design/](./frontend-design/) | Visual design for AI-generated UI (incl. Python reactive-UI builders) | 2 |
| [github/](./github/) | GitHub workflow management | 12 |
| [huggingface-trackio/](./huggingface-trackio/) | ML experiment tracking with Trackio | 1 |
| [mcp/](./mcp/) | MCP: server authoring (FastMCP) + terminal client (mcporter) | 2 |
| [media/](./media/) | Media content generation | 3 |
| [mlops/](./mlops/) | ML operations: evaluation, inference, models | 6 |
| [note-taking/](./note-taking/) | Note-taking and knowledge management | 2 |
| [productivity/](./productivity/) | Productivity and document management | 21 |
| [research/](./research/) | Research and content discovery | 18 |
| [security/](./security/) | Security review, audit orchestration, forensics, rule authoring + STRIDE app threat modeling | 5 |
| [smart-home/](./smart-home/) | Smart home device control | 1 |
| [social-media/](./social-media/) | Social media content | 2 |
| [software-development/](./software-development/) | Development tools and workflows + failure-signal auditing | 47 |
| [web-development/](./web-development/) | Web/API client derivation (HAR-based) + versioned static-site publishing | 3 |

**Total: 202 skills across 23 categories** — the per-category DESCRIPTIONs regenerate from live frontmatter via `python tools/gen-skills-index.py`; this table is hand-maintained and enforced against disk by verify-all's doc-count gate.

### Skill Catalog

One line per skill lives in [SKILLS-INDEX.md](./SKILLS-INDEX.md), generated from each
skill's frontmatter by `python tools/gen-skills-index.py` and drift-checked by verify-all.
Browse a category folder above for the files themselves. (This README used to carry a
hand-written copy of that list; it drifted twice, so it was removed in round-45.)

## Skill Structure

Each skill follows the standard Hermes skill format:

```text
category/
├── DESCRIPTION.md        # Category-level description (required when >1 skill)
└── skill-name/
    ├── SKILL.md          # Main skill definition with frontmatter
    ├── references/       # Supporting reference docs
    ├── scripts/          # Helper scripts
    ├── tests/            # Test files
    └── templates/        # Template files
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

> **Note:** The audit enforces the fields above. Some imported skills also carry extra top-level keys from their upstream format (`category:`, `triggers:`, `prerequisites:`, `dependencies:`); they are left as shipped because Hermes may read them.

## Provenance

Skills come from three sources (see [audit notes](docs/archive/audit-notes-skills-repo-pass.md) for the full history):

1. **Imported skills** — copied in from three live Hermes profiles during the initial import: `default` (`~/.hermes/skills/`), `the-skill-maker` (`~/.hermes/profiles/the-skill-maker/skills/`, the primary working profile) and `the-memory-controller` (`~/.hermes/profiles/the-memory-controller/skills/`). Where a skill existed in more than one, the highest-priority profile's version was kept.
2. **Pre-existing repo skills** — authored directly in this repository (e.g. the 22+ `mattpocock-*` methodology skills, devops and top-level category skills).
3. **Research-harvest ports** — added across successive starred-repo deep-dive rounds, including hub installs (`hermes skills install official/...`) and external ports with their licenses carried in frontmatter.

The per-skill origin is recorded round-by-round in [audit notes](docs/archive/audit-notes-skills-repo-pass.md) up to 2026-09-14 and in `round-NN` commit messages since; the live set of record is always `SKILLS-INDEX.md` (regenerated from frontmatter).

## Cron Job Authoring

Skills for writing self-contained, autonomous cronjob prompts that run without session context. The core pattern is documented in `cron-job-authoring`: general scheduling in its SKILL.md, repo-automation jobs in its `references/repo-cronjob.md`.

This repository also includes a ready-to-use **cronjob registry** at [`.hermes/cron/`](./.hermes/cron/) with templates and active job definitions:

- **`.hermes/cron/templates/`** — Prompt and script templates for the two most common patterns
- **`.hermes/cron/active/`** — Active cronjob definitions (JSON config) ready to be loaded via `cronjob()`
- **`.hermes/cron/archive/`** — Deprecated or old cronjob definitions kept for reference

> **Registration status (Owner machine, verified 2026-09-17).** This is the one place the README records it. Registrations are per machine, and only the Owner machine has a scheduler (`%LOCALAPPDATA%/hermes/cron/jobs.json`; the Loggg machine has none as of 2026-10-01). It had three registered jobs: `aspirecures-weekly-research` (**disabled**), `hermes-skills-audit` (**enabled**, Sun 3 AM — silent when clean, runs the repo's own audit via a shim), and `hermes-skills-bidirectional-sync` (registered but **paused by design** until the owner opts it on). Load/enable a definition with the `cronjob()` tool to change that. Until then, run the checks yourself: `py tools/verify-all.py`.

### Core Skills

| Skill | Purpose | Key References |
|-------|---------|-----------------|
| [`cron-job-authoring`](./autonomous-ai-agents/cron-job-authoring/SKILL.md) | Author autonomous cron prompts with guardrails. Covers `cronjob()` tool usage, schedule formats, delivery targets, and self-contained prompt patterns; for repos with existing CI pipelines, embeds the repo's guardrails, dedup logic, and two-agent split (preparer + commit agent). | [repo-cronjob](./autonomous-ai-agents/cron-job-authoring/references/repo-cronjob.md), [prompt-template](./autonomous-ai-agents/cron-job-authoring/references/prompt-template.md), [drafting-guide](./autonomous-ai-agents/cron-job-authoring/references/drafting-guide.md), [agent-vs-script-checklist](./autonomous-ai-agents/cron-job-authoring/references/agent-vs-script-checklist.md), [two-agent-architecture](./autonomous-ai-agents/cron-job-authoring/references/two-agent-architecture.md) |
| [`cron-config-authoring`](./autonomous-ai-agents/cron-config-authoring/SKILL.md) | Author cronjob JSON configs: structured skills object with per-skill phase + rationale, threshold key alignment with script output, skill reference path resolution, model pinning, and approval-mode configuration. | [cronjob-config-patterns](./autonomous-ai-agents/cron-config-authoring/references/cronjob-config-patterns.md) |
| [`product-price-monitor`](./productivity/product-price-monitor/SKILL.md) | Price/availability monitoring via cronjob ticks. Uses `cronjob(action="create")` with normalized price alerts. | — |
| [`competitor-news-monitor`](./research/competitor-news-monitor/SKILL.md) | Company-focused news tracking via cronjob. Loads `blogwatcher` and `parallel-cli` for enrichment. | — |
| [`apple-reminders`](./apple/apple-reminders/SKILL.md) | Scheduled reminder checks via cronjob. Loads `cron-job-authoring` for automation patterns. | — |
| [`findmy`](./apple/findmy/SKILL.md) | Ongoing AirTag/device tracking via cronjob. Loads `imessage` for notifications and `cron-job-authoring` for scheduling. | — |

### Related Skills (via `related_skills` or `skill_view` calls)

| Skill | Cronjob Connection |
|-------|--------------------|
| [`hermes-agent`](./autonomous-ai-agents/hermes-agent/SKILL.md) | Linked from `cron-job-authoring` (the `cronjob()` tool and cron config reference) |
| [`mattpocock-yeet`](./github/mattpocock-yeet/SKILL.md) | References `cron-job-authoring` in related_skills |
| [`mattpocock-using-git-worktrees`](./software-development/mattpocock-using-git-worktrees/SKILL.md) | References `cron-job-authoring` in related_skills |
| [`cron-config-authoring`](./autonomous-ai-agents/cron-config-authoring/SKILL.md) | Documents the structured skills object pattern used across all cronjob configs; references `cron-job-authoring` and `hermes-agent-skill-authoring` |

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

## Claude Code

This repo doubles as a Claude Code plugin, so the same second brain is available
to Claude Code in every project on the machine — not just to Hermes.

**Why a manifest is needed.** Claude Code's loader only auto-discovers skills one
level under a plugin's `skills/` directory. It does not walk category folders, so
a repo shaped `<category>/<skill>/SKILL.md` resolves to zero skills. Verified
against Claude Code 2.1.270:

| Layout | Skills discovered |
|--------|-------------------|
| `skills/<category>/<skill>/SKILL.md` | 0 |
| `skills/<skill>/SKILL.md` | 2 of 2 |
| explicit `skills` array in `plugin.json` | 2 of 2 |

[`tools/gen-claude-plugin.py`](./tools/gen-claude-plugin.py) therefore writes an
explicit `skills` array into [`.claude-plugin/plugin.json`](./.claude-plugin/plugin.json),
listing each nested skill path. The Hermes-native layout is preserved, nothing is
duplicated, and 199 skills load (`docx`, `pdf`, and `xlsx` are held back because
Claude Code ships first-party skills of the same name — two near-identical entries
for one request only degrades skill selection).

### Install on this machine

```bash
py tools/gen-claude-plugin.py
powershell -File tools/install-claude-code.ps1
```

The installer points a directory junction at `~/.claude/skills/hermes`, which
Claude Code auto-loads as `hermes@skills-dir`. A junction, not a copy: the repo
stays the single source of truth and a `git pull` is live immediately. Junctions
need neither administrator rights nor Developer Mode. Restart Claude Code
afterwards — skills are read once at session start.

Verify, and see what it costs per session:

```bash
claude plugin details hermes
```

Roughly 3.9k tokens always-on (~20 per skill description); each skill body is
only read when that skill fires. Remove it again with
`powershell -File tools/install-claude-code.ps1 -Uninstall`.

### Install on another machine

[`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json) makes the
repo installable directly, no clone or junction needed:

```bash
claude plugin marketplace add loggger101/Hermes_Skills
```

```bash
claude plugin install hermes@hermes-skills
```

The install step prompts once to trust the plugin source, so run it in an
interactive terminal — piped or non-interactive shells will hang on that prompt.

Both manifests are generated, and `verify-all.py` gates them for drift — rerun
`py tools/gen-claude-plugin.py` after adding, renaming, or removing a skill.

## Tools

This repository includes Python scripts in the `tools/` directory that automate repository maintenance:

| Tool | Purpose | Cron Integration |
|------|---------|------------------|
| [`verify-all.py`](./tools/verify-all.py) | **Start here.** Runs every gate in one shot: audit (incl. zero-threshold hardcoded-secret scan), links, index drift (the four generated indexes, the Claude Code manifests and the per-machine installed-plugins doc), cron validators (config validator proves no_agent threshold keys match script output), README/DESCRIPTION count consistency, self-test harness execution, router coverage (skill-flow-router vs the catalog it maps), and mutation self-tests of six gates. Exit 0 = all 19 gates pass | Manual; run before any commit |
| [`audit-skills.py`](./tools/audit-skills.py) | Validates all 202 skills: YAML frontmatter, description length, `related_skills` resolution, body section presence, `skill_view()` call sync, category `DESCRIPTION.md` checks | Weekly job `hermes-skills-audit` ([registration status](#cron-job-authoring)) |
| [`sync-hermes-skills.py`](./tools/sync-hermes-skills.py) | Bidirectional sync between GitHub repo and local Hermes env: git pull, skill/memories/profiles sync, retirement of merged skills (local copies of the dirs listed in [`tools/retired-skills.txt`](./tools/retired-skills.txt) move to `~/.hermes/retired-skills/` and are never copied back), full index regeneration (all five machine-generated indexes), audit + FULL verify-all as the pre-push gate (refuses commit+push when any gate fails or could not run), git push. Has `--dry-run` — always dry-run before a first live run (round 19b caught two latent phantom-action bugs this way; round-34 fixed a third: profile counts now hash-compare instead of counting every file) | Weekly job in `sync-hermes-skills.json` ([registration status](#cron-job-authoring)); verified end-to-end once via manual trigger 2026-09-14 |
| [`_index_output.py`](./tools/_index_output.py) | Shared write-guard for the generators: refuses to overwrite an index when the scan came back suspiciously empty, and implements their `--check` (compare-don't-write) drift mode | Imported by the four generators |
| [`check-links.py`](./tools/check-links.py) | Broken-link gate: verifies every relative markdown link in the repo resolves (skips URLs, code spans, historical profiles-export snapshots); exit 1 on any broken link | After doc edits; pairs with audit as a pre-commit pair |
| [`gen-skills-index.py`](./tools/gen-skills-index.py) | Rebuilds SKILLS-INDEX.md (flat one-line-per-skill index, the cheapest lookup path in the repo); stdlib-only | After adding/removing/renaming skills |
| [`gen-code-index.py`](./tools/gen-code-index.py) | Rebuilds CODE-INDEX.md: every script/helper/test/template with kind, language, size, and a one-line purpose from its docstring/header comment; stdlib-only | After adding/removing/renaming code files |
| [`regen-dependency-map.py`](./tools/regen-dependency-map.py) | Standalone DEPENDENCY.md regenerator (same format as the sync script's built-in map): scans all SKILL.md frontmatter, rebuilds hub/standalone tables and xref validation line | Manual / after bulk skill additions |
| [`gen-references-index.py`](./tools/gen-references-index.py) | Rebuilds REFERENCES-INDEX.md: every skill's `references/*.md` with its title, one line each; stdlib-only | After adding/removing/renaming reference docs |
| [`check-router-coverage.py`](./tools/check-router-coverage.py) | Router coverage gate: every skill in `skill-flow-router`'s declared scope is either routed or declined with a reason | Gate in verify-all.py |
| [`gen-claude-plugin.py`](./tools/gen-claude-plugin.py) | Rebuilds `.claude-plugin/plugin.json` and `marketplace.json` so Claude Code can load the nested skill tree (its loader does not walk category folders); stdlib-only | After adding/removing/renaming skills |
| [`run-skill-tests.py`](./tools/run-skill-tests.py) | Discovery-based pytest runner: finds every `<skill>/tests/` suite at runtime and runs each; exit 1 on any failure, empty scan is FATAL | CI job `skill-tests`; manual before shipping a new test suite |
| [`run-self-tests.py`](./tools/run-self-tests.py) | Discovery-based runner for the standalone `*_verify.py` / `*-verify.py` harnesses (the repo's other fail-loud mechanism). Registered manifest of auto-run vs excluded; missing optional deps classify as SKIP, real regressions FAIL. New unregistered verify scripts make it exit 1 until someone decides how to handle them | CI job `self-test-harnesses`; also a gate in verify-all.py |
| [`mutation-test-selftest-gate.py`](./tools/mutation-test-selftest-gate.py) | Mutation self-test for run-self-tests.py: proves PASS / SKIP(rc77) / SKIP(missing dep) / FAIL classification and manifest-drift detection on throwaway temp fixtures — a gate that cannot be proven to fail is worse than no gate | Final gate in verify-all.py (always runs, stdlib-only) |
| [`mutation-test-doc-gate.py`](./tools/mutation-test-doc-gate.py), [`mutation-test-secret-gate.py`](./tools/mutation-test-secret-gate.py), [`mutation-test-audit-gate.py`](./tools/mutation-test-audit-gate.py), [`mutation-test-cron-gate.py`](./tools/mutation-test-cron-gate.py), [`mutation-test-router-gate.py`](./tools/mutation-test-router-gate.py) | The other five gates' mutation self-tests: each plants defects in a temp copy (a wrong count, a fake credential, a skill with no frontmatter, a phantom threshold key, an unrouted skill) and asserts its gate fails | Gates in verify-all.py |
| [`install-claude-code.ps1`](./tools/install-claude-code.ps1) | Junctions this repo into `~/.claude/skills/hermes` so every Claude Code session on the machine loads it; `-Uninstall` removes the link, never the repo | Once per machine |
| [`validate-skill-refs.py`](./.hermes/cron/validate-skill-refs.py) | Validates all skill references in cronjob JSON configs resolve to existing in-repo skill directories | Pre-flight check before scheduling any cronjob |
| [`validate-cronjobs.py`](./.hermes/cron/validate-cronjobs.py) | Comprehensive cronjob JSON validation: structural schema, skill ref resolution, threshold key alignment (every no_agent threshold/report-template key must be a string the script actually emits — phantom keys are errors; out-of-repo scripts skip with a label), no_agent consistency. `--job <file>` validates one config | Run before committing any cronjob config change |

## Verification

The repository includes an automated audit script at [`tools/audit-skills.py`](./tools/audit-skills.py) that validates all skills on a configurable schedule. It checks:

- **YAML frontmatter integrity** — required fields (`name`, `version`, `author`, `platforms`, `metadata.hermes`) parse correctly
- **Description length** — all `description` fields are ≤59 chars (the routing-signal budget)
- **`related_skills` resolution** — every cross-reference resolves to an existing in-repo skill (no broken refs, no self-references)
- **Body section presence** — each skill has `## What This Skill Does` and `## When to Use` sections
- **`skill_view()` call sync** — every `skill_view("xxx")` call in body text has a corresponding `related_skills` entry
- **Category `DESCRIPTION.md`** — every category directory with >1 skill has a `DESCRIPTION.md`
- **Referenced script existence** — scripts listed in frontmatter `script:` fields exist on disk
- **Duplicate skill name detection** — no two `SKILL.md` files share the same `name` field (threshold = 0)

Requires **pyyaml** (`pip install -r requirements.txt`). Without it the audit refuses to run rather than reporting an empty pass.

The single command that runs everything:

```bash
py tools/verify-all.py      # 19 gates; exit 0 = all pass
```

Every tool fails **closed**: a wrong interpreter, a missing pyyaml, an unreadable file, a scan that
comes back empty, or an index that has drifted all produce a non-zero exit and a `[FATAL]`/`[DRIFT]`
line -- never a quiet "clean" result. Individually:

```bash
# Run the audit (exit 0 = within thresholds, exit 1 = threshold breached or scan failed)
py tools/audit-skills.py
```

On Windows, use `py` wherever bare `python` is the Microsoft Store alias stub (it exits 49 without
running anything; true on the Owner machine, not on the Loggg one). Linux/macOS: `python3`.

`.hermes/cron/active/skill-audit.json` runs the same audit weekly (Sun 3 AM, `no_agent`, `deliver: local`)
as `hermes-skills-audit`; see [Cron Job Authoring](#cron-job-authoring) for where it is registered.
`verify-all.py` remains the pre-commit path.

### CI (GitHub Actions)

[`.github/workflows/ci.yml`](./.github/workflows/ci.yml) makes "the repo passes its own gates" a property of the remote, not just local discipline. Every push to `main` and every PR runs three jobs:

1. **Health gates** — `pip install pyyaml`, then `python tools/verify-all.py`.
2. **Skill test suites** — [`tools/run-skill-tests.py`](./tools/run-skill-tests.py) discovers them at runtime: every `<skill>/tests/` dir with a pytest file is picked up automatically, so no workflow edit is needed when a new suite ships.
   - Seven suites currently: comfyui 117 / docx 29 / pdf 21 / powerpoint 21 / xlsx 12 / regex-vs-llm-structured-text 14 / sqlite-queries 20 (gate-enforced since round-33 — verify-all's doc-count check recomputes every count from the live `def test_` definitions and fails on drift; originally counted by hand 2026-09-09).
   - The sqlite suite is stdlib-only and its four `sqlite3`-CLI tests skip on hosts without the binary, so it adds zero new dependencies.
   - Test deps for the library-backed suites come from [`test-requirements.txt`](./test-requirements.txt), a single source of truth created by running all suites in a clean venv until green (verified 2026-09-09: all pass, pure wheels only, no poppler binary needed because `pypdfium2` covers rasterization). When you add test dependencies to any skill's suite, update that file too.
3. **Self-test harnesses** — runs [`tools/run-self-tests.py`](./tools/run-self-tests.py) against a real install of duckdb/polars/pyarrow/numpy/pyomo/highspy (deps from [`selftest-requirements.txt`](./selftest-requirements.txt)), so the standalone `*_verify.py` harnesses — which re-execute documented engine behavior against concrete cases — actually execute on Linux instead of classifying as SKIP. An upstream API change therefore breaks CI loudly rather than quietly rotting a reference doc.

### Live Invariants

✅ items are checked by `tools/audit-skills.py` / `tools/check-links.py` on every audit run; the threshold-gated subset (a non-zero count fails the run) is `broken_refs`, `yaml_errors`, `long_descriptions`, `duplicate_skills`, `missing_body_sections`, `temps_scripts`. 📎 items are conventions no tool enforces — hold them by hand.

- ✅ All 202 skills have valid frontmatter (`name`, `version`, `author`, `platforms`, `metadata.hermes`) and parse without errors
- ✅ No duplicate skill names; no empty skill directories
- ✅ All `related_skills` references resolve to existing in-repo skills — 538 cross-references across 202 skills (see [DEPENDENCY.md](./DEPENDENCY.md))
- ✅ All descriptions ≤59 chars, double-quoted YAML strings
- ✅ Every skill has a body section (`## What This Skill Does` or an audit-recognized alternative) and standard header capitalization
- ✅ Every multi-skill category directory has a `DESCRIPTION.md` (all 23 do)
- 🔒 Line endings normalized via `.gitattributes` (`text=auto`) — CRLF in working tree, LF in git storage. Enforced by git itself at checkout/commit, not by the audit
- 📎 *Convention, not a gate:* repo-authored files end with a newline. Two exceptions are kept byte-for-byte as their source emits them: the vendored conference templates under `research/research-paper-writing/templates/`, and the sync-owned `memories/` files (the historical snapshot in singular `profile/` is likewise untouched by sync, which skips it). Markdown trailing whitespace is **not** blanket-stripped — a double trailing space is a hard line break, so a blanket strip would silently reflow docs; only stray single spaces go.
- 📎 *Convention, not a gate:* Python is formatted with `ruff format` and kept clean under `ruff check` (settings in [`ruff.toml`](./ruff.toml), 100 columns). Markdown keeps a blank line around every heading, list, fenced block and table, and uses `-` bullets. Skills bundled with Hermes Agent (listed in `profile/.bundled_manifest`) are left as upstream ships them: Hermes stops updating a bundled skill once its files change, so a cosmetic reformat would opt it out of upstream fixes.
- ✅ Broken-link gate: every relative markdown link resolves (`tools/check-links.py`, skips URLs/code spans/`profiles-export/` snapshots)

One-off historical fixes (duplicate removals, ref repairs, header renames, sync setup) are logged in [audit notes](docs/archive/audit-notes-skills-repo-pass.md) up to 2026-09-14, and in `round-NN` commit messages since.

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

MIT, see [`LICENSE`](LICENSE). That covers this repository's own work: the
indexes, the root documentation and the skills written here. Individual skills
carry a `license:` field in their SKILL.md frontmatter, and that field governs
the skill it sits in. All but two are MIT. Those two are CC-BY-SA-4.0:
`security/semgrep-rule-creator` and `software-development/property-based-testing`.
One file inside an MIT skill carries its own CC-BY-SA-4.0 notice:
`software-development/python-craft/references/modern-python-tooling.md`, ported
from trailofbits/skills. One skill, `devops/system-design-scaling`, is MIT but
distilled from donnemartin/system-design-primer, which is CC BY 4.0.
