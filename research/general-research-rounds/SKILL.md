---
name: general-research-rounds
description: "Run source-anchoring rounds on the General_Research repo."
version: 1.0.0
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

Runs a source-anchoring round on the `General_Research` registry repo: picks unanchored load-bearing numbers from the read-only `economicspace` / `spacecost` CSVs, discovers and live-verifies accessible sources (NTRS-first), registers them in per-domain CSVs with tier + access provenance + exact pipeline mapping, hosts legally redistributable full texts, updates INDEX.md, regenerates the aggregate `sources.csv`, then commits/pushes/verifies. Encodes all registry conventions and round pitfalls so any session can run a correct round without prior context.

## When to Use

Use when running (or resuming) a General_Research source-anchoring round — including picking up verified-but-unregistered anchors recorded in memory at the end of an interrupted round. The standing task: each turn ends with a committed round or an explicit blocker statement.

Standing multi-round task: anchor every load-bearing number in the user's `economicspace` and `spacecost` repos with sources that are actually accessible from this machine, registered in the `General_Research` registry repo.

## Repo layout (C:/Users/Owner/OneDrive/Documents/GitHub/General_Research)
- Domains 01–05: `<NN_name>/sources_domain.csv` + `FINDINGS.md` (+ `full_texts/` for hosted PDFs). Domain 4 = launch economics.
- Root: `INDEX.md` (per-domain source tables + contiguous round log) and aggregate `sources.csv`.
- Only this repo is editable. The target repos are read-only — their CSV cells get anchored, never modified.

## Registry conventions
- Per-domain CSV columns: id, tier, short_title, journal_or_series, year, doi_or_url, authors_short, access_status, pipeline_mapping.
- Tiers: T1 = peer-reviewed paper (journal/conference); T2 = official institutional document or presentation; T3 = dataset / derived product.
- `access_status` is free text with provenance baked in: `full_text_hosted (<how verified>)` or `open_not_pulled (<why not pulled, what was recorded instead>)`. Paywalled-but-OA items are logged, never downloaded. Only legally redistributable full texts (NTRS / public domain / OA license) go into `full_texts/`.
- `pipeline_mapping` names the exact target file + column/cell and states match quality: EXACT / near-exact (with delta) / ceiling-anchor — never present a bounding figure as pinning a cell it only bounds.

## Round procedure (in order)
1. Pick unanchored targets from the read-only CSVs — re-read them fresh each round; earlier reads may be stale or empty.
2. Discover sources: `web_search` with site-scoped queries (`site:ntrs.nasa.gov`, AIAA, conference names). NTRS is the workhorse for US launch/propulsion documents.
3. Download + extract locally (urllib with Mozilla UA into a temp dir; pymupdf in a venv under `%LOCALAPPDATA%\Temp`). Verify every number you will claim: verbatim text search first; word-coordinate alignment for tables (see `ocr-and-documents` → references/table-alignment-verification.md).
4. Verify access + metadata live from this machine BEFORE registering — an item that cannot be fetched here is not registered as accessible; record the exact failure in `access_status` instead.
5. Register in the per-domain CSV (list existing IDs first to avoid duplicates), host the PDF if legally redistributable, append exactly ONE FINDINGS block for the round.
6. Update INDEX.md: new row(s) at the correct position in the domain table + one contiguous round-log entry — no stray blank lines inside tables or log sections.
7. Regenerate aggregate `sources.csv` from all per-domain CSVs with csv.DictReader, preserving every column of the existing aggregate header (including `domain_dir`). Verify field-by-field against git HEAD before committing (see Pitfalls).
8. Commit (`--author="loggger <loggger101@gmail.com>"`), push, verify remote HEAD via `git ls-remote origin main` + clean tree. Update memory with the new state (item counts by tier, HEAD sha) — replace the old CURRENT STATE entry; do not append a second one.

## Pitfalls
- **Aggregate regen drops a column.** Reconstructing rows from per-domain files without reading the existing aggregate's header silently loses columns and git diff shows every row changed even though content is identical. Read the old header first; after regen, parse both versions with csv.DictReader and assert all pre-existing rows are field-identical before committing.
- **Counting CSV lines with wc -l.** Files without trailing newlines undercount, so commit messages claiming "regenerated" can be false — verify counts with csv.DictReader against git history when backfilling logs.
- **Writing FINDINGS from memory of the extraction.** Re-read the target CSV and re-run verification before writing claims; a draft that mislabels which row or configuration variant a figure belongs to (e.g. expendable vs reusable) is worse than no claim. State match quality explicitly per cell.
- **INDEX.md contiguity.** Insert new table rows at their correct position in the domain section and keep the round log contiguous — stray blank lines break downstream parsing of the index.
- **Overclaiming configuration cells.** A source giving a vehicle's rated-max capability does not pin a reusability-derated row; register it as ceiling anchor + consistency check with both numbers stated.
- **Round ends with verified-but-unregistered anchors.** If session/tool limits stop you after verification but before registration, record in memory exactly which items were live-verified (with their key numbers) plus the remaining steps — re-verifying on resume is fine; losing the verified state wastes a round.

## Source access notes
Per-site fetch patterns (NTRS, ADS, AIAA, vendor datasheets) verified from this machine: see `references/source-access-notes.md`.
