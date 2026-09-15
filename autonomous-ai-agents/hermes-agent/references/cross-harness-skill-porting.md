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

## OpenAI/Codex plugin packaging (verified from petergyang/no-ai-slop v1.0.6)

The second real-world reference implementation for this doc — a minimal skills-only ChatGPT/Codex plugin, MIT: https://github.com/petergyang/no-ai-slop. Anatomy of the whole distributable (14 files total):

| Piece | Role |
|---|---|
| `.codex-plugin/plugin.json` | The manifest. Required top-level keys: `name`, `version`, `description`, `author{name,url}`, plus optional `homepage`/`repository`/`license`/`keywords`. `"skills": "./skills/"` points at the skill tree (each `<skill>/SKILL.md`). The `interface{}` object is what surfaces in ChatGPT: `displayName`, `shortDescription`, `longDescription`, `developerName`, `category`, `capabilities[]`, `defaultPrompt[]` (**max 3 entries, each ≤128 chars — enforced by the build script**), plus optional `websiteURL`, `privacyPolicyURL`, `termsOfServiceURL`, `brandColor`, `composerIcon`, `logo`. |
| `agents/openai.yaml` (repo root AND inside `<skill>/`) | Per-skill agent metadata: `interface.display_name` ("/no-ai-slop" slash-command form), `short_description`, and a `default_prompt` that references the skill by `$name` — "Use $no-ai-slop to remove AI patterns from this draft...". The root copy is for repo-level discovery; the per-skill copy travels with the packaged skill. |
| `scripts/build_plugin.py` (127 lines, stdlib only) | Build + validate in one pass: (1) `validate_source` — fail on missing manifest/interface keys or prompt violations BEFORE building anything; (2) stage a clean tree into `dist/<name>/` by explicit copy of each file (no glob-copy — the package is an allowlist); (3) zip with sorted entries for deterministic output, named `<slug>-plugin-<version>.zip`; (4) `validate_build` — assert the staged set EQUALS the expected file set exactly (`expected != actual` → fail), byte-compare packaged SKILL.md/eval.md against canonical sources, and check zip integrity. A `--check` flag runs everything then deletes all build output (CI-friendly: validate without artifacts). |
| `.github/workflows/plugin.yml` | Two jobs: `validate` on every PR + push to main (checkout → setup-python 3.12 → run build script → upload the zip as a workflow artifact) and `release`, gated on `refs/tags/v*` with `needs: validate`, which downloads that SAME validated artifact, then attaches it via `gh release create "$GITHUB_REF_NAME" ... --generate-notes --verify-tag`. Note the security posture from commit history ("Harden plugin workflow permissions"): job-level `permissions:` scoped to minimum (validate = contents read; release adds actions read + contents write), and every action pinned by full SHA with a version comment. |
| `plugin-submission.md` | The marketplace submission dossier: positioning, starter prompts, 5 positive test cases + 3 negative test cases ("user asks whether AI wrote it → do not guess authorship; offer pattern audit"), release notes. Keep this file in the repo — it doubles as the acceptance spec for the skill's trigger behavior. |
| `PRIVACY.md` / `TERMS.md` | One-paragraph each: skills-only plugin, no server/account/telemetry ("text is processed by the ChatGPT or Codex product where you use the plugin"), MIT + user-responsible-for-output disclaimer. The manifest's privacyPolicyURL/termsOfServiceURL point at these blob URLs — they must exist for submission. |
| `dist/` in `.gitignore` | Build output never committed; CI rebuilds from source every time, so a stale zip can't ship. |

Key patterns worth copying: **the build script is the spec** (manifest schema + package contents are both machine-checked before anything ships); **release attaches only what validate produced** (artifact handoff between jobs, not a second build — no chance of shipping an unvalidated artifact); and **negative test cases in the submission doc define when the skill must NOT trigger**, which is as important as the positive ones for marketplace review.

