# Installed Plugins — Live Environment Catalog

> **Machine-generated** by `scripts/sync-installed-plugins.py` — do not edit by hand.
> Regenerate: `python3 hermes-agent/scripts/sync-installed-plugins.py`
> Check drift: `python3 hermes-agent/scripts/sync-installed-plugins.py --check`
> Generated on machine: `Owner` (OS user). Each machine has its own plugin set;
> `--check` on another machine skips rather than reporting drift.

## Summary

| Metric | Count |
|--------|-------|
| Total plugins installed | 16 |
| Enabled | 15 |
| Disabled | 1 |
| Dashboard/UI-only plugins | 4 |
| Tool-providing plugins | 6 |
| Community catalog plugins | 14 |
| Official catalog plugins | 2 |
| Standalone desktop plugins | 0 |
| Total toolsets | 29 |
| Toolsets enabled | 21 |
| Toolsets disabled | 8 |

## Plugin Catalog

| # | Plugin | Version | Catalog | Status | Source | Revision | Type |
|---|--------|---------|---------|--------|--------|----------|------|
| 1 | agent-analytics | 0.1.0 | community | enabled | Agent-Analytics/agent-analytics-hermes-plugin | 63f11d36 | dashboard |
| 2 | bot-forge | 0.4.1 | community | enabled | BkashJEE/hermes-bot-forge | 88dd338a | tool |
| 3 | hermes-ledgerline | 0.1.9 | community | enabled | Adolanium/hermes-ledgerline | a89efcea | dashboard |
| 4 | hermes-memory-ui | 0.6.4 | community | enabled | xraysight/hermes-memory-ui | 8f798101 | dashboard |
| 5 | hermes-telemetry | 0.9.1 | community | disabled | nujovich/hermes-telemetry | 872eadc4 | unknown |
| 6 | hindsight | 1.2.3 | community | enabled | vectorize-io/hindsight#hindsight-integrations/hermes | d952b6e6 | unknown |
| 7 | holographic | 0.26.2 | community | enabled | itpartypattaya/hermes-plugin-holographic | 327adc7b | unknown |
| 8 | home-dashboard | 1.3.0 | community | enabled | albertocvrrbs/hermes-home-dashboard | a8a01822 | unknown |
| 9 | homeassistant | 2.0.1 | official | enabled | NousResearch/hermes-official-plugins#homeassistant | 4d492b1d | unknown |
| 10 | icarus | 0.3.0 | community | enabled | esaradev/icarus-plugin | e46cba30 | tool |
| 11 | job-search | 0.9.0 | community | enabled | agent-data/job-search | dba0c099 | tool |
| 12 | memory-wiki | 1.0.0 | official | enabled | NousResearch/hermes-memory-wiki | 9bc3913b | dashboard |
| 13 | mnemosyne-dashboard | 0.14.0 | community | enabled | wysie/mnemosyne-dashboard | a918e5e0 | tool |
| 14 | prompt-optimizer | 1.0.0 | community | enabled | Sahil-SS9/hermes-multichannel-prompt-optimizer | e83eba9a | unknown |
| 15 | web-search-plus | 5.1.7 | community | enabled | robbyczgw-cla/hermes-web-search-plus | 4eebfd77 | tool |
| 16 | yantrikdb | 0.27.1 | community | enabled | yantrikos/yantrikdb-hermes-plugin | d9badf26 | tool |

## Tool Configuration

> Auto-generated from `hermes tools list` — 21/29 toolsets enabled.

### Enabled toolsets

