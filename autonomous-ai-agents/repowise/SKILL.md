---
name: repowise
description: "Index a repo once; the agent reads answers, not grep loops"
version: v0.1.0
author: Hermes Agent (mined from repowise-dev/repowise docs + live install test)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [codebase-indexing, mcp-server, token-optimization, agent-context, git-signals, code-health]
    related_skills: [hermes-agent, fastmcp, mcporter, code-quality-signal, codebase-onboarding]
---

<!-- source: repowise-dev/repowise (AGPL-3.0) — docs/layers/* + docs/agent/* mined 2026-09-10 at clone HEAD 9f52f0a; every operational claim re-tested live on this Windows box with v0.49.0 in an isolated uv venv, then RE-PROBED against v0.51.0 (PyPI latest) on 2026-09-17 — the table below is current as of that date. AGPL means knowledge distillation only — never port its code into MIT-licensed skills -->

# Repowise: Precomputed Codebase Intelligence for Agents

`repowise` (PyPI, `pip install repowise`) computes answers to "who calls this / what breaks if I change it / which files are dangerous" **once** and keeps them current on every commit. The agent then reads the answer instead of re-grepping the codebase per task. One index produces five queryable layers: dependency graph (19 languages, confidence-scored call edges), git behavioural signals (hotspots, co-change coupling, bug history), generated wiki docs, mined architectural decisions with evidence spans, and a deterministic 49-detector code-health score.

## What This Skill Does

Covers how to install, index, wire into Hermes as an MCP server, use the `distill` token-compression CLI, and — most durably — the **general engineering patterns** in its design that apply to any agent-context tooling (see references). All operational facts below were executed live on Windows 11 / Python 3.13; version-sensitive claims re-probed against repowise 0.51.0 (2026-09-17) after the v0.49→v0.51 drift was caught by an upstream SHA check.

## When to Use

- Agent burns tokens re-exploring a repo it has seen before ("why is my agent grepping the same files every session?")
- You want per-file defect risk, change-risk on PRs, or dead-code triage without an LLM in the loop
- Noisy command output (300 lines of passing tests around 4 failures) is eating context — `repowise distill <cmd>` compresses it before the agent reads it
- Evaluating whether a codebase-intelligence layer is worth adding to your setup

## Verified on This Machine (re-probed 2026-09-17, v0.51.0)

| Claim | Live result |
|---|---|
| `uv pip install repowise` in isolated venv | installs clean; CLI at `<venv>/Scripts/repowise.exe`, works on Windows py3.13 (`--version` → 0.51.0) |
| Keyless indexing: no API key needed for first index | `init --no-prose` built `.repowise/wiki.db` + structural wiki pages in ~2s on a scratch project, zero provider calls; v0.51 additionally prints a doc-quality audit table (page overlap %, question-shaped text, house vocabulary) at the end of init |
| Distillation is real and reversible | `distill "git log --stat -35"` → **417 lines → 25** on a scratch repo with 36 commits; errors-first ordering kept; exit code preserved exactly (inner rc=128 → outer rc=128); `expand <ref>` round-trips byte-for-byte except CRLF normalization under Windows text-mode capture |
| Cost accounting | `repowise saved` renders a per-filter table (git_log: 3,287 raw / 392 distilled tokens = 88%) PLUS a new "Net (billed tokens)" section that debits the resident CLAUDE.md block and states its ceiling-vs-floor honesty explicitly — deterministic tiktoken counts, not estimates |
| MCP server over stdio | real handshake via the official `mcp` python client: **10 tools advertised by default** in single-repo mode (`get_overview get_answer get_context get_symbol search_codebase get_risk get_change_risk get_why get_dead_code get_health`) — unchanged from v0.49, but now part of a larger surface (see below) |
| Configurable tool surface (NEW in 0.5x) | **18 tools registered total**: the 10 canonical + `list_repos` (workspace mode only) + 7 opt-in specialists (`get_architecture get_blast_radius get_dependency_path get_execution_flows generate_refactoring_code get_conformance set_finding_status`). Configure via `.repowise/config.yaml` → `mcp.tools`: +/- deltas against the default or an explicit allowlist |
| Transports (NEW) | stdio, streamable-http (port 7338), and legacy sse — `repowise mcp --transport {stdio\|streamable-http\|sse}` |
| Editor auto-setup (CHANGED) | `init` now **automatically registers the MCP server + installs proactive hooks for Claude Code** (one `repowise` key per config; indexing a second repo repoints it); `--codex` writes Codex config/hooks; opt out with `--no-editor-setup` or `REPOWISE_SKIP_EDITOR_SETUP=1` — use that on scratch/CI repos |
| Tool responses are structured, not prose dumps | `get_overview` returned JSON envelope `_meta{completeness, contract_version: 1, embedder, embedder_degraded, index_age_days, index_behind, index_scope, indexed_commit, live_head, response_budget{limit_chars: 24000, tier: default}, semantic_search}` — the stale-warning inputs (`index_behind`, `live_head`) are now explicit fields |
| Release notice (NEW) | server polls PyPI for a newer repowise and announces "upgrade and restart" in-band once per version seen — observed live during handshake |
| Failure shield | un-indexed repo → tool returns `{error, remedy, guidance}` JSON (remedy even instructs the agent "suggest it once, do not run it yourself") instead of a raw traceback; nested task-group failures are unwrapped to depth ≤2 before shielding |
| Telemetry is ON by default | opt-out model confirmed in v0.51 source (`cli/platform/settings.py`): precedence `DO_NOT_TRACK` (new cross-tool hard off) > `REPOWISE_TELEMETRY_DISABLED` > stored consent > enabled; new `REPOWISE_TELEMETRY_DEBUG=1` prints the exact payload to stderr instead of sending it — verify what would leave your machine before deciding. Consent state in `~/.repowise/platform.json` |

## Quickstart (verified)

```bash
# isolated venv keeps it out of your main environment
uv venv repowise-venv && uv pip install --python <venv>/python repowise

cd /path/to/repo
repowise init --no-prose        # keyless: graph + git + decisions + health layers, structural wiki only
# upgrade to model-written prose later, per page/directory, cost shown before confirm (needs a provider then)

repowise distill pytest         # wrap noisy commands; [repowise#<ref>] markers expand back losslessly
repowise saved                  # tokens + $ actually saved, grouped by filter kind
```

### Wire into Hermes as an MCP server

`init` writes `.mcp.json` for Claude/Cursor/VS Code. For Hermes, add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  repowise:
    command: "<venv>/Scripts/repowise"   # absolute path — bare 'repowise' won't resolve from the agent's env
    args: ["mcp", "/absolute/path/to/repo"]   # PATH arg scopes the server to one repo (verified)
```

Then restart Hermes. Tools arrive as `mcp_repowise_get_overview` etc. **Allowlist caveat**: if your platform has a saved `platform_toolsets.<platform>` list, MCP servers are only injected when their name is in that list — see `hermes-agent/references/native-mcp.md` (verified against this install's source).

### The ten tools (task-shaped by design)

| Tool | Only-this-tool answers |
|---|---|
| `get_overview()` | First call on any unfamiliar codebase: architecture summary, module map, entry points, git health |
| `get_answer(question)` | Hybrid retrieval (full-text + vector via RRF fusion, PageRank bias, 1-hop graph expansion) → one cited answer with calibrated `retrieval_quality` — collapses search→read→reason into a round-trip |
| `get_context(targets[], include?)` | Triage cards for files/modules/symbols: summary, signatures, hotspot bit, governing decisions. **Batch many targets in one call** |
| `get_symbol("file.py::Name")` | Source of one symbol with exact line bounds — cheaper than Read + offset math |
| `search_codebase(query, kind?)` | Semantic search over the wiki, filterable by implementation/test/config/doc |
| `get_risk(targets[], changed_files?)` | Hotspots, dependents, co-change partners, ownership, test gaps; PR mode returns a `directive` block |
| `get_change_risk(revspec)` | Pre-merge defect score for a whole commit/range from diff shape, ranked as percentile vs the repo's own recent commits |
| `get_why(query?, targets?)` | Architectural decisions with **verbatim evidence spans**, stamped exact/fuzzy/unverified; falls back to git archaeology when none exist |
| `get_dead_code(...)` | Unreachable code by confidence tier + cleanup-impact estimates |
| `get_health(targets?, include?)` | Per-file scores across defect-risk / maintainability / performance signals + structured refactoring plans (Extract Class/Method, Move Method, Break Cycle) — zero LLM, <30s |

Every response carries `_meta{index_age_days, indexed_commit, stale_warning}` — on v0.51 the inputs are explicit fields (`index_behind`, `live_head`), and the warning fires only when indexed HEAD diverges from live `.git/HEAD`, so the agent always knows how much to trust what it just read. The ten-tool default is a deliberate ceiling **for single-repo mode**: "a small task-shaped surface is easier for an agent to choose than a large entity-shaped one (one file per call forces long sequential chains)". Since v0.5x the registry holds 18 tools — workspace mode adds `list_repos`, and 7 specialists (`get_architecture get_blast_radius get_dependency_path get_execution_flows generate_refactoring_code get_conformance set_finding_status`) are opt-in via `.repowise/config.yaml` → `mcp.tools: ["+get_execution_flows"]` (deltas) or an explicit allowlist. Keep the default surface small; add specialists only when a task genuinely needs them — schema overhead is paid on every call.

## Design Patterns Worth Stealing (general knowledge)

Full write-up with formulas and the benchmarking methodology in `references/codebase-intelligence-patterns.md`. The short list:

1. **Reversible distillation contract** — compress command output errors-first, preserve exit code exactly, leave `[ref]` markers that expand byte-for-byte. Lossless-by-construction beats "summarize with an LLM".
2. **Deterministic core, model as opt-in upgrade path** — the whole index builds with zero LLM calls; prose conversion is per-page and shows cost before confirm. Same principle for any agent tooling: make the free tier complete, not a crippled demo.
3. **Recency-decayed git signals anchored to the change date, not today** — decayed bug-fix counts (half-life 90d) mean "recent-equivalent fixes"; anchoring to the commit makes re-scoring idempotent. A raw number is meaningless without its local population: rank against the repo's own recent commits as a percentile.
4. **Confidence-scored edges, not binary** — call resolution emits per-edge confidence; downstream consumers can threshold instead of trusting everything equally (same for mined decisions: exact/fuzzy/unverified stamps).
5. **Stale-aware responses** — every read carries its provenance age and a divergence warning rather than silently serving stale data.
6. **Benchmark discipline for your own claims** — sealed holdout split held out from improvement rounds, deterministic grading (no LLM judge), publish the rows you lose alongside wins, validate defect prediction leakage-free with ROC AUC before claiming it works.

## Pitfalls (measured)

- `repowise mcp` without a PATH arg resolves the repo by walking up from **cwd** for `.repowise/`; if none is found it silently serves an empty registry — every tool then returns the "no index yet" remedy JSON instead of failing loudly. Pass the explicit path in your MCP config (as `init` does).
- Windows: paths stored in the repo DB use backslashes; querying by forward-slash path string misses (use name or ID, or omit `repo`).
- Telemetry posts to api.repowise.dev even in fully-local mode — set `REPOWISE_TELEMETRY_DISABLED=1` before indexing sensitive repos. v0.51 additions: the cross-tool standard `DO_NOT_TRACK=1` is also a hard off (highest precedence), and `REPOWISE_TELEMETRY_DEBUG=1` prints the exact payload to stderr instead of sending — use it once on an unfamiliar machine to see what would leave before deciding.
- **Editor auto-setup is ON by default since v0.5x**: `init` writes/repaints a single `repowise` MCP key in your Claude Code config and installs hooks; indexing repo B repoints the entry away from repo A (it prints a notice). On scratch clones, worktrees, CI runners or benchmark repos pass `--no-editor-setup` (or `REPOWISE_SKIP_EDITOR_SETUP=1`) — an unattended agent run should not be mutating editor configs as a side effect.
- AGPL-3.0: fine as a subprocess/MCP server; do not import its modules into permissively licensed code.

## v0.5x feature worth knowing (2026-09-17)

**doc-drift analysis (#2290)** — the index now reads the repo's own markdown, extracts what each document *claims* about the tree, and reports claims the tree refutes. Four reference classes ship: path, link, in-page anchor, build command; a fifth (symbol) was measured first and **rejected** because backticks in technical prose mean "literal token", not code symbol — their top false flags were `string`, `boolean`, `OPENAI_API_KEY`. Verdicts are four-way, not two: resolves / missing / ambiguous / uncheckable, with the last being an honest denominator (691 of 1,784 refs in their own repo are uncheckable — saying so is what separates a detector from a noise generator). Measured: 19 findings on their repo, 17 real defects; fastapi at 4,123 refs across 1,526 docs → zero findings. The precision rules (path checkable only with a separator + real top-level first segment — took that class from 49% flag rate to 1.3%; historical docs excluded by stem pattern so `release-notes.md` matches too; commands read only inside inline code spans) are the transferable part: see references for the full write-up and how it maps onto this repo's own check-links gate.