**Live incident: canonical-ID collision in the ChatGPT/Codex Plugin Directory (issue #43, verified 2026-08-28).** Two different published products — No AI Slop (Peter Yang v1.0.6) and "Slop Curator" (Mamdouh Aboammar v1.0.1) — both installed with the SAME canonical plugin ID `no-ai-slop@openai-curated-remote` but different remote IDs (`plugins_6a…b4d7f` vs `plugins_6a…5b`). Reproduced on Codex desktop (macOS) + CLI x2: account catalog returned 248 curated records with only 247 unique names; all hosts exposed only the *other* product's cache/runtime. Impact list from the report: install/cache ownership, explicit invocation, automatic skill selection, version updates/promotion, uninstall-by-name — all ambiguous when two products share a canonical ID. Lesson for anything you publish to a shared directory: **the display-name slug is not yours until verified** — check the live catalog for an existing entry with your name before submission (a fork/clone of a popular skill inherits its identity namespace), and treat "same display name, different remote ID" as the collision signature when debugging "my plugin updates into someone else's".

**More patterns from upstream's open/closed community PRs (not in main at mine time).**
- **Self-linting: `scripts/lint_docs.py`** — a style skill lints its OWN README/SKILL/eval against the mechanically-checkable subset of its own rules, because "a style checker that breaks its own rules is the one kind of bug that costs it credibility." Implementation details worth stealing: the banned-word list is parsed LIVE from SKILL.md (regex on `Banned outright:`) so the linter can't drift from the rule; per-file em-dash budgets (`{README: 0, SKILL: 2, eval: 2}`); colon-case check with proper-noun and introduces-speech carve-outs; frontmatter skipped via a structural `---` fence walk (not line-count guessing). The killer check is **cross-file pattern coverage**: every bolded pattern name in the rules file must be reachable by its head noun in the eval/checklist file — catches exactly the drift where a rule gets added or renamed in one file only. This is the same philosophy as this repo's doc-count gate + mutation self-test, applied to prose skills; it generalizes: any skill that ships paired files (rules ↔ checks, SKILL ↔ references) should have a coverage check between them.
- **Tag/archive consistency in release CI** — the archive name comes from `plugin.json`'s version, the release name comes from the tag. Bump the tag without bumping the manifest and the glob `dist/*.zip` SILENTLY publishes the previous version's zip under the new release name (the glob hides the mismatch). Fix: before attaching, assert `dist/<slug>-plugin-${TAG#v}.zip` exists (fail with a "bump the manifest" message), then attach by EXACT path instead of glob. General rule for any artifact pipeline: never hand a versioned artifact to release tooling through a glob — name it from the tag and verify existence first.
- **PR #41's AI-review workflow carries two transferable CI patterns.** (a) *Check out the BASE branch, never the PR head, in any job that runs with repository secrets* (`ref: ${{ github.event.pull_request.base.sha }}`) — a malicious PR cannot alter code that executes alongside its own secrets; this repo's `ci.yml` is currently immune because it references NO repo secrets (contents-read only), but re-verify before adding any secret-consuming job. (b) *LiteLLM gotcha:* `OPENAI__API_BASE` is a GLOBAL override, not scoped to the openai/ provider — setting it unconditionally routes gemini/ and other cloud calls at the local endpoint and fails them; pass it only for locally-served (`openai/`-prefixed) model ids. Their trigger design (label-gated `apex-review` + comment-driven re-runs, bot senders excluded, per-PR concurrency with cancel-in-progress) is a sane shape for opt-in AI review on any repo.
- **Windows path-separator bug in their exact-file-set check (PR #36).** `validate_build` compared packaged vs expected file sets via `str(path.relative_to(...))` — backslashes on Windows, so the equality silently failed/falsely passed depending on how the other side was built; fix is `.as_posix()` before any string-level comparison. Verified live on this host: `'profiles-export/' in str(Path('C:/x/profiles-export/foo'))` is **False** (backslash path). This repo's tools are already protected — audit-skills.py/check-links normalize with `str(rel).replace("\\", "/")`, the index generators use `.as_posix()` — but keep that discipline: any NEW code doing string-level set-equality or substring matching on `relative_to()` output must posix-normalize first, while pathlib-native operations (`mkdir(tmp / rel.parent)`) are safe as-is.

## Verification doctrine (the repo's own standards)

- **Unique-marker test** for any injection mechanism: inject nonsense through the suspected path, fresh session, confirm it reached context WITHOUT a tool call.
- **A fork does not inherit its parent's behavior.** A Gemini-derived CLI may expose the parent's manifest fields and `@`-syntax yet honor neither — verify with markers, never assume.
- Byte-diff for pure reorders; grep-residue lists as acceptance criteria (every remaining platform mention must fall in a documented carve-out); one concern per commit even on trivial-looking edits.
