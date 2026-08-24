# Hermes Skills

A curated collection of **114 skills** for [Hermes Agent](https://hermes-agent.nousresearch.com/) — procedural knowledge, workflows, and tooling reference.

## Quick Start

Skills are picked up automatically by placing a `SKILL.md` file (with YAML frontmatter) in the right location. Load one in chat with `skill_view(name)`, or let Hermes auto-route by description.

## Categories

### Apple (4 skills)

- **`apple-notes`** — Manage Apple Notes via memo CLI: create, search, edit.
- **`apple-reminders`** — Apple Reminders via remindctl: add, list, complete.
- **`findmy`** — Track Apple devices/AirTags via FindMy.app on macOS.
- **`imessage`** — Send and receive iMessages/SMS via the imsg CLI on macOS.

### Autonomous Ai Agents (9 skills)

- **`autonomous-repo-cronjob`** — Write self-contained cronjob prompts for existing repos.
- **`claude-code`** — Delegate coding to Claude Code CLI (features, PRs).
- **`codex`** — Delegate coding to OpenAI Codex CLI (features, PRs).
- **`computer-use`** — Drive the desktop in the background without stealing focus.
- **`hermes-agent`** — Use, configure, theme, extend, and orchestrate Hermes Agent.
- **`mattpocock-resolving-merge-conflicts`** — Resolve git merge conflicts by tracing each side's intent.
- **`mattpocock-subagent-driven-development`** — Dispatch fresh subagents per task with review.
- **`merge-reconciler`** — Neutral third-party resolution of agent merge conflicts.
- **`opencode`** — Delegate coding to OpenCode CLI (features, PR review).

### Creative (17 skills)

- **`architecture-diagram`** — Dark-themed SVG architecture/cloud/infra diagrams as HTML.
- **`ascii-art`** — ASCII art: pyfiglet, cowsay, boxes, image-to-ascii.
- **`ascii-video`** — ASCII video: convert video/audio to colored ASCII MP4/GIF.
- **`baoyu-infographic`** — Infographics: 21 layouts x 21 styles (信息图, 可视化).
- **`claude-design`** — Design one-off HTML artifacts (landing, deck, prototype).
- **`comfyui`** — Generate images, video, and audio via diffusion workflows.
- **`design-md`** — Author/validate/export Google's DESIGN.md token spec files.
- **`excalidraw`** — Hand-drawn Excalidraw JSON diagrams (arch, flow, seq).
- **`humanizer`** — Humanize text: strip AI-isms and add real voice.
- **`manim-video`** — Manim CE animations: 3Blue1Brown math/algo videos.
- **`mattpocock-prototype`** — Build a throwaway prototype to answer a design question.
- **`p5js`** — p5.js sketches: gen art, shaders, interactive, 3D.
- **`popular-web-designs`** — 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS.
- **`pretext`** — Build creative browser demos with DOM-free text layout.
- **`sketch`** — Throwaway HTML mockups: 2-3 design variants to compare.
- **`songwriting-and-ai-music`** — Songwriting craft and Suno AI music prompts.
- **`touchdesigner-mcp`** — Control TouchDesigner via twozero MCP.

### Devops (5 skills)

- **`docker-containers`** — Build and debug Docker containers and Compose stacks.
- **`rest-api-client`** — Call REST APIs: auth, pagination, rate limits, errors.
- **`sdlc-review`** — Review Kanban handoffs and route verified outcomes.
- **`sqlite-queries`** — Query, inspect, and export SQLite databases.
- **`ssh-remote`** — Run commands and transfer files on remote machines over SSH.

### Doc Coauthoring (1 skills)

- **`doc-coauthoring`** — Guide users through a structured workflow for co-authoring documentation. Use when user wants to wri

### Dogfood (1 skills)

- **`adversarial-ux-test`** — Roleplay a hostile user to find and triage UX pain points.

### Email (2 skills)

- **`email-inbox-triage`** — Triage an inbox: prioritize threads, draft replies safely.
- **`himalaya`** — Himalaya CLI: IMAP/SMTP email from terminal.

### Frontend Design (1 skills)

- **`frontend-design`** — Guidance for distinctive, intentional visual design when building new UI or reshaping an existing on

### Github (11 skills)

- **`codebase-inspection`** — Inspect codebases w/ pygount: LOC, languages, ratios.
- **`github-auth`** — GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login.
- **`github-code-review`** — Review PRs: diffs, inline comments via gh or REST.
- **`github-issue-to-pr`** — Carry a GitHub issue to a verified PR with honest CI state.
- **`github-issues`** — Create, triage, label, assign GitHub issues via gh or REST.
- **`github-pr-workflow`** — GitHub PR lifecycle: branch, commit, open, CI, merge.
- **`github-repo-management`** — Clone/create/fork repos; manage remotes, releases.
- **`mattpocock-code-review`** — Two-axis code review: Standards and Spec via sub-agents.
- **`mattpocock-finishing-a-development-branch`** — Complete git branches with merge/PR options.
- **`mattpocock-gh-fix-ci`** — Debug failing GitHub Actions checks on a PR.
- **`mattpocock-yeet`** — Git workflow: stage, commit, push, open PR.

### Huggingface Trackio (1 skills)

- **`huggingface-trackio`** — Track and visualize ML training experiments with Trackio. Use when logging metrics during training (

### Media (3 skills)

- **`gif-search`** — Search/download GIFs from Tenor via curl + jq.
- **`songsee`** — Audio spectrograms/features (mel, chroma, MFCC) via CLI.
- **`youtube-content`** — YouTube transcripts to summaries, threads, blogs.

### Mlops (5 skills)

- **`evaluating-llms-harness`** — lm-eval-harness: benchmark LLMs (MMLU, GSM8K, etc.).
- **`huggingface-hub`** — HuggingFace hf CLI: search/download/upload models, datasets.
- **`llama-cpp`** — llama.cpp local GGUF inference + HF Hub model discovery.
- **`serving-llms-vllm`** — vLLM: high-throughput LLM serving, OpenAI API, quantization.
- **`weights-and-biases`** — W&B: log ML experiments, sweeps, model registry, dashboards.

### Note Taking (1 skills)

- **`obsidian`** — Read, search, create, and edit notes in the Obsidian vault.

### Productivity (18 skills)

- **`airtable`** — Airtable REST API via curl. Records CRUD, filters, upserts.
- **`box`** — Box manages cloud files, sharing, search, and metadata.
- **`document-to-action-items`** — Extract cited obligations, deadlines, tasks from documents.
- **`docx`** — Create, read, edit, template, and review Word .docx files.
- **`google-workspace`** — Gmail, Calendar, Drive, Docs, Sheets via gws CLI or Python.
- **`maps`** — Geocode, POIs, routes, timezones via OpenStreetMap/OSRM.
- **`mattpocock-handoff`** — Compact a conversation into a handoff doc for another agent.
- **`meeting-action-items`** — Turn meeting notes into cited decisions, owners, tickets.
- **`nano-pdf`** — Edit text in existing PDFs via natural-language prompts.
- **`notion`** — Notion API + ntn CLI: pages, databases, markdown, Workers.
- **`ocr-and-documents`** — Extract text from PDFs/scans (pymupdf, marker-pdf).
- **`pdf`** — Create, read, merge, fill, and secure PDF files.
- **`powerpoint`** — Create, read, edit .pptx decks with python-pptx.
- **`product-price-monitor`** — Watch product, flight, or listing prices; alert on target.
- **`session-librarian`** — Organize sessions by prompt: find, rename, archive, prune.
- **`teams-meeting-pipeline`** — Teams meeting summaries, job replay, Graph subscriptions.
- **`weekly-review-planning`** — Weekly reset: commitments, stalled work, next-week plan.
- **`xlsx`** — Create, read, edit Excel .xlsx workbooks and CSVs.

### Research (9 skills)

- **`arxiv`** — Search arXiv papers by keyword, author, category, or ID.
- **`blocked-page-recovery`** — Recover blocked/paywalled/WAF'd pages via fallbacks.
- **`blogwatcher`** — Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool.
- **`competitor-news-monitor`** — Watch named companies for material news; cited digests.
- **`grounded-citations`** — Ground answers and documents in cited, verifiable sources.
- **`llm-wiki`** — Karpathy's LLM Wiki: build/query interlinked markdown KB.
- **`mattpocock-research`** — Research a question against primary sources.
- **`parallel-cli`** — Agent-native web search, deep research, and enrichment.
- **`research-paper-writing`** — Write ML papers for NeurIPS/ICML/ICLR: design→submit.

### Security (1 skills)

- **`mattpocock-security-review`** — Review code for security vulnerabilities by language.

### Smart Home (1 skills)

- **`openhue`** — Control Philips Hue lights, scenes, rooms via OpenHue CLI.

### Social Media (1 skills)

- **`xurl`** — X/Twitter via xurl CLI: raw post search, posting, DM, media.

### Software Development (24 skills)

- **`dogfood`** — Exploratory QA of web apps: find bugs, evidence, reports.
- **`hermes-agent-skill-authoring`** — Author in-repo SKILL.md files: frontmatter and structure.
- **`inspecting-hermes-desktop-dom`** — Read the live Hermes desktop DOM/CSS over CDP.
- **`mattpocock-ask-if-underspecified`** — Ask clarifying questions when a request is ambiguous.
- **`mattpocock-codebase-design`** — Design deep modules with small interfaces.
- **`mattpocock-diagnosing-bugs`** — Diagnose hard bugs via tight feedback loops and bisection.
- **`mattpocock-domain-modeling`** — Sharpen domain terms and update CONTEXT.md and ADRs inline.
- **`mattpocock-evidence-driven`** — Validate code changes with evidence and testing gates.
- **`mattpocock-improve-codebase-architecture`** — Survey code for module deepening opportunities and fix them.
- **`mattpocock-multi-agent-code-review`** — Multi-agent PR review: bug-hunter, security, contracts.
- **`mattpocock-spec-driven-development`** — Spec-driven development with planning and quality gates.
- **`mattpocock-tdd`** — TDD red-green-refactor at pre-agreed seams.
- **`mattpocock-to-tickets`** — Break a plan or spec into tracer-bullet tickets with edges.
- **`mattpocock-using-git-worktrees`** — Set up isolated git worktrees for feature work.
- **`mattpocock-writing-for-agents`** — Write docs agents can consume: skills, AGENTS.md, specs.
- **`node-inspect-debugger`** — Debug Node.js via --inspect + Chrome DevTools Protocol CLI.
- **`plan`** — Write a markdown plan to .hermes/plans/; no execution.
- **`python-debugpy`** — Debug Python: pdb REPL + debugpy remote (DAP).
- **`requesting-code-review`** — Pre-commit review: security scan, quality gates, auto-fix.
- **`simplify-code`** — Parallel 4-agent cleanup of recent code changes.
- **`spike`** — Throwaway experiments to validate an idea before build.
- **`systematic-debugging`** — 4-phase root cause debugging: understand bugs before fixing.
- **`test-driven-development`** — TDD: enforce RED-GREEN-REFACTOR, tests before code.


---

**Total: 114 skills** across 19 categories.
Last synced from Hermes local skills directory.
