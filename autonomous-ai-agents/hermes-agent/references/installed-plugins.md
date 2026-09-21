# Installed Plugins — Live Environment Catalog

> **Machine-generated** by `scripts/sync-installed-plugins.py` — do not edit by hand.
> Regenerate: `python3 hermes-agent/scripts/sync-installed-plugins.py`
> Check drift: `python3 hermes-agent/scripts/sync-installed-plugins.py --check`

## Summary

| Metric | Count |
|--------|-------|
| Total plugins installed | 10 |
| Enabled | 10 |
| Disabled | 0 |
| Dashboard/UI-only plugins | 4 |
| Tool-providing plugins | 6 |
| Community catalog plugins | 9 |
| Official catalog plugins | 1 |
| Standalone desktop plugins | 1 |
| Total toolsets | 31 |
| Toolsets enabled | 21 |
| Toolsets disabled | 10 |

## Plugin Catalog

| # | Plugin | Version | Catalog | Status | Source | Revision | Type |
|---|--------|---------|---------|--------|--------|----------|------|
| 1 | agent-analytics | 0.1.0 | community | enabled | Agent-Analytics/agent-analytics-hermes-plugin | 63f11d36 | dashboard |
| 2 | bot-forge | 0.4.1 | community | enabled | BkashJEE/hermes-bot-forge | 88dd338a | tool |
| 3 | hermes-ledgerline | 0.1.7.post2 | community | enabled | Adolanium/hermes-ledgerline | 9be4b850 | dashboard |
| 4 | hermes-memory-ui | 0.6.0 | community | enabled | xraysight/hermes-memory-ui | 9472bed7 | dashboard |
| 5 | icarus | 0.3.0 | community | enabled | esaradev/icarus-plugin | e46cba30 | tool |
| 6 | job-search | 0.9.0 | community | enabled | agent-data/job-search | dba0c099 | tool |
| 7 | memory-wiki | 1.0.0 | official | enabled | NousResearch/hermes-memory-wiki | 9bc3913b | dashboard |
| 8 | mnemosyne-dashboard | 0.14.0 | community | enabled | wysie/mnemosyne-dashboard | a918e5e0 | tool |
| 9 | web-search-plus | 4.2.0 | community | enabled | robbyczgw-cla/hermes-web-search-plus | d4840c9b | tool |
| 10 | yantrikdb | 0.25.0 | community | enabled | yantrikos/yantrikdb-hermes-plugin | d7ccc7ec | tool |

## Tool Configuration

> Auto-generated from `hermes tools list` — 21/31 toolsets enabled.

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
| `homeassistant` | Home Assistant | (no API key) | built-in |
| `spotify` | Spotify | (not configured) | built-in |
| `yuanbao` | Yuanbao | (not configured) | built-in |
| `a2a` | A2A | Agent-to-Agent protocol | a2a |

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

- **Version**: 0.1.7.post2
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/Adolanium/hermes-ledgerline
- **Revision**: `9be4b850` (`9be4b850c874cebaa18b0077cdc5164b5e7b953b`) — pinned
- **Type**: Dashboard/UI panel
- **Tools**: None (dashboard panel only)
- **Description**: Inspect session costs and usage in Hermes Desktop.

### 4. `hermes-memory-ui`

- **Version**: 0.6.0
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/xraysight/hermes-memory-ui
- **Revision**: `9472bed7` (`9472bed7e20a51ac4f6c48f882bd9f80ea54d4ee`) — pinned
- **Type**: Dashboard/UI panel
- **Tools**: None (dashboard panel only)
- **Description**: Read-only Hermes Dashboard and Desktop plugin for inspecting built-in, holographic, Mem0, Honcho, Mnemosyne, Hindsight, and ByteRover memory.

### 5. `icarus`

- **Version**: 0.3.0
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/esaradev/icarus-plugin
- **Revision**: `e46cba30` (`e46cba30fb95a0b54b7c4d6c26169a424283d72b`) — pinned
- **Type**: Agent tool-providing
- **Tools**: `fabric` (Fabric) — self-memory + replacement model tools
- **Description**: Self-memory and replacement models for Hermes agents. Remember your work. Train your replacement.

