# Hermes Skills Repository

A comprehensive collection of **197 Hermes Agent skills** across 23 categories — the second brain for its owner's Hermes Agent environment. See [DESCRIPTION.md](./DESCRIPTION.md) for the task-to-skill...[truncated]

## Table of Contents

- [Overview](#overview)
- [Skills Index (flat, grep-friendly)](./SKILLS-INDEX.md)
- [Code Index (scripts/helpers/tests, flat)](./CODE-INDEX.md)
- [Quick Start](#quick-start)
- [Skill Structure](#skill-structure)
- [Provenance](#provenance)
- [Cron Job Authoring](#cron-job-authoring)
- [Tools](#tools)
- [Verification](#verification)
- [Usage](#usage)
- [License](#license)

## Quick Start

```bash
# Load a skill in Hermes
hermes skill load software-development/mattpocock-code-review

# Or load multiple skills for cronjob automation
hermes skill load autonomous-ai-agents/autonomous-repo-cronjob
hermes skill load github/mattpocock-yeet
hermes skill load software-development/mattpocock-using-git-worktrees

# View a skill's details
skill_view(name='autonomous-repo-cronjob')
```

**Looking for a specific capability?** Grep the flat index first — it's one line per skill and costs nothing:

```bash
grep -i "delta-v" SKILLS-INDEX.md   # or: nicegui, triage, diagram...
# Looking for runnable code (scripts/helpers/tests) instead?
grep -i "raster\|token bridge" CODE-INDEX.md
```

**New to the repo?** Start with the [Skill Structure](#skill-structure) and [Verification](#verification) sections below (they define every convention in this second brain), then the [Cron Job Authoring](#cron-job-authoring) section for the two-agent automation pattern, or browse the [Dependency Map](./DEPENDENCY.md) for skill relationships.

## Overview

This repository serves as a centralized database of all **197 Hermes Agent skills**, organized by category. Skills are reusable procedures and workflows that extend Hermes Agent's capabilities. All skills follow the standard `SKILL.md` format with consistent frontmatter, section headers, and `related_skills` cross-references (491 cross-references mapped across 197 skills, 2 with no outbound `related_skills`). See [audit notes](docs/archive/audit-notes-skills-repo-pass.md) for the full audit details and [DEPENDENCY.md](./DEPENDENCY.md) for the full relationship map.

### Source Profiles

Skills were imported from three Hermes profiles:
1. **Default profile** (`~/.hermes/skills/`) — system-level skills
2. **the-skill-maker** (`~/.hermes/profiles/the-skill-maker/skills/`) — primary working profile
3. **the-memory-controller** (`~/.hermes/profiles/the-memory-controller/skills/`) — memory management profile

When a skill existed in multiple profiles, the version from the highest-priority profile was used.

> ⚠️ **Known remaining issues** — see [audit notes](docs/archive/audit-notes-skills-repo-pass.md) for the full audit.

### Categories

| Category | Description | Skill Count |
|----------|-------------|-------------|
| [apple/](./apple/) | Apple platform integrations | 4 |
| [autonomous-ai-agents/](./autonomous-ai-agents/) | Multi-agent orchestration and delegation | 12 |
| [communication/](./communication/) | Decision-brief formats (1-3-1 rule) | 1 |
| [creative/](./creative/) | Creative content generation and design | 28 |
| [data-science/](./data-science/) | Data science workflows and tools | 15 |
| [devops/](./devops/) | Infrastructure, containers, and deployment + zero-install SSH tunnels (Pinggy) | 8 |
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
| [research/](./research/) | Research and content discovery | 16 |
| [security/](./security/) | Security review and auditing | 3 |
| [smart-home/](./smart-home/) | Smart home device control | 1 |
| [social-media/](./social-media/) | Social media content | 1 |
| [software-development/](./software-development/) | Development tools and workflows | 52 |
| [web-development/](./web-development/) | Web/API client derivation (HAR-based) + versioned static-site publishing | 3 |

**Total: 197 skills across 23 categories** — counts below are regenerated from live frontmatter; keep them in sync via `python tools/gen-skills-index.py` and the audit.

### Skill Catalog

All 197 skills organized by category:

#### Apple

- [`apple-notes`](./apple/apple-notes) — Manage Apple Notes via memo CLI: create, search, edit.
- [`apple-reminders`](./apple/apple-reminders) — Apple Reminders via remindctl: add, list, complete.
- [`findmy`](./apple/findmy) — Track Apple devices/AirTags via FindMy.app on macOS.
- [`imessage`](./apple/imessage) — Send and receive iMessages/SMS via the imsg CLI on macOS.
#### Autonomous AI Agents

- [`autonomous-repo-cronjob`](./autonomous-ai-agents/autonomous-repo-cronjob) — Write self-contained cronjob prompts for existing repos.
- [`claude-code`](./autonomous-ai-agents/claude-code) — Delegate coding to Claude Code CLI (features, PRs).
- [`codex`](./autonomous-ai-agents/codex) — Delegate coding to OpenAI Codex CLI (features, PRs).
- [`computer-use`](./autonomous-ai-agents/computer-use) — Drive the desktop in the background without stealing focus.
- [`cron-config-authoring`](./autonomous-ai-agents/cron-config-authoring) — Author cronjob JSON configs with structured skills.
- [`cron-job-authoring`](./autonomous-ai-agents/cron-job-authoring) — Author autonomous cron prompts with guardrails.
- [`hermes-agent`](./autonomous-ai-agents/hermes-agent) — Use, configure, theme, extend, orchestrate Hermes Agent.
- [`mattpocock-resolving-merge-conflicts`](./autonomous-ai-agents/mattpocock-resolving-merge-conflicts) — Resolve git merge conflicts by tracing each side's intent.
- [`merge-reconciler`](./autonomous-ai-agents/merge-reconciler) — Neutral third-party resolution of agent merge conflicts.
- [`opencode`](./autonomous-ai-agents/opencode) — Delegate coding to OpenCode CLI (features, PR review).
#### Communication

- [`one-three-one-rule`](./communication/one-three-one-rule) — 1-3-1 decision briefs: problem, three options, one pick.
#### Creative

- [`architecture-diagram`](./creative/architecture-diagram) — Dark-themed SVG architecture/cloud/infra diagrams as HTML.
- [`ascii-art`](./creative/ascii-art) — ASCII art: pyfiglet, cowsay, boxes, image-to-ascii.
- [`ascii-video`](./creative/ascii-video) — ASCII video: convert video/audio to colored ASCII MP4/GIF.
- [`baoyu-infographic`](./creative/baoyu-infographic) — Infographics: 21 layouts x 21 styles (信息图, 可视化).
- [`claude-design`](./creative/claude-design) — Design one-off HTML artifacts (landing, deck, prototype).
- [`comfyui`](./creative/comfyui) — Generate images, video, and audio via diffusion workflows.
- [`design-md`](./creative/design-md) — Author/validate/export Google's DESIGN.md token spec files.
- [`design-taste-frontend`](./creative/design-taste-frontend) — Anti-slop frontend skill: brief-inferred design direction.
- [`diagram-design`](./creative/diagram-design) — Create 39 diagram types as standalone HTML/SVG/PNG files.
- [`excalidraw`](./creative/excalidraw) — Hand-drawn Excalidraw JSON diagrams (arch, flow, seq).
- [`full-output-enforcement`](./creative/full-output-enforcement) — Enforce complete output; ban placeholder patterns.
- [`humanizer`](./creative/humanizer) — Humanize text: strip AI-isms and add real voice.
- [`manim-video`](./creative/manim-video) — Manim CE animations: 3Blue1Brown math/algo videos.
- [`mattpocock-prototype`](./creative/mattpocock-prototype) — Build a throwaway prototype to answer a design question.
- [`p5js`](./creative/p5js) — p5.js sketches: gen art, shaders, interactive, 3D.
- [`popular-web-designs`](./creative/popular-web-designs) — 54 real design systems as HTML/CSS.
- [`pretext`](./creative/pretext) — Build creative browser demos with DOM-free text layout.
- [`pygame`](./creative/pygame) — Use when building or testing pygame/SDL games.
- [`redesign-existing-projects`](./creative/redesign-existing-projects) — Audit-first redesign of existing sites to premium quality.
- [`sketch`](./creative/sketch) — Throwaway HTML mockups: 2-3 design variants to compare.
- [`songwriting-and-ai-music`](./creative/songwriting-and-ai-music) — Songwriting craft and Suno AI music prompts.
- [`static-site-seo`](./creative/static-site-seo) — Static site SEO: JSON-LD, meta tags, analytics, CSP.
- [`touchdesigner-mcp`](./creative/touchdesigner-mcp) — Control TouchDesigner via twozero MCP.
#### Data Science

- [`astro-toolkit-selection`](./data-science/astro-toolkit-selection) — Choose astrodynamics tools: brahe, nyx, OpenSCvx, skyfield.
- [`bit-identity-float-pipelines`](./data-science/bit-identity-float-pipelines) — Verify correctness via exact float hashes / bit-identity.
- [`build-systems-data`](./data-science/build-systems-data) — Data build systems: orchestration, versioning, CSV at scale.
- [`duckdb-querying`](./data-science/duckdb-querying) — Query CSV/Parquet/S3 data ad-hoc via DuckDB Friendly SQL.
- [`economicspace-pipeline`](./data-science/economicspace-pipeline) — Use on economicspace (asteroid-mining pipeline).
- [`evolutionary-ml`](./data-science/evolutionary-ml) — Evolutionary ML: GA, NEAT, tournaments, parallel eval.
- [`jupyter-notebook`](./data-science/jupyter-notebook) — Iterative Python via live Jupyter kernel (hamelnb).
- [`model-export-deploy`](./data-science/model-export-deploy) — Model export: ONNX, TorchScript, HDF5, NumPy, JSON.
- [`orbital-mechanics-data`](./data-science/orbital-mechanics-data) — Orbital mechanics: delta-v, transfers, rendezvous, KSP/KRPC.
- [`python-data-science`](./data-science/python-data-science) — Python DS: EDA, cleaning, modeling, eval, viz.
- [`regex-vs-llm-structured-text`](./data-science/regex-vs-llm-structured-text) — Regex-first parsing; LLM only for flagged edge cases.
- [`space-data-pipelines`](./data-science/space-data-pipelines) — Build space/astro data pipelines with verified API gotchas.
- [`space-mission-computation-paradigms`](./data-science/space-mission-computation-paradigms) — Choose trajectory method: closed-form vs propagation etc.
- [`sql-for-data`](./data-science/sql-for-data) — SQL for data: queries, joins, windows, aggregation.
#### DevOps

- [`docker-containers`](./devops/docker-containers) — Build and debug Docker containers and Compose stacks.
- [`rest-api-client`](./devops/rest-api-client) — Call REST APIs: auth, pagination, rate limits, errors.
- [`sdlc-review`](./devops/sdlc-review) — Review Kanban handoffs and route verified outcomes.
- [`sqlite-queries`](./devops/sqlite-queries) — Query, inspect, and export SQLite databases.
- [`ssh-remote`](./devops/ssh-remote) — Commands and file transfer on remote machines over SSH.
- [`pinggy-tunnel`](./devops/pinggy-tunnel) — Zero-install localhost tunnels over SSH via Pinggy (webhook/MCP/demo recipes).
- [`watchers`](./devops/watchers) — Poll RSS, JSON APIs, and GitHub with watermark dedup.
- [`wizard`](./devops/wizard) — Bash wizard walking a human through manual-only steps.
#### Doc Co-authoring

- [`doc-coauthoring`](./doc-coauthoring) — Guide structured documentation co-authoring workflows.
#### Dogfood

- [`adversarial-ux-test`](./dogfood/adversarial-ux-test) — Roleplay a hostile user to find and triage UX pain points.
#### Email

- [`email-inbox-triage`](./email/email-inbox-triage) — Triage an inbox: prioritize threads, draft replies safely.
- [`himalaya`](./email/himalaya) — Himalaya CLI: IMAP/SMTP email from terminal.
#### Frontend Design

- [`frontend-design`](./frontend-design) — Distinctive visual design for AI-generated UI.
- [`nicegui-app-builder`](./frontend-design/nicegui-app-builder) — Build Python reactive web/desktop apps with NiceGUI.
#### GitHub

- [`codebase-inspection`](./github/codebase-inspection) — Inspect codebases w/ pygount: LOC, languages, ratios.
- [`github-auth`](./github/github-auth) — GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login.
- [`github-code-review`](./github/github-code-review) — Review PRs: diffs, inline comments via gh or REST.
- [`github-issue-to-pr`](./github/github-issue-to-pr) — Carry a GitHub issue to a verified PR with honest CI state.
- [`github-issues`](./github/github-issues) — Create, triage, label, assign GitHub issues via gh or REST.
- [`github-pr-workflow`](./github/github-pr-workflow) — GitHub PR lifecycle: branch, commit, open, CI, merge.
- [`github-repo-management`](./github/github-repo-management) — Clone/create/fork repos; manage remotes, releases.
- [`issue-triage-state-machine`](./github/issue-triage-state-machine) — Triage issues/PRs: categorise, verify, grill, agent briefs.
- [`mattpocock-code-review`](./github/mattpocock-code-review) — Two-axis code review: Standards and Spec via sub-agents.
- [`mattpocock-finishing-a-development-branch`](./github/mattpocock-finishing-a-development-branch) — Complete git branches with merge or PR options.
- [`mattpocock-gh-fix-ci`](./github/mattpocock-gh-fix-ci) — Debug failing GitHub Actions checks on a PR.
- [`mattpocock-yeet`](./github/mattpocock-yeet) — Git workflow: stage, commit, push, open PR.
#### HuggingFace Trackio

- [`huggingface-trackio`](./huggingface-trackio) — Log and retrieve ML training experiments with Trackio.
#### MCP

- [`fastmcp`](./mcp/fastmcp) — Build, test, and deploy Python MCP servers.
- [`mcporter`](./mcp/mcporter) — List, auth, and call MCP servers/tools from the terminal (npx).
#### Media

- [`gif-search`](./media/gif-search) — Search/download GIFs from Tenor via curl + jq.
- [`songsee`](./media/songsee) — Audio spectrograms and feature extraction via CLI.
- [`youtube-content`](./media/youtube-content) — YouTube transcripts to summaries, threads, blogs.
#### MLOps

- [`evaluating-llms-harness`](./mlops/evaluation/evaluating-llms-harness) — lm-eval-harness: benchmark LLMs (MMLU, GSM8K, etc.).
- [`huggingface-hub`](./mlops/huggingface-hub) — HuggingFace hf CLI: search/download/upload models.
- [`llama-cpp`](./mlops/inference/llama-cpp) — llama.cpp local GGUF inference + HF Hub model discovery.
- [`serving-llms-vllm`](./mlops/inference/serving-llms-vllm) — vLLM: LLM serving, OpenAI API, quantization.
- [`weights-and-biases`](./mlops/evaluation/weights-and-biases) — W&B: log ML experiments, sweeps, registry, dashboards.

#### Note Taking

- [`knowledge-ops`](./note-taking/knowledge-ops) — KB ops: ingest, dedupe, sync, retrieve across stores.
- [`obsidian`](./note-taking/obsidian) — Read, search, create, and edit notes in the Obsidian vault.
#### Productivity

- [`airtable`](./productivity/airtable) — Airtable REST API via curl. Records CRUD, filters, upserts.
- [`box`](./productivity/box) — Box manages cloud files, sharing, search, and metadata.
- [`decision-questionnaire`](./productivity/decision-questionnaire) — Turn an unanswerable decision into a questionnaire doc.
- [`document-to-action-items`](./productivity/document-to-action-items) — Extract cited obligations, deadlines, tasks from documents.
- [`docx`](./productivity/docx) — Create, read, edit, template, and review Word .docx files.
- [`google-workspace`](./productivity/google-workspace) — Gmail, Calendar, Drive, Docs, Sheets via gws CLI or Python.
- [`maps`](./productivity/maps) — Geocode, POIs, routes, timezones via OpenStreetMap/OSRM.
- [`mattpocock-handoff`](./productivity/mattpocock-handoff) — Compact conversation into a handoff doc for another agent.
- [`meeting-action-items`](./productivity/meeting-action-items) — Turn meeting notes into cited decisions, owners, tickets.
- [`nano-pdf`](./productivity/nano-pdf) — Edit text in existing PDFs via natural-language prompts.
- [`notion`](./productivity/notion) — Notion API + ntn CLI: pages, databases, markdown, Workers.
- [`ocr-and-documents`](./productivity/ocr-and-documents) — Extract text from PDFs/scans (pymupdf, marker-pdf).
- [`pdf`](./productivity/pdf) — Create, read, merge, fill, and secure PDF files.
- [`powerpoint`](./productivity/powerpoint) — Create, read, edit .pptx decks with python-pptx.
- [`product-price-monitor`](./productivity/product-price-monitor) — Watch product, flight, or listing prices; alert on target.
- [`session-librarian`](./productivity/session-librarian) — Organize sessions by prompt: find, rename, archive, prune.
- [`teach`](./productivity/teach) — Teach a topic across sessions via mission and lessons.
- [`teams-meeting-pipeline`](./productivity/teams-meeting-pipeline) — Teams meeting summaries, job replay, Graph subscriptions.
- [`website-audit`](./productivity/website-audit) — Audit websites/codebases into .docx reports; read-only.
- [`weekly-review-planning`](./productivity/weekly-review-planning) — Weekly reset: commitments, stalled work, next-week plan.
- [`xlsx`](./productivity/xlsx) — Create, read, edit Excel .xlsx workbooks and CSVs.
#### Research

- [`arxiv`](./research/arxiv) — Search arXiv papers by keyword, author, category, or ID.
- [`bioinformatics`](./research/bioinformatics) — Gateway to 400+ genomics and computational biology skills.
- [`blocked-page-recovery`](./research/blocked-page-recovery) — Recover blocked/paywalled/WAF'd pages via fallbacks.
- [`blogwatcher`](./research/blogwatcher) — Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool.
- [`competitor-news-monitor`](./research/competitor-news-monitor) — Watch named companies for material news; cited digests.
- [`gget`](./research/gget) — Quick bioinformatics lookups (Ensembl, BLAST) via gget CLI/Python + evidence logs.
- [`grounded-citations`](./research/grounded-citations) — Ground answers and documents in cited, verifiable sources.
- [`llm-wiki`](./research/llm-wiki) — Karpathy's LLM Wiki: build/query interlinked markdown KB.
- [`literature-review`](./research/literature-review) — Plan, screen, synthesize and cite technical literature.
- [`mattpocock-research`](./research/mattpocock-research) — Research a question against primary sources.
- [`parallel-cli`](./research/parallel-cli) — Agent-native web search, deep research, and enrichment.
- [`pubmed-database`](./research/pubmed-database) — PubMed/NCBI E-utilities: MeSH queries, PMID lookup, API-backed search logs.
- [`qmd`](./research/qmd) — Hybrid local search over notes, docs, and transcripts.
- [`research-paper-writing`](./research/research-paper-writing) — Write ML papers for NeurIPS/ICML/ICLR: design→submit.
- [`scrapling`](./research/scrapling) — Scrape sites with stealth browsing and Cloudflare bypass.
- [`scholar-evaluation`](./research/scholar-evaluation) — Scholarly work rubric: papers, proposals, evidence quality.
#### Security

- [`mattpocock-security-review`](./security/mattpocock-security-review) — Review code for security vulnerabilities by language.
- [`oss-forensics`](./security/oss-forensics) — GitHub supply-chain forensics: recovery, IOCs, reporting.
- [`semgrep-rule-creator`](./security/semgrep-rule-creator) — Create tested Semgrep rules with taint-mode support.
#### Smart Home

- [`openhue`](./smart-home/openhue) — Control Philips Hue lights, scenes, rooms via OpenHue CLI.
#### Social Media

- [`xurl`](./social-media/xurl) — X/Twitter via xurl CLI: post search, posting, DM, media.
#### Software Development

- [`ast-grep`](./software-development/ast-grep) — AST-aware structural code search and rewrite via ast-grep.
- [`brainstorming`](./software-development/brainstorming) — Triage as spike/bounded/architectural; approve first.
- [`codebase-onboarding`](./software-development/codebase-onboarding) — Onboard to a new repo: arch map + starter AGENTS.md.
- [`cli-tool-craft`](./software-development/cli-tool-craft) — CLI tools: subcommands, config validation, env substitution.
- [`code-quality-signal`](./software-development/code-quality-signal) — Score Python repos on 5 ungameable structural metrics.
- [`code-wiki`](./software-development/code-wiki) — Generate wiki docs + Mermaid diagrams for any codebase.
- [`conversation-to-spec`](./software-development/conversation-to-spec) — Turn a conversation into a publishable spec.
- [`dogfood`](./software-development/dogfood) — Exploratory QA of web apps: find bugs, evidence, reports.
- [`generating-python-installer`](./software-development/generating-python-installer) — Nuitka + Inno Setup: smallest, fastest Windows installers.
- [`github`](./software-development/github) — GitHub via gh CLI: PRs, issues, reviews, repos, auth.
- [`grilling-interview`](./software-development/grilling-interview) — Stress-test a plan by interviewing in design-tree rounds.
- [`hermes-agent-skill-authoring`](./software-development/hermes-agent-skill-authoring) — Author in-repo SKILL.md files: frontmatter and structure.
- [`inspecting-hermes-desktop-dom`](./software-development/inspecting-hermes-desktop-dom) — Read the live Hermes desktop DOM/CSS over CDP.
- [`living-docs-governance`](./software-development/living-docs-governance) — Docs governance: constitution, map, status, history roles.
- [`mattpocock-ask-if-underspecified`](./software-development/mattpocock-ask-if-underspecified) — Ask clarifying questions when a request is ambiguous.
- [`mattpocock-codebase-design`](./software-development/mattpocock-codebase-design) — Design deep modules with small interfaces.
- [`mattpocock-diagnosing-bugs`](./software-development/mattpocock-diagnosing-bugs) — Diagnose hard bugs via tight feedback loops and bisection.
- [`mattpocock-domain-modeling`](./software-development/mattpocock-domain-modeling) — Sharpen domain terms and update CONTEXT.md and ADRs inline.
- [`mattpocock-evidence-driven`](./software-development/mattpocock-evidence-driven) — Validate code changes with evidence and testing gates.
- [`mattpocock-improve-codebase-architecture`](./software-development/mattpocock-improve-codebase-architecture) — Survey code for module deepening, fix opportunities.
- [`mattpocock-multi-agent-code-review`](./software-development/mattpocock-multi-agent-code-review) — Multi-agent PR review: bug-hunter, security, contracts.
- [`mattpocock-spec-driven-development`](./software-development/mattpocock-spec-driven-development) — Spec-driven development with planning and quality gates.
- [`mattpocock-subagent-driven-development`](./software-development/mattpocock-subagent-driven-development) — Dispatch fresh subagents per task with task review.
- [`mattpocock-tdd`](./software-development/mattpocock-tdd) — TDD red-green-refactor at pre-agreed seams.
- [`mattpocock-to-tickets`](./software-development/mattpocock-to-tickets) — Break a plan or spec into tracer-bullet tickets with edges.
- [`mattpocock-using-git-worktrees`](./software-development/mattpocock-using-git-worktrees) — Set up isolated git worktrees for feature work.
- [`mattpocock-writing-for-agents`](./software-development/mattpocock-writing-for-agents) — Write docs agents can consume: skills, AGENTS.md, specs.
- [`modern-python-tooling`](./software-development/modern-python-tooling) — Set up Python projects with uv, ruff, ty, PEP 723.
- [`node-inspect-debugger`](./software-development/node-inspect-debugger) — Debug Node.js via --inspect + Chrome DevTools Protocol CLI.
- [`plan`](./software-development/plan) — Write a markdown plan to .hermes/plans/; no execution.
- [`property-based-testing`](./software-development/property-based-testing) — Hypothesis property tests: roundtrip, oracle, invariant.
- [`python-craft`](./software-development/python-craft) — Python craft: style, typing, patterns, testing, packaging.
- [`python-debugpy`](./software-development/python-debugpy) — Debug Python: pdb REPL + debugpy remote (DAP).
- [`receiving-code-review`](./software-development/receiving-code-review) — Verify review feedback against the codebase before acting.
- [`requesting-code-review`](./software-development/requesting-code-review) — Pre-commit review: security scan, quality gates, auto-fix.
- [`rest-graphql-debug`](./software-development/rest-graphql-debug) — Debug REST and GraphQL APIs: auth, schemas, repro.
- [`retro`](./software-development/retro) — Retrospective on a session proposing environment fixes.
- [`simplify-code`](./software-development/simplify-code) — Parallel 4-agent cleanup of recent code changes.
- [`skill-flow-router`](./software-development/skill-flow-router) — Route any task through the right skill flow in this brain.
- [`spike`](./software-development/spike) — Throwaway experiments to validate an idea before build.
- [`streamlit-dashboards`](./software-development/streamlit-dashboards) — Streamlit dashboards: layout, caching, charts, state.
- [`systematic-debugging`](./software-development/systematic-debugging) — 4-phase root cause debugging: understand before fixing.
- [`test-driven-development`](./software-development/test-driven-development) — TDD: enforce RED-GREEN-REFACTOR, tests before code.
- [`test-infra-ml`](./software-development/test-infra-ml) — Testing ML systems: sims, EAs, tournaments, checkpoints.
- [`windows-desktop-e2e`](./software-development/windows-desktop-e2e) — Windows desktop E2E testing with pywinauto + UI Automation.- [`verification-before-completion`](./software-development/verification-before-completion) — No completion claims without fresh verification evidence.
- [`verification-culture`](./software-development/verification-culture) — Doc-driven verification: backlog, audits, regression.
- [`wayfinder-map-planning`](./software-development/wayfinder-map-planning) — Plan multi-session work as a map of decision tickets.
#### Web Development

- [`har-derived-api-client`](./web-development/har-derived-api-client) — Record a site's XHR into a HAR, derive an HTTP client.
- [`publish-site`](./web-development/publish-site) — Versioned deploys to GitHub/Cloudflare/Netlify Pages with rollback + live verification.
- [`static-site-patterns`](./web-development/static-site-patterns) — Static-site perf/UX: PWA installability + Core Web Vitals.


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

## Provenance

Skills come from three sources (see [audit notes](docs/archive/audit-notes-skills-repo-pass.md) for the full history):

1. **Imported skills** — copied in from live Hermes profiles (`default`, `the-skill-maker`, `the-memory-controller`) during the initial import; where a skill existed in multiple profiles, the highest-priority profile's version was kept.
2. **Pre-existing repo skills** — authored directly in this repository (e.g. the 22+ `mattpocock-*` methodology skills, devops and top-level category skills).
3. **Research-harvest ports** — added across successive starred-repo deep-dive rounds (145 → 162 → 166 → 167 → 172 → 173 → 174 → 177 → 180 → 181 → 183 → 184 → 185 → 190 → 196 → 197), including hub installs (`hermes skills install official/...`) and MIT-licensed external ports with their licenses carried in frontmatter.

The per-skill origin is recorded in [audit notes](docs/archive/audit-notes-skills-repo-pass.md) round-by-round; the live set of record is always `SKILLS-INDEX.md` (regenerated from frontmatter).

## Cron Job Authoring

Skills for writing self-contained, autonomous cronjob prompts that run without session context. The core pattern is documented in `autonomous-repo-cronjob` (for repo-automation tasks) and `cron-job-authoring` (for general scheduling).

This repository also includes a ready-to-use **cronjob registry** at [`.hermes/cron/`](./.hermes/cron/) with templates and active job definitions:

- **`.hermes/cron/templates/`** — Prompt and script templates for the two most common patterns
- **`.hermes/cron/active/`** — Active cronjob definitions (JSON config) ready to be loaded via `cronjob()`
- **`.hermes/cron/archive/`** — Deprecated or old cronjob definitions kept for reference

> **Registration status (verified 2026-09-08).** These are job *definitions*, not running jobs. The live Hermes scheduler (`%LOCALAPPDATA%/hermes/cron/jobs.json`) currently has one registered job — `aspirecures-weekly-research`, and it is **disabled** — so `skill-audit` and `sync-hermes-skills` have never executed. Load a definition with the `cronjob()` tool to actually schedule it. Until then, run the checks yourself: `py tools/verify-all.py`.

### Core Skills

| Skill | Purpose | Key References |
|-------|---------|-----------------|
| [`autonomous-repo-cronjob`](./autonomous-ai-agents/autonomous-repo-cronjob/SKILL.md) | Write self-contained cronjob prompts for repos with existing CI pipelines. Embeds the repo's guardrails, dedup logic, and two-agent split (preparer + commit agent). | [prompt-template](./autonomous-ai-agents/autonomous-repo-cronjob/references/prompt-template.md), [drafting-guide](./autonomous-ai-agents/autonomous-repo-cronjob/references/drafting-guide.md), [agent-vs-script-checklist](./autonomous-ai-agents/autonomous-repo-cronjob/references/agent-vs-script-checklist.md), [two-agent-architecture](./autonomous-ai-agents/autonomous-repo-cronjob/references/two-agent-architecture.md) |
| [`cron-job-authoring`](./autonomous-ai-agents/cron-job-authoring/SKILL.md) | Author autonomous cron prompts with guardrails. Covers `cronjob()` tool usage, schedule formats, delivery targets, and self-contained prompt patterns. | — |
| [`cron-config-authoring`](./autonomous-ai-agents/cron-config-authoring/SKILL.md) | Author cronjob JSON configs: structured skills object with per-skill phase + rationale, threshold key alignment with script output, skill reference path resolution, model pinning, and approval-mode configuration. | [cronjob-config-patterns](./autonomous-ai-agents/cron-config-authoring/references/cronjob-config-patterns.md) |
| [`product-price-monitor`](./productivity/product-price-monitor/SKILL.md) | Price/availability monitoring via cronjob ticks. Uses `cronjob(action="create")` with normalized price alerts. | — |
| [`competitor-news-monitor`](./research/competitor-news-monitor/SKILL.md) | Company-focused news tracking via cronjob. Loads `blogwatcher` and `parallel-cli` for enrichment. | — |
| [`apple-reminders`](./apple/apple-reminders/SKILL.md) | Scheduled reminder checks via cronjob. Loads `cron-job-authoring` for automation patterns. | — |
| [`findmy`](./apple/findmy/SKILL.md) | Ongoing AirTag/device tracking via cronjob. Loads `imessage` for notifications and `cron-job-authoring` for scheduling. | — |

### Related Skills (via `related_skills` or `skill_view` calls)

| Skill | Cronjob Connection |
|-------|--------------------|
| [`hermes-agent`](./autonomous-ai-agents/hermes-agent/SKILL.md) | References `autonomous-repo-cronjob` in related_skills |
| [`mattpocock-yeet`](./github/mattpocock-yeet/SKILL.md) | References `autonomous-repo-cronjob` in related_skills |
| [`mattpocock-using-git-worktrees`](./software-development/mattpocock-using-git-worktrees/SKILL.md) | References `autonomous-repo-cronjob` in related_skills |
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

## Tools

This repository includes Python scripts in the `tools/` directory that automate repository maintenance:

| Tool | Purpose | Cron Integration |
|------|---------|------------------|
| [`verify-all.py`](./tools/verify-all.py) | **Start here.** Runs every gate in one shot: audit, links, index drift (all four generated indexes), cron validators, and README/DESCRIPTION count consistency. Exit 0 = all 9 gates pass | Manual; run before any commit |
| [`audit-skills.py`](./tools/audit-skills.py) | Validates all 197 skills: YAML frontmatter, description length, `related_skills` resolution, body section presence, `skill_view()` call sync, category `DESCRIPTION.md` checks | Defined for Sun 3 AM in `skill-audit.json` — **not registered**; run manually |
| [`sync-hermes-skills.py`](./tools/sync-hermes-skills.py) | Bidirectional sync between GitHub repo and local Hermes env: git pull, skill/memories/profiles sync, DEPENDENCY.md regeneration, audit, git push | Defined for Sun 2 AM in `sync-hermes-skills.json` — **not registered**; run manually |



| [`_index_output.py`](./tools/_index_output.py) | Shared write-guard for the generators: refuses to overwrite an index when the scan came back suspiciously empty, and implements their `--check` (compare-don't-write) drift mode | Imported by the four generators |
| [`check-links.py`](./tools/check-links.py) | Broken-link gate: verifies every relative markdown link in the repo resolves (skips URLs, code spans, historical profiles-export snapshots); exit 1 on any broken link | After doc edits; pairs with audit as a pre-commit pair |
| [`gen-skills-index.py`](./tools/gen-skills-index.py) | Rebuilds SKILLS-INDEX.md (flat one-line-per-skill index, the cheapest lookup path in the repo); stdlib-only | After adding/removing/renaming skills |
| [`gen-code-index.py`](./tools/gen-code-index.py) | Rebuilds CODE-INDEX.md: every script/helper/test/template with kind, language, size, and a one-line purpose from its docstring/header comment; stdlib-only | After adding/removing/renaming code files |
| [`regen-dependency-map.py`](./tools/regen-dependency-map.py) | Standalone DEPENDENCY.md regenerator (same format as the sync script's built-in map): scans all SKILL.md frontmatter, rebuilds hub/standalone tables and xref validation line | Manual / after bulk skill additions |
| [`validate-skill-refs.py`](./.hermes/cron/validate-skill-refs.py) | Validates all skill references in cronjob JSON configs resolve to existing in-repo skill directories | Pre-flight check before scheduling any cronjob |
| [`validate-cronjobs.py`](./.hermes/cron/validate-cronjobs.py) | Comprehensive cronjob JSON validation: structural schema, skill ref resolution, threshold key alignment, no_agent consistency, enabled_toolsets correctness | Run before committing any cronjob config change |

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
py tools/verify-all.py      # 9 gates; exit 0 = all pass
```

Every tool fails **closed**: a wrong interpreter, a missing pyyaml, an unreadable file, a scan that
comes back empty, or an index that has drifted all produce a non-zero exit and a `[FATAL]`/`[DRIFT]`
line -- never a quiet "clean" result. Individually:

```bash
# Run the audit (exit 0 = within thresholds, exit 1 = threshold breached or scan failed)
py tools/audit-skills.py         # Windows: use `py`. Bare `python`/`python3` are
                                 # Microsoft Store alias stubs -- they exit 49 without
                                 # running the script. Linux/macOS: python3 tools/audit-skills.py

# .hermes/cron/active/skill-audit.json defines a weekly (Sun 3 AM, no_agent=true)
# job for this -- but that definition is not registered with the scheduler yet,
# so today the audit only runs when you (or verify-all.py) run it.
```

The audit script is referenced by `.hermes/cron/active/skill-audit.json` — a weekly cronjob definition that would emit a JSON report via the cronjob system's `deliver: origin` target. That definition is **not currently registered** with the live scheduler (see the registration status note in [Cron Job Authoring](#cron-job-authoring)), so the audit runs on demand today.

### CI (GitHub Actions)

[`.github/workflows/ci.yml`](./.github/workflows/ci.yml) makes "the repo passes its own gates" a property of the remote, not just local discipline: every push to `main` and every PR runs two jobs — **Health gates** (`pip install pyyaml`, then `python tools/verify-all.py`) and **Skill test suites**, which [`tools/run-skill-tests.py`](./tools/run-skill-tests.py) discovers at runtime (every `<skill>/tests/` dir with a pytest file is picked up automatically — no workflow edit needed when a new suite ships). Seven suites currently: comfyui 117 / docx 29 / pdf 21 / powerpoint 21 / xlsx 12 / regex-vs-llm-structured-text 14 / sqlite-queries 20 (counted 2026-09-09; the sqlite suite is stdlib-only and its four `sqlite3`-CLI tests skip on hosts without the binary, so it adds zero new dependencies). Test deps for the library-backed suites come from [`test-requirements.txt`](./test-requirements.txt) — a single source of truth created by running all suites in a clean venv until green (verified 2026-09-09: all pass, pure wheels only, no poppler binary needed because `pypdfium2` covers rasterization). When you add test dependencies to any skill's suite, update that file too.

### Live Invariants

✅ items are checked by `tools/audit-skills.py` / `tools/check-links.py` on every audit run; the threshold-gated subset (a non-zero count fails the run) is `broken_refs`, `yaml_errors`, `long_descriptions`, `duplicate_skills`, `missing_body_sections`, `temps_scripts`. 📎 items are conventions no tool enforces — hold them by hand.

- ✅ All 197 skills have valid frontmatter (`name`, `version`, `author`, `platforms`, `metadata.hermes`) and parse without errors
- ✅ No duplicate skill names; no empty skill directories
- ✅ All `related_skills` references resolve to existing in-repo skills — 491 cross-references across 197 skills (see [DEPENDENCY.md](./DEPENDENCY.md))
- ✅ All descriptions ≤59 chars, double-quoted YAML strings
- ✅ Every skill has a body section (`## What This Skill Does` or an audit-recognized alternative) and standard header capitalization
- ✅ Every multi-skill category directory has a `DESCRIPTION.md` (all 23 do)
- 🔒 Line endings normalized via `.gitattributes` (`text=auto`) — CRLF in working tree, LF in git storage. Enforced by git itself at checkout/commit, not by the audit
- 📎 *Convention, not a gate:* repo-authored files end with a newline. Two exceptions are kept byte-for-byte as their source emits them: the vendored conference templates under `research/research-paper-writing/templates/`, and the sync-owned `memories/` + `profile/` files. Trailing whitespace is **not** stripped — in markdown a double trailing space is a hard line break, so a blanket strip would silently reflow docs.
- ✅ Broken-link gate: every relative markdown link resolves (`tools/check-links.py`, skips URLs/code spans/`profiles-export/` snapshots)

One-off historical fixes (duplicate removals, ref repairs, header renames, sync setup) are logged round-by-round in [audit notes](docs/archive/audit-notes-skills-repo-pass.md).

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
