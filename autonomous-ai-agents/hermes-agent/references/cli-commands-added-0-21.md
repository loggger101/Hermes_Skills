# Hermes CLI commands the older references do not cover (live `--help`, v0.21.5)

Source: the installed CLI on this machine, `hermes --version` -> **Hermes Agent v0.21.5+5369.g34f8ec3 (2026.9.24)**, upstream
34f8ec3b; repo HEAD at review time `9b6fc23` (2026-10-05). Method: parse the "positional arguments" block of `hermes --help`
(71 top-level commands) and look for `hermes <name>` anywhere under `autonomous-ai-agents/hermes-agent/`; **34 commands were
not mentioned**. Then `hermes <cmd> --help` was run for each of them plus four documented names absent from the top-level list.
Every command returned exit 0. **Only `--help` was run: none of the actions below was executed**, so behaviour is as the help
text states it. `cli-reference.md` remains the base; this file adds what it lacks.

Names `gui` (really `hermes desktop`), `login` (deprecated), `photon` and `pm` do exist but are **not listed** in the top-level
help, so a list-diff against `hermes --help` misses them; probe by running `hermes <name> --help`.

## Safety, stop switches and housekeeping

| Command | What the help says |
|---|---|
| `hermes pause [--reason R]` / `hermes resume` | global emergency stop: halts **new** work only (cron dispatch, kanban dispatch, new gateway turns); in-flight work is never killed; `resume` removes the ESTOP sentinel and dispatch continues on the next tick |
| `hermes worktree {list,ls,audit,prune}` | reclaim `.worktrees/` made by `hermes -w` sessions: `list` (default) classifies each tree by age, size, verdict, reason; `prune` removes safe trees and fully merged local branches. Never deletes uncommitted tracked changes, unique unpushed commits or in-use trees; untracked-only scratch is archived to `~/.hermes/archive/worktree-prune/` first |
| `hermes checkpoints {status,list,prune,clear,clear-legacy}` | the shadow git repo used to snapshot working directories before `write_file`/`patch`/terminal calls: size per project, prune orphans and GC, `clear` wipes **all `/rollback` history**, `clear-legacy` removes only v1 migration archives |
| `hermes backup [-o OUT] [-q] [-l LABEL] [-k N]` | zip of config, skills, sessions and data (not the codebase); `--quick` snapshots only config, `state.db`, `.env`, auth and cron; after a full backup keeps the newest N (default 3, 0 keeps all) `hermes-backup-*.zip` |
| `hermes import ZIP [--force]` | restore a backup into the Hermes home |
| `hermes uninstall [--full\|--gui\|--data] [--dry-run] [-y]` | `--data` removes only user data (the one mode that works on Nix, bundled-app and Docker installs); `--gui` removes only the desktop app; `--dry-run` prints what would go |
| `hermes approvals {suggest,test}` | `suggest` mines past approvals from the session DB and proposes `command_allowlist` entries; `test` dry-runs the approval verdict for a command without executing it |
| `hermes security audit` | one-shot OSV.dev scan of the Hermes venv, Python deps declared by plugins under `~/.hermes/plugins/`, and pinned `npx`/`uvx` MCP servers in `config.yaml`; does not scan global packages or editor/browser extensions |
| `hermes dump [--show-keys]` | compact plain-text setup summary for support; `--show-keys` shows first/last 4 characters of API keys instead of set/not set |
| `hermes debug {share,delete}` | `share` uploads system info plus recent logs to a paste service and prints a URL (asks first; `--yes`, `--lines N`, `--expire D`, `--local` to print only, `--no-redact`, `--nous` private storage); `delete <url>` removes it |

## Usage, cost and prompt budget (offline or read-only)

- `hermes insights [--days 30] [--source cli|telegram|discord...]`: token usage, costs, tool patterns and activity from session history.
- `hermes usage [--provider P] [--json]`: the account-limit block `/usage` prints (Codex 5 h and weekly windows, plan, banked resets;
  Anthropic OAuth windows; OpenRouter credits); **exit 1** when no credential is configured or the fetch fails.
- `hermes prompt-size [--platform P] [--json]`: the fixed prompt budget of a fresh session (system prompt, skills index, memory,
  user profile, tool-schema JSON), **offline, no API call**. Pairs with `references/context-budget-and-cache-placement.md`.
- `hermes monitoring status`: OTLP export of service-health metrics and redacted diagnostics to an operator-set endpoint;
  "content-free by construction" (no prompts, messages, tool args or usage analytics); configured under `monitoring.*`.
- `hermes journey [--reveal 0..1] [--play] [--json] {list,delete,edit}`: timeline of learned skills and memories; `delete`
  archives a learned skill (or removes a memory) by node id, `edit` opens it in `$EDITOR`. Aliases `learning`, `memory-graph`.

## Networking, credentials and integrations

