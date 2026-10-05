---
name: general-research-rounds
description: "Run source-anchoring rounds on the General_Research repo."
version: 1.2.0
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
- `access_status` starts with one of the classes in the repo README's "Access classes" (seven since R74 added `registered_not_pulled`), then the provenance: `full_text_hosted` · `public_domain_excerpt_hosted` · `verified_live_not_pulled` · `open_not_pulled` · `open_service` · `registered_not_pulled` · `skipped`. Write `open_service` (not `open service`); a full text you pulled but may not redistribute is `verified_live_not_pulled`. Paywalled-but-OA items are logged, never downloaded. Only legally redistributable full texts go into `full_texts/`, and each one gets a `domain_dir,id,file` row in `full_texts_manifest.csv`.
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
8. Commit (`--author="hermes-cronbot <cronbot@hermes.local>"` — the standing automation convention; do NOT use a personal identity for cron rounds), `git pull --rebase` again, push, then verify `git ls-remote origin main` equals local HEAD and the tree is clean. If the push is rejected, rebase, re-run step 7, push again. Update memory with the new state (item counts by tier, HEAD sha) — replace the old CURRENT STATE entry; do not append a second one.

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

## Round-craft pitfalls (rounds R42–R66)

Lessons from rounds R42–R66, carried in the copy committed as `069e19a` (2026-09-27) and merged with v1.1.0 on 2026-10-01; the ones `tools/validate.py` now enforces were dropped.

