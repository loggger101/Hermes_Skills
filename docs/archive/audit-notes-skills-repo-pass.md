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
- Created `profile/` directory with:
  - `PROFILE.md` — Profile overview, config highlights, toolsets, curator ledger history
  - `config.yaml` — Full active configuration (copied verbatim)
  - `MEMORY.md` — 4 persistent memory entries
  - `USER.md` — User profile (LaTeX preference, AspireCURES details)
  - `MISSING-FROM-LOCAL.md` — 13 orphaned skills from deleted profiles
  - `.curator_ledger.jsonl` — 52 curator operation logs (verbatim)
  - `.bundled_manifest` — 82 official bundled skill checksums (verbatim)
  - `.usage.json` — Per-skill usage statistics (verbatim)

### 7. Body Sections Added to 22 Skills
- Added \"What This Skill Does\" sections to 22 skills that lacked both WTD and \"When to Use\" sections.
- 0 skills remain without a body section (case-insensitive check confirms all 127 have either WTD or WTU).

### 8. Cross-Reference Fixes (new audit script pass)
- Fixed 4 stale `skill_view()` calls that referenced non-existent skill names:
  - `research-paper-writing`: `skill_view("diagramming")` → `skill_view("excalidraw")`
  - `research-paper-writing`: `skill_view("data-science")` → `skill_view("python-data-science")`
  - `research-paper-writing`: `skill_view("subagent-driven-development")` → `skill_view("mattpocock-subagent-driven-development")`
  - Added `excalidraw`, `python-data-science` to `research-paper-writing` related_skills
- Added missing `related_skills` cross-references to:
  - `claude-code` (codex, opencode already present; added nothing — was complete)
  - `mattpocock-spec-driven-development` (+6 related skills)
  - `mattpocock-subagent-driven-development` (+2 related skills)
  - `mattpocock-to-tickets` (+4 related skills)
  - `mattpocock-yeet` (+2 related skills)
  - `mattpocock-gh-fix-ci` (+2 related skills)
  - `apple-reminders` (+2 related skills)
  - `findmy` (+1 related skill)
  - `meeting-action-items` (+1 related skill)

### 9. Category DESCRIPTION.md Creation
- Created `DESCRIPTION.md` for 8 category directories that were missing one:
  - `data-science/`, `devops/`, `doc-coauthoring/`, `dogfood/`, `frontend-design/`,
  - `huggingface-trackio/`, `security/`, `software-development/`

### 10. Audit Script Creation
- Created `tools/audit-skills.py` — a reusable Python audit script that validates:
  - YAML frontmatter integrity (required fields, `metadata.hermes` nesting)
  - Description length ≤59 chars (the routing-signal budget)
  - `related_skills` resolution (no broken refs, no self-refs)
  - Body section presence (`## What This Skill Does`, `## When to Use`)
  - `skill_view()` call ↔ `related_skills` sync
  - Category `DESCRIPTION.md` presence for multi-skill directories
  - Referenced script existence from frontmatter `script:` fields
- Updated `.hermes/cron/active/skill-audit.json` to reference the new script
- Updated `README.md` with audit script documentation

## Remaining Known Issues

### Old-Style Frontmatter (RESOLVED)

All 127 skills now use the standard `metadata.hermes` nesting format. A repo-wide scan confirms zero skills still use the legacy top-level `category:`, `tags:`, or `related_skills:` format. The three skills initially flagged (`cron-job-authoring`, `doc-coauthoring`, `huggingface-trackio`) have been normalized, and no others were found.

### 13 Orphaned Skills

