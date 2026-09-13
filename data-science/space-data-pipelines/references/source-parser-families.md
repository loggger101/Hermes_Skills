---
description: "Per-source parsing families from space-datasets (round-15): TLE two-line-element char positions + epoch century rule, PDS3/PDS4 fixed-width colspecs, GOES netCDF status pivot, Wikidata SPARQL dedup, HTML fixture testing"
source_repos: juliensimon/space-datasets @ 5f886cd (round-15 pass, 2026-09-13; scripts read in full this pass)
tested_version: clone %LOCALAPPDATA%\Temp\space-ds-dive (re-cloned for round 15); fixtures kuiper.html/starlink-gen1.html verified present in repo tree
verified_date: "2026-09-13"
---

# Per-Source Parser Families (general code patterns, source-read from space-datasets)

Round-14 covered the shared library; this file covers **how each distinct source format is actually parsed** — six families across ~226 scripts. All snippets are verbatim-in-spirit from `scripts/update-*.py`; every one generalizes beyond its home dataset.

## 1. TLE two-line elements (`update-tle-history.py`)

TLEs are **fixed-position text, not delimited** — the parser is a table of character slices:

| field | line | slice (0-indexed) |
|---|---|---|
| norad_id | 1 | `[2:7]` int |
| intl_designator | 1 | `[9:17]` strip |
| epoch year | 1 | `[18:20]` **century rule: `>=57 → 1900+yy else 2000+yy`** (TLE epochs cross the century at 57, not 50/60) |
| epoch day-of-year | 1 | `[20:32]` float; convert via `datetime(year,1,1)+timedelta(days=day-1)` in UTC |
| mean_motion_dot (ndot) | 1 | `[33:43]` plain float |
| bstar | 1 | `[53:61]` **implicit-decimal scientific**: `±NNNNN±EE` → `sign * 0.NNNNN * 10**EE`; literal `"00000-0"`/`"00000+0"` = 0.0 |
| inclination / raan / arg_perigee / mean_anomaly | 2 | `[8:16] [17:25] [34:42] [43:51]` plain floats (degrees) |
| eccentricity | 2 | `[26:33]` **implicit decimal**: `"0." + slice` |
| mean_motion | 2 | `[52:63]` rev/day, keep float64 precision (`round(...,8)`) — it's the most information-dense column for decay studies |

Other rules worth copying:
- Pair parsing is **stateful**: buffer a line starting `"1 "`, parse when the next line starts `"2 "`; anything else resets the buffer. Malformed pairs return None and are silently dropped (count them if you care).
- Derived altitude via Kepler's third law, not from any TLE field: `a = (MU/(n*2π/86400)²)**(1/3)` with MU=398600.4418 km³/s², then `alt = a*(1−e) − 6371`. Negative result flags decayed objects or parse errors — keep it as a data-quality signal column.
- Schema-enforced writes: build the day's batch with **PyArrow** (`pa.Table.from_pylist(records, schema=SCHEMA)`), merge in pandas, re-cast to `pa.Table` before writing — so a bad field can't silently change the year file's parquet schema mid-stream (int32 norad_id, float32 angles, timestamp[us,UTC] epoch).
- Idempotent daily append: delete existing rows where `epoch.dt.date == yesterday` BEFORE merge-dedup on `(norad_id, epoch)` — re-running a failed day never doubles it. Year-partitioned files (`tle_{year}.parquet`) with Jan-1 rollover creating the new file.
- **Empty response ≠ failure**: Space-Track can lag; zero TLEs → `::warning:` + exit 0 (skip), not an error that trips the watchdog into re-hammering a rate-limited API.

## 2. PDS4 fixed-width `.tab` (`update-bus-demeo.py`)

PDS Small Bodies Node tables are plain-text **fixed-width** with layout documented in sibling `.lbl` label files:
- Parse with `pd.read_fwf(StringIO(resp.text), colspecs=[(0,7),(8,25),...], names=[...])` — the colspec tuples come straight from the .lbl (start,end pairs). Bus-DeMeo's two tables: demeotax.tab 6 cols + pcscores.tab 8 cols.
- **Dual-key merge for numbered vs unnumbered objects**: split both frames by `asteroid_number > 0`, merge numbered-on-numbered, unnumbered-on-provisional-designation (strip whitespace first!), concat back. A naive single-key join loses every provisional-only object or double-counts the rest.
- Class strings carry suffix semantics: strip trailing `"w"` (slope>0.25 µm⁻¹) and `":"` (uncertain) before mapping to broad complex; unknown classes → NA, not a crash.

## 3. PDS3 fixed-width (`update-sdss-taxonomy.py`) — the big-table variant

Same family, older PDS3 layout, with three extra patterns for ~107k-row tables:
- Colspecs stored as **`(name, start, width)` triples** and converted at parse time to `(start, start+width)` pairs.
- `dtype=str` on the read_fwf call, THEN per-column strip + sentinel replace (`{"nan","","-"}` → None), THEN numeric coercion — never let read_fwf guess types from fixed-width text (a column of `-` becomes a float -1.0 and poisons stats).
- **Domain sentinels**: proper elements stored as `0.0` mean *unavailable* in this dataset — explicitly map `== 0.0 → None` after coercion, or your "fraction with known orbits" stat is wrong by the null fraction.
- Memory discipline on big tables: `del <frame>; gc.collect()` between download/parse/merge stages (the raw text string alone is ~10× the parsed frame).

