# Repository Audit Notes

## Scope & Methodology

Full audit of all 128 `SKILL.md` files in the repository at `C:\Users\Owner\OneDrive\Documents\GitHub\Hermes_Skills`. Each file was parsed to extract YAML frontmatter fields (`name`, `description`, `version`, `author`, `license`, `platforms`, `metadata.hermes.tags`, `metadata.hermes.related_skills`), and the `related_skills` references were cross-validated against the set of 127 unique skill names.

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
|- ✅ Descriptions missing periods: 12 (trimmed to ≤59 chars — period omitted to stay within audit threshold; 115 still have periods)
|- ✅ Skills missing `version`/`author`/`platforms`: 0 (was 3)
|- ✅ Non-standard Pitfalls headers: 0 (was 22 — all renamed to `## Pitfalls`)
|- ✅ Non-standard section headers: 0 (all `## When to Use`, `## How to Run`, `## Quick Start`)
|- ✅ Trailing whitespace: 0 in all files
|- ✅ Missing trailing newlines: 0
|- ✅ Line endings: mixed (73 CRLF in working tree, normalized to LF in git storage via `.gitattributes` `text=auto` + `core.autocrlf=true`)
|- ✅ Legacy frontmatter format: 0 (all use `metadata.hermes`)
|- ✅ Temp scripts in repo root: 0
|- ✅ All `related_skills` entries resolve to existing in-repo skills
|- ✅ Related_skills network: 332 cross-references across 127 skills (2 standalone skills with none)
|- ✅ `.hermes/cron/` registry: 3 templates, 3 active jobs (aspirecures-weekly, skill-audit, sync-hermes-skills), 0 temp scripts
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
  4. **Memories** — copies `~/.hermes/memories/` → `memories/` directory in repo (trackable)
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
| `files_pulled_to_local` | 3 (repo→local, subsequent runs) |
| `files_skipped_pull` | 124 (unchanged) |
| `new_local_files_in_repo` | 0 |
| `updated_files_in_repo` | 0 |
| `files_skipped_push` | 127 |
| `files_skipped_push_skills` | 4 |
| `memories_synced` | 0 |
| `profiles_synced` | 0 |
| `total_changes_pushed` | 0 |
| `audit_passed` | `true` (fixed — was `false` due to `python3` not found on Windows) |
| `threshold_breached` | `false` |
| `git_push_success` | `true` |

