---
description: The agent's persistent memory — notes and user profile that carry across sessions (the "brain" part of this second brain).
---

# memories

The live Hermes agent memory store, mirrored here so the second brain is self-contained. These files are injected into every session as system context; they are **not** skills and have no frontmatter-driven tooling — treat them like any other tracked document (edit deliberately, keep entries compact).

- [`MEMORY.md`](./MEMORY.md) — agent notes: environment facts, conventions, verified findings from research passes. The largest file in this directory; high-signal only by design.
- [`USER.md`](./USER.md) — user profile: who the user is, working style, standing preferences and security rules.

*Regenerated from live frontmatter — keep in sync with `tools/gen-skills-index.py`.*