| Toolset | Display name | Tools | Plugin source |
|---------|--------------|-------|---------------|
| `web` | Web Search & Scraping | web_search, web_extract | built-in |
| `browser` | Browser Automation | navigate, click, type, scroll | built-in |
| `terminal` | Terminal & Processes | terminal, process | built-in |
| `file` | File Operations | read, write, patch, search | built-in |
| `code_execution` | Code Execution | execute_code | built-in |
| `vision` | Vision / Image Analysis | vision_analyze | built-in |
| `image_gen` | Image Generation | image_generate | built-in |
| `tts` | Text-to-Speech | text_to_speech | built-in |
| `skills` | Skills | skill_view, skill_manage, skills_list | built-in |
| `todo` | Task Planning | todo_list | built-in |
| `memory` | Memory | yantrikdb_remember, yantrikdb_recall, yantrikdb_forget, yantrikdb_conflicts, yantrikdb_relate, yantrikdb_tasks, yantrikdb_resolve_conflict | yantrikdb |
| `session_search` | Session Search | session_search | built-in |
| `connections` | Connections | connections | built-in |
| `clarify` | Clarifying Questions | clarify | built-in |
| `delegation` | Task Delegation | delegate_task | built-in |
| `cronjob` | Cron Jobs | cronjob_manage (create/list/update/pause/resume/run) | built-in |
| `computer_use` | Computer Use (macOS/Windows/Linux) | computer_use (list_apps, capture, click, type, ...) | built-in |
| `bot_forge` | Bot Forge | agent that builds complete working bots | bot-forge |
| `fabric` | Fabric | self-memory + replacement model tools | icarus |
| `mnemosyne-dashboard` | Mnemosyne-Dashboard | memory browsing & visualization | mnemosyne-dashboard |
| `web-search-plus` | Web-Search-Plus | multi-provider search, URL extraction, reports | web-search-plus |

### Disabled toolsets

| Toolset | Display name | Reason | Plugin source |
|---------|--------------|--------|---------------|
| `video` | Video Analysis | (requires video-capable model) | built-in |
| `video_gen` | Video Generation | (not enabled) | built-in |
| `x_search` | X (Twitter) Search | (requires xAI OAuth or XAI_API_KEY) | built-in |
| `stt` | Speech-to-Text | (not enabled) | built-in |
| `kanban` | Kanban | (opt-in task board) | built-in |
| `context_engine` | Context Engine | (no active context engine) | built-in |
| `a2a` | A2A | Agent-to-Agent protocol | a2a |
| `homeassistant` | Homeassistant | (no API key) | built-in |

## Per-Plugin Details

### 1. `agent-analytics`

- **Version**: 0.1.0
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/Agent-Analytics/agent-analytics-hermes-plugin
- **Revision**: `63f11d36` (`63f11d3669330e40dad977b7d32f9b69e69a9fb8`) — pinned
- **Type**: Dashboard/UI panel
- **Tools**: None (dashboard panel only)
- **Description**: Dashboard-only read plugin for Agent Analytics inside Hermes.

### 2. `bot-forge`

- **Version**: 0.4.1
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/BkashJEE/hermes-bot-forge
- **Revision**: `88dd338a` (`88dd338a0e1358541725e87a142a0c6618c4f265`) — pinned
- **Type**: Agent tool-providing
- **Tools**: `bot_forge` (Bot Forge) — agent that builds complete working bots
- **Description**: Say "make me a <role>" and your Hermes agent builds a complete, working Bot — name, face, SOUL.md, memory, tools, skills, routines, Bot Chat and gateway — tested and rolled back on failure.

### 3. `hermes-ledgerline`

- **Version**: 0.1.9
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/Adolanium/hermes-ledgerline
- **Revision**: `a89efcea` (`a89efceab1ff5eb0cc3f58c0482c0f1d368a6d1b`) — pinned
- **Type**: Dashboard/UI panel
- **Tools**: None (dashboard panel only)
- **Description**: Inspect session costs and usage in Hermes Desktop.

### 4. `hermes-memory-ui`

