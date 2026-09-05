---
description: Snapshot of the owner's active Hermes profile (config + identity docs) for reference and portability — not skills; excluded from skill audit/sync push.
---

# Profile Snapshot

A point-in-time copy of one live Hermes Agent profile, kept here so any agent or machine can see exactly how this second brain is configured:

| File | What it is |
|---|---|
| `config.yaml` | Model/provider config (local LM Studio default + fallback), tool settings. **Contains no secrets** — tokens are redacted; never add them back. |
| `PROFILE.md` | The agent's identity/role document for this profile. |
| `MEMORY.md`, `USER.md` | Copies of the persistent memory files (canonical live versions sync to top-level `memories/`). |
| `MISSING-FROM-LOCAL.md` | Notes on items present in this snapshot but absent from a given local environment, if any. |

**Rules:** treat as read-only reference. The weekly sync cronjob excludes `profile/` from skill push (it is not skill content). If you need the *current* memory state, use top-level [`memories/`](../memories/) — it is what the live agent actually reads and writes.
