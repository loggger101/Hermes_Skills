---
name: hermes-extensions
description: "Hermes themes, desktop/TUI/Python plugins, pets."
version: 1.0.0
author: Hermes Agent (promoted from hermes-agent references and templates)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, plugins, themes, skins, tui-widgets, desktop-plugins, petdex, python-plugins, extensions]
    related_skills: [hermes-agent, hermes-agent-skill-authoring, inspecting-hermes-desktop-dom, fastmcp, mcporter]
---

# Extending Hermes

## What This Skill Does

Covers the five ways to extend a Hermes install without touching its source: a **skin** (one YAML file that themes the CLI, TUI and desktop together), a **desktop plugin** (one ESM file for panes, statusbar items, commands, routes), a **TUI widget** (one `.mjs` file for docked panels or modal tools), a **Python agent plugin** (`~/.hermes/plugins/` with hooks and skills), and **pets** (animated mascots). Each has a reference and, where useful, a working template. Setup, CLI, providers, configuration and troubleshooting stay in `hermes-agent`.

## When to Use

- "Make me a synthwave theme", match brand colours, or change a symbol colour
- A new desktop UI element, a Cmd+K command, or surfacing computed data in the app
- A live TUI panel (ticker, clock, countdown) or a modal picker bound to a slash command
- A Python plugin with `register_skill` or `pre_llm_call` hooks, or bootstrap injection
- Installing, selecting or diagnosing a pet
- Not for installing, configuring or troubleshooting Hermes itself (`hermes-agent`), writing skills (`hermes-agent-skill-authoring`), or inspecting the desktop app's DOM (`inspecting-hermes-desktop-dom`)

## Which reference

| You want | Reference and template | Where it lives |
|---|---|---|
| A theme/skin | `references/themes.md` + `templates/skin.yaml` | `<hermes-home>/skins/<name>.yaml`; missing keys inherit the `default` skin; theming is semantic, so one key colours every element playing that role |
| A desktop UI element | `references/desktop-plugins.md` + `templates/plugin.js` | `$HERMES_HOME/desktop-plugins/<id>/plugin.js` (loads enabled, hot reloads); or the desktop half of a unified plugin at `plugins/<id>/desktop/plugin.js` (opt-in toggle in Settings, Plugins) |
| A TUI widget | `references/tui-widgets.md` + `templates/clock.mjs` | `~/.hermes/tui-widgets/<name>.mjs`; hot-loads in about a second; `/widgets-reload` rescans; id becomes the slash command |
| A Python agent plugin | `references/python-agent-plugins.md` | `~/.hermes/plugins/<name>/` with `__init__.py` exposing `register(ctx)` and `plugin.yaml` |
| A pet | `references/petdex.md` | `hermes pets list|install|select|scale|show|off|remove|doctor` |

## Procedure

1. Pick the surface from the table; read its reference's prerequisites first (the TUI must be running with `hermes --tui`; the desktop app must be installed for desktop plugins).
2. Start from the template where one exists and keep its export shape.
3. Desktop plugins: the only import surface is `@hermes/plugin-sdk` plus `react`, and the file is not compiled, so write UI with `jsx()` calls, not JSX syntax.
4. Python plugins: pass `pathlib.Path`, not `str`, to `ctx.register_skill`; a `str` silently disables the whole plugin. Inject bootstrap text through `pre_llm_call` returning `{"context": ...}`. After installing, restart sessions and check `skills_list`.
5. Skins: write `<hermes-home>/skins/<name>.yaml`, activate it with `hermes config set`, confirm the change landed.
6. Pets: run `hermes pets doctor` when a pet does not show; truecolor half-block rendering is the fallback without a graphics terminal.

## Pitfalls

- A desktop plugin "not appearing" is often the opt-in toggle for the desktop half of a unified package; check it before debugging.
- Hermes has no post-compaction hook, so a long session that compacts over its first turn loses injected bootstrap text; start a fresh session.
- Python plugin failures are silent: a missing skill in `skills_list` means the plugin died in `register()`; check gateway logs before debugging content.
- TUI widgets do not render in the classic CLI or messaging platforms; fetch failures must land as an error phase, never a crash.
- Auto-open (`sdk.openWidget`) re-docks on every `/widgets-reload`; only add it when asked.

## Verification

- [ ] The extension loaded (toast, `skills_list`, `/widgets-reload`, `hermes pets doctor`) with no error
- [ ] The change is visible on every surface it targets
- [ ] The Python plugin's skills resolve with `skill_view("plugin:skill-name")`
- [ ] No secrets or personal paths were written into a shared file

## References

- `references/themes.md` - author a skin: element-to-key table, fallbacks, activation, live iteration
- `references/desktop-plugins.md` - desktop plugin contract: two on-disk doors, `@hermes/plugin-sdk` surface, host state atoms, hot reload, Python backend namespace
- `references/tui-widgets.md` - TUI widget apps: `register(sdk)`, ambient docked panels and modal overlays, slash commands, error phases
- `references/python-agent-plugins.md` - plugin anatomy, the registration traps that silently kill a plugin, bootstrap injection, install and verify loop
- `references/petdex.md` - petdex gallery, `hermes pets` commands, config and diagnosis
- `templates/skin.yaml`, `templates/plugin.js`, `templates/clock.mjs` - starting points for a skin, a desktop plugin and a TUI widget
