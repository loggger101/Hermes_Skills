# Troubleshooting

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider: `pip install faster-whisper` or set API key
3. In gateway: `/restart`. In CLI: exit and relaunch.

### Tool not available
1. `hermes tools` — check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues
1. `hermes doctor` — check config and dependencies
2. `hermes auth` — re-authenticate OAuth providers (or `hermes auth add <provider>`)
3. Check `.env` has the right API key
4. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### Skills not showing
1. `hermes skills list` — verify installed
2. `hermes skills config` — check platform enablement
3. Load explicitly: `hermes -s name` (or the skill's own `/<name>` slash command)

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

Common gateway problems:
- **Gateway dies on SSH logout**: Enable linger: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires `systemd=true` in `/etc/wsl.conf` for systemd services to work. Without it, gateway falls back to `nohup` (dies when session closes).
- **Gateway crash loop**: Reset the failed state: `systemctl --user reset-failed hermes-gateway`

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **Slack bot only works in DMs**: Must subscribe to `message.channels` event. Without it, the bot ignores public channels.
- **Windows-specific issues** (`Alt+Enter` newline, WinError 10106, UTF-8 BOM config, line endings): see `references/windows-quirks.md`.

### Auxiliary models not working
If `auxiliary` tasks (vision, compression, session_search) fail silently, the `auto` provider can't find a backend. Either set `OPENROUTER_API_KEY` or `GOOGLE_API_KEY`, or explicitly configure each auxiliary task's provider:
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

### "Reset permissions" / auto-approving everything
See `references/security-privacy.md` — wipe the "Always allow" stores, don't touch yolo mode.

### Plugin fails to load on every gateway start
Symptom: repeated WARNING lines in `~/.hermes/logs/gateway.log`, e.g. `Plugin 'X' not loaded: uses N import path(s) removed on <date>` or `Failed to load plugin 'X': No __init__.py in ...`. Diagnose with:
```bash
grep -hE "not loaded:|Failed to load plugin" ~/.hermes/logs/gateway.log | sed 's/^.*WARNING //' | sort | uniq -c
hermes plugins compat   # lists removed import paths for enabled plugins; clean = no output
```
Two known root causes (home-dashboard, fixed 2026-09-21):
1. **Missing top-level `__init__.py`** — the agent plugin loader hard-fails directory plugins without it (`plugins_loader._load_directory_module`). UI-only plugins still need one: add a no-op stub with docstring + empty `def register(ctx):` (pattern: hermes-ledgerline). Note this is user-plugin territory; the in-tree case where omitting `__init__.py` was load-bearing applies to core's own trees, not installed plugins.
2. **Stale imports of refactored core paths** — e.g. `hermes_cli.web_server.<symbol>` removed 2026-09-14 when web routers moved to `hermes_cli/web_routers/<topic>.py`. Repoint each lazy import to the defining module; verify every target exists in live source AND imports under the core venv before restarting. Commit locally inside `~/.hermes/plugins/<name>` (it's a git clone); do NOT push third-party upstreams.
Fixes apply at next gateway start — grep gateway.log after restart for zero new warnings of that plugin to verify.

### Memory files corrupted / memory tool refuses writes
Symptom: MEMORY.md or USER.md contains truncated mid-word entries, doubled dashes, stray prose (e.g. `cycles: N` footers) from a failed background consolidation; the memory tool then reports `no entry matched '<old_text>'`, and after 3 failures/turn returns TERMINAL "stop retrying" (#42405). The store re-reads disk under lock on every op, so direct file repair is safe — but only if the result round-trips:
1. Back up both files: `cp MEMORY.md MEMORY.md.pre-audit-backup.$(date +%Y%m%d_%H%M%S)` (same for USER.md).
2. Rewrite each as a clean list of entries joined by exactly `\n§\n` — no headers, footers, or prose outside entries; the store rewrites whole files on any op, so leftover non-entry text becomes "external drift" and blocks all future replace/remove (drift guard #26045).
3. Verify round-trip: parse = split on `\n§\n`, strip, drop empties; require `raw.strip() == '\n§\n'.join(parsed)`.
Mid-session edits are safe for prompt caching: the system-prompt block is a frozen load-time snapshot and each memory-tool call re-reads disk. After repair, retry the intended add/replace batch — it now matches real entries.

