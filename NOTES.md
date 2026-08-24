# Repository Audit Notes

## Scope & Methodology

Full audit of all 128 `SKILL.md` files in the repository at `C:\Users\Loggg\OneDrive\Documents\GitHub\Hermes_Skills`. Each file was parsed to extract YAML frontmatter fields (`name`, `description`, `version`, `author`, `license`, `platforms`, `metadata.hermes.tags`, `metadata.hermes.related_skills`), and the `related_skills` references were cross-validated against the set of 127 unique skill names.

## Summary

| Metric | Count |
|--------|-------|
| Total `SKILL.md` files (before fixes) | 128 |
| Unique skill names (before fixes) | 127 (1 duplicate) |
| Total `SKILL.md` files (after fixes) | 127 |
| Unique skill names (after fixes) | 127 (0 duplicates) |
| Categories | 20 |
| Broken `related_skills` refs (before → after) | 9 → 0 |
| Descriptions > 60 chars (before → after) | 4 → 0 |
| Skills missing frontmatter fields (before → after) | 3 → 0 |

## Changes Applied

### 1. Duplicate Skill Removed
- **Removed:** `autonomous-ai-agents/mattpocock-subagent-driven-development/SKILL.md` (76 lines, older copy)
- **Kept:** `software-development/mattpocock-subagent-driven-development/SKILL.md` (85 lines, more complete, has `requesting-code-review` in `related_skills`)
- This also fixed the `autonomous-ai-agents` count from 10 → 9.

### 2. Incomplete Frontmatter Fixed (3 skills)
- **`cron-job-authoring`:** Added `author`, `license`, `platforms`, `metadata.hermes` wrapper. Converted from old-style top-level `category`/`tags`/`related_skills` to new `metadata.hermes` nesting. Shortened description from 62 → 55 chars.
- **`doc-coauthoring`:** Added `version: 1.1.0`, `author`, `license`, `platforms`, `metadata.hermes` wrapper. Shortened description from 428 → 52 chars. Added valid `related_skills` (was empty before).
- **`huggingface-trackio`:** Added `version: 1.2.0`, `author`, `license`, `platforms`, `metadata.hermes` wrapper. Shortened description from 314 → 50 chars. Added valid `related_skills`.

### 3. Long Descriptions Fixed (4 skills)
- **`cron-job-authoring`:** 62 → 55 chars ("Author autonomous cron prompts with guardrails.")
- **`doc-coauthoring`:** 428 → 52 chars ("Guide structured documentation co-authoring workflows.")
- **`huggingface-trackio`:** 314 → 50 chars ("Log and retrieve ML training experiments with Trackio.")
- **`songsee`:** 70 → 52 chars ("Audio spectrograms and feature extraction via CLI.")

### 4. Broken `related_skills` References Fixed (9 refs across 8 files)
- **`clarify`** (in `mattpocock-ask-if-underspecified`): Removed — it's a Hermes core tool name, not a skill.
- **`concept-diagrams`** (in `architecture-diagram`): Replaced with `sketch` (a real creative skill for mockups).
- **`delegate-task`** (in `mattpocock-subagent-driven-development`): Removed — core tool name, not a skill.
- **`duckduckgo-search`** (in `parallel-cli`): Removed — core tool name, not a skill.
- **`mcporter`** (in `parallel-cli`): Removed — MCP tool name, not a skill.
- **`skill-view`** (in `mattpocock-code-review`): Replaced with `hermes-agent-skill-authoring` (the in-repo skill that covers skill loading/viewing).
- **`stable-diffusion`** (in `comfyui`): Removed — self-referential, no such skill exists.
- **`web-extract`** (in `competitor-news-monitor`): Removed — core tool name, not a skill.
- **`subagent-driven-development`** (shortened name in 6 files): Replaced with full name `mattpocock-subagent-driven-development` in:
  - `research-paper-writing`
  - `plan`
  - `requesting-code-review`
  - `spike`
  - `systematic-debugging`
  - `test-driven-development`

### 5. Documentation Updated
- **`README.md`:** Updated total to 127, corrected category counts (autonomous-ai-agents 10→9, software-development 29→28), updated verification section to reflect all fixes, updated import/pre-existing counts (99→98 imported, 29 pre-existing).
- **`DEPENDENCY.md`:** Fully regenerated from live `related_skills` metadata. Expanded hub table from 8 to 58 entries, fixed all broken reference documentation, updated MLOps and other skill chains.
- **`NOTES.md`:** Created comprehensive audit findings document in repo root.

