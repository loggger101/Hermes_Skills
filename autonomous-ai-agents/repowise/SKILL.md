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

<!-- source: repowise-dev/repowise (AGPL-3.0) — docs/layers/* + docs/agent/* mined 2026-09-10 at clone HEAD 9f52f0a; every operational claim below re-tested live on this Windows box with v0.49.0 in an isolated uv venv. AGPL means knowledge distillation only — never port its code into MIT-licensed skills -->

# Repowise: Precomputed Codebase Intelligence for Agents

`repowise` (PyPI, `pip install repowise`) computes answers to "who calls this / what breaks if I change it / which files are dangerous" **once** and keeps them current on every commit. The agent then reads the answer instead of re-grepping the codebase per task. One index produces five queryable layers: dependency graph (19 languages, confidence-scored call edges), git behavioural signals (hotspots, co-change coupling, bug history), generated wiki docs, mined architectural decisions with evidence spans, and a deterministic 49-detector code-health score.

## What This Skill Does

Covers how to install, index, wire into Hermes as an MCP server, use the `distill` token-compression CLI, and — most durably — the **general engineering patterns** in its design that apply to any agent-context tooling (see references). All operational facts below were executed live on Windows 11 / Python 3.13 with repowise 0.49.0 before being recorded.

## When to Use

- Agent burns tokens re-exploring a repo it has seen before ("why is my agent grepping the same files every session?")
- You want per-file defect risk, change-risk on PRs, or dead-code triage without an LLM in the loop
- Noisy command output (300 lines of passing tests around 4 failures) is eating context — `repowise distill <cmd>` compresses it before the agent reads it
- Evaluating whether a codebase-intelligence layer is worth adding to your setup

## Verified on This Machine (2026-09-10, v0.49.0)

| Claim | Live result |
|---|---|
| `uv pip install repowise` in isolated venv | installs clean; CLI at `<venv>/Scripts/repowise.exe`, works on Windows py3.13 |
| Keyless indexing: no API key needed for first index | `repowise init --no-prose` built `.repowise/wiki.db` + 8 structural wiki pages in ~2s on a scratch project, zero provider calls |
| Distillation is real and reversible | `distill "git log --stat -30"` → **12,448 → 1,362 tokens (89%)**, errors-first ordering kept; exit code preserved exactly (rc=0→0, rc=1→1); `expand <ref>` round-trips byte-for-byte except CRLF normalization under Windows text-mode capture |
| Cost accounting | `repowise saved` renders a per-filter table: 2 git_log events, 11,086 tokens (89%) saved — deterministic tiktoken counts, not estimates |
| MCP server over stdio | real handshake via the official `mcp` python client: **exactly 10 tools** (`get_overview get_answer get_context get_symbol search_codebase get_risk get_change_risk get_why get_dead_code get_health`) |
| Tool responses are structured, not prose dumps | `get_overview` returned a JSON envelope with `code_health{average_health: 9.94, band: healthy, ...}` and `_meta{contract_version: 1, response_budget{limit_chars: 24000}}` |
| Failure shield | un-indexed repo → tool returns `{error, remedy, guidance}` JSON (remedy even instructs the agent "suggest it once, do not run it yourself") instead of a raw traceback; nested task-group failures are unwrapped to depth ≤2 before shielding |
| Telemetry is ON by default | observed live `POST https://api.repowise.dev/telemetry/events → 200` from local mode. Hard off: env `REPOWISE_TELEMETRY_DISABLED=1`; consent state in `~/.repowise/platform.json`. Decide before first run on a sensitive repo |

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

Every response carries `_meta{index_age_days, indexed_commit, stale_warning}` — the warning fires only when indexed HEAD diverges from live `.git/HEAD`, so the agent always knows how much to trust what it just read. Ten is a deliberate ceiling: a small task-shaped surface is easier for an agent to choose than a large entity-shaped one (one file per call forces long sequential chains).

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
- Telemetry posts to api.repowise.dev even in fully-local mode — set `REPOWISE_TELEMETRY_DISABLED=1` before indexing sensitive repos.
- AGPL-3.0: fine as a subprocess/MCP server; do not import its modules into permissively licensed code.