## 4. GOES netCDF flare summary (`update-solar-flares.py`) — long-to-wide status pivot

NCEI serves a **mission-length NetCDF** whose filename changes over time:
- Discover it by regex-scraping the directory listing for `href="(sci_xrsf-l2-flsum_g16_[^\"]+\.nc)"` — never hardcode the versioned filename.
- The file is long-format: one row per (flare_id, status) with status ∈ {EVENT_START, EVENT_PEAK, EVENT_END}. Pivot to one-row-per-flare by dict-keying on flare_id and filling start/peak/end + peak flux from whichever status row arrives. Masked-array values (`np.ma.is_masked`) → None before float().
- Time is seconds since `2000-01-01T12:00` epoch — add a timedelta, don't assume Unix time.
- Flare class extracted with regex `^([ABCMX])\d+\.?\d*`; the letter alone (A/B/C/M/X = 10⁻⁸…10⁻⁴ W/m² decades) is kept as its own column for filtering.

## 5. Wikidata SPARQL (`update-astronauts.py` + 9 sibling scripts, all CC0-licensed output)

Endpoint `https://query.wikidata.org/sparql?query=...&format=json`, 3 retries with exponential backoff (Wikidata is rate-limit-prone). The JSON bindings shape drives four recurring fixes:
- **Multi-value properties fan out rows**: one person with two nationalities returns two binding rows. Dedup by entity ID, but keep the row carrying the most data — their trick: sort by `len(employers)` desc before `drop_duplicates(subset=["wikidata_id"], keep="first")`.
- Entity IDs arrive as full URIs (`.../entity/Q1029`) → `.rsplit("/", 1)[-1]` to get the Q-ID.
- **Junk-entity filter**: rows whose only "name" is a bare `Q\d+` label are stub entities with no real name — drop them (`~df["name"].str.match(r"^Q\d+$")`). This is what CHECKLIST.md means by "mostly-empty stub entities".
- Missing properties (e.g. P27 nationality) get a **hand-maintained override dict** keyed by Q-ID, applied only where the column is null — targeted curation instead of re-querying.

## 6. HTML scraping with committed fixtures (`update-fcc-ngso-filings.py`) — the anti-fragility pattern

fcc.report (FCC IBFS filings) serves **two different layouts** for the same data type; the script's parser must handle both, and that is exactly what makes it testable:
- **Commit real page snapshots to git as fixtures** (`scripts/data/fixtures/kuiper.html` 23 KB = Form-312 layout with transcribed sections; `starlink-gen1.html` 12 KB = overview-table-only legacy layout) and run the parser against them in a pure unit test — no network, no HF. The docstring even ships the exact `curl -A "space-datasets/fcc-ngso-filings"` commands to refresh fixtures when a layout change is *intentional*.
- Layout drift thus fails **locally before the weekly cron ships broken data**, not in production after 40 filings are mis-parsed. The legacy fixture specifically asserts that fields absent from its layout fall back (empty string / overview-table cell) instead of raising — both code paths pinned by tests.
- Fail-fast on empty input: `parse_filing_html("<html></html>", ...)` must raise RuntimeError("No applicant found..."), tested explicitly.
- Hand-curated values live in a **seed JSON with an invariant enforced at load time**: for every filing, `sum(shell.satellite_count) == requested_satellites` — so extending the seed by hand can't silently break the dataset's core consistency claim (load_seed validates before any publish).

## 6b. Multi-config datasets + resumable binary assets (`update-spacex-launches.py`)

spacex.com's content API (JSON, no auth) is split into **three configs** in one HF repo — launches / timelines (countdown+deployment events per launch) / carousel (mission photos with captions). Patterns:
- Multi-config upload = multiple parquet files under `data/` + README frontmatter listing each config (`default: true` on the primary, or load_dataset fails — see shared-library-internals ref).
- **Resumable image download**: keep an `(image_url, image_path)` table in the carousel parquet; on re-run, skip slugs whose file already exists locally and only fetch the delta (streaming `requests.get(..., stream=True)`, write to temp then rename so a half-written JPEG never counts as "present"). This is what makes a 600-photo dataset cheap to refresh monthly.

## Cross-family rules of thumb

1. Fixed-width sources: colspecs come from the source's own label files (.lbl / format docs), not eyeballing; `dtype=str` first, coerce second.
2. Every parser needs a **sentinel map** for its specific "missing" encodings (`-`, `0.0`, `"null"`, masked arrays, implicit-decimal zeros) — there is no universal one.
3. Long-format event tables (start/peak/end rows per ID) pivot by dict-keying on the entity ID; never assume status ordering in the file.
4. Versioned filenames → discover via directory-listing regex at run time.
5. Anything scraped from HTML gets a committed fixture + offline test before it's allowed to publish on schedule (the FCC pattern is the template for all of them).
6. Multi-value joins fan out rows — dedup with a data-richness sort, not keep="first" blindly.
