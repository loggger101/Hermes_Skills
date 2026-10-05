---
description: Hermes Agent second brain — 205 skills across 23 categories, memories, cron configs.
---

# Hermes Skills Repository (Second Brain)

This repository is the **second brain** of its owner's Hermes Agent environment: a centralized collection of **205 verified, audit-passing skills**, persistent agent memories, and cronjob configuration — organized so that any agent can clone it and be productive in under a minute.

## Start here (cheapest → most thorough)

1. **[SKILLS-INDEX.md](./SKILLS-INDEX.md)** — flat one-line-per-skill index of all 205 skills. `grep -i <term>` is the fastest way to find a capability.
2. **[CODE-INDEX.md](./CODE-INDEX.md)** — flat index of every script, shared helper, test and template (the executable knowledge layer). `grep -i <term> CODE-INDEX.md` finds runnable code by purpose or owner skill.
3. **[REFERENCES-INDEX.md](./REFERENCES-INDEX.md)** — flat index of all 413 reference docs inside skills' `references/` dirs (nested subdirs included). `grep -i <term> REFERENCES-INDEX.md` finds verified API maps and gotchas tables by topic without knowing which skill owns them.
4. **[DEPENDENCY.md](./DEPENDENCY.md)** — relationship map: hub skills, standalone skills, full cross-reference validation.
5. **[docs/](./docs/README.md)** — the knowledge-layer index: verified API references and working code patterns from the 41-repo starred deep dive. Skills say *how to work*; their references say *what exists in these libraries and what breaks*.
6. **[README.md](./README.md)** — human-facing overview: categories with skill counts, conventions, cron authoring, Claude Code install, verification.

The reference docs in `docs/` were reorganized on 2026-09-07 to live inside each owning skill's `references/` dir:

| Skill | Carries |
|-------|---------|
| `astro-toolkit-selection` | brahe, skyfield, OpenSCvx, catalog and optimization refs |
| `economicspace-pipeline` | Δv-oracles and soft-assumption sources |
| `python-data-science` | polars and pymc |
| `nicegui-app-builder` | frontend tooling |
| `github-pr-workflow` | git recipes |

## Task → Skill Quick Table

The fastest way from a job you have in mind to the skill that does it. Not sure which row fits? Grep [SKILLS-INDEX.md](./SKILLS-INDEX.md) first.

### Finding a skill

| You want to… | Start with |
|--------------|------------|
| Find any capability in this brain (any task below) | `grep -i <term>` on [SKILLS-INDEX.md](./SKILLS-INDEX.md) — one line per skill, zero parsing cost |
| Don't know which planning/spec/debug/review flow fits | `skill-flow-router` (main flow + 3 on-ramps mapped to installed skills) |

### Planning, review and engineering workflow

| You want to… | Start with |
|--------------|------------|
| Plan a big ambiguous build / stress-test an idea | `grilling-interview` → `wayfinder-map-planning` (multi-session map of decision tickets) |
| Turn a design discussion into a spec | `conversation-to-spec` |
| Triage an ambiguous ask before planning it | `brainstorming`; act on review feedback honestly → `receiving-code-review`, claim done only after proof → `verification-before-completion` |
| Triage issues/PRs, write agent-ready briefs | `github/issue-triage-state-machine` (+ its AGENT-BRIEF / OUT-OF-SCOPE references) |
| Review code or PRs | `mattpocock-code-review`, `requesting-code-review` (pre-commit gate), `mattpocock-security-review` |
| Debug a hard bug | `systematic-debugging`, `mattpocock-diagnosing-bugs` |
| Test-first development | `test-driven-development`, `mattpocock-tdd` |
| Onboard to an unfamiliar repository | `codebase-onboarding` (4-phase recon → arch map → conventions → starter AGENTS.md) |
| Stop agents re-grepping a repo they've seen before / compress noisy command output | `repowise` (precomputed local index: graph, git risk signals, decisions, health + 10 MCP tools; `distill <cmd>` reversible token compression) |
| Score codebase structural health / find what to refactor next | `architecture-metrics`: `quality_signal.py` (5 ungameable root-cause metrics → one score + bottleneck) says what's wrong; `architecture_metrics.py` (Lakos levels, blast radius, Martin A/I/D distance, SDP coupling, test gaps) says which files — stdlib-only, run both |
| Design a scalable system / prep a system design interview (CAP, caching, sharding, fan-out) | `system-design-scaling` (primer-distilled trade-off tables + 8 case-study patterns; runnable LRU/base62/MapReduce-top-k/availability scripts inside) |

### Docs and knowledge

| You want to… | Start with |
|--------------|------------|
| Write docs that agents can actually consume | `mattpocock-writing-for-agents` (skills/AGENTS.md/specs) |
| Keep a long-lived project's docs from rotting | `living-docs-governance` (constitution/map/status/history roles, delete-zone) |
| Save / sync / dedupe knowledge across stores | `knowledge-ops` (6-layer KB architecture + ingest workflow) |

