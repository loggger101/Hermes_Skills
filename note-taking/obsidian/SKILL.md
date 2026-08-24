---
name: obsidian
description: "Read, search, create, and edit notes in the Obsidian vault."
version: 1.0.0
author: Teknium (teknium1), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Obsidian, Notes, Markdown, Vault]
    related_skills: [apple-notes, notion]
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## When to Use

- Reading notes from an Obsidian vault by file path
- Searching for specific content across all notes
- Listing all notes in the vault or a specific folder
- Creating new notes with markdown content
- Appending content to existing notes
- Adding wikilinks (`[[Note Name]]`) to connect related notes

**Skip when:** You need graph-view analysis, backlink traversal beyond filesystem links, or plugin-specific features — those belong to the Obsidian GUI, not this skill.

## What This Skill Does

Provides a file-tool-based workflow for interacting with Obsidian vaults stored on disk. Obsidian stores notes as plain Markdown files in a folder structure, so this skill uses `read_file`, `write_file`, `patch`, and `search_files` to manipulate them — no Obsidian API or plugin required.

## Vault Path Resolution

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `${HERMES_HOME:-~/.hermes}/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Prerequisites

- An Obsidian vault existing on disk
- The vault path (from `OBSIDIAN_VAULT_PATH` env var or `~/Documents/Obsidian Vault` as fallback)
- No additional software required — file tools handle Markdown natively

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.

## Pitfalls

- **Path resolution**: Never pass unresolved `$VAR` paths to file tools — always resolve to absolute paths first
- **Spaces in vault path**: The default `~/Documents/Obsidian Vault` path contains spaces — use file tools, not shell commands
- **File encoding**: Obsidian uses UTF-8 — ensure `write_file` saves in UTF-8
- **Large files**: Reading notes with 2000+ lines requires pagination (`read_file` with offset/limit)
- **Concurrent edits**: If the user is actively editing in Obsidian, changes may conflict — warn before overwriting

## Verification

- [ ] Vault path was resolved to an absolute path before any file operation
- [ ] Notes were read back after creation/editing to verify content
- [ ] Wikilinks point to existing note files (or are intentional forward references)
- [ ] No shell variable paths were passed to file tools
