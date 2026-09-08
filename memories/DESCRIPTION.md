---
description: The agent's persistent memory — notes and user profile that carry across sessions (the "brain" part of this second brain).
---

# memories

The live Hermes agent memory store, mirrored here so the second brain is self-contained. These files
are injected into every session as system context; they are **not** skills and have no
frontmatter-driven tooling.

- [`MEMORY.md`](./MEMORY.md) — agent notes: environment facts, conventions, verified findings from
  research passes. The largest file in this directory; high-signal only by design.
- [`USER.md`](./USER.md) — user profile: who the user is, working style, standing preferences and
  security rules.

## These are exports — edit the live files, not these

The sync is **one-way, local → repo**: `sync_memories()` in `tools/sync-hermes-skills.py` copies from
the local Hermes memories directory into this one. An edit made *here* is not read by the agent and
is overwritten by the next weekly sync (Sunday 2 AM). To change what the agent remembers, edit the
live files under `%LOCALAPPDATA%/hermes/memories/` (`MEMORY.md`, `USER.md`) and let the sync mirror
them here — or copy them across in the same commit.

Entry format is one fact per paragraph, separated by a lone `§` line.

Because this directory is a machine-generated export, `tools/check-links.py` skips it: entries quote
markdown-shaped fragments as prose (a note about fixing a `[cat/](./cat/DESCRIPTION.md)` link is text,
not a link to follow), and the repo cannot fix a link inside a file the sync will overwrite anyway.

**Before committing an update, scan for credentials.** These files record live environment detail; the
standing rule is that keys, tokens and passwords are replaced with `[REDACTED]` and never committed.

*Last mirrored from the live store: 2026-09-08 (26 entries).*