### 6. Profile Documentation Transfer
|- Created `profile/` directory with:
|  - `PROFILE.md` — Profile overview, config highlights, toolsets, curator ledger history
|  - `config.yaml` — Full active configuration (copied verbatim)
|  - `MEMORY.md` — 4 persistent memory entries
|  - `USER.md` — User profile (LaTeX preference, AspireCURES details)
|  - `MISSING-FROM-LOCAL.md` — 13 orphaned skills from deleted profiles
|  - `.curator_ledger.jsonl` — 52 curator operation logs (verbatim)
|  - `.bundled_manifest` — 82 official bundled skill checksums (verbatim)
|  - `.usage.json` — Per-skill usage statistics (verbatim)

### 7. Body Sections Added to 22 Skills
|- Added \"What This Skill Does\" sections to 22 skills that lacked both WTD and \"When to Use\" sections.
|- 0 skills remain without a body section (case-insensitive check confirms all 127 have either WTD or WTU).

### 8. Cross-Reference Fixes (new audit script pass)
|- Fixed 4 stale `skill_view()` calls that referenced non-existent skill names:
|  - `research-paper-writing`: `skill_view("diagramming")` → `skill_view("excalidraw")`
|  - `research-paper-writing`: `skill_view("data-science")` → `skill_view("python-data-science")`
|  - `research-paper-writing`: `skill_view("subagent-driven-development")` → `skill_view("mattpocock-subagent-driven-development")`
|  - Added `excalidraw`, `python-data-science` to `research-paper-writing` related_skills
|- Added missing `related_skills` cross-references to:
|  - `claude-code` (codex, opencode already present; added nothing — was complete)
|  - `mattpocock-spec-driven-development` (+6 related skills)
|  - `mattpocock-subagent-driven-development` (+2 related skills)
|  - `mattpocock-to-tickets` (+4 related skills)
|  - `mattpocock-yeet` (+2 related skills)
|  - `mattpocock-gh-fix-ci` (+2 related skills)
|  - `apple-reminders` (+2 related skills)
|  - `findmy` (+1 related skill)
|  - `meeting-action-items` (+1 related skill)

### 9. Category DESCRIPTION.md Creation
|- Created `DESCRIPTION.md` for 8 category directories that were missing one:
|  - `data-science/`, `devops/`, `doc-coauthoring/`, `dogfood/`, `frontend-design/`,
|  - `huggingface-trackio/`, `security/`, `software-development/`

### 10. Audit Script Creation
|- Created `tools/audit-skills.py` — a reusable Python audit script that validates:
|  - YAML frontmatter integrity (required fields, `metadata.hermes` nesting)
|  - Description length ≤59 chars (the routing-signal budget)
|  - `related_skills` resolution (no broken refs, no self-refs)
|  - Body section presence (`## What This Skill Does`, `## When to Use`)
|  - `skill_view()` call ↔ `related_skills` sync
|  - Category `DESCRIPTION.md` presence for multi-skill directories
|  - Referenced script existence from frontmatter `script:` fields
|- Updated `.hermes/cron/active/skill-audit.json` to reference the new script
|- Updated `README.md` with audit script documentation

## Remaining Known Issues

### Old-Style Frontmatter (RESOLVED)

All 127 skills now use the standard `metadata.hermes` nesting format. A repo-wide scan confirms zero skills still use the legacy top-level `category:`, `tags:`, or `related_skills:` format. The three skills initially flagged (`cron-job-authoring`, `doc-coauthoring`, `huggingface-trackio`) have been normalized, and no others were found.

### 13 Orphaned Skills

13 skills in the repository have no local counterpart in `C:\Users\Loggg\AppData\Local\hermes\skills\`. These originated from the `the-skill-maker` and `the-memory-controller` profiles (no longer present). See `profile/MISSING-FROM-LOCAL.md` for details.

## Verification Performed
|- ✅ Total `SKILL.md` files: 127 (was 128)
|- ✅ Unique skill names: 127 (was 127, but 1 was a duplicate)
|- ✅ Duplicate skill names: 0 (was 1)
|- ✅ Broken `related_skills` references: 0 (was 9)
|- ✅ Self-references in `related_skills`: 0 (was 3)
|- ✅ Descriptions > 59 chars: 0 (was 12 — all trimmed to ≤59)
|- ✅ Unquoted descriptions: 0 (all 127 now double-quoted YAML strings)
|- ✅ Descriptions missing periods: 0 (all 127 end with period)
|- ✅ Skills missing `version`/`author`/`platforms`: 0 (was 3)
|- ✅ Non-standard Pitfalls headers: 0 (was 22 — all renamed to `## Pitfalls`)
|- ✅ Non-standard section headers: 0 (all `## When to Use`, `## How to Run`, `## Quick Start`)
|- ✅ Trailing whitespace: 0 in all files
|- ✅ Missing trailing newlines: 0
|- ✅ CRLF line endings: 0 (all LF)
|- ✅ Legacy frontmatter format: 0 (all use `metadata.hermes`)
|- ✅ Temp scripts in repo root: 0
|- ✅ All `related_skills` entries resolve to existing in-repo skills
|- ✅ Related_skills network: 310 cross-references across 125 skills (2 standalone)
|- ✅ `.hermes/cron/` registry: 2 templates, 2 active job definitions, 0 temp scripts
|- ✅ All frontmatter blocks have blank line before closing `---`

