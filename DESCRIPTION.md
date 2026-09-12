---
description: Hermes Agent second brain — 196 skills across 23 categories, memories, cron configs.
---

# Hermes Skills Repository (Second Brain)

This repository is the **second brain** of its owner's Hermes Agent environment: a centralized collection of **196 verified, audit-passing skills**, persistent agent memories, and cronjob configuration — organized so that any agent can clone it and be productive in under a minute.

## Start here (cheapest → most thorough)
- **[SKILLS-INDEX.md](./SKILLS-INDEX.md)** — flat one-line-per-skill index of all 196 skills; `grep -i <term>` is the fastest way to find a capability.
- **[CODE-INDEX.md](./CODE-INDEX.md)** — flat index of every script, shared helper, test, and template (the executable knowledge layer); `grep -i <term> CODE-INDEX.md` finds runnable code by purpose or owner skill.
- **[REFERENCES-INDEX.md](./REFERENCES-INDEX.md)** — flat index of all 318 reference docs living inside skills' `references/` dirs (nested subdirs included); `grep -i <term> REFERENCES-INDEX.md` finds verified API maps / gotchas tables by topic without knowing which skill owns them.
- **[DEPENDENCY.md](./DEPENDENCY.md)** — relationship map: hub skills, standalone skills, full cross-reference validation.
- **[docs/](./docs/README.md)** — **knowledge-layer index**: verified API references + working code patterns from the 41-repo starred deep dive, reorganized 2026-09-07 to live inside each owning skill's `references/` dir (astro-toolkit-selection carries brahe/skyfield/OpenSCvx/catalog/optimization refs; economicspace-pipeline carries Δv-oracles + soft-assumption sources; python-data-science carries polars/pymc; nicegui-app-builder carries frontend tooling; github-pr-workflow carries git recipes). Skills say *how to work*; their references say *what exists in these libraries and what breaks*.
- **[README.md](./README.md)** — human-facing overview with the full catalog and verification status.

## Task → Skill Quick Table

The fastest way from a job you have in mind to the skill that does it:

| You want to… | Start with |
|---|---|
| Find any capability in this brain (any task below) | `grep -i <term>` on [SKILLS-INDEX.md](./SKILLS-INDEX.md) — one line per skill, zero parsing cost |
| Don't know which planning/spec/debug/review flow fits | `skill-flow-router` (main flow + 3 on-ramps mapped to installed skills)
| Plan a big ambiguous build / stress-test an idea | `grilling-interview` → `wayfinder-map-planning` (multi-session map of decision tickets) |
| Turn a design discussion into a spec | `conversation-to-spec` |
| Triage issues/PRs, write agent-ready briefs | `github/issue-triage-state-machine` (+ its AGENT-BRIEF / OUT-OF-SCOPE references) |
| Review code or PRs | `mattpocock-code-review`, `requesting-code-review` (pre-commit gate), `mattpocock-security-review` |
| Debug a hard bug | `systematic-debugging`, `mattpocock-diagnosing-bugs` |
| Test-first development | `test-driven-development`, `mattpocock-tdd` |
| Build a Python web/desktop UI (dashboards, internal tools) | `nicegui-app-builder`; data dashboards → `streamlit-dashboards` |
| Design or redesign frontend / landing pages | `design-taste-frontend`, `redesign-existing-projects`, `popular-web-designs` (54 real design systems), `claude-design` |
| Create diagrams (39 types, 3 variants each) | `diagram-design`; dark SVG arch → `architecture-diagram`; hand-drawn → `excalidraw` |
| Generate images / video / audio | `comfyui`, `manim-video`, `ascii-video`, `songwriting-and-ai-music` (Suno prompts) |
| Asteroid-mining economics pipeline work | `economicspace-pipeline`; tool choice → `astro-toolkit-selection`; method choice → `space-mission-computation-paradigms` |
| Build space/astro data pipelines (fetch→parquet→HF) | `space-data-pipelines` (verified API gotchas table inside) |
| Data science: EDA, modeling, SQL at scale | `python-data-science`, `sql-for-data`; exact-float verification → `bit-identity-float-pipelines` |
| Write docs that agents can actually consume | `mattpocock-writing-for-agents` (skills/AGENTS.md/specs) |
| Automate a repo with cronjobs | `autonomous-repo-cronjob`, `cron-job-authoring`; two-agent pattern → README "Cron Job Authoring" section |
| Test a Windows desktop app end-to-end (WPF/WinForms/Qt) | `windows-desktop-e2e` (pywinauto + UIA, page-object skeleton inside) |
| Ship a Python app as a small fast Windows installer | `generating-python-installer` (Nuitka one-file + Inno Setup; slimming scripts in its scripts/) |
| Search biomedical literature / genomic databases | `pubmed-database` (NCBI E-utilities), `gget` (Ensembl/BLAST lookups); full genomics/computational-biology work → `bioinformatics` (gateway to 400+ skills) |
| Evaluate a paper, proposal, or evidence claim | `scholar-evaluation` (9-dimension rubric); build the review itself → `literature-review` |
| Save / sync / dedupe knowledge across stores | `knowledge-ops` (6-layer KB architecture + ingest workflow) |
| Onboard to an unfamiliar repository | `codebase-onboarding` (4-phase recon → arch map → conventions → starter AGENTS.md) |
| Keep a long-lived project's docs from rotting | `living-docs-governance` (constitution/map/status/history roles, delete-zone) |
| Triage an ambiguous ask before planning it | `brainstorming`; act on review feedback honestly → `receiving-code-review`, claim done only after proof → `verification-before-completion` |
| Expose a local service / receive webhooks with no extra install | `pinggy-tunnel` (SSH reverse tunnel, webhook + MCP + LLM-endpoint recipes inside) |
| Call tools on an MCP server from the terminal | `mcporter` (npx; list/call/auth/daemon); authoring servers → `fastmcp` |
| Stop agents re-grepping a repo they've seen before / compress noisy command output | `repowise` (precomputed local index: graph, git risk signals, decisions, health + 10 MCP tools; `distill <cmd>` reversible token compression) |
| Score codebase structural health / find what to refactor next | `code-quality-signal` (5 ungameable root-cause metrics → one score); where in the dependency graph it hurts → `architecture-metrics` (Lakos levels, blast radius, Martin A/I/D distance, SDP coupling, test gaps) — both stdlib-only, run together: signal says what's wrong, arch-metrics says which files |
| Ship UI that doesn't look templated — pick the aesthetic first | `design-taste-frontend` (anti-slop default), presets: `soft-premium-ui`, `editorial-minimalism-ui`, `industrial-brutalist-ui`; motion-heavy → `awwwards-gsap-motion`; Google Stitch DESIGN.md → `stitch` |
| Publish a site/dashboard/docs build with versioned deploys + rollback | `publish-site` (GitHub Pages → Cloudflare → Netlify ladder, live-URL verification) |
| Verify this repo's own health | `py tools/verify-all.py` — all 9 gates in one run (`python` is a Store stub on Windows) |

## Organization

Skills are organized into 23 categories (each has a `DESCRIPTION.md`):

| Category | Focus |
|----------|-------|
| [apple/](./apple/) | Apple platform integrations (macOS, iOS) |
| [autonomous-ai-agents/](./autonomous-ai-agents/) | Multi-agent orchestration, cronjob patterns |
| [communication/](./communication/) | Decision-brief formats (1-3-1 rule) |
| [creative/](./creative/) | Creative content generation, design, media, diagrams |
| [data-science/](./data-science/) | Data science workflows, Python, SQL, orbital mechanics, space pipelines |
| [devops/](./devops/) | Docker, REST APIs, SSH, SQLite |
| [doc-coauthoring/](./doc-coauthoring/) | Structured documentation co-authoring |
| [dogfood/](./dogfood/) | Exploratory QA and adversarial UX testing |
| [email/](./email/) | Email management and triage |
| [frontend-design/](./frontend-design/) | Visual design for AI-generated UI + Python reactive-UI builders (NiceGUI) |
| [github/](./github/) | GitHub workflows, PR review, issues, CI, issue-triage state machine |
| [huggingface-trackio/](./huggingface-trackio/) | ML experiment tracking |
| [mcp/](./mcp/) | Model Context Protocol servers (FastMCP) |
| [media/](./media/) | GIF search, audio analysis, YouTube content |
| [mlops/](./mlops/) | Evaluation harnesses, HuggingFace Hub, vLLM, W&B |
| [note-taking/](./note-taking/) | Obsidian vault + multi-layer knowledge-base ops (ingest/sync/dedupe/retrieve) |
| [productivity/](./productivity/) | Documents, spreadsheets, meetings, calendars, website audits |
| [research/](./research/) | Paper writing pipeline, citation verification, monitoring + bioinformatics (PubMed/gget) & scholarly evaluation |
| [security/](./security/) | Code security review |
| [smart-home/](./smart-home/) | Philips Hue control |
| [social-media/](./social-media/) | X/Twitter via xurl CLI |
| [software-development/](./software-development/) | TDD, spec-driven dev, debugging, planning (grilling/wayfinder), Python, Node + repo onboarding & living-docs governance |
| [web-development/](./web-development/) | Web/API client derivation from HAR recordings |

