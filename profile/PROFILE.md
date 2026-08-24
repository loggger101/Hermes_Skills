# Profile Documentation

This directory documents the current Hermes Agent profile state that this skills repository was compiled from and synced with.

## Profile Location

```
C:\Users\Loggg\AppData\Local\hermes\
```

This is the **default** profile (no named profile subdirectory under `profiles/`). The profile root is `C:\Users\Loggg\AppData\Local\hermes\` with skills at `C:\Users\Loggg\AppData\Local\hermes\skills\`.

## Active Configuration

See [config.yaml](./config.yaml) for the full configuration. Key settings:

### Model
- **Default model:** `qwen/qwen3.6-35b-a3b`
- **Provider:** `lmstudio`
- **Base URL:** `http://127.0.0.1:1231/v1`

### Agent
- Max turns: 500
- Verbose: false
- Reasoning effort: medium

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
- Memory char limit: 22000
- User char limit: 2375

### Compression
- Enabled: true (threshold: 0.5, target ratio: 0.2, protect last 20 messages)

### Tool Loop Guardrails
- Warnings enabled: true, Hard stop enabled: false
- Warn after: 2 exact failures, 3 same-tool failures, 2 idempotent no-progress
- Hard stop after: 5 exact failures, 8 same-tool failures, 5 idempotent no-progress

## Toolsets

### CLI (active)
`bfl`, `browser`, `clarify`, `code_execution`, `computer_use`, `cronjob`, `delegation`, `file`, `image_gen`, `memory`, `session_search`, `skills`, `terminal`, `todo`, `tts`, `vision`, `web`

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

**Note:** `mattpocock-static-analysis` was deleted by curator and absorbed into `mattpocock-security-review` (see [NOTES.md](./NOTES.md) in repo root). The `mattpocock-subagent-driven-development` duplicate in `autonomous-ai-agents/` was removed in favor of the more complete `software-development/` version.

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

## Sync Status

The local skills directory at `C:\Users\Loggg\AppData\Local\hermes\skills\` has been synced with this repository. All 114 local skills that exist in both locations are now identical (repo → local sync applied on 2026-08-24).

The repository contains 13 additional skills that originated from the `the-skill-maker` and `the-memory-controller` profiles (which are no longer present on this machine) — these are cataloged in [MISSING-FROM-LOCAL.md](./MISSING-FROM-LOCAL.md).

## Files in This Directory

| File | Description |
|------|-------------|
| [PROFILE.md](./PROFILE.md) | This document — profile overview |
| [config.yaml](./config.yaml) | Full active configuration |
| [MEMORY.md](./MEMORY.md) | Persistent memory notes (agent-discovered facts) |
| [USER.md](./USER.md) | User profile (preferences, environment, conventions) |
| [MISSING-FROM-LOCAL.md](./MISSING-FROM-LOCAL.md) | 13 skills in repo but not in local profile |
| [.curator_ledger.jsonl](./.curator_ledger.jsonl) | Curator operation log (verbatim) |
| [.bundled_manifest](./.bundled_manifest) | Official bundled skill checksums (verbatim) |
| [.usage.json](./.usage.json) | Per-skill usage statistics (verbatim) |