- **Version**: 0.6.4
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/xraysight/hermes-memory-ui
- **Revision**: `8f798101` (`8f798101a61a33e16f38eb22c3b1ad50ef9484a1`) — pinned
- **Type**: Dashboard/UI panel
- **Tools**: None (dashboard panel only)
- **Description**: Read-only Hermes Dashboard and Desktop plugin for inspecting built-in, holographic, Mem0, Honcho, Mnemosyne, Hindsight, and ByteRover memory.

### 5. `hermes-telemetry`

- **Version**: 0.9.1
- **Catalog**: community
- **Status**: disabled
- **Install source**: https://github.com/nujovich/hermes-telemetry
- **Revision**: `872eadc4` (`872eadc4b1e6797bc72c8eed3daf54f199d2bed5`) — pinned
- **Type**: Agent tool-providing
- **Tools**: Not reflected in `hermes tools list` (may register via agent tool discovery)
- **Description**: Observability + budget guardrails for Hermes Agent — tokens, cost, latency, tool calls per session and cron job. Persists to local SQLite. Exposes /stats and /budget slash commands.

### 6. `hindsight`

- **Version**: 1.2.3
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/vectorize-io/hindsight#hindsight-integrations/hermes
- **Revision**: `d952b6e6` (`d952b6e655fccab4581ee0722b51c5f103873d12`) — pinned
- **Type**: Agent tool-providing
- **Tools**: Not reflected in `hermes tools list` (may register via agent tool discovery)
- **Description**: Hindsight — long-term memory with knowledge graph, entity resolution, and multi-strategy retrieval.

### 7. `holographic`

- **Version**: 0.26.2
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/itpartypattaya/hermes-plugin-holographic
- **Revision**: `327adc7b` (`327adc7bfdf55c6d85209b5fc9dbf485111394a1`) — pinned
- **Type**: Agent tool-providing
- **Tools**: Not reflected in `hermes tools list` (may register via agent tool discovery)
- **Description**: Holographic memory — local SQLite fact store with FTS5 search, trust scoring, and HRR-based compositional retrieval; optional online search by meaning through an embeddings API (off by default).

### 8. `home-dashboard`

- **Version**: 1.3.0
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/albertocvrrbs/hermes-home-dashboard
- **Revision**: `a8a01822` (`a8a018225d8ecd21b281788131775adeade4c577`) — pinned
- **Type**: Agent tool-providing
- **Tools**: Not reflected in `hermes tools list` (may register via agent tool discovery)
- **Description**: Personalizable rice-style Home page with draggable, resizable glass widgets for Hermes Web and Desktop.

### 9. `homeassistant`

- **Version**: 2.0.1
- **Catalog**: official
- **Status**: enabled
- **Install source**: https://github.com/NousResearch/hermes-official-plugins#homeassistant
- **Revision**: `4d492b1d` (`4d492b1dc5326af3e38bb2cf3e4b9ad6d65f0072`) — pinned
- **Type**: Agent tool-providing
- **Tools**: Not reflected in `hermes tools list` (may register via agent tool discovery)
- **Description**: Home Assistant for Hermes Agent: a gateway platform adapter plus four smart-home tools. The adapter subscribes to HA's WebSocket event bus and forwards state-change events (with per-entity cooldowns and domain/entity filtering) to the agent; replies are delivered as HA persistent notifications, and cron deliver=homeassistant goes through the target's notify service (notify.<target>). The homeassistant toolset (ha_list_entities, ha_get_state, ha_list_services, ha_call_service) queries and controls devices over the REST API. Formerly built into Hermes core.


### 10. `icarus`

- **Version**: 0.3.0
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/esaradev/icarus-plugin
- **Revision**: `e46cba30` (`e46cba30fb95a0b54b7c4d6c26169a424283d72b`) — pinned
- **Type**: Agent tool-providing
- **Tools**: `fabric` (Fabric) — self-memory + replacement model tools
- **Description**: Self-memory and replacement models for Hermes agents. Remember your work. Train your replacement.

### 11. `job-search`

