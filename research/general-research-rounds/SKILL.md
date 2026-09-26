---
name: general-research-rounds
description: "Run source-anchoring rounds on the General_Research repo."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [research, citations, data-anchoring, registry, space-data]
    category: research
    related_skills: [grounded-citations, literature-review, ocr-and-documents, blocked-page-recovery]
---

# General_Research Rounds

## What This Skill Does

Runs a source-anchoring round on the `General_Research` registry repo: picks unanchored load-bearing numbers from the read-only `economicspace` / `spacecost` / `AsteroidCatalog` tables, discovers and live-verifies accessible sources (NTRS-first), registers them in per-domain CSVs with tier + access provenance + exact pipeline mapping, hosts legally redistributable full texts, records every contradiction as a revision candidate, updates INDEX.md, regenerates the derived files with the repo's own tools, validates, then commits/pushes/verifies. The repo's `AGENTS.md` is the source of truth for its rules; this skill is the procedure around them — if the two disagree, follow `AGENTS.md` and `tools/validate.py`.

## When to Use

Use when running (or resuming) a General_Research source-anchoring round — including picking up verified-but-unregistered anchors recorded in memory at the end of an interrupted round. The standing task: each turn ends with a committed round or an explicit blocker statement.

Standing multi-round task: anchor every load-bearing number in the user's `economicspace`, `spacecost` and `AsteroidCatalog` repos with sources that are actually accessible from this machine, registered in the `General_Research` registry repo.

## Repo layout

`General_Research` sits in the user's GitHub folder (`.../OneDrive/Documents/GitHub/General_Research` — the user profile differs per machine, e.g. `C:/Users/Owner/...` or `C:/Users/Loggg/...`); remote `loggger101/General_Research`, branch `main`.
- Domains `01_…` through `11_…` (more get added): `<NN_name>/sources_domain.csv` + `FINDINGS.md`, plus `full_texts/` for hosted files and `extracted_data/` for the numbers pulled out of each source. README "Layout" lists every domain.
- Root: `INDEX.md` (per-domain source tables + research log), `sources.csv` (**generated** — never hand-edit), `full_texts_manifest.csv`, `revision_candidates.csv`, `AGENTS.md`, `tools/build_registry.py`, `tools/validate.py`.
- Only this repo is editable. The target repos are read-only — their cells get anchored or flagged, never modified.

## Registry conventions
- Per-domain CSV columns: id, tier, short_title, journal_or_series, year, doi_or_url, authors_short, access_status, pipeline_mapping.
- IDs: lowercase letters, digits, `_` and `-`; permanent. Use the full registry id everywhere — INDEX rows, extracted-data `source_id`, candidate `source_ids` — never an abbreviation.
- Tiers: T1 = peer-reviewed paper (journal/conference); T2 = official institutional document or presentation; T3 = dataset / derived product.
- `access_status` starts with one of six classes, then the provenance: `full_text_hosted` · `public_domain_excerpt_hosted` · `verified_live_not_pulled` · `open_not_pulled` · `open_service` · `skipped`. Write `open_service` (not `open service`); a full text you pulled but may not redistribute is `verified_live_not_pulled`. Paywalled-but-OA items are logged, never downloaded. Only legally redistributable full texts go into `full_texts/`, and each one gets a `domain_dir,id,file` row in `full_texts_manifest.csv`.
- `pipeline_mapping` names the exact target file + column/cell and states match quality: EXACT / near-exact (with delta) / ceiling-anchor — never present a bounding figure as pinning a cell it only bounds.
- Contradictions go to `revision_candidates.csv`: next `rc-NNN`, status `open`, target_repo / target_file / target_row / field, the **current upstream value**, the proposed change, evidence, `checked_against` = `<repo>@<short sha>` you read it from, `checked_date`. Statuses: `open`, `applied`, `declined`, `superseded`, `blocked`. When a re-check finds upstream changed, update that row's status, `checked_against` and `checked_date` — never add a duplicate.