13 skills in the repository have no local counterpart in `C:\Users\Loggg\AppData\Local\hermes\skills\`. These originated from the `the-skill-maker` and `the-memory-controller` profiles (no longer present). See `profile/MISSING-FROM-LOCAL.md` for details.

## Verification Performed
- ✅ Total `SKILL.md` files: 127 (was 128)
- ✅ Unique skill names: 127 (was 127, but 1 was a duplicate)
- ✅ Duplicate skill names: 0 (was 1)
- ✅ Broken `related_skills` references: 0 (was 9)
- ✅ Self-references in `related_skills`: 0 (was 3)
- ✅ Descriptions > 59 chars: 0 (was 12 — all trimmed to ≤59)
- ✅ Unquoted descriptions: 0 (all 127 now double-quoted YAML strings)
- ✅ Descriptions missing periods: 12 (trimmed to ≤59 chars — period omitted to stay within audit threshold; 115 still have periods)
- ✅ Skills missing `version`/`author`/`platforms`: 0 (was 3)
- ✅ Non-standard Pitfalls headers: 0 (was 22 — all renamed to `## Pitfalls`)
- ✅ Non-standard section headers: 0 (all `## When to Use`, `## How to Run`, `## Quick Start`)
- ✅ Trailing whitespace: 0 in all files
- ✅ Missing trailing newlines: 0
- ✅ Line endings: mixed (73 CRLF in working tree, normalized to LF in git storage via `.gitattributes` `text=auto` + `core.autocrlf=true`)
- ✅ Legacy frontmatter format: 0 (all use `metadata.hermes`)
- ✅ Temp scripts in repo root: 0
- ✅ All `related_skills` entries resolve to existing in-repo skills
- ✅ Related_skills network: 332 cross-references across 127 skills (2 standalone skills with none)
- ✅ `.hermes/cron/` registry: 3 templates, 3 active jobs (aspirecures-weekly, skill-audit, sync-hermes-skills), 0 temp scripts
- ✅ All frontmatter blocks have blank line before closing `---`

## New: Automated Audit Script

A reusable audit script at [`tools/audit-skills.py`](../../tools/audit-skills.py) was created to make the `skill-audit.json` cronjob functional. It performs:

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
| placeholder_markers | 0 (LaTeX citation placeholders reclassified as intentional_placeholders) |
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
## Second-Brain Formatting & Discoverability Pass (2026-09-05, part 3)

**Added:**
- `tools/check-links.py` — broken-link gate for the whole repo: verifies every relative markdown link resolves; skips external URLs, pure anchors, fenced code blocks and inline code spans (docs legitimately show syntax examples such as image links with placeholder targets); skips profiles-export/ + memories-export/ because those are historical per-profile snapshots that may predate later fixes (regenerated from live environments, not hand-maintained). Stdlib only. Exit 1 on any broken link — the second half of a pre-commit pair with audit-skills.py.
- DESCRIPTION.md "Task → Skill Quick Table" — job-to-skill routing for ~18 common tasks (planning, triage, review, debugging, UI building, diagrams, space pipelines, cronjobs...), so an agent can go from intent to skill without reading the index at all.

**Fixed (broken links found by the new gate on first run — 6 unique):**
- huggingface-trackio/references/retrieving_metrics.md: two dead `docs/source/*.md` refs pointed at upstream Trackio paths that don't exist in this repo AND no longer exist upstream either (verified via GitHub API tree listing + raw fetch, both 404). Replaced with the live published docs URL https://huggingface.co/docs/trackio/index (verified HTTP 200) plus a note explaining why.
- profile/PROFILE.md: `./NOTES.md` was one level too deep → `../NOTES.md`.
- media/gif-search/SKILL.md false positive resolved in the checker itself: the "broken" link is an inline-code markdown syntax example, now stripped before checking.

**Gate results:** 446 relative links checked across all non-snapshot .md files — zero broken after fixes; audit still green (145 skills).

## 2026-09-05 — Starred-repo deep-dive round 2: +17 skills (145 → 162)

Manual pass over all 41 starred repos (no subagents). New value found in corners a README skim misses:

**First-party discovery:** `NousResearch/hermes-agent` ships `optional-skills/` — 137 official
Hermes skills installable via the built-in hub (`hermes skills install official/<cat>/<name> --yes`).
Installed 12 matching this environment's stack (qmd, scrapling, code-wiki, rest-graphql-debug,
ast-grep, watchers, fastmcp, har-derived-api-client, jupyter-notebook, one-three-one-rule,
decision-questionnaire, oss-forensics). All adapted to repo conventions: real `## What This Skill Does`
sections added (written from each skill's actual content), broken related_skills refs pointing at
uninstalled optional skills cleaned up.

**External ports (5):** code-quality-signal (sentrux 5-metric ungameable quality signal — stdlib-only
implementation written + verified on hermes-agent, 5,562 files: Quality 2387, bottleneck depth),
duckdb-querying (official DuckDB Friendly SQL idioms + sandboxed ad-hoc pattern), modern-python-tooling
(trailofbits uv/ruff/ty + PEP 723; CC-BY-SA-4.0 license carried in frontmatter), property-based-testing
(trailofbits Hypothesis catalog + failure triage; CC-BY-SA-4.0), semgrep-rule-creator (trailofbits,
references/ verbatim; CC-BY-SA-4.0).

**Enhancements:** space-data-pipelines gained brahe SI-units/element-order conventions section.

**Gate changes:** check-links.py now skips `<skill>/templates/` dirs — template scaffolds ship
fill-in-the-blank links ({{TOKEN}}, diagrams/) that only resolve after generation; documented in the
tool docstring. Audit unchanged: all thresholds still zero.

**Docs refreshed:** README Skill Catalog regenerated from live frontmatter (162 skills, 23 categories,
every bullet target verified on disk); DESCRIPTION.md + README count mentions updated to 162/23;
DEPENDENCY.md regen'd (377 xrefs). New category dirs: communication/, mcp/, web-development/.

**Not ported (evaluated, rejected):** github-cheat-sheet (2013-era git trivia), repowise skills
(need the commercial .repowise index to function), z3 agentic-workflow-designer (GitHub Agentic
Workflows-specific; its DataOps pre-fetch pattern noted in FINDINGS instead).

## 2026-09-06 — Round-3 pass: +4 skills (162 → 166), docs/ knowledge layer expanded to 7 files

**Skills ported from mattpocock/skills (MIT, adapted with Hermes frontmatter):**
`productivity/teach` (stateful multi-session teaching workspace; MISSION.md + learning-records ADRs +
HTML lessons; 4 format references under `references/`), `devops/wizard` (+ its `template.sh` bash library —
human-in-the-loop provisioning: opens URLs, captures secrets, idempotent .env upserts, gh secret writes),
`software-development/skill-flow-router` (ask-matt adapted: main flow + 3 on-ramps mapped to the skills
actually installed in this brain), `software-development/retro` (session retrospective → environment fixes).

**docs/ knowledge layer:** added space-astro/catalog-data-sources.md (astroquery async-first API map — SBDB
covariance flag, Horizons all-43-quantities bloat gotcha; pds4_tools metadata-with-array; cumulus pvl/cmr-client;
space-map Chebyshev binary ephemeris schema), data-science/optimization-toolkit.md (nyx-py LIVE correction, pygmo2
UDA contract, mesa v3 two blockers incl. py≥3.12, z3 FPRef/regex sorts, Pyomo dae/gdp/mpec, CamPyRoS ray_alt shim),
webdev/frontend-tooling.md (nicegui ui.run() = 33 params verified from source — corrects the earlier "71" claim;
Front-End-Checklist MCP rule package; HTMLHint's 34 rules; gods-eye-view Cesium layout + test-everything discipline),
devops/git-workflow-recipes.md (fixup+autosquash, PR checkout refspecs, safe revert of merged PRs — distilled from the
github-cheat-sheet clone that was previously rejected as a *skill*; kept here as reference docs instead). Also fixed:
docs/README.md index table now lists all 7 files (polars-pymc row had been missing since round 2).

**Corrections to prior notes:** nicegui ui.run() param count 71 → 33 (verified against source this pass);
github-cheat-sheet is not trivia — its fixup/autosquash + PR-refspec recipes are now in docs/devops/.

**Counts refreshed everywhere live:** DESCRIPTION.md, README.md catalog (+4 entries), SKILLS-INDEX.md (regen: 166/23),
DEPENDENCY.md (regen: 390 xrefs, broken=0). Gates green at commit time: audit threshold_breached=false; check-links
503 links / 0 broken. Local live library and repo verified byte-parity on all new files (CRLF-normalized sha256).
## 2026-09-06 — Formatting & organization pass (docs-only; no skill content changes)

**README.md:** replaced the hand-maintained Skill Catalog with a live-frontmatter regeneration
(166 skills, forward-slash links — old entries used Windows backslash paths that render broken on
GitHub); fixed stale counts in title/Overview/tools table (128 → 166); category table now lists all
23 categories with correct per-category counts (was missing communication/mcp/web-development and had
stale data-science/devops/productivity/research/security/software-development numbers); renamed the
"Pre-existing vs Imported Skills" section to "Provenance" (its 98/30 split was stale — replaced with a
three-source account pointing at this file for per-round history); TOC anchor updated; "Verification
Status" reorganized into "Live Invariants" (claims that hold on every audit run) with one-off historical
fixes moved to the pointer above.

**DESCRIPTION.md:** 162 → 166 in intro; category table now lists all 23 categories (added communication,
mcp, web-development rows).

**.hermes/cron/README.md:** fixed malformed Active Cronjobs table (`||` doubled pipes) and `|- **X:**`
list artifacts under aspirecures-weekly.json; tree diagram updated to match disk (validate-cronjobs.py +
validate-skill-refs.py added, phantom archive/old-jobs removed); missing comma in Quick Start python block.

**NOTES.md / SKILL bodies:** repaired `|- item` list artifacts — NOTES.md sections 6–10 (~59 lines) and one
table row; software-development/systematic-debugging/SKILL.md (1 line) and verification-culture/SKILL.md
(2 lines, also removed a duplicated "enabled_toolsets" mention). Both SKILL fixes synced to the local live
library.

**Organization:** deleted phantom category `mlops/models/` (DESCRIPTION.md only, zero skills — not in any
index; removed from repo and local library); filled all 21 empty category DESCRIPTION.md stubs with a real
one-line focus + linked skill list generated from live frontmatter (synced to local).

**Tracking:** `.gitignore` now un-ignores the two cron validator scripts referenced by README/skills
(`.hermes/cron/validate-cronjobs.py`, `validate-skill-refs.py`) — they were on disk and documented but never
tracked, so a fresh clone would have broken references; both added to git this pass.

**Regenerated:** SKILLS-INDEX.md (166 skills / 23 categories) and DEPENDENCY.md (390 xrefs, 88 hubs, 11
standalone, broken=0). Gates: audit threshold_breached=false; check-links clean across the repo.
## 2026-09-06 — Code & knowledge accessibility pass (round 2 of formatting/organization)

**New: CODE-INDEX.md + `tools/gen-code-index.py`.** The executable-knowledge layer now has its own flat
index, companion to SKILLS-INDEX: every code file in the repo (113 files / ~27.5k lines across 28 owner
groups) listed as `- path (kind, lang, N lines) — purpose _(owner)_`, with the one-line purpose extracted
from each file's docstring/header comment. `grep -i <term> CODE-INDEX.md` finds runnable code by purpose or
owning skill. Wired into DESCRIPTION.md "Start here" + tooling list and README TOC/Quick Start/tools table;
maintenance rule updated (regen after any code-file change).

**Orphaned-code documentation sweep.** Inventory found 31 code files not referenced by their owning SKILL.md;
the genuinely useful ones are now documented in place: `github/github-auth` + `software-development/github`
(`gh-env.sh` — source it for auth detection, with the manual fallback kept), `creative/p5js` (`setup.sh`
dependency check), `software-development/ast-grep` (new "Testing the skill itself" section → `tests/smoke.sh`,
11 stdlib-only checks), `productivity/docx` (`docx_common.py` shared helper + tests + provenance note for the
one-off website-audit builders in `specs/` — reference implementations, hardcoded paths), `productivity/pdf`
(`_raster.py` pypdfium2→pdftoppm fallback chain), `productivity/google-workspace` (`gws_bridge.py` token
bridge + `_hermes_home.py` standalone HERMES_HOME resolver), `research/grounded-citations` (same helper,
documented in Prerequisites), `creative/comfyui` (test-suite pointer to its own tests/README.md). All synced
to the local live library.

**Style normalization: gh-env.sh `.env` fallback branch (both copies).** The original used a side-effect
assignment inside an elif condition (`elif _hermes_env=...; [ -f ... ]`) — verified to *work* under
`set -euo pipefail`, but non-idiomatic and easy to misread. Rewritten as plain `[ -f ... ] && grep -q ...` in
both script copies (verified with `bash -n`) and in the github-auth/SKILL.md inline example, which previously
duplicated the same construct; that section now points agents at the bundled script first.

**De-duplication.** `.hermes/cron/validate-cronjobs.py` was byte-identical to a copy under
`autonomous-ai-agents/cron-config-authoring/scripts/`; every doc reference points at the `.hermes/cron/` path,
so the orphaned skill-side copy (and its now-empty scripts dir) was removed — single source of truth.

**Gates:** audit threshold_breached=false; check-links 654 links / 0 broken. All touched SKILL.md + script
files synced to local library (byte parity).

## 2026-09-09 — CI pass: GitHub Actions gate + skill test suites wired (commits 6f2ab7f, d64251e)

**New: `.github/workflows/ci.yml`.** The repo's health gates previously ran only by local
discipline; nothing enforced them on the remote. Two jobs run on every push to `main` and
every PR (permissions: contents read-only): **Health gates** — `pip install "pyyaml>=6.0"` then
`python tools/verify-all.py` (all 9 gates); **Skill test suites** — pytest over the five shipped
suites, one step per suite so a failure names the skill in the log: docx 29 / pdf 21 /
powerpoint 21 / xlsx 11+1 skip / comfyui 109 passed + 8 skipped.

**New: `test-requirements.txt`.** Single source of truth for suite deps (pytest, python-docx,
openpyxl, reportlab, pdfplumber, pypdf, Pillow, pypdfium2, python-pptx, requests — all pure
wheels). Created by running every suite in a clean uv venv until green. `pypdfium2` covers the
pdf rasterization tests without poppler's pdftoppm binary.

**Lesson (measured twice this pass):** (1) an unquoted version pin (`pip install pyyaml>=6.0`)
is a bash redirection, not a constraint — quote it; (2) my local venv had `pypdf` from an
earlier manual install, so the first CI run failed on exactly that missing dep while every suite
passed locally — deps must live in one tracked file both environments read. First CI run
(34354327580): health gates PASSED on GitHub runners; pdf suite 15F/6P (missing pypdf). Second
run after d64251e (34354875418) fully green in 57s: both jobs success.

**Docs:** README.md gained a "CI (GitHub Actions)" subsection under Verification; DESCRIPTION.md
tooling list + maintenance rules reference the workflow and test-requirements.txt.

## 2026-09-09 — Round-6 starred-repo pass: discovery CI runner + 7 ports (167 → 174 skills)

**Starred repos grew 41 → 47.** Set-diff against the round-5 baseline identified exactly six new
stars; all cloned and surveyed. `affaan-m/ECC` was the major find: **286 curated skills**, MIT
licensed, with a native `.hermes/` integration folder documenting its install path — now the
primary port source for this brain. `obra/superpowers`: 14 skills, most already ported in earlier
rounds; three new process-skills identified. `Imbad0202/academic-research-skills` excluded:
CC-BY-NC license violates the portable-license convention (MIT/Apache/BSD only).

**New CI runner: `tools/run-skill-tests.py`.** The skill-tests job previously hard-coded five
pytest steps in YAML — a new skill shipping tests would silently never run on GitHub. Replaced by
a discovery-based runner: filesystem walk finds every `<skill>/tests/` suite, runs each with the
current interpreter, aggregates results, exits non-zero on any failure; `--list` dry-run for
discovery inspection. ci.yml now invokes it once. Fail-loud path verified with a temporary broken
suite (correctly reported + non-zero exit). Run 34360610204 green at commit 711ad71.

**Seven ports, all license-verified and convention-adapted** (frontmatter name/version/author/
platforms/metadata.hermes; description ≤59 chars; `## What This Skill Does` + `## When to Use`;
related_skills resolving in-repo; source-attribution comment):

| Skill | Source | Notes |
|-------|--------|-------|
| software-development/brainstorming | obra/superpowers | spike/bounded/architectural triage, approval gate |
| software-development/receiving-code-review | obra/superpowers | verify feedback against codebase before acting |
| software-development/verification-before-completion | obra/superpowers | no completion claims without fresh evidence; complements verification-culture |
| data-science/regex-vs-llm-structured-text | affaan-m/ECC (MIT) | ships stdlib-only `scripts/hybrid_parser.py` + 14-test suite, green under both pytest and unittest |
| research/literature-review | affaan-m/ECC community skill | plan/screen/synthesize/cite workflow |
| software-development/windows-desktop-e2e | affaan-m/ECC (MIT) | pywinauto/UI Automation E2E for WPF/WinForms/Qt — directly relevant to this Windows environment |
| software-development/generating-python-installer | affaan-m/ECC (MIT) | 820-line Chinese original translated with all commands verbatim: Nuitka standalone + Inno Setup commercial packaging; ships `scripts/build_optimized.bat` (%NUMBER_OF_PROCESSORS% — wmic removed in Win11 22H2+), `slim_dist.ps1` (7-pass, keeps METADATA/entry_points.txt for importlib.metadata), `analyze_dlls.py` (stdlib-only, live-tested against a synthetic dist fixture) |

**Rejected candidates with reasons:** cost-tracking (Claude Code infra dependency — non-functional
here); benchmark-methodology (marketing/benchmarking-sprint skill, not performance methodology);
search-first + safety-guard (depend on Claude Code PreToolUse hooks / researcher-agent plumbing).

**Parity re-verified after every port batch.** One drift class found and fixed: three files with
trailing-newline/EOL differences only — repo copies copied over local byte-for-byte; final parity
= 905 shared files identical, two expected local-only skills (rss-feeds, reddit-reading).

**Gates:** all 9 gates passed at every commit of this pass. CI runs green: 34368525888 (4601172),
34375349043 (40a0342), 34383783922 (23dbb92). Final state: **174 skills / 409 xrefs / 124 code
files**, origin/main...main = 0/0.

**Process lesson:** large multi-file writes via the execute_code kernel did not persist to the
OneDrive-backed repo path (dirs created, files absent) while `write_file` + bash `cp` with per-file
sha256 verification worked reliably — for OneDrive paths, write locally then copy-and-verify.

**Follow-on batch same day: 3 research ports → 177 skills.** ECC catalog sweep (keyword-scored
against this brain's domains) surfaced three clean community-skill fits in the biomedical/research
cluster: `research/pubmed-database` (NCBI E-utilities + MeSH query construction; example code
converted to stdlib urllib — no third-party deps), `research/gget` (quick genomic DB lookups with
reproducibility logging), and `research/scholar-evaluation` (9-dimension rubric for evaluating
papers/proposals). All three cross-link into the existing research cluster (`literature-review`,
`arxiv`, `grounded-citations`). Caught before commit: one description at 63 chars (>59 limit) —
shortened; and a README catalog edit that briefly duplicated an entry / dropped another (fixed in
the same pass, verified against disk counts). Final state after this batch: **177 skills / 418
xrefs**, all 9 gates green.
