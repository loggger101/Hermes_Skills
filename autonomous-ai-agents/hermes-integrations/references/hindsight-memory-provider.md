---
description: "Hindsight as a Hermes memory provider: catalog install/update/pin, three modes, recall/retain config, why recall comes back empty, and bank/tag rules that prevent cross-user leaks"
source_repo: vectorize-io/hindsight (MIT)
tested_version: "Plugin docs and guides read via GitHub API at v0.10.2 (2026-09-29). Hermes CLI flags and the catalog entry were checked live on Hermes Agent v0.21.5 (2026.9.24), Windows. Hindsight itself was NOT installed or run here: this machine's active provider is yantrikdb, and it has no LLM key configured for Hindsight"
verified_date: "2026-10-05"
---

# Hindsight memory provider for Hermes

Hindsight is an external memory provider ("long-term memory with knowledge graph, entity resolution, and multi-strategy
retrieval"). `installed-plugins.md` records it on the other machine; the doc below is what to do and what goes wrong.
Only **one** external provider can be active at a time (checked: `hermes memory --help`), and the built-in
`MEMORY.md`/`USER.md` store is always on unless switched off.

## Install, update, pin (CLI checked live)

```bash
hermes plugins search hindsight            # catalog row seen: memory / community / pinned 1.2.1 @ d56c4acd
hermes plugins install hindsight --enable  # --enable / --no-enable skip the confirmation prompt (scripts, unattended)
hermes memory setup                        # choose hindsight; writes memory.provider and ~/.hermes/hindsight/config.json
hermes memory status                       # provider + Status: available
hermes plugins check-updates               # read-only; `plugins list` flags update_available
hermes plugins update hindsight            # move to the catalog's current pin
```

Facts from the plugin docs (source-read) that bite:

- `hermes plugins enable` does **not** activate a memory provider. Providers are `kind: exclusive`; the config key
  `memory.provider: hindsight` (written by `memory setup`) does it. Other providers are listed by `hermes memory status`.
- **Nothing updates the plugin on its own.** `hermes update` reinstalls its dependencies but leaves the checkout; run
  `hermes plugins update hindsight`. The catalog is re-fetched at most every 6 hours. Re-running `install` refuses with
  "already exists".
- An update that finds new plugin dependencies asks `<plugin> declares Python dependencies` and **waits**: an unattended
  `hermes update` stalls there.
- Pin a version: `hermes plugins install vectorize-io/hindsight/hindsight-integrations/hermes --force --ref <40-char SHA>`.
  `--ref` takes one full 40-character commit SHA (the local help says "exactly one immutable 40-character Git commit
  SHA"), not a tag. A pinned install is skipped by `plugins update`; reinstall with a new `--ref`. Install from the source
  path without `--ref` to track `main` (unreviewed).
- The old standalone pip plugin `hindsight-hermes` is deprecated; on current Hermes its tools fail with
  `Timeout context manager should be used inside a task`. The same message came from `hindsight-embed` 0.10.0; the plugin
  floor is `hindsight-client >= 0.10.1` and `hindsight-embed >= 0.10.1`.
- Memories do not live in the Hermes tree: Cloud, or for local embedded `~/.hindsight/profiles/<profile>` plus an embedded
  PostgreSQL under `~/.pg0/instances/hindsight-embed-<profile>/`. Reinstalling the plugin does not touch them.
- This repo's `installed-plugins.md` lists hindsight at 1.0.1 for the other machine; the catalog now pins 1.2.1. Run
  `hermes plugins check-updates` on that machine before assuming parity.

## Modes

| Mode | Needs | Notes |
|---|---|---|
| `cloud` (default) | `HINDSIGHT_API_KEY` in `~/.hermes/.env` | `api_url` defaults to the vendor cloud |
| `local_embedded` | an LLM key (`HINDSIGHT_LLM_API_KEY`), any OpenAI-compatible endpoint works (`openai_compatible` + `llm_base_url`; LM Studio, llama.cpp, vLLM, Ollama) | Daemon runs as a separate process, starts on first use, stops after 5 min idle. First boot 60-90 s (`initdb`). ~200 MB download. Embeddings and reranking run locally |
| `local_external` | a reachable Hindsight URL (+ key if set) | No daemon management; share a `bank_id` across a team |

Daemon logs: `~/.hermes/logs/hindsight-embed.log` (startup) and `~/.hindsight/profiles/<profile>.log` (runtime). Web UI for
embedded mode: `hindsight-embed -p hermes ui start`. Windows notes from the vendor: set `PYTHONUTF8=1` and
`PYTHONIOENCODING=utf-8` (checkmark/box characters crash cp1252), consider `LongPathsEnabled`, and exclude `~/.hindsight/`
from Defender if the embedded Postgres is quarantined or slow.

## Config that changes behaviour (`~/.hermes/hindsight/config.json`)

| Key | Default | Why it matters |
|---|---|---|
| `memory_mode` | `hybrid` | `hybrid` = auto-injection + tools; `context` = injection only (tools hidden by design); `tools` = no auto-recall at all |
| `auto_recall` / `auto_retain` | true / true | per-turn recall before the reply, retain after |
| `recall_types` | **`observation`** | Raw `world`/`experience` facts are no longer returned by auto-recall **or** the `hindsight_recall` tool. Restore with `"observation,world,experience"` |
| `recall_sync` | false | default recalls in the background and injects on the **next** turn |
| `recall_prefetch_method` | `recall` | `reflect` = LLM synthesis (slower, costs tokens). Older guides call this `prefetch_method` |
| `recall_budget` | `mid` | low 50-100 ms, mid 100-300 ms, high 300-500 ms (vendor figures) |
| `bank_id` / `bank_id_template` | `hermes` / unset | template placeholders `{profile} {workspace} {platform} {user} {session}`; `hermes-{profile}` isolates per Hermes profile; empty placeholders collapse |
| `retain_every_n_turns` | 1 | raise to cut LLM extraction cost |
| `recall_indicator` / `retain_indicator` | true | print a status line into the channel: turn off for customer-facing bots |

Environment overrides: `HINDSIGHT_API_KEY`, `HINDSIGHT_LLM_API_KEY`, `HINDSIGHT_API_LLM_BASE_URL`, `HINDSIGHT_API_URL`,
`HINDSIGHT_BANK_ID`, `HINDSIGHT_BUDGET`, `HINDSIGHT_MODE`. Disable the flat-file store so the model does not prefer it:
`hermes config set memory.memory_enabled false` and `memory.user_profile_enabled false` (this removes the built-in `memory`
tool entirely).

## "Memory is not recalling": order of checks

Doc drift to keep in mind: an April 2026 guide uses key names (`prefetch_method`) and a port (`9077`) that the current
integration page does not repeat; trust the current page and your `config.json`.

1. `hermes memory status` shows hindsight active and `Status: available`. `not available` in `local_embedded` means the
   plugin's own packages are missing from the venv: `hermes pm repair`, restart.
2. `memory_mode` is not `tools`.
3. Backend healthy: cloud key present in `.env`; embedded daemon log clean (for a local server `curl http://localhost:<port>/health`).
4. **Do a controlled test across two turns**: state a distinctive fact, let the reply finish, ask about it on the *next*
   turn. Retain is asynchronous (`retain_async: true`) and extraction is an LLM call, so same-turn checks fail by design.
5. Ask for `hindsight_recall` explicitly. Works while auto-injection does not => mode, hooks (`pre_llm_call` /
   `post_llm_call` need a Hermes build with lifecycle hooks) or `recall_types`.
6. The bank is the bank you think: print `bank_id` after any migration or manual edit.
7. The built-in `memory` tool is not winning over Hindsight (see above). Set `"debug": true` in the config for provider logs.

## Retain and recall rules (vendor best-practices, source-read)

- A **bank** is an isolated store; banks never share data. Auto-created on first use; set `retain_mission` /
  `bank_mission` before ingesting.
- Retain raw content, not your own summary: the LLM extracts facts, entities and relationships and the raw text is not
  stored verbatim. Pre-summarising loses entity links and timestamps.
- Always give `context` (a specific description of what the content is) and `timestamp` (ISO 8601; omitting it disables
  temporal ranking).
- `document_id` is an upsert key: the same ID deletes and reprocesses the previous version. Use a stable session ID and
  re-send the growing conversation; a random UUID per call makes duplicates.
- Tags scope visibility and are the only filterable field (`metadata` is not filterable). Match modes: `any` (default) and
  `all` **also return untagged memories**; `any_strict` / `all_strict` do not. For per-user partitioning use
  `any_strict` (the vendor lists `any` on a multi-tenant bank as an anti-pattern because untagged items come back to every user).
- Recall runs four strategies in parallel (semantic, BM25, graph, temporal). Use `recall` when the agent reasons over
  facts or needs citations; `reflect` when Hindsight should answer.
- Observations (consolidated beliefs with evidence and proof counts) are built after retain, not by it. Mental models are
  stored reflect answers for repeated queries: one narrow model per knowledge dimension, not "everything about the user".

## Memory Defense (secrets in memory)

Per-bank, **off by default**, applies to future retain calls only: 45 regex patterns (provider keys such as `sk-ant-`,
`ghp_`, `AKIA...`, payment and similar tokens) replaced with `[REDACTED:type]` (`redact`) or the item dropped (`block`;
a fully blocked request returns 422). Enable by PATCHing the bank config with
`{"memory_defense": {"enabled": true, "rules": [{"on": "sensitive_data", "action": "redact"}]}}`. Existing memories are
not rescanned. Turn this on before pointing an agent that handles credentials at a shared bank; it is regex-based, so
it does not catch free-form secrets.
