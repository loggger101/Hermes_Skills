# Cron Approval Mode

## Overview

Cron jobs run without a user present to approve tool calls. The **cron approval mode** config (`approvals.cron_mode` in `config.yaml`) controls whether dangerous tool calls (typically `terminal` commands matching Tier-2 or Tier-3 patterns) are **auto-approved** or **blocked** in cron context.

- `approvals.cron_mode: deny` (default) — dangerous commands are **blocked**. No human can respond.
- `approvals.cron_mode: approve` — dangerous commands are **auto-approved** without human intervention.

This setting affects only the **approval gate** — it does not bypass `execute_code`'s hard block (see below).

## When to set it

Set `cron_mode: approve` whenever a cron job uses tools that may trigger dangerous-command checks:

- `terminal` — the most common case. Any command matching a Tier-2 pattern (e.g. `git push`, `npm publish`, `rm`, `chmod`, `chown`, `sudo`) or Tier-3 pattern (e.g. destructive file ops, network-bound writes) triggers the gate.
- `file` / `write_file` — writing to sensitive paths (e.g. `~/.ssh/`, `/etc/`).
- `web` / `browser` downloads to arbitrary paths.

Jobs that only use safe tools (`skill_view`, `skill_manage`, `read_file`, `search_files`, `web_search`) don't need this setting. But if a job calls `terminal` for anything beyond trivial commands, set it to `approve`.

## How to set it

```bash
# Via the CLI (preferred)
hermes config set approvals.cron_mode approve

# Or edit config.yaml directly
# approvals:
#   cron_mode: approve
```

Then re-run the job:
```bash
hermes cron run <job_id>
```

## How to tell it was the problem

### In the audit log (errors.log)

```
BLOCKED: Command flagged as dangerous (…) but cron jobs run without a user present to approve it.
```

### In the session transcript

The agent sees the blocked tool result:
```json
{"status": "not_approved", "error": "BLOCKED: Command was flagged (…) and auto-approved by smart approval"}
```

### In job execution state

The run may appear to fail with a cryptic error, or the agent may silently skip the failing step and continue (producing incomplete output). Check `last_status` in `cron/jobs.json` — it may still show `ok` even though a terminal call was blocked mid-run.

## execute_code hard-block

**Important:** Setting `cron_mode: approve` does **NOT** enable `execute_code` in cron jobs. The `execute_code` tool runs arbitrary local Python (including subprocess calls that bypass shell-string approval checks) and is **hard-blocked** in all cron contexts by design:

```
BLOCKED: execute_code runs arbitrary local Python (including subprocess calls that bypass shell-string approval checks). Cron jobs run without a user present to approve it
```

Cron jobs that need shell access must use `terminal` instead. The `terminal` tool respects `cron_mode` and will auto-approve flagged commands when set to `approve`.

## Config file location

This setting lives in the **profile config** file, not the global config:

```
~/AppData/Local/hermes/profiles/<profile>/config.yaml
```

For the `the-skill-maker` profile:
```
C:\Users\Owner\AppData\Local\hermes\profiles\the-skill-maker\config.yaml
```