| Command | What the help says |
|---|---|
| `hermes egress {install,setup,start,stop,restart,reload,status,disable,config}` | manages **iron-proxy**, an optional TLS-intercepting egress firewall that swaps proxy tokens for real API credentials before requests leave a sandbox; disabled by default; `reload` hot-reloads `proxy.yaml` with no restart or dropped connections |
| `hermes vault {add,list,rm,sources}` | locally encrypted store for logins, cards and addresses; the agent sees handles and login identifiers only, passwords are injected server-side by `browser_vault_fill` on the exact origin they were saved for; `sources` shows detected 1Password and Bitwarden (on automatically); `list` never shows values |
| `hermes browser close-profile` | **destructive**: kills the browser process tree holding the real profile (`browser.use_real_profile`) so Hermes can copy it; unsaved tabs are lost; run only with the user's explicit OK |
| `hermes peer {add,set,list,ls,remove,rm,dm,run,status,stop}` | register other Hermes gateways as peers: `peer dm <peer>[/<agent>] "..."` delivers into the remote agent's Bot Chat over its API server and prints the reply; `run` starts an async turn (`--idempotency-key`) and returns a run id; `status`/`stop` take `<peer> <run_id>`. The peer must run the `api_server` platform; its `API_SERVER_KEY` is kept in `~/.hermes/.env`. Exit 0 ok, 1 delivery/peer error, 2 usage |
| `hermes sync {status,pull,push,now,enable,disable,device,propose}` | Skill Sync: moves your own skills between devices, and (for an organisation) pulls its shared skills and lets you `propose` yours back; `enable <skill>` includes a skill in your sync |
| `hermes logout [--provider nous\|openai-codex\|xai-oauth\|spotify]` | remove stored credentials and reset provider config (default: active provider) |
| `hermes login ...` | **deprecated**: use `hermes auth` for credentials, `hermes model` for the provider, `hermes setup` for the wizard |
| `hermes slack manifest` | print or write a Slack app manifest with every gateway command registered as a native slash command |
| `hermes whatsapp` / `hermes whatsapp-cloud` | personal-account Baileys bridge paired by QR code, versus the official Meta WhatsApp Business Cloud API adapter (needs a Business account and a public webhook URL) |
| `hermes lsp {status,list,install,install-all,restart,which}` | the LSP layer that powers post-write semantic diagnostics in `write_file`/`patch`; `install-all` installs every server with a known auto-install recipe; `restart` tears down running clients (the next edit respawns) |
| `hermes computer-use {install,status,doctor,permissions,screen}` | installs/checks the pinned `cua-driver` for the `computer_use` toolset (macOS, Windows, Linux); `doctor` runs its `health_report`; `permissions` is macOS Accessibility + Screen Recording; `screen` is the headless Bot Desktop on Linux |
| `hermes photon {setup,status,install-sidecar,telemetry}` | Spectrum SDK sidecar (device login, project, user, `npm install` in the sidecar dir); `telemetry` toggles SDK telemetry |

## Migration and project tooling

- `hermes import-agent [claude-code|codex] [--source DIR] [--dry-run] [--overwrite] [--yes] [--sync]`: one-command import of another
  agent's setup: `CLAUDE.md`/`AGENTS.md` instructions, permission allowlists, MCP servers, skills and memories. Always previews;
  **API keys and credentials are never imported** (run `hermes setup`). `--sync` re-imports every previously imported source whose files
  changed (registry in `HERMES_HOME/import-sync.json`), without prompts. Complements `references/cross-harness-skill-porting.md`.
- `hermes claw {migrate,cleanup,clean}`: from OpenClaw to Hermes (settings, memories, skills, API keys); `cleanup` archives leftovers.
- `hermes migrate {xai,relay}`: diagnose and optionally rewrite `config.yaml` for retired models or deprecated settings (`xai`: models
  retired 2026-05-15; `relay`: legacy `HERMES_NEMO_RELAY_ATIF_*/ATOF_*` exporter variables into `relay-plugins.toml`).
- `hermes codex-runtime migrate`: re-projects `mcp_servers` and installed codex plugins into the managed block of `~/.codex/config.toml`;
  toggling the runtime stays the chat command `/codex-runtime on|off`.
- `hermes verify [path] [--detect-only] [--save] [--skip-start] [--phase bootstrap|build|test|start] [--port N] [--timeout 600] [--ready-timeout 60] [--json]`:
  detects how a project builds, tests and starts (or loads `.hermes/environment.json`), then runs bootstrap -> build -> test -> start
  in the background -> poll readiness -> teardown. `--detect-only` runs nothing and prints the recipe as JSON.
- `hermes pm {lock,install,env,doctor,repair,gc,bundle,status,update}`: Hermes' own package manager (relock `uv.lock`, install, compare installed state with the
  lockfile, rebuild, GC the store, stage a relocatable payload, machine-readable sync receipt).
- `hermes console`: a curated command REPL; "not a raw shell and does not expose the full Hermes CLI".

## Serving and the desktop app

- `hermes serve [--port 9119] [--host 127.0.0.1] [--skip-build] [--isolated] [--stop] [--status]`: headless JSON-RPC/WebSocket backend
  for the desktop app and remote clients. **`--insecure` is a deprecated no-op**: since the June 2026 hardening a public bind always
  requires an auth provider; bind 127.0.0.1 and tunnel instead. `--skip-build` is for Windows Scheduled Tasks and CI without npm
  (pre-build with `cd web && npm run build`). `--isolated` runs a profile-scoped server instead of attaching to the machine-level one.
- `hermes gui` is `hermes desktop`: installs workspace Node deps, builds the unpacked Electron app for this OS and launches it
  (`--source` runs `electron .`, `--build-only`, `--skip-build`, `--force-build`, `--local`, `--ignore-existing`, `--hermes-root`, `--cwd`).

## Re-running the freshness check

The two-step check above is mechanical: (1) list `hermes --help` top-level commands, (2) grep the skill for `hermes <name>`.
Run it after each Hermes release (`gh release list -R NousResearch/hermes-agent`); v0.21.5 was released 2026-09-24 and the installed
build reports `+5369` after that tag in its version string.