- **Version**: 0.9.0
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/agent-data/job-search
- **Revision**: `dba0c099` (`dba0c0992e9d7fc6533dd1be3003df7a311168f0`) — pinned
- **Type**: Agent tool-providing
- **Tools**: Not reflected in `hermes tools list` (may register via agent tool discovery)
- **Description**: A private, local-first job-search assistant that finds postings, judges them against your prose preferences (no scores), and writes digests on a schedule you control.

### 12. `memory-wiki`

- **Version**: 1.0.0
- **Catalog**: official
- **Status**: enabled
- **Install source**: https://github.com/NousResearch/hermes-memory-wiki
- **Revision**: `9bc3913b` (`9bc3913b8474eaf4d7eec32e97af4d77957c36df`) — pinned
- **Type**: Dashboard/UI panel
- **Tools**: None (dashboard panel only)
- **Description**: Memory Wiki dashboard tab: browsable subject pages and daily logs derived from local session history, plus a read-only Persistent Memory audit panel (MEMORY.md / USER.md).

### 13. `mnemosyne-dashboard`

- **Version**: 0.14.0
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/wysie/mnemosyne-dashboard
- **Revision**: `a918e5e0` (`a918e5e0841fdc85baad7ab582432b2b7499b2f2`) — pinned
- **Type**: Agent tool-providing
- **Tools**: `mnemosyne-dashboard` (Mnemosyne-Dashboard) — memory browsing & visualization
- **Description**: Local-only web dashboard for browsing and visualising Mnemosyne memories, triples, stats, and consolidation history.

### 14. `prompt-optimizer`

- **Version**: 1.0.0
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/Sahil-SS9/hermes-multichannel-prompt-optimizer
- **Revision**: `e83eba9a` (`e83eba9a8e102ed255a5bfd20cc88ea50e3af28f`) — pinned
- **Type**: Agent tool-providing
- **Tools**: Not reflected in `hermes tools list` (may register via agent tool discovery)
- **Description**: Model-aware prompt rewriter with token-efficiency scoring, coaching metrics, and slash commands.

### 15. `web-search-plus`

- **Version**: 5.1.7
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/robbyczgw-cla/hermes-web-search-plus
- **Revision**: `4eebfd77` (`4eebfd77a4572111306f4ff551be4e53ef76f450`) — pinned
- **Type**: Agent tool-providing
- **Tools**: `web-search-plus` (Web-Search-Plus) — multi-provider search, URL extraction, reports
- **Description**: Multi-provider web search, URL extraction, quality reports, and opt-in research mode

### 16. `yantrikdb`

- **Version**: 0.27.1
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/yantrikos/yantrikdb-hermes-plugin
- **Revision**: `d9badf26` (`d9badf26807aaf086fe05705b1c5617e3611fafa`) — pinned
- **Type**: Agent tool-providing
- **Tools**: `memory` (Memory) — yantrikdb_remember, yantrikdb_recall, yantrikdb_forget, yantrikdb_conflicts, yantrikdb_relate, yantrikdb_tasks, yantrikdb_resolve_conflict
- **Description**: YantrikDB — self-maintaining memory for Hermes with canonicalization, contradiction tracking, recency-aware ranking, explainable recall, and pluggable embedders (bundled potion-2M default; first-class loaders for the model2vec family and the HF sentence-transformers ecosystem; custom Python embedder class as escape hatch). As of v0.2.0 the default backend is in-process (`pip install` and go); HTTP-to-server is optional for HA cluster setups.

## Sync

This reference is machine-generated from the live Hermes environment:

- `python3 hermes-agent/scripts/sync-installed-plugins.py` — regenerate from live env
- `python3 hermes-agent/scripts/sync-installed-plugins.py --check` — verify no drift
- Data sources: `hermes plugins list --json`, `.install-metadata.json`, `config.yaml`, `hermes tools list`, `desktop-plugins/` dir scan
- CI note: when no local Hermes installation is found, the gate skips (exit 77, shown as SKIP)

