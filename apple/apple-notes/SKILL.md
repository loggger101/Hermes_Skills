---
name: apple-notes
description: "Manage Apple Notes via memo CLI: create, search, edit."
version: 1.0.1
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [Notes, Apple, macOS, note-taking]
    related_skills: [obsidian, apple-reminders]
prerequisites:
  commands: [memo]
---

# Apple Notes

Manage Apple Notes via the `memo` CLI: create, search, list, edit, and export notes. Notes sync across all Apple devices via iCloud.

## When to Use

- User asks to create, view, or search Apple Notes
- Saving information to Notes.app for cross-device access (iPhone/iPad/Mac)
- Organizing notes into folders
- Exporting notes to Markdown/HTML

**Skip when:** Obsidian vault management (load `skill_view(name='obsidian')`), Bear Notes (separate app), or quick agent-only notes (use the `memory` tool).

## What This Skill Does

Uses the `memo` CLI tool to interact with Apple Notes.app via AppleScript. Covers: listing notes, searching by content, creating new notes, editing existing notes, moving between folders, and exporting to Markdown/HTML.

## Prerequisites

- **macOS** with Notes.app and iCloud sync enabled
- Install: `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
- Grant Automation access to Notes.app when prompted (System Settings → Privacy → Automation)
- Verify: `memo notes` should list your notes

## Quick Reference

### View Notes
```bash
memo notes                        # List all notes
memo notes -f "FolderName"        # Filter by folder
memo notes -s "query"             # Search notes (fuzzy)
```

### Create Notes
```bash
memo notes -a                     # Add a note (opens your $EDITOR)
memo notes -a -f "FolderName"     # Add a note into a specific folder
```

`-a`/`--add` is a bare flag — it opens your `$EDITOR` to compose the note; it does not take a title argument. Use `-f/--folder` to target a folder. Set `$EDITOR` first (e.g. `export EDITOR=vim`).

### Edit Notes
```bash
memo notes -e                     # Interactive selection to edit
```

### Delete Notes
```bash
memo notes -d                     # Interactive selection to delete
```

### Move Notes
```bash
memo notes -m                     # Move note to folder (interactive)
```

### Export Notes
```bash
memo notes -ex                    # Export to HTML/Markdown
```

## Detailed Workflow

### 1. List and search
Start with `memo notes` to see your folders and notes. Use `-s` for fuzzy search:
```bash
memo notes -s "meeting notes"  # Find notes containing "meeting notes"
```

### 2. Create a note
```bash
export EDITOR=nano  # or vim, code, etc.
memo notes -a -f "Meetings"
```
Your editor opens — write the note content, save, and close.

### 3. Edit an existing note
```bash
memo notes -e
# Select the note from the interactive picker
# Your editor opens with the current content
```

### 4. Export to Markdown
```bash
memo notes -ex
# Select the note → choose export format → specify output path
```

## Pitfalls

- **Editor not set**: `memo notes -a` fails silently if `$EDITOR` is unset — always set it first
- **Interactive prompts**: Require terminal PTY access — use `pty=true` in terminal tool if needed
- **Folder names with spaces**: Wrap in quotes — `-f "My Folder"`
- **Large note lists**: `memo notes` without filters can be slow — always search first
- **Sync delays**: iCloud sync can take seconds to minutes — newly created notes may not appear immediately on other devices
- **Attachments**: `memo` cannot edit notes containing images or attachments — the note must be plain text

## Verification

- [ ] `memo` is installed and accessible (`which memo`)
- [ ] Automation permission granted (check System Settings → Privacy → Automation)
- [ ] Notes list loads without errors
- [ ] Creating a note works and appears in Notes.app
- [ ] Search returns expected results
- [ ] Export produces valid Markdown/HTML

## Related Skills

- `skill_view(name='obsidian')` — for filesystem-first Markdown vault management
- `skill_view(name='apple-reminders')` — for task management via Reminders.app