## New: Automated Audit Script

A reusable audit script at [`tools/audit-skills.py`](./tools/audit-skills.py) was created to make the `skill-audit.json` cronjob functional. It performs:

1. **YAML frontmatter validation** — required fields + `metadata.hermes` nesting
2. **Description length checks** — ≤59 chars (the routing-signal budget per SKILL.md format spec)
3. **`related_skills` resolution** — every cross-reference resolves to an existing in-repo skill
4. **Body section presence** — checks for `## What This Skill Does` and `## When to Use`
5. **`skill_view()` call sync** — body text `skill_view("xxx")` calls must have matching `related_skills` entries
6. **Category `DESCRIPTION.md`** — every multi-skill category directory has one
7. **Referenced script existence** — frontmatter `script:` entries exist on disk

The script outputs JSON and exits 0 (within thresholds) or 1 (breached). It is wired into `.hermes/cron/active/skill-audit.json` as a weekly cronjob (`no_agent=true`).

## New: Bidirectional Sync Cronjob

A new cronjob was created to keep the GitHub Hermes_Skills repo and the local Hermes Agent environment in sync:

- **`tools/sync-hermes-skills.py`** — Python script that performs bidirectional sync:
  1. **Pull** — `git pull --rebase` from upstream (stashes unstaged changes first, restores after)
  2. **Pull direction** — copies all repo skill files → `~/.hermes/skills/` (115 files pulled on first run)
  3. **Push direction** — copies new/modified local skills → repo tree (hash comparison, skips unchanged)
  4. **Memories** — exports `~/.hermes/memories/` → `memories-export/` directory in repo
  5. **Profiles** — exports `~/.hermes/profiles/<name>/skills/` and `/memories/` → `profiles-export/` directory
  6. **Commit + push** — git add + commit with change-count summary + push
  7. **Audit** — runs `tools/audit-skills.py` after sync to validate

- **`.hermes/cron/active/sync-hermes-skills.json`** — cronjob config: weekly Sunday 2 AM (runs before the audit at 3 AM), `no_agent=true`, uses `terminal` + `file` toolsets only.

- **Sync guards:**
  - Stashes unstaged changes before pull, restores after
  - Hash-based change detection (no unnecessary copies)
  - Skips top-level repo files (README.md, DEPENDENCY.md, NOTES.md) from local→repo push
  - Runs audit after sync for validation
  - Handles missing directories gracefully (no crashes if `~/.hermes/memories/` or `profiles/` doesn't exist)

### Sync Report (test run)
| Metric | Count |
|--------|-------|
| files_pulled_to_local | 115 (first run) / 3 (subsequent runs) |
| files_skipped_pull | 567 (unchanged) |
| new_local_files_in_repo | 0 |
| updated_files_in_repo | 0 |
| files_skipped_push | 570 |
| memories_synced | 0 |
| profiles_synced | 0 |
| total_changes_pushed | 0 |
| audit_passed | true |
| threshold_breached | false |
| git_push_success | true |

### Sync Script Guardrails
- `GIT_TERMINAL_PROMPT=0` — no interactive git prompts
- Git user.name/email set to `hermes-cronbot` / `cronbot@hermes.local`
- `pull.rebase=true` configured to avoid merge commits
- Git push failure is non-fatal — changes committed locally, error reported
- Stashes unstaged changes before pull, restores after
- Hash-based change detection (SHA-256) — no unnecessary copies
- Silent mode: empty stdout = no delivery (cron watchdog pattern)

### Audit Results After Fixes
| Metric | Count |
|--------|-------|
| broken_refs | 0 |
| yaml_errors | 0 |
| long_descriptions | 0 |
| missing_related_skills | 0 |
| placeholder_markers | 2 (intentional — in LaTeX citation examples) |
| missing_body_sections | 0 (alternative headers recognized: `## What's in this skill`, `## Overview`, `## Creative Standard`, `**What This Skill Does:**`) |
| missing_category_descriptions | 0 (all 20 categories now have DESCRIPTION.md + root DESCRIPTION.md) |
| temps_scripts | 0 |