### Frontend, diagrams and media

| You want to… | Start with |
|--------------|------------|
| Build a Python web/desktop UI (dashboards, internal tools) | `nicegui-app-builder`; data dashboards → `streamlit-dashboards` |
| Design or redesign frontend / landing pages | `design-taste-frontend`, `redesign-existing-projects`, `popular-web-designs` (54 real design systems), `claude-design` |
| Ship UI that doesn't look templated — pick the aesthetic first | `design-taste-frontend` (anti-slop default), presets: `soft-premium-ui`, `editorial-minimalism-ui`, `industrial-brutalist-ui`; motion-heavy → `awwwards-gsap-motion`; Google Stitch DESIGN.md → `stitch` |
| Create diagrams (39 types, 3 variants each) | `diagram-design`; dark SVG arch → `architecture-diagram`; hand-drawn → `excalidraw` |
| Generate images / video / audio | `comfyui`, `manim-video`, `ascii-video`, `songwriting-and-ai-music` (Suno prompts) |

### Data, science and research

| You want to… | Start with |
|--------------|------------|
| Data science: EDA, modeling, SQL at scale | `python-data-science`, `sql-for-data`; exact-float verification → `bit-identity-float-pipelines` |
| Asteroid-mining economics pipeline work | `economicspace-pipeline`; method then tool choice → `astro-toolkit-selection` |
| Build space/astro data pipelines (fetch→parquet→HF) | `space-data-pipelines` (verified API gotchas table inside) |
| Search biomedical literature / genomic databases | `pubmed-database` (NCBI E-utilities), `gget` (Ensembl/BLAST lookups); full genomics/computational-biology work → `bioinformatics` (gateway to 400+ skills) |
| Evaluate a paper, proposal, or evidence claim | `scholar-evaluation` (9-dimension rubric); build the review itself → `literature-review` |

### Automation, shipping and infrastructure

| You want to… | Start with |
|--------------|------------|
| Automate a repo with cronjobs | `cron-job-authoring` (repo jobs: its `references/repo-cronjob.md`); JSON job configs → `cron-config-authoring`; two-agent pattern → README "Cron Job Authoring" section |
| Test a Windows desktop app end-to-end (WPF/WinForms/Qt) | `windows-desktop-e2e` (pywinauto + UIA, page-object skeleton inside) |
| Ship a Python app as a small fast Windows installer | `generating-python-installer` (Nuitka one-file + Inno Setup; slimming scripts in its scripts/) |
| Publish a site/dashboard/docs build with versioned deploys + rollback | `publish-site` (GitHub Pages → Cloudflare → Netlify ladder, live-URL verification) |
| Expose a local service / receive webhooks with no extra install | `pinggy-tunnel` (SSH reverse tunnel, webhook + MCP + LLM-endpoint recipes inside) |
| Call tools on an MCP server from the terminal | `mcporter` (npx; list/call/auth/daemon); authoring servers → `fastmcp` |
| Verify this repo's own health | `py tools/verify-all.py` — all 21 gates in one run |

## Organization