## Round procedure (in order)
0. `git pull --rebase`, then `python tools/validate.py`. The repo is edited from more than one machine and session; if validation fails before you start, fix or report that first — never build a round on a broken tree.
1. Pick targets from the read-only tables — re-read them fresh from each repo's latest `main` every round; earlier reads may be stale. Also re-check `open` rows in `revision_candidates.csv` whose upstream may have changed.
2. Discover sources: `web_search` with site-scoped queries (`site:ntrs.nasa.gov`, AIAA, conference names). NTRS is the workhorse for US launch/propulsion documents.
3. Download + extract locally (urllib with Mozilla UA into a temp dir; pymupdf in a venv under `%LOCALAPPDATA%\Temp`). Verify every number you will claim: verbatim text search first; word-coordinate alignment for tables (see `ocr-and-documents` → references/table-alignment-verification.md).
4. Verify access + metadata live from this machine BEFORE registering — an item that cannot be fetched here is not registered as accessible; record the exact failure in `access_status` instead.
5. Register: list existing IDs first, then **append** the row to the domain's `sources_domain.csv`. Host the PDF if legally redistributable and add its manifest row. Write extracted numbers to `<domain>/extracted_data/rNN_<topic>_key_numbers.csv` with `csv.writer` on a file opened with `newline=''` (columns `source_id,item,value,unit,location_in_source,notes` where they fit). Append exactly ONE FINDINGS block for the round. Add or update `revision_candidates.csv` rows.
6. Update INDEX.md by **targeted insertion, never a full-file rewrite**: append the new row(s) at the end of the domain table (same order as `sources_domain.csv`), using the header `| id | tier | source (short) | access | backs / could replace |` — five cells and a closing `|`, no blank line inside the table. Insert exactly one log entry, `- **Round N** (YYYY-MM-DD): ...`, directly under `## Research log` (newest first). A new domain gets a `## Domain N — title` section above `## Research log` with that same header, and a line in README "Layout".
7. `python tools/build_registry.py` (regenerates `sources.csv`, fills manifest `bytes`/`sha256`), then `python tools/validate.py` — it must exit 0. Read `git diff --stat` and write the commit message from what the diff actually contains.
8. Commit (`--author="loggger <loggger101@gmail.com>"`), `git pull --rebase` again, push, then verify `git ls-remote origin main` equals local HEAD and the tree is clean. If the push is rejected, rebase, re-run step 7, push again. Update memory with the new state (item counts by tier, HEAD sha) — replace the old CURRENT STATE entry; do not append a second one.

## Pitfalls
- **Rewriting INDEX.md drops history.** R43's full-file rewrite deleted Rounds 0–41 from the log and R46's deleted R45; all were recovered from git on 2026-09-26. `validate.py` fails if the log does not run 0..N without gaps — when it does, recover the missing entries (`git log -S'**Round N**' -- INDEX.md`, then `git show <sha>:INDEX.md`); never renumber or paper over.
- **Narrow tables hide data.** 20 INDEX rows had three cells and domains 8–11 had three-column headers. GitHub drops cells beyond the header width, so the access and mapping columns silently vanished. Always the five-column header.
- **Root-level `extracted_data/`.** FINDINGS paths are relative to the domain folder; R47–R57 wrote seven files to a root folder no link reached. Always `<domain>/extracted_data/`.
- **Hand-built CSVs.** Never hand-edit `sources.csv`, and never join strings into CSV rows: ten extracted-data files had unquoted commas that shifted cells, and one written without `newline=''` had doubled carriage returns.
- **Commit messages that claim work not done.** R53's message said a research-log entry was added; INDEX.md never received one. Claims like "regenerated" have been false before. Validate and read the diff before writing the message.
- **Counting CSV lines with wc -l.** Files without trailing newlines undercount — count rows with csv.DictReader.
- **Writing FINDINGS from memory of the extraction.** Re-read the target CSV and re-run verification before writing claims; a draft that mislabels which row or configuration variant a figure belongs to (e.g. expendable vs reusable) is worse than no claim. State match quality explicitly per cell.
- **Overclaiming configuration cells.** A source giving a vehicle's rated-max capability does not pin a reusability-derated row; register it as ceiling anchor + consistency check with both numbers stated.
- **Round ends with verified-but-unregistered anchors.** If session/tool limits stop you after verification but before registration, record in memory exactly which items were live-verified (with their key numbers) plus the remaining steps — re-verifying on resume is fine; losing the verified state wastes a round.

## Source access notes
Per-site fetch patterns (NTRS, NASA OIG, ADS, AIAA, vendor datasheets) verified from this machine: see `references/source-access-notes.md`.
