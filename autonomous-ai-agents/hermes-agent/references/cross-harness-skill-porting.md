# Cross-Harness Skill Porting — making one skill corpus auto-trigger on N agent runtimes

Distilled from obra/superpowers v6.3.0 `docs/porting-to-a-new-harness.md` (827 lines) + `docs/windows/polyglot-hooks.md` + the shipped hook/plugin code (MIT). Use when: porting a skill set to another harness (Claude Code, Codex, Cursor, Gemini CLI, OpenCode, pi, Copilot CLI...), or designing your own agent-plugin that must inject context at session start.

## The three components every integration needs

1. **Skills** — harness-agnostic content; the source of truth shared verbatim by every runtime. Write them to name ACTIONS ("dispatch a subagent", "read a file"), never tool names. One skill body then runs unedited on all runtimes.
2. **Tool mapping (per-harness)** — action -> real-tool translation, in a per-harness reference file and/or inline in the bootstrap injector. Get REAL machine tool names from the harness itself: ask a live session "list the exact machine names of every tool you can call" — never copy from docs or old sessions (stale model names hard-error on some runtimes).
3. **Bootstrap (per-harness)** — at EVERY session start, inject a small meta-skill that teaches "skills exist; check for one before ANY response". **The bootstrap is the entire integration.** Without it the skill files are inert: present on disk, never invoked.

**Two rules:** (1) skills name actions, not tools — porting adds mapping + injector, NEVER edits skill bodies to swap tool names. (2) everything ships through the harness's OWN install mechanism; a port must not hand-edit user config (`~/.gemini/config/AGENTS.md`, `settings.json`, `.bashrc`...). If the installer can't carry the bootstrap, surface that limitation — never bridge it by editing user files.

## Hard requirement: automatic session-start injection

The harness must inject text into context at every session start with NO per-session opt-in (hook stdout, in-process lifecycle callback, or install-declared instructions file). "User pastes a prompt each time" = not a port; the acceptance test below will fail.

**Acceptance test:** clean session, message exactly `Let's make a react todo list` -> PASS only if the design/brainstorming skill auto-triggers BEFORE any code is written. Smoke check first: ask the model to describe its skills — if it can't, bootstrap isn't loading; fix that before bothering with the acceptance test.

## The three integration shapes (they compose)

| Shape | Mechanism | Reference implementation |
|---|---|---|
| **A: shell hook** | session-start command prints JSON whose field/nesting DIFFERS per harness | Claude Code / Cursor / Copilot CLI hooks |
| **B: in-process plugin** | JS/TS module with lifecycle callbacks; mutate the message array | OpenCode (`.js`), pi (`.ts`) |
| **C: instructions file** | extension-declared context file loaded every session (`contextFileName`, `@`-includes) | Gemini CLI, Antigravity |

Decide separately: where do skills get DISCOVERED vs how does the BOOTSTRAP reach the model. Both must ride the install mechanism.

### Shape A gotchas (shell hooks)
- **JSON contract per harness** — Claude Code `{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext}}`, Cursor `{additional_context}`, Copilot/SDK-standard `{additionalContext}`. Emitting wrong or EXTRA fields = silent failure OR double injection (Claude reads both without dedup). Detect via env vars (`CLAUDE_PLUGIN_ROOT` vs `CURSOR_PLUGIN_ROOT` vs `COPILOT_CLI`) and order branches so a harness that sets an earlier branch's var isn't shadowed.
- **Hook-config schema varies** too: Cursor uses `"version":1`, lowercase `sessionStart` key, relative command, no matcher/type/async; Claude Code uses `matcher:"startup|clear|compact"`. Copy the closest existing file, not a canonical template.
- A hook SYSTEM is not a session-start EVENT — one real harness had "SessionStart" strings in its binary (telemetry) but only pre/post-tool + stop events. Confirm the specific event can write to model context.

