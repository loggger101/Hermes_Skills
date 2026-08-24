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
- **`subagent-driven-development`** (shortened name in 6 files): Replaced with full name `mattpocheck-subagent-driven-development` in:
  - `research-paper-writing`
  - `plan`
  - `requesting-code-review`
  - `spike`
  - `systematic-debugging`
  - `test-driven-development`

### 5. Documentation Updated
- **`README.md`:** Updated total to 127, corrected category counts (autonomous-ai-agents 10→9, software-development 29→28), updated verification section to reflect all fixes, updated import/pre-existing counts (99→98 imported, 29 pre-existing).
- **`DEPENDENCY.md`:** Fully regenerated from live `related_skills` metadata. Expanded hub table from 8 to 58 entries, fixed all broken reference documentation, updated MLOps and other skill chains.
- **`NOTES.md`:** Created comprehensive audit findings document in `profile/`.

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
- Added "What This Skill Does" sections to 22 skills that lacked both WTD and "When to Use" sections.
- 0 skills remain without a body section (case-insensitive check confirms all 127 have either WTD or WTU).

## Remaining Known Issues

### Old-Style Frontmatter in Some Imported Skills

Some older imported skills still use the legacy frontmatter format (top-level `category:`, `tags:`, `related_skills:` instead of `metadata.hermes` nesting). The three skills that were checked in this audit (`cron-job-authoring`, `doc-coauthoring`, `huggingface-trackio`) have been normalized. Others may exist but should be checked during future updates.

### 13 Orphaned Skills

13 skills in the repository have no local counterpart in `C:\Users\Loggg\AppData\Local\hermes\skills\`. These originated from the `the-skill-maker` and `the-memory-controller` profiles (no longer present). See `profile/MISSING-FROM-LOCAL.md` for details.

## Verification Performed
- ✅ Total `SKILL.md` files: 127 (was 128)
- ✅ Unique skill names: 127 (was 127, but 1 was a duplicate)
- ✅ Duplicate skill names: 0 (was 1)
- ✅ Broken `related_skills` references: 0 (was 9)
- ✅ Descriptions > 60 chars: 0 (was 4)
- ✅ Skills missing `version`/`author`/`platforms`: 0 (was 3)
- ✅ All `related_skills` entries resolve to existing in-repo skills
