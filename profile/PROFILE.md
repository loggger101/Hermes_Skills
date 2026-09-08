# Profile Documentation

This directory documents the Hermes Agent profile state that this skills repository was compiled from and synced with.

> **Verified 2026-09-08** against the live profile: model/provider/base-URL, agent + memory + compression + guardrail settings and the CLI toolset list were re-read from `config.yaml` (mirrored here), and the skill counts were re-counted on disk. The Curator Ledger table below is a historical record and is not re-verified per pass.

## Profile Location

```
C:\Users\Owner\AppData\Local\hermes\
```

This is the **default** profile (no named profile subdirectory under `profiles/`). The profile root is `C:\Users\Owner\AppData\Local\hermes\` with skills at `C:\Users\Owner\AppData\Local\hermes\skills\`.

## Active Configuration

See [config.yaml](./config.yaml) for the full configuration. Key settings:

### Model
- **Default model:** `qwen3.8-27b@q4_k_xl`
- **Provider:** `lmstudio`
- **Base URL:** `http://127.0.0.1:42069/v1`

### Agent
- Max turns: 500
- Verbose: false
- Reasoning effort: `ultra` (agent) / `xhigh` (delegation, max_iterations 250)

### Terminal
- Backend: `local`
- Timeout: 180s
- Container support: persistent (5GB memory, 50GB disk)

### Browser
- Backend: `browser-use`
- Inactivity timeout: 120s

### Memory
- Memory enabled: true
- User profile enabled: true
- Memory char limit: 80000
- User char limit: 20000

### Compression
- Enabled: true (threshold: 0.5, target ratio: 0.2, protect last 5 messages, max 3 attempts)

### Tool Loop Guardrails
- Warnings enabled: true, Hard stop enabled: false
- Warn after: 2 exact failures, 3 same-tool failures, 2 idempotent no-progress
- Hard stop after: 5 exact failures, 8 same-tool failures, 5 idempotent no-progress

## Toolsets

### CLI (active) — 16 toolsets
`browser`, `clarify`, `code_execution`, `computer_use`, `cronjob`, `delegation`, `file`, `image_gen`, `memory`, `session_search`, `skills`, `terminal`, `todo`, `tts`, `vision`, `web`

Known plugin toolsets (cli): `a2a`, `spotify`.

### Builtin (available)
Same as above plus: `context_engine`, `discord`, `discord_admin`, `homeassistant`, `spotify`, `stt`, `video`, `video_gen`, `x_search`, `yuanbao`

### Platform-specific
Telegram, Discord, WhatsApp, Slack, Signal, Home Assistant, QQBot, Yuanbao, Teams, Google Chat

## Curator Ledger History

The `.curator_ledger.jsonl` tracks all curator-managed skill operations. Key events:

| Date | Action | Skill | Actor |
|------|--------|-------|-------|
| 2026-08-17 | create (4 devops skills) | ssh-remote, docker-containers, sqlite-queries, rest-api-client | agent |
| 2026-08-23 | create + write_file (3 refs) | autonomous-repo-cronjob | curator |
| 2026-08-23 | create (10 mattpocock skills) | mattpocock-diagnosing-bugs, mattpocock-domain-modeling, mattpocock-to-tickets, mattpocock-handoff, mattpocock-code-review, mattpocock-writing-for-agents, mattpocock-improve-codebase-architecture, mattpocock-research, mattpocock-codebase-design, mattpocock-finishing-a-development-branch, etc. | agent |
| 2026-08-23 | delete | mattpocock-static-analysis | agent (absorbed into mattpocock-security-review) |
| 2026-08-23 | create | mattpocock-subagent-driven-development (autonomous-ai-agents) | agent |
| 2026-08-23 | patch | mattpocock-subagent-driven-development | agent |

**Note:** `mattpocock-static-analysis` was deleted by curator and absorbed into `mattpocock-security-review` (see [audit notes](../docs/archive/audit-notes-skills-repo-pass.md) in the repo). The `mattpocock-subagent-driven-development` duplicate in `autonomous-ai-agents/` was removed in favor of the more complete `software-development/` version.

## Bundled Manifest

The `.bundled_manifest` file lists 82 bundled skills that ship with Hermes. These are the official bundled skills verified by SHA256 hash. The remaining ~45 skills in the repository are optional/local skills.

## Skill Usage Stats

The `.usage.json` file tracks per-skill usage metadata:
- `created_at` / `created_by` (agent or installed)
- `last_used_at` / `last_viewed_at`
- `use_count` / `view_count`
- `patch_count` / `patch_generation`
- `state` (active/archived)
- `pinned` (whether the skill is pinned)

## Cron Job Authoring

Skills for writing self-contained, autonomous cronjob prompts. The core patterns are in `autonomous-repo-cronjob` (repo automation with two-agent split) and `cron-job-authoring` (general scheduling). See the [README cronjob section](../README.md#cron-job-authoring) in the repo root for the full skill index and tool API reference.

## Sync Status

The local skills directory is in parity with this repository: **all 167 repo skills are present locally**, plus 2 local-only by design (`research/rss-feeds`, `social-media/reddit-reading`), for 169 local `SKILL.md` files. Verified 2026-09-08 by comparing frontmatter names across both trees.

Previously, 13 skills were missing from local (12 from `data-science/` and 1 `cron-job-authoring`). These have been synced from the repository. The local profile also has 1 pre-installed skill (`hermes-agent`) that is core to Hermes itself — the repository contains a curated copy.

See [MISSING-FROM-LOCAL.md](./MISSING-FROM-LOCAL.md) for the detailed sync history.

## Files in This Directory

| File | Description |
|------|-------------|
| [PROFILE.md](./PROFILE.md) | This document — profile overview |
| [config.yaml](./config.yaml) | Full active configuration |
| [MEMORY.md](./MEMORY.md) | Persistent memory notes (agent-discovered facts) |
| [USER.md](./USER.md) | User profile (preferences, environment, conventions) |
| [MISSING-FROM-LOCAL.md](./MISSING-FROM-LOCAL.md) | Sync status: all 127 repo skills now local (was 13 missing) |
| [.curator_ledger.jsonl](./.curator_ledger.jsonl) | Curator operation log (verbatim) |
| [.bundled_manifest](./.bundled_manifest) | Official bundled skill checksums (verbatim) |
| [.usage.json](./.usage.json) | Per-skill usage statistics (verbatim) |