### Shape B gotchas (in-process plugins)
- Inject as a **user-role message, NOT system** — system messages bloat tokens when repeated every turn and multiple system messages break some models. Don't "fix" it back.
- **Dedup guard:** lifecycle callbacks fire repeatedly (per agent step vs per turn differ by harness); check for the bootstrap marker before injecting; cache content at module level. Matching a stable tag beats custom constants.
- **Compaction:** re-inject after history compaction, AFTER leading summary messages.
- Message-object shape is per-harness and INCOMPATIBLE between references — discover yours from its API; copying an object literal verbatim fails silently.

### Shape C gotchas (instructions files)
- Only works because the file ships INSIDE the installed extension and the manifest declares it; never substitute "edit the user's global AGENTS.md".
- **Don't trust `@`-include expansion — prove it with a unique-marker test:** a Gemini-derived harness accepted `@./path` syntax but treated it as a hint (model MAY read it) instead of guaranteed inline expansion. If the marker isn't in context without a tool call, INLINE the content.
- Plugin installers silently strip UNDECLARED files — if your bootstrap file vanishes from installs, declare it via a `contextFileName`-style field; don't give up and edit user config.

## Windows: cross-platform polyglot hooks (shell-hook shape only)

One dispatcher file valid as BOTH batch and shell script (`hooks/run-hook.cmd` is the canonical implementation):
```bash
: << 'CMDBLOCK'      # Unix: heredoc on no-op -> entire CMD block ignored
@echo off            # Windows: cmd.exe runs this, finds bash (Program Files\Git\bin\bash.exe
...                  #   then PATH), execs the named script; exit /b stops before Unix section
CMDBLOCK
exec bash "${SCRIPT_DIR}/${SCRIPT_NAME}" "$@"    # Unix path
```
Rules it enforces: **hook scripts are extensionless** (`session-start`, not `.sh`) because Claude Code on Windows auto-prepends `bash` to any command containing `.sh`; no per-OS script variants; silent exit 0 when bash is absent (plugin works, injection skipped). Related trap: declare `"shell": "bash"` in hook config — a quoted-path command string breaks PowerShell parsing and cmd.exe quote-stripping on paths with metacharacters like `(`.

## Driving TUI harnesses for verification (tmux recipe)

Interactive REPLs can't be driven by piping stdin; run detached in tmux:
```bash
mkdir -p /tmp/port-smoke && tmux new-session -d -s port-test -c /tmp/port-smoke '<launch>'
sleep 12                       # real TUIs take longer than you think (model handshake)
tmux capture-pane -t port-test -p   # clear any first-run/trust modal BEFORE typing prompts
tmux send-keys -t port-test 'What are your superpowers?'; sleep 0.4; tmux send-keys -t port-test Enter
# text and Enter as SEPARATE send-keys with a beat between — together they race on some TUIs
sleep 8; tmux capture-pane -t port-test -p   # POLL in a loop until the turn finishes
tmux kill-session -t port-test               # always clean up
```
Gotchas: pre-trust your scratch dir or answer trust prompts via send-keys (a detached session stalls SILENTLY on modals); one-shot `run "prompt"` modes are frequently flaky/auth-gated — be ready to do everything through tmux; long conversations need the harness's own transcript file as record of truth, not capture-pane.

## Distribution channels (per ecosystem)

Native plugin marketplace (`/plugin install`) / external fork synced by script with anchored include-exclude lists + PR automation / git-URL extension install / package-manifest fields in repo-root `package.json` / local installer staging dir. Version discipline: register every versioned manifest in a single bump config (path+field pairs) so one script keeps them in lockstep; an unregistered new manifest ships stale forever. When adding a per-harness dotdir, add it to the OTHER harnesses' sync excludes so it doesn't leak into their distributions.

## Verification doctrine (the repo's own standards)

- **Unique-marker test** for any injection mechanism: inject nonsense through the suspected path, fresh session, confirm it reached context WITHOUT a tool call.
- **A fork does not inherit its parent's behavior.** A Gemini-derived CLI may expose the parent's manifest fields and `@`-syntax yet honor neither — verify with markers, never assume.
- Byte-diff for pure reorders; grep-residue lists as acceptance criteria (every remaining platform mention must fall in a documented carve-out); one concern per commit even on trivial-looking edits.
