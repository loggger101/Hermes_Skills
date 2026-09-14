# Missing From Local (Skills in Repository but Not in Local Profile)

This document tracks skills that exist in the repository but may not be present
in the local Hermes skills directory at `C:\Users\Owner\AppData\Local\hermes\skills\`.

## Sync Status

**Verified 2026-09-13 (round-19 integrity pass).** Nothing in the repository is missing from
the local profile: all **202** repo skills are present locally, verified by a full bidirectional
inventory diff of every file (CRLF-normalized hashes), not just `SKILL.md` frontmatter names.

The local tree carries no extra *skills* beyond the repo — only hub/curator infrastructure that is
local-only **by design** and never pushed: `.hub/`, `.usage.json`, `.curator_ledger.jsonl`,
`.bundled_manifest`, plus per-skill telemetry sidecars. (An orphaned `web/DESCRIPTION.md` stub in
the local tree from an early import was removed on 2026-09-14; the sync script now also refuses to
re-introduce such stubs — only top-level dirs containing a SKILL.md are treated as skill categories.)

### Historical note: former "local-only by design" skills are now IN the repo

| Skill | Resolution (round-16, commit 282e0f0) |
|---|---|
| `research/rss-feeds` | Was hub-installed and kept out of the catalog; committed to git with audit repairs so a fresh clone is complete |
| `social-media/reddit-reading` | Same — now tracked in the repo |

Re-check method (use this, not file counts): full bidirectional inventory diff across both trees
with CRLF-normalized SHA-256 per relative path; skill directories and raw file counts drift for
reasons unrelated to coverage. `profile/MISSING-FROM-LOCAL.md` is the standing record of that check's result.

## History

### 2026-09-08 (superseded by the round-19 verification above)

All **167** repo skills were present locally; the two extras in the local tree at the time
(`research/rss-feeds`, `social-media/reddit-reading`) were hub-installed and deliberately kept out
of the repo catalog. That state changed in round 16 when both were committed to git.

### Previously Missing (Now Synced) — original 2026-08-24 record

The section below is the original record, when 13 skills were missing locally and were synced in
from the repository. It is kept as a historical note; every row has long since been resolved.

| # | Category | Skill Name | Notes |
|---|----------|-----------|-------|
| 1 | data-science | `build-systems-data` | Data build pipeline skill — now local |
| 2 | data-science | `cli-tool-craft` | CLI tool development craft skill — now local |
| 3 | data-science | `evolutionary-ml` | Evolutionary ML techniques — now local |
| 4 | data-science | `model-export-deploy` | Model export and deployment — now local |
| 5 | data-science | `orbital-mechanics-data` | Orbital mechanics data processing — now local |
| 6 | data-science | `python-craft` | Python development craft skill — now local |
| 7 | data-science | `python-data-science` | Python data science workflows — now local |
| 8 | data-science | `sql-for-data` | SQL for data analysis — now local |
| 9 | data-science | `static-site-seo` | Static site SEO optimization — now local |
| 10 | data-science | `streamlit-dashboards` | Streamlit dashboard creation — now local |
| 11 | data-science | `test-infra-ml` | ML infrastructure testing — now local |
| 12 | data-science | `verification-culture` | Verification culture practices — now local |
| 13 | autonomous-ai-agents | `cron-job-authoring` | Cron job authoring patterns — now local |

## Local-Only Skill (historical)

At the time of the original record, the local profile had **1 skill** that did not exist in the
repository:

| # | Skill Name | Local Path | Notes |
|---|-----------|------------|-------|
| 1 | `hermes-agent` | `C:\Users\Owner\AppData\Local\hermes\skills\autonomous-ai-agents\hermes-agent` | Pre-installed by Hermes core; the repo version is a curated copy |

This no longer applies: `autonomous-ai-agents/hermes-agent` exists in both trees and stays in
sync via the bidirectional inventory diff.

## Action Items

- [x] Sync all 13 missing skills from the repository to local profile (2026-08-24)
- [x] Verify repo coverage by frontmatter-name diff, then upgrade to full file-level diff (round-16 onward)
- [x] Commit former hub-only skills (`rss-feeds`, `reddit-reading`) into the repository (round 16)
- [x] Document sync status in this file with a dated verification section
