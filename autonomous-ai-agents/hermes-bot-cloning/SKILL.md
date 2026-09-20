---
name: hermes-bot-cloning
description: "Clone Hermes profiles to create identical subagent bots"
description_short: "Clone profiles into identical subagent bots"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, bots, profiles, subagents, cloning, group-chat]
    related_skills: [hermes-agent, cron-job-authoring]
---

# Hermes Bot Cloning

## What This Skill Does

Creates identical Hermes bots (profiles) from an existing profile via `hermes profile create --clone-from`. Each clone is a fully independent profile with its own chat history, memory, and skills — but starts with the same config, SOUL.md, credentials, and skill set as the source.

## When to Use

Use when you need multiple bots that share a starting point — e.g., 3 identical subagents for a group chat, or a fleet of specialized agents each seeded from the same base configuration.

## The Procedure

### 1. Verify the source profile

```bash
hermes profile list
```

Confirm the source profile name (e.g., `default`) and that it's configured with the right model, skills, and credentials.

### 2. Clone each bot

```bash
hermes profile create <bot-name> --clone-from <source>
```

For multiple bots, run sequentially — parallel invocations can race on profile directory creation. If one times out (exit 124), check `hermes profile list` to see if it actually succeeded, then re-run only the missing ones.

### 3. Verify all bots exist

```bash
hermes profile list
```

### 4. (Optional) Give bots distinct names/titles

In the Hermes desktop app: Bots tab → right-click a bot → Edit Profile, or edit `~/.hermes/profiles/<bot-name>/SOUL.md`.

## Key Invariants

- **Skills are cloned, not linked** — future updates to the source profile's skills do NOT sync to clones. To sync, re-clone or manually copy the skills directory.
- **Memory is NOT shared** — each profile has its own separate memory store. Clones start with empty memory.
- **Credentials ARE copied** — the `.env` file is cloned, so bots inherit the same API keys/tokens.
- **Bots are fully independent** — they appear in the Bots tab, can be @mentioned in group chats, and can message each other.

## Pitfalls

- **Do not run clones in parallel** — `--clone-from` spawns subshell processes that can race on profile directory creation. Run sequentially and verify with `hermes profile list` after.
- **Clone timeout is 30s hard limit** — if `hermes profile create` exits 124 (timeout), check whether the profile was actually created before re-running. The profile directory may exist even when the command times out.
- **Wrapper scripts go to `~/.local/bin`** — the create command offers to create a `bot-name` wrapper script, but `~/.local/bin` may not be in PATH on Windows. Bots work fine without the wrapper.
- **Clones inherit the source model provider** — if the source uses a local provider (e.g., LMStudio on port 42069), the bot will fail until that server is running. After cloning, run `hermes -p <bot> chat -q "test"` to verify the bot can actually connect. If it times out with a connection error, see references/free-model-discovery.md for how to switch to an online provider.
- **`hermes config set` can write values to the wrong YAML section** — specifically, setting `provider` outside of `model:` creates a stray top-level key that Hermes won't read. Always verify with `hermes config get model.provider --profile <bot>` after config changes. To fix manually, edit `~/.hermes/profiles/<bot>/config.yaml` and ensure the `model:` section has both `default:` and `provider:` keys together.

## References

- references/free-model-discovery.md — discovering free models on Nous Portal, switching bots from paid/local to free online providers, and verifying connectivity.

## Related

- [Hermes Agent](../hermes-agent/SKILL.md) — the hub skill for Hermes itself
- [Cron Job Authoring](../cron-job-authoring/SKILL.md) — for scheduling recurring routines on bots