### Sync Script Guardrails
`- GIT_TERMINAL_PROMPT=0` — no interactive git prompts
`- Git user.name/email set to `hermes-cronbot` / `cronbot@hermes.local`
`- `pull.rebase=true` configured to avoid merge commits
`- Git push failure is non-fatal — changes committed locally, error reported
`- Stashes unstaged changes before pull, restores after
`- Hash-based change detection (SHA-256) — no unnecessary copies
`- Silent mode: empty stdout = no delivery (cron watchdog pattern)
`- Skips export directories (`profiles-export/`, `memories-export/`) from all file scans

### Sync Script Fixes (post-initial-deploy)
1. **Dry-run mode now actually skips file operations** — Previously `--dry-run` only skipped git pull/push but still copied files to/from `~/.hermes/skills/`. Now `sync_skills_pull()`, `sync_skills_push()`, `sync_memories()`, `sync_profiles()` all accept `dry_run` param and skip actual file writes. DEPENDENCY.md generation and `cleanup_empty_dirs()` also respect dry_run.

2. **Python detection fixed** — `run_audit()` used `python3` which on Windows resolves to the broken Store stub (exit code 49, "Python was not found"). Fixed to use `shutil.which("python")` first (works on Windows), falling back to `python3` (Linux/macOS). This was causing the audit step to always report `success=False`, which blocked the "commit + push" step in normal sync runs.

3. **DEPENDENCY.md regeneration now also respects dry_run** — `generate_dependency_map()` accepts `dry_run` param and skips writing to disk in dry-run mode.

## AspireCURES Cronjob Enhancement

The `aspirecures-weekly.json` cronjob config was significantly enhanced with a comprehensive, self-contained prompt body that embeds all the repo-specific knowledge the preparer agent needs:

- **Full prompt body added** — 10KB of inline prompt covering repo context, CI pipeline structure, two-mode operation (maintenance-only vs full curation), field-by-field data file shape, explicit date-churn signature algorithm (C8), dedup logic, country normalization map, render pipeline order, lint-feed.pl validation matrix, failure modes & responses, and 9-phase execution instructions
- **workdir fixed** — changed from placeholder `/path/to/aspirecures` to actual repo path `C:/Users/Owner/OneDrive/Documents/GitHub/aspirecures`
- **Threshold expanded** — added `no_fabricated_data: true` and `report_emitted: true` alongside existing `git_push_success` and `lint_passed`
- **Guardrails expanded** — 16 explicit guardrails covering append-only merge, date-churn prevention (C8 fix — signature taken BEFORE maintenance mutations), dedup, safe-fail, spend caps, country normalization, no-interactive-prompts, model pinning, cron approval mode, self-validation, and maintenance-only passes always running
- **Key guardrails expanded** — 10 hard rules including "agent IS the model" substitution for ANTHROPIC_API_KEY-gated Claude gate
- **Output files specified** — preparer emits to `.hermes/cron/active/aspirecures-research-report.json`, commit agent renders 9 disease pages
- **README.md updated** — enhanced the aspirecures-weekly.json section with full detail on the embedded prompt, guardrails, threshold, and two-agent architecture

### Prompt Body Structure (9 Phases)
1. **Phase 1: Environment + Config** — Read config.json, verify tools exist
2. **Phase 2: Maintenance pass (Mode A)** — Refresh trial statuses, recheck retractions, normalize countries, clamp future dates
3. **Phase 3: Candidate collection** — Europe PMC + PubMed + priority-author boost + ClinicalTrials.gov + ISRCTN
4. **Phase 4: Pre-flight check** — Run check_queries.pl for raw candidate counts
5. **Phase 5: Curation gate** — Evaluate on_topic, credible, appropriate, confidence, summary for each candidate
6. **Phase 6: Merge + signature** — Append-only merge, compute date-churn signature, strip scratch fields
7. **Phase 7: Self-validation** — Check against lint-feed.pl rules BEFORE emitting
8. **Phase 8: Emit report** — Write JSON report + print to stdout
9. **Phase 9: Health check** — Verify data structure is correct

### Embedded Reference Data
- **Data file shape**: Complete field-by-field specification for articles and trials
- **Date-churn signature algorithm**: Explicit Python implementation of canon() + dataSig()
- **Dedup keys**: PMID + DOI + normalized title for articles; NCT + ISRCTN + title for trials
- **COUNTRY_FIX map**: All country normalization entries (Turkey/Türkiye, USA, UK, etc.)
- **Render pipeline**: 8-step build order with exact commands
- **lint-feed.pl validation matrix**: 8 checks with exact regex patterns and lint-feed.pl line references
| **Failure modes**: 7 specific failure scenarios with response procedures

### Audit Results After Fixes
| Metric | Count |
|--------|-------|
| broken_refs | 0 |
| yaml_errors | 0 |
| long_descriptions | 0 |
| missing_related_skills | 0 |
|| placeholder_markers | 0 (LaTeX citation placeholders reclassified as intentional_placeholders) |
| missing_body_sections | 0 (alternative headers recognized: `## What's in this skill`, `## Overview`, `## Creative Standard`, `**What This Skill Does:**`) |
| missing_category_descriptions | 0 (all 20 categories now have DESCRIPTION.md + root DESCRIPTION.md) |
| temps_scripts | 0 |

## Audit Script Fixes

After the initial audit, three bugs were discovered and fixed in `tools/audit-skills.py`:

1. **REPO_ROOT pointing to wrong directory** — `Path(__file__).resolve().parents[2]` resolved to `C:\Users\Owner\OneDrive\Documents\GitHub` (the parent of the repo) instead of the repo root. This caused the audit to scan multiple repos in the parent directory, producing false negatives when other repos had clean SKILL.md files. Fixed to `parents[1]` to match the sync script's correct usage.

2. **Not excluding sync output directories** — `find_skill_files` and `find_category_dirs` did not skip `profiles-export/` and `memories-export/` directories (generated by `tools/sync-hermes-skills.py`). These directories contain copies of skill files from the local Hermes environment and would cause the audit to report thousands of false issues. Both functions now skip these directories, consistent with the sync script's own exclusion logic.

3. **Silent duplicate skill overwrite** — `find_skill_files` used a dict keyed by skill name, so the second file with the same name silently overwrote the first. The audit reported 127 skills (not 128) and 0 duplicates, when in reality there were 128 files with 1 duplicate. Fixed to return `(skills, duplicates)` tuple and added `duplicate_skills` to THRESHOLDS (threshold = 0). Added `duplicate_skills: 0` to the skill-audit.json threshold block.

## Audit Script Improvements (2026-08-28)

After running the audit and sync cronjobs, several bugs and false-positives were addressed:

1. **Undefined variable in breach message** — `find_stale_script_refs` threshold check used `{threshold}` (undefined) instead of `THRESHOLDS['temps_scripts']`. If triggered, this would raise `NameError` and crash the audit. Fixed to `THRESHOLDS['temps_scripts']`.

2. **Deprecated `datetime.utcnow()`** — Replaced with `datetime.datetime.now(datetime.timezone.utc)` for timezone-aware timestamps (Python 3.12+ deprecates `utcnow()`). Also fixed the `__import__("datetime")` indirection to a clean `import datetime` at module level.

