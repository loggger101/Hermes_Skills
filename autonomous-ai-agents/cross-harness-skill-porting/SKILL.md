---
name: cross-harness-skill-porting
description: "Port one skill corpus to many agent harnesses."
version: 1.0.0
author: Hermes Agent (promoted from hermes-agent references; obra/superpowers and no-ai-slop source reads)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, porting, harness, session-start, hooks, plugins, codex, claude-code, gemini, opencode]
    related_skills: [hermes-agent, hermes-agent-skill-authoring, skill-intake-and-release, hermes-extensions, enricher-pipeline-architecture]
---

# Cross-harness skill porting

## What This Skill Does

Explains how to make one set of skills trigger automatically on several agent runtimes (Claude Code, Codex, Cursor, Copilot CLI, OpenCode, pi, Gemini CLI and others), distilled from obra/superpowers' porting guide and the shipped hook and plugin code, plus the Codex plugin packaging of petergyang/no-ai-slop. Read from source; the acceptance test below is the check.

## When to Use

- Moving a skill collection to another harness, or making one skill set work on several
- Writing a session-start hook, an in-process plugin or an instructions file that loads skills
- Skills are installed but never trigger
- Packaging a skills-only plugin for the Codex or ChatGPT directory
- Not for writing a single skill (`hermes-agent-skill-authoring`), vetting third-party skills (`skill-intake-and-release`), or Hermes themes and plugins (`hermes-extensions`)

## Quick Reference

| Piece | Rule |
|---|---|
| Skills | harness-agnostic text that names actions ("dispatch a subagent"), never tool names; porting never edits skill bodies |
| Tool mapping | one per-harness file; get real tool names by asking a live session to list them |
| Bootstrap | a small meta-skill injected at every session start: "skills exist; check for one before any response". It is the whole integration |
| Shape A | shell hook printing JSON whose fields differ per harness (Claude Code, Cursor, Copilot CLI); extra or wrong fields fail silently or double-inject |
| Shape B | in-process plugin (OpenCode, pi); inject as a user-role message with a dedup guard, and re-inject after compaction |
| Shape C | instructions file declared by the extension manifest (Gemini CLI, Antigravity); prove `@`-includes expand with a unique marker |
| Windows | one polyglot dispatcher valid as both batch and shell for shell-hook harnesses |

## Procedure

1. Confirm the harness can inject text at every session start with no per-session opt-in; if it cannot, it cannot be ported.
2. Write the tool-mapping file and the bootstrap; ship both through the harness's own install mechanism, never by editing the user's global config.
3. Pick the shape (hook, plugin, instructions file) and copy the closest existing implementation rather than a generic template.
4. Run the unique-marker test: inject a nonsense string, start a fresh session, confirm it reached context without a tool call.
5. Run the acceptance test: in a clean session send `Let's make a react todo list` and pass only if the design or brainstorming skill triggers before any code is written.
6. For a Codex plugin, let the build script validate the manifest and package contents, and have the release job attach only what validation produced.

## Pitfalls

- Treating a hook system as a session-start event; confirm the specific event can write to model context.
- Injecting as a system message every turn, which bloats tokens.
- Forks that expose a parent's manifest fields but ignore them.
- Plugin installers that silently strip undeclared files.
- A tag bumped without the manifest version, so the release glob publishes the old archive.

## Verification

- [ ] The marker reached context without a tool call
- [ ] The acceptance test passed on a clean session
- [ ] No user config file was edited by the install
- [ ] Skill bodies are byte-identical across harnesses

## References

- `references/cross-harness-skill-porting.md` - components, session-start requirement, the three shapes and their gotchas, Windows polyglot hooks, tmux verification, distribution channels, Codex plugin packaging, verification doctrine