### 6. `job-search`

- **Version**: 0.9.0
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/agent-data/job-search
- **Revision**: `dba0c099` (`dba0c0992e9d7fc6533dd1be3003df7a311168f0`) — pinned
- **Type**: Agent tool-providing
- **Tools**: Not reflected in `hermes tools list` (may register via agent tool discovery)
- **Description**: A private, local-first job-search assistant that finds postings, judges them against your prose preferences (no scores), and writes digests on a schedule you control.

### 7. `memory-wiki`

- **Version**: 1.0.0
- **Catalog**: official
- **Status**: enabled
- **Install source**: https://github.com/NousResearch/hermes-memory-wiki
- **Revision**: `9bc3913b` (`9bc3913b8474eaf4d7eec32e97af4d77957c36df`) — pinned
- **Type**: Dashboard/UI panel
- **Tools**: None (dashboard panel only)
- **Description**: Memory Wiki dashboard tab: browsable subject pages and daily logs derived from local session history, plus a read-only Persistent Memory audit panel (MEMORY.md / USER.md).

### 8. `mnemosyne-dashboard`

- **Version**: 0.14.0
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/wysie/mnemosyne-dashboard
- **Revision**: `a918e5e0` (`a918e5e0841fdc85baad7ab582432b2b7499b2f2`) — pinned
- **Type**: Agent tool-providing
- **Tools**: `mnemosyne-dashboard` (Mnemosyne-Dashboard) — memory browsing & visualization
- **Description**: Local-only web dashboard for browsing and visualising Mnemosyne memories, triples, stats, and consolidation history.

### 9. `web-search-plus`

- **Version**: 4.2.0
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/robbyczgw-cla/hermes-web-search-plus
- **Revision**: `d4840c9b` (`d4840c9b9572281735d67d511814dd9a51f922d0`) — pinned
- **Type**: Agent tool-providing
- **Tools**: `web-search-plus` (Web-Search-Plus) — multi-provider search, URL extraction, reports
- **Description**: Multi-provider web search, URL extraction, quality reports, and opt-in research mode

### 10. `yantrikdb`

- **Version**: 0.25.0
- **Catalog**: community
- **Status**: enabled
- **Install source**: https://github.com/yantrikos/yantrikdb-hermes-plugin
- **Revision**: `d7ccc7ec` (`d7ccc7ec423591438f1897ad9a2f4ca197500fe5`) — pinned
- **Type**: Agent tool-providing
- **Tools**: `memory` (Memory) — yantrikdb_remember, yantrikdb_recall, yantrikdb_forget, yantrikdb_conflicts, yantrikdb_relate, yantrikdb_tasks, yantrikdb_resolve_conflict
- **Description**: YantrikDB — self-maintaining memory for Hermes with canonicalization, contradiction tracking, recency-aware ranking, explainable recall, and pluggable embedders (bundled potion-2M default; first-class loaders for the model2vec family and the HF sentence-transformers ecosystem; custom Python embedder class as escape hatch). As of v0.2.0 the default backend is in-process (`pip install` and go); HTTP-to-server is optional for HA cluster setups.

## Standalone Desktop Plugins

> Plugins in `desktop-plugins/` without a `.hermes-package.json` — these are
> not visible to `hermes plugins list` (no Python component) and must be scanned
> from disk directly.

| Plugin | Source | plugin.js size | Description |
|--------|--------|----------------|-------------|
| `hermes-home-dashboard` | bundled | 120584 bytes | Built-in Hermes Desktop home dashboard: grid-layout workspace with ascii art, clock, gateway status, session list, cron jobs, system stats, and analytics. |

## Sync

This reference is machine-generated from the live Hermes environment:

- `python3 hermes-agent/scripts/sync-installed-plugins.py` — regenerate from live env
- `python3 hermes-agent/scripts/sync-installed-plugins.py --check` — verify no drift
- Data sources: `hermes plugins list --json`, `.install-metadata.json`, `config.yaml`, `hermes tools list`, `desktop-plugins/` dir scan
- CI note: when no local Hermes installation is found, the gate skips gracefully (exit 0)