- **Citation sweep to find unanchored rows**: re-read every reference CSV live each round; extract source tokens (arXiv ids, NTRS 8-digit ids, DOIs, author-year) from the notes column and check each against registry ids + corpus text. The regex over-captures month-years as 'author years' — treat those hits as noise and verify real candidates by targeted id/corpus lookup before acting.
- **User WIP in target repos is read-only input — sweep it, never touch it.** Uncommitted changes (or a merged PR) in spacecost/economicspace are inputs: diff `reference/*.csv` between HEAD and the pre-change commit to find NEW rows/changed values carrying institutional claims, anchor those; record problems as revision candidates. After any value-level change, re-verify that previously pinned anchors still hold against the new numbers (R52: PR #3 grew launch_vehicles 36→76 rows — delta_v_segments was unchanged so R49's pin survived; had values moved it would have been a finding). Company-target rows (SpinLaunch) need no institutional anchor.
- **Join ssoBFT/parquet bodies on `number`, never name.** R42's first join on number=69230 returned "Hermes" — Bennu is number 101955. The name column can mislead; verify identity via JPL `ssd-api.jpl.nasa.gov/sbdb.api?sstr=<name>` (the working per-object endpoint; the bulk-only `sbdb_query.api` rejects s=/id=/des= params with HTTP 400).
- **Live data services are T3, not T2** (ssoBFT/MP3C/MPC precedent): an endpoint you query live each round — e.g. LBMA fixings JSON at prices.lbma.org.uk — is a dataset/service → T3 with `open_service` access_status and the extracted snapshot committed under `extracted_data/`. Reserve T2 for fixed institutional documents (PDFs/xlsx) that can be hosted in `full_texts/`. The registry row's value is the *route + schema + verification*, not a file.
- **Vendor-published data with restrictive terms = extraction-only T2.** JM PGM market report: free public download but its disclaimer says prices "are the property of Johnson Matthey Plc" + use without consent prohibited → do NOT commit to `full_texts/`; register as T2 with access_status `verified_live_not_pulled (<terms>)` and put every number into extracted_data. Check the vendor's terms page BEFORE downloading, not after.
- **Deepening an already-hosted source = FINDINGS block + extracted CSV only; registry stays unchanged** (R50/R52 convention). The round still gets its own log entry stating "registry unchanged at N" and a final verify that asserts the aggregate row count + tier split are IDENTICAL to HEAD. A deep-dive pass is how criterion #2 (pull ALL relevant info) gets satisfied: after registering an audit/report, later rounds should re-scan it for every remaining load-bearing figure (R52 mined IG-24-001's Table 1 element costs, the Shuttle case study and the F9H contract price out of a report R51 had already registered).
- **Never hand-type percentage deltas or unit conversions — compute them.** R46 shipped five wrong pcts into four files before catch: $1,750/troy oz is ~$56.3k/kg (not "~$41k"), and several diffs were off by 1-2 points. Build the extracted CSV with `pct(ours, ref)` computed in code from raw values, then copy ONLY verified numbers into prose; re-grep all four files for stale variants before committing.
- **Verify displayed statistics from RAW component cells at full precision — never from derived columns stored with limited decimals.** R56: a verify pass recomputed a fleet band over 5-decimal delta columns and got an endpoint one display-ulp off the build-time `%.4f` formatting (spurious FAIL); recomputing dry/(dry+prop) from the raw component cells matched exactly. Derived CSV columns are lossy; components are canonical.
- **Programmatic quote slicing has two failure modes** (R52): (1) fixed-length slices cut INSIDE the probe when `length < len(probe)` — always slice `full[i:i+max(length, len(probe))]`; (2) "extend to sentence boundary" must start from the PROBE'S END (`i+len(probe)`), not from `i+length` — an overshooting length walks past the intended period and grabs the next sentence. Verify by re-reading every slice printed at apply time.
- **Verifying quote fidelity: use an explicit fragment list, never regex-extract quoted spans.** A `"([^"]+)"` sweep over a FINDINGS section pairs quotes ACROSS sentences (the span between one closing and the next opening quote is prose) → false failures. Keep the exact probe strings in both apply and verify scripts; check each against (a) the hosted PDF text, (b) the extracted CSV's verbatim column, and only those actually quoted in FINDINGS against the section.
- **Append scripts must be idempotent or a mid-script crash corrupts state.** R45's apply script crashed AFTER both CSV appends but BEFORE FINDINGS/INDEX (a helper-signature bug) — re-running naively would have double-appended the registry rows. Every file mutation in an apply script needs a presence guard (`if <id> not already in parsed: append`), and post-crash verification must check for duplicate ids, not just "row exists".
- **Idempotency guards must derive counts from live state** (R66): an apply script asserting `len(new) == len(old)+4` breaks on its own re-run once the first pass already wrote. Compute expected = current aggregate ids + missing NEW ids, and guard every file mutation with a presence check.
- **Line endings: repo files are CRLF on disk (core.autocrlf=true) but LF in git.** Do all string surgery in a `\n`-normalized space, write back as pure CRLF (`s.replace("\n","\r\n")`, assert no stray CR first). Mixing conventions turns a 19-line diff into a whole-file rewrite. CSVs: append rows with csv.writer(lineterminator="\r\n"); never re-serialize the whole file (quoting drift = false churn).
- **Text-mode one-liners silently flip CRLF→LF on Windows.** A quick `open(p).read()/replace/write` round-trip strips every CR (universal-newline mode) and a 100-line file becomes pure LF — the next verify pass catches it as "lf_only=100". For any surgical md edit use binary read + `.decode()` + explicit `.encode().replace(b"\n", b"\r\n")` write (or fix after: assert `b.count(b"\r")==0`, then replace LF→CRLF — lossless when no CRs remain). The same universal-newline conversion bites READS too (R56): a verify script that reads CRLF files in plain text mode and searches for anchors containing explicit "\r\n" silently finds nothing — an empty section slice produces false FAILs. Read with `newline=""` or binary, always.
- **OneDrive stat churn makes `git status --porcelain` columns unreliable** — a file whose index entry equals HEAD can still show "M" in column 1 after mtime changes. For final-verify change-set checks use `git diff --name-only` + `git ls-files --others --exclude-standard` (content-based), not porcelain parsing.
- **Never put markdown backticks inside a double-quoted `git commit -m`.** R49's message contained `` `NRHO → low lunar orbit` `` — bash ran it as command substitution, dropped the text from the pushed message and printed stray "command not found" noise. Write multi-line messages to a file in scratch and use `-F <native path>` (MSYS `/c/...` paths fail for git's -F; pass `C:/Users/...`). If an already-pushed message is cosmetically wrong: do NOT force-push — the approval gate blocks it without user consent. Fix with a follow-up `git commit --allow-empty -F <file>` addendum that restates the lost text and notes no file content changed.
- **A wedged browser wastes ~20 min per attempt.** Two distinct failure modes: (a) CLI missing — error says "Browser Use CLI not installed" → fix = `hermes tools` install, NO restart needed; (b) daemon wedged — 420s timeouts even on a fresh named session → record "backend fault", move to non-browser routes, tell the user a Hermes restart is needed. If it fails once in a round, do NOT retry more than one additional time either way. Distinguish backend faults from target-site blocks before updating any registry access_status.

## Source access notes

Per-site fetch patterns (NTRS, NASA OIG, ADS, AIAA, vendor datasheets) verified from this machine: see `references/source-access-notes.md`.

Registry rules added since this skill was written (seven access classes, licence-from-the-file rule, append-at-top log, rejection and permanent ids, revision-candidate updates) and fetch routes re-checked on 2026-10-05, including User-Agent gates that run in opposite directions per host: see `references/registry-rules-and-routes.md`.