Non-skill content: [`memories/`](./memories/DESCRIPTION.md) (the agent's persistent notes + user profile — the "brain" part) and [`profile/`](./profile/DESCRIPTION.md) (a reference snapshot of one live Hermes profile). See each directory's `DESCRIPTION.md`.

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

- **`verify-all.py`** — **the one command**: runs all 9 gates (audit, links, index drift x4, cron validators x2, doc-count consistency) and prints a pass/fail table. Run before every commit.
- **`audit-skills.py`** — validates all skills against repo conventions; exit 0 = clean. Hard-fails if pyyaml is missing or the scan finds <100 skills, so an unrunnable audit can never report clean.

- **`check-links.py`** — broken-link gate: every relative markdown link must resolve (skips URLs, code spans, historical `profiles-export/` snapshots). Run alongside the audit before committing doc changes.
- **`gen-skills-index.py`** — rebuilds `SKILLS-INDEX.md` + every category `DESCRIPTION.md` from live frontmatter (stdlib-only). `--check` reports drift without writing.
- **`gen-code-index.py`** — rebuilds `CODE-INDEX.md` from every code file in the repo: path, kind (script/helper/test/template), language, size, one-line purpose extracted from its docstring/header comment. Run after adding/removing/renaming scripts.
- **`gen-references-index.py`** — rebuilds `REFERENCES-INDEX.md` from every skill's `references/*.md`: flat grep index with each doc's frontmatter description and owning skill. Run after adding/removing reference docs.
- **`regen-dependency-map.py`** — rebuilds `DEPENDENCY.md` from live frontmatter (safe standalone; the sync script's built-in generator can hang on import interactively).
- **`sync-hermes-skills.py`** — full bidirectional GitHub↔local-Hermes sync. A weekly cron job is *defined* for it in `.hermes/cron/active/` but is **not registered** with the live scheduler, so today it only runs when invoked. Has `--dry-run`. Its delete phase is capped at `MAX_DELETIONS = 25` files per run (override: `--allow-mass-delete`), and it refuses to commit or push when the audit did not pass.
- **`_index_output.py`** — shared write-guard behind the four generators: blocks an empty-scan overwrite, and provides their `--check` drift mode (compare against disk, exit 1 if stale, write nothing).
- **CI ([`.github/workflows/ci.yml`](./.github/workflows/ci.yml))** — runs all 9 gates plus the five skill pytest suites on every push/PR; test deps from [`test-requirements.txt`](./test-requirements.txt) (single source of truth — update it when adding suite dependencies).

## Getting Started

```bash
# Find a capability (cheapest path)
grep -i "delta-v" SKILLS-INDEX.md

# Load a skill in Hermes
hermes skill load <category>/<skill-name>

# View a skill's details
skill_view(name='<skill-name>')

# Run the audit / regenerate generated docs
# (Windows: `py`. Bare `python`/`python3` are Store alias stubs that run nothing.)
py tools/audit-skills.py
py tools/gen-skills-index.py && py tools/regen-dependency-map.py
```

## Maintenance rules (summary)

Run `py tools/verify-all.py` before every commit (CI re-runs it on every push); never break the audit; keep `description` ≤59 chars; regenerate DEPENDENCY.md + SKILLS-INDEX.md after frontmatter changes, CODE-INDEX.md after code-file changes, and REFERENCES-INDEX.md after reference-doc changes; update `test-requirements.txt` when adding test dependencies to a skill's suite; log significant changes in [audit notes](docs/archive/audit-notes-skills-repo-pass.md); commit author for automation is `hermes-cronbot <cronbot@hermes.local>`; never commit credentials. The full convention list is enforced by `tools/audit-skills.py` (see its docstring and the Verification section of README.md).