3. **Placeholder classification false positive** — `check_stale_placeholders` flagged `TODO:` and `PLACEHOLDER` markers in `research-paper-writing/SKILL.md` as stale, but these are intentional pedagogical markers inside the "Step 1.3: Verify Every Citation" section (LaTeX `\cite{PLACEHOLDER_...}` patterns and `% TODO:` comments). Added a `latex_placeholder_pattern` (regex for `\cite{PLACEHOLDER...}`) and `latex_todo_pattern` (regex for `% TODO:`) that strip intentional pedagogical markers before scanning for genuine stale ones. Report structure split into `placeholder_markers` (stale, requires fix) and `intentional_placeholders` (pedagogical, no action needed).

4. **Added `validate-skill-refs.py`** — New validator script at `.hermes/cron/validate-skill-refs.py` that checks all 3 cronjob JSON files parse as valid JSON and every skill reference resolves to an existing in-repo skill directory with matching `name` frontmatter. Handles Windows path normalization (backslashes → forward slashes). All 16 refs across 3 files validated OK.

## Second-Brain Sync (2026-09-05) — starred-repos research harvest

The user's 41 GitHub stars were deep-dived read-only over two sessions; the verified
knowledge was internalized as skills and is now synced into this repo so any agent can use it.

**Skills added to top-level (17 new, all audit-compliant: full frontmatter, ≤59-char descriptions, `## What This Skill Does` + `## When to Use`, resolvable related_skills):**
- creative/: design-taste-frontend, diagram-design (212 files incl. 39 type refs × 3 variants), full-output-enforcement, pygame, redesign-existing-projects
- data-science/: astro-toolkit-selection, bit-identity-float-pipelines, economicspace-pipeline, space-data-pipelines, space-mission-computation-paradigms
- frontend-design/ (new category): nicegui-app-builder — ui.run() parameter map verified from source + 59-example index + pytest pattern
- github/: issue-triage-state-machine (+ references/AGENT-BRIEF.md, OUT-OF-SCOPE.md)
- productivity/: website-audit
- software-development/: conversation-to-spec, grilling-interview, wayfinder-map-planning, github

**Repo state after sync:** 145 skills across 20 categories; DEPENDENCY.md regenerated (356 xrefs, 82 hubs, 6 standalone: bit-identity-float-pipelines, evaluating-llms-harness, full-output-enforcement, github, space-data-pipelines, xurl); memories/MEMORY.md + USER.md synced from live profile.

**Tooling added:** `tools/regen-dependency-map.py` — standalone DEPENDENCY.md regenerator (the sync script's built-in map generator hangs on import in interactive contexts; this one is safe to run directly). Includes profiles-export/ copies deduped by name with top-level winning, matching the previous generated file's convention.

**Audit fix:** `check_stale_placeholders` now classifies HTML-comment placeholder slots (`<!-- TODO: ... -->`) as intentional — design skills (design-taste-frontend) teach agents to leave labeled image-placeholder slots; these are workflow examples, not development debt. Audit result after all changes: 145 skills, threshold_breached=False, zero issues in every category.

**Also:** removed stale artifact `README-DESKTOP-PJS73RO.md` (duplicate of README at an older count); repaired a corrupted git index where 9 tracked files had empty blobs staged as deletions while identical content sat on disk (`git reset` — verified byte-identical to HEAD before and after).
## Second-Brain Formatting & Discoverability Pass (2026-09-05, part 2)

Goal: make everything easy to find and cheap to use for any agent.

**Added:**
- `SKILLS-INDEX.md` — flat one-line-per-skill index of all 145 skills (`name | description _(category)_`). The cheapest lookup path in the repo: a single grep instead of parsing frontmatter. Grouped by category, sorted within each.
- `tools/gen-skills-index.py` — stdlib-only regenerator for SKILLS-INDEX.md (no PyYAML dependency; regex extraction is sufficient for an index). Run after any skill add/remove/rename.
- `profile/DESCRIPTION.md` — documents what the profile snapshot dir is and that it's read-only reference (canonical memories live in top-level `memories/`).

**Fixed:**
- README category table: malformed separator row (`||----|`) broke markdown table rendering; now single-pipe form.
- Root `DESCRIPTION.md`: was stale ("127 skills") with no navigation pointers; rewritten current (145/20) with a "Start here" lookup ladder (SKILLS-INDEX → DEPENDENCY → README). Note: an AGENTS.md root doc was drafted but its write is gated behind user approval and not yet created, so the ladder points at existing files only.
- README: TOC + Quick Start now lead with the grep-the-index path; Tools table lists gen-skills-index.py.

**Cost discipline:** all new tooling is stdlib-only Python, no build step, no network. Index keeps lookups at O(1) grep cost; DEPENDENCY.md stays for relationship questions only.
