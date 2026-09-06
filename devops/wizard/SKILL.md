---
name: wizard
description: "Bash wizard walking a human through manual-only steps."
version: 1.0.0
author: "Matt Pocock (mattpocock/skills, MIT) + Hermes Agent"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [provisioning, credentials, ci-secrets, migration, human-in-the-loop, bash]
    related_skills: [github-auth, ssh-remote]
---

# Wizard

## What This Skill Does

Generates an **interactive bash wizard** that walks a *human* step by step through a manual procedure the agent cannot perform itself — opening each URL, saying exactly what to click and copy, capturing values (secrets hidden), writing them where they belong (`.env`, GitHub secrets/variables), confirming at every stage, showing stages remaining. The UX is already solved by [template.sh](./template.sh): progress gates, cross-platform URL opening (incl. WSL + Windows `explorer.exe`), idempotent `.env` upserts, `gh secret`/`gh variable` writes, closing summary. **Your job is only to scope the procedure and author its stages** below the `STAGES` marker — never hand-edit the library above it; that consistency across wizards is the point.

## When to Use

- Provisioning infrastructure, setting up credentials or CI secrets, walking an unfamiliar third-party dashboard, one-off migrations/cutovers where a human must click in a browser and copy values back.
- **Do NOT use** for steps the agent can perform itself — just do those directly. A wizard is ephemeral by default: built for one run, saved to scratch or `scripts/`, deleted when done; commit it only when the user wants a repeatable setup path in the repo (then link it from the README).

## Process

### 1. Scope the procedure
Read the repo first — don't ask cold. For setup: `.env*`, README, docker-compose files, framework config, and every `secrets.*`/`vars.*` reference in `.github/workflows/*` (each is a value the wizard must produce). For migrations: current state, target state, irreversible actions between them. Then show the user the ordered stages + values each produces; they may add/drop/reorder.
**Done when:** every stage named in order and for each captured value you know (a) where the human gets it, (b) where it's written (`.env`, GitHub secret, both, or nowhere — some stages are pure actions), (c) whether it's secret.

### 2. Map each stage's journey
For each stage write the precise path: which URL, what to do there, where a value appears, which variable it fills ("Dashboard → Developers → API keys → Reveal test key → copy"). Where you don't actually know the current UI or exact command, say so and check docs/ask — never invent steps that may not exist.
**Done when:** every stage traces to concrete instructions a stranger could follow.

### 3. Author the wizard
Copy `template.sh` to the target path; replace the example stage with one `stage` per step in dependency order using the library helpers: `stage`, `say`/`step`, `open_url`, `ask`/`ask_secret`, `write_env`, `set_secret`/`set_var`, `pause`/`confirm`. Set `TOTAL_STAGES`. Hold the template's bar: open the URL *before* asking for its value; `ask_secret` for anything secret; `write_env` every persisted value; `set_secret` only what CI actually needs; `confirm` before any irreversible action. Each stage clears the screen — keep one focused task per stage so nothing scrolls away.

### 4. Verify and hand off
- `bash -n <script>` (and shellcheck if available); `chmod +x`.
- **Don't run it end-to-end yourself** — it opens browsers and blocks on human input. Trace statically instead: every value from step 1 is captured and lands where step 1 said; every `set_secret` name exactly matches a `secrets.*` reference in CI.
- Tell the user how to run it. If repeatable, commit + link from README so the next person runs the script instead of asking an agent.

## Windows note
The template's `open_url` already handles Windows (`explorer.exe`) and WSL (`wslview`). Run the wizard in git-bash/WSL; `.env` upserts are POSIX-shell based, which is fine on this machine (bash available).