Skills are organized into 23 categories, each with its own `DESCRIPTION.md`. The category table, with skill counts checked against disk, is in [README.md](./README.md#categories).

Non-skill content:

- [`memories/`](./memories/DESCRIPTION.md) — the agent's persistent notes and user profile (the "brain" part).
- [`profile/`](./profile/DESCRIPTION.md) — a historical reference snapshot of one live Hermes profile, taken 2026-08-24.
- `profiles-export/` (plural) is a different thing: a gitignored local mirror that sync writes on every run. It never enters git.

See each directory's `DESCRIPTION.md` for details.

## Structure

```text
category/
├── DESCRIPTION.md        # Category description (generated from the skills' frontmatter)
└── skill-name/
    ├── SKILL.md          # Skill definition (frontmatter + body; required sections enforced by audit)
    ├── references/       # Supporting reference docs (loaded on demand)
    ├── scripts/          # Helper scripts
    ├── tests/            # Test files
    └── templates/        # Template files
```

## Tooling (`tools/`)

### verify-all

**`verify-all.py`** is the one command. It runs all 21 gates and prints a pass/fail table. Run it before every commit.

- **Audit** — includes the zero-threshold hardcoded-secret scan over every skill script and SKILL.md.
- **Links** — every relative markdown link resolves.
- **Index drift (x6)** — SKILLS, CODE, REFERENCES, DEPENDENCY, `.claude-plugin` and installed-plugins.
- **Cron validators (x2)** — the config validator proves every `no_agent` threshold key is a string its script actually emits.
- **Doc-count consistency** — hand-written counts match disk.
- **Router coverage** — every skill in the router's declared scope is either routed or explicitly declined with a reason.
- **Skill pointers** — every `skill_view` / `hermes skill load` / `skill_manage install` pointer in prose names a skill that exists.
- **Self-test harness execution** — via `run-self-tests.py`.
- **Mutation self-tests** — of the doc-count gate, the secret gate, the rest of the audit, the harness runner, the cron contract check, the router gate and the pointer gate.

### Checks and generators

- **`audit-skills.py`** — validates all skills against repo conventions; exit 0 = clean. Hard-fails if pyyaml is missing or the scan finds <100 skills, so an unrunnable audit can never report clean.
- **`check-links.py`** — broken-link gate: every relative markdown link must resolve (skips URLs, code spans, historical `profiles-export/` snapshots). Run alongside the audit before committing doc changes.
- **`gen-skills-index.py`** — rebuilds `SKILLS-INDEX.md` and every category `DESCRIPTION.md` from live frontmatter (stdlib-only). `--check` reports drift without writing.
- **`gen-code-index.py`** — rebuilds `CODE-INDEX.md` from every code file in the repo: path, kind (script/helper/test/template), language, size, and a one-line purpose extracted from its docstring or header comment. Run after adding, removing or renaming scripts.
- **`gen-references-index.py`** — rebuilds `REFERENCES-INDEX.md` from every skill's `references/*.md`: a flat grep index with each doc's frontmatter description and owning skill. Run after adding or removing reference docs.
- **`regen-dependency-map.py`** — rebuilds `DEPENDENCY.md` from live frontmatter. Safe standalone; `sync-hermes-skills.py`'s step 5.5 shells out to it rather than carrying a second copy.
- **`_index_output.py`** — shared write-guard behind the four generators: blocks an empty-scan overwrite, and provides their `--check` drift mode (compare against disk, exit 1 if stale, write nothing).

### Sync

**`sync-hermes-skills.py`** is the full bidirectional GitHub ↔ local-Hermes sync. A weekly cron job is defined for it in `.hermes/cron/active/`; where it is registered and whether it is paused is recorded once, in README's [Cron Job Authoring](./README.md#cron-job-authoring) section.

- Has `--dry-run`. Always dry-run before a first live run: round 19b caught two latent phantom-action bugs that way (an un-skipped repo `docs/` dir and an orphaned local stub).
- Its delete phase is capped at `MAX_DELETIONS = 25` files per run (override: `--allow-mass-delete`).
- It only treats top-level dirs containing a SKILL.md as skill categories.
- Its pre-push gate runs the FULL health suite (`tools/verify-all.py`, all gates) after regenerating every machine-generated index. It refuses to commit and push when any of them fails or could not run.

### CI

[`.github/workflows/ci.yml`](./.github/workflows/ci.yml) runs three jobs on every push and PR:

1. Runs all 21 health gates.
2. The nine skill pytest suites (comfyui, docx, pdf, powerpoint, xlsx, regex-vs-llm-structured-text, sqlite-queries, evolutionary-ml, ascii-video), with deps from [`test-requirements.txt`](./test-requirements.txt).
3. A dedicated `self-test-harnesses` job that executes every registered `*_verify.py` harness against real duckdb/polars/pyarrow/numpy/pyomo/highspy installs (deps from [`selftest-requirements.txt`](./selftest-requirements.txt)). An upstream engine change then breaks CI instead of quietly rotting the docs.

## Getting Started

```bash
# Find a capability (cheapest path)
grep -i "delta-v" SKILLS-INDEX.md

# Load a skill in Hermes
hermes skill load <category>/<skill-name>

# Run the audit / regenerate generated docs
# (Windows: `py` wherever bare `python` is the Store alias stub, as on the Owner machine.)
py tools/audit-skills.py
py tools/gen-skills-index.py && py tools/regen-dependency-map.py
```

To view a skill's details from inside an agent, call `skill_view(name='<skill-name>')`.

## Maintenance rules (summary)

- Run `py tools/verify-all.py` before every commit (CI re-runs it on every push), and never break the audit.
- Keep every skill `description` ≤59 chars.
- Regenerate after changes:
  - `DEPENDENCY.md` and `SKILLS-INDEX.md` after frontmatter changes
  - `CODE-INDEX.md` after code-file changes
  - `REFERENCES-INDEX.md` after reference-doc changes
- Update `test-requirements.txt` when adding test dependencies to a skill's suite.
- The change log is git history: one `round-NN:` commit per round, whose message says what changed and why. The [audit notes](docs/archive/audit-notes-skills-repo-pass.md) hold the log before 2026-09-14.
- Commit author for automation is `hermes-cronbot <cronbot@hermes.local>`.
- Never commit credentials.

The full convention list is enforced by `tools/audit-skills.py` (see its docstring and the Verification section of README.md).
