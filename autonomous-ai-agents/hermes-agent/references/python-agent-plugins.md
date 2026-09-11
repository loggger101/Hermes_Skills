# Python Agent Plugins (the `~/.hermes/plugins/` system) — verified API notes

Source: working reference implementation in obra/superpowers v6.3.0 `.hermes-plugin/` (`__init__.py`, MIT; install via `hermes plugins install obra/superpowers --enable`) plus its README Hermes section. Facts below are from the shipped code's comments, which record empirical verification dates — treat them as tested, not guessed.

## Anatomy of a plugin package

```
<plugin-dir>/
  __init__.py        # exposes register(ctx)
  plugin.yaml        # name, version, description, author, provides_hooks: [pre_llm_call]
  skills/<name>/SKILL.md   (optional — registered with the native skill loader)
```

`register(ctx)` is called at load; `ctx.register_skill(name, path)` and `ctx.register_hook(event, fn)` are the registration surface.

## Verified API facts (the traps that silently kill a plugin)

1. **`ctx.register_skill` requires a `pathlib.Path`, not `str`.** Passing a str raises AttributeError internally — and Hermes SILENTLY disables the whole plugin rather than surfacing it. Check: after install, does ANY skill from the plugin appear in `skills_list`?
2. **Bootstrap/context injection path = `pre_llm_call` returning `{"context": ...}`.** The context is appended to the first turn's user message (hook signature includes `is_first_turn`). Verified empirically 2026-07-23: `on_session_start` return values are IGNORED, and `ctx.inject_message` REFUSES from that hook. Do not "fix" a working pre_llm_call injector to on_session_start.
3. **Hermes has no post-compaction hook.** A very long session that compacts over its first turn loses the injected bootstrap — skills stop triggering; start a fresh session (this is documented in superpowers' README as expected behavior, not a bug).
4. **Skills register with the native loader** so `skill_view("plugin:skill-name")` works after install; if namespaced lookup returns "not found", fall back to reading `<skills-dir>/<name>/SKILL.md` directly (the sanctioned no-skill-tool path — see cross-harness-plugin-porting.md).
5. **Skill discovery layout:** for a git-clone install the plugin dir is the repo root, so `../skills` relative to `.hermes-plugin/`; for flattened installs `skills/` sits next to the module. Resolve BOTH candidates and raise loudly if neither matches — "a bootstrap that silently skips is how a broken install masquerades as a working one."
6. **Frontmatter stripping:** when inlining SKILL.md content into an injected message, strip YAML frontmatter (`^---\n...\n---\n`) but keep the body verbatim; wrap injected guidance in `<EXTREMELY_IMPORTANT>` and include an "already loaded — do not try to load this again" note so the model doesn't re-invoke itself.

## Bootstrap injection pattern (what superpowers does)

On `is_first_turn`: return `{"context": "<EXTREMELY_IMPORTANT>\n<marker line>\nYou have <capability>.\n<body of meta-skill verbatim>\n<harness tool-mapping table>\n</EXTREMELY_IMPORTANT>"}`. The marker line exists for dedup if the hook ever fires twice; matching a stable tag (the EXTREMELY_IMPORTANT wrapper) is more robust than a custom constant.

## Install/verify loop

```
hermes plugins install <git-url> --enable   # git-clone layout
# restart active sessions — plugin loads at session start
skills_list                                # expect the plugin's skills present
skill_view("plugin:meta-skill")            # namespaced lookup works?
```

If a skill is missing from `skills_list`, the plugin died in `register()` (usually trap #1) — check gateway logs before debugging content.
