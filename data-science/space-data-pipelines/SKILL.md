---
name: space-data-pipelines
description: "Build space/astro data pipelines with verified API gotchas."
version: v1.2.0
author: Hermes Agent (ported from starred-repo research; deep passes on juliensimon/space-datasets 2026-09-12 shared library + 2026-09-13 parser families; reconurge/flowsint pipeline architecture 2026-09-15)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pipelines, parquet, huggingface, api-gotchas, licensing]
    related_skills: [astro-toolkit-selection, orbital-mechanics-data, economicspace-pipeline, cron-pipeline-watchdog]
---

## What This Skill Does

Pattern for self-maintaining public space/astronomy datasets, distilled from the `juliensimon/space-datasets` repo (230 auto-updating HF Parquet datasets, 108 GitHub Actions workflows). Use when ingesting NASA/JPL/VizieR/HEASARC/CelesTrak sources into clean tabular data that refreshes on a schedule.

## When to Use

- Ingesting public space/astronomy feeds (JPL SSD, VizieR TAP, HEASARC TAP, MAST TAP, CelesTrak, Space-Track) into Parquet datasets
- Building or maintaining scheduled data pipelines that must survive flaky upstreams
- Deciding how to license redistributed space data (ESA/VizieR traps — see references below)

## One script per dataset (6 steps)

Every pipeline is ONE script following the same shape:
1. **Fetch** — HTTP to public API/file; set `timeout=`, sleep between sequential calls, use one shared retry helper.
2. **Transform** — pandas: type coercion (`pd.to_numeric(errors="coerce")`), snake_case rename (`distance_au` not `dist`), derived columns. JPL returns some numerics as strings — coerce after unwrap; NHATS nests `min_dv`/`min_dur` as `{"dv":…, "dur":…}` dicts.
3. **Validate** — gate with `check_dataset(df)` BEFORE upload: min rows, expected columns present, entirely-null column = hard fail, critical-column null thresholds, row-count trend vs last run (catches silent source breakage). Incremental pipelines set `fail_on_drop=True` — data loss is the real failure mode there.
4. **Write** — `df.to_parquet(path, index=False, engine="pyarrow", compression="zstd")`.
5. **Upload** — HF via huggingface_hub; local test = script fails at upload but parquet is already written to temp dir first. Skip `create_repo` when the repo exists (rate-limit avoidance); retry 429/5xx with capped backoff; on a broken-LFS-pointer rejection, delete the offending remote file and re-upload once.
6. **Status** — update status.json with date + row count per key; keys written alphabetically so concurrent daily pushes don't merge-conflict.

**Runnable reference implementation:** `scripts/pipeline_skeleton.py` (this skill) carries three shared helpers verbatim-in-spirit from space-datasets — `jpl_query()` (retry/backoff on 5xx), `vizier_query()` (recno-cursor pagination, VizieR TAP has no OFFSET), `check_dataset()` (hard-fail row/schema/null gates + truncated-upload guard) — wired to a live NHATS fetch as the self-test. Verified end-to-end 2026-09-07: 7,045 rows fetched, validation passed with 0 warnings.

## Per-source parser families (full detail in `references/source-parser-families.md`)

How each distinct source format is actually parsed — six families, all portable:
- **TLE two-line elements**: fixed-position char slices (`norad [2:7]`, epoch year `[18:20]` with the century rule `>=57→1900s else 2000s`, bstar/eccentricity as implicit-decimal scientific), stateful line-1/line-2 pairing, Kepler-derived altitude column as a data-quality signal, PyArrow schema-enforced writes so one bad day can't mutate the year file's schema, empty-response = warning+skip (not an error) for lagging Space-Track.
- **PDS3/PDS4 fixed-width `.tab`**: colspecs from the source's own `.lbl` files; `dtype=str` then strip/sentinel-map then coerce; dual-key merge split by numbered-vs-unnumbered objects (join provisional designations separately or you lose them); PDS3 proper-elements sentinel `0.0 = unavailable`.
- **GOES netCDF**: discover the versioned filename via directory-listing regex at run time; long-format status rows (EVENT_START/PEAK/END) pivoted to one-row-per-flare by dict-keying on flare_id; seconds-since-2000-01-01T12:00 epoch.
- **Wikidata SPARQL**: multi-value properties fan out rows — dedup with a data-richness sort, not blind keep="first"; strip full URIs to Q-IDs; drop bare `Q\d+` stub entities; hand-maintained override dict for missing properties applied only where null.
- **HTML scraping (FCC filings)**: commit real page snapshots as git fixtures + pure offline parser tests covering BOTH layouts the site serves — layout drift fails locally before the weekly cron ships broken data, not in production. Seed JSON with a load-time invariant (`sum(shell counts) == requested total`).

## Shared-library internals (full deep read in `references/shared-library-internals.md`)

The upstream repo's `hf_dataset_utils` package is the reference implementation of every pattern above; source-read 2026-09-12:
- **Retry budget**: one helper, waits `(30, 60, 120, 240, 480)` (~21 min worst case) — sized to outlast a real CelesTrak TCP black-hole outage (Aug–Sep 2026: 6+ min stretches from GitHub runners). Safe only because non-retryable statuses (404/401/400) raise immediately; 403 IS retried (CelesTrak transiently blocks runner IPs).
- **HEASARC TAP**: query failures arrive as **HTTP 200** with a plain-text `---- Messages ----` block containing a `Failure:` line — unguarded, it parses into a bogus one-column DataFrame that passes non-empty checks. Guard for the `Failure:` prefix before parsing (re-probed live on this machine 2026-09-12).
- **MAST TAP**: sync cap 100K rows/request; keyset pagination on primary key beats composite ORDER BY; on 504 halve page size down to a 5,000 floor and never ramp back up.

## Update strategies

- Full rebuild: re-fetch entire source (single file or small sources).
- Incremental: download existing parquet from HF, fetch 7–14 day window, `pd.concat` + `drop_duplicates(keep="last")`; fall back to full rebuild if no prior data exists. **Guard rail**: abort when the downloaded "existing" dataset is smaller than a floor (e.g. 100 rows) so a bad small fetch can't overwrite months of history. Best for append-only streams (TLEs, flares, Kp index).

## Verified source API gotchas

| Source | Gotcha |
|--------|--------|
| VizieR TAP | Always `SELECT *`; check real CSV headers with curl first — column names differ from docs (`logAge50` not `Age`, brackets sanitized). **No OFFSET** — paginate via the `recno` pseudo-column. Error responses come back as VOTable XML even when CSV was requested — guard `startswith("<?xml")`. |
| HEASARC TAP | Use `FORMAT=text` (pipe-delimited); `FORMAT=csv` can return VOTable XML instead. **Failures = HTTP 200 + text block** with a `Failure:` line, not an error status. Sync truncates large tables (~28K) — add `MAXREC=500000`. |
| SIMBAD TAP | Query the `basic` table only — JOINs with `allfluxes`/`mesDistance` fail. Use `OR` chains, not `IN (...)`. No `regexp()`. |
| CelesTrak | 500s are common and it black-holes TCP connections from CI runners for minutes at a time (2026-08-28..31 took out 5 pipelines; 2026-09-08 outage outlasted the then-current budget). Never hand-roll retries — one shared helper with a ~21 min budget, tuned in ONE place. |
| GFZ Kp API | Unreliable — prefer NOAA SWPC endpoint. |
| Space-Track | Authenticated cookie session. Be extremely conservative (a daily pipeline should make exactly 2 requests/day: login + one query). GP history returns only TLEs *generated* that day, not a snapshot — forward-fill for backfills. Accounts get banned for aggressive use; the upstream repo keeps this in its watchdog NO_RETRY set for the same reason. |
| Wikidata SPARQL | Mostly-empty stub entities — drop >95% null columns after fetch and guard README stats with `if "col" in df.columns`. |

## Asterank mining-economics endpoint (re-probed live 2026-09-12)

`http://www.asterank.com/api/asterank?query=<JSON>&limit=<N>&offset=<M>` — keyless, ~600K rows via limit/offset pagination.
**Two query modes with different schemas:** bulk scans (`query={}`) never carry a `dv` key; **targeted queries DO** (re-verified this machine 2026-09-12: `{"name":"Eros"}` → dv=6.112354). Query param is a JSON object, not free text — plain numbers give HTTP 500; working keys are `name` and `pdes`. Economics fields (`price`/`profit`) remain partially garbage (real values for some bodies, 1e-44-scale nonsense for others) — order-of-magnitude priors only. Reliably present in both modes: spectral types (`spec`=SMASSII, `spec_B`, `spec_T`), diameter + sigma, albedo, rotation period, GM, full orbital elements, orbit-quality fields (condition_code/data_arc/rms/orbit_id), **per-element covariance diagonal** (`sigma_a`…`sigma_tp`) and obs provenance. Full correction history: skill `economicspace-pipeline`, ref `dv-oracles-and-economics-sources.md`.

## Keyless HF mirrors of the same feeds (see `references/hf-mirror-catalog.md`)

~230 datasets under `juliensimon/*` on Hugging Face — no API keys, one-line load. Useful as frozen snapshots for cross-checks/backfills when the live feed needs auth (Space-Track), per-body calls (Asterank dv), or has dead endpoints (UCS). Cadence: ~50 daily / ~20 weekly / rest static; upstream `status.json` tracks dates + row counts.

## Licensing redistributed space data (see `references/space-data-licensing-audit.md`)

Default "NASA/ESA public API ⇒ CC-BY-4.0" is **wrong** for a large fraction of providers: ESA Space Science Archives = **CC BY-NC 3.0 IGO** (no commercial use), WDC Kyoto geomagnetic indices no-commercial, SILSO sunspot numbers CC BY-NC 4.0, AAVSO NC-only, and VizieR's own terms are "scientific context" — not CC-BY at all. The source license travels with the data: fetching ESA catalogs via VizieR/HEASARC mirrors does NOT strip the restriction. When unsure, label `license: other` + upstream policy link rather than over-permissive cc-by-4.0.

## Lunar-surface GIS (see `references/lunar-gis-patterns-aegis.md`)

South-pole LPS projection math from nasa/aegis (AEGIS) — re-derived and **verified against the real lgrs 0.3.0 package to ≤5.8e-11 m** (`scripts/lps_projection_verify.py`, stdlib-only, exit-code gated): exact constants (R=1737.4 km, K0=0.994, false E/N = 500000 m), the -80° domain limit, lgrs API traps ((latitude, longitude) constructor order; `to_lps()` returns an object with `.easting`/`.northing`, not a tuple; PyPI needs Python ≥3.13), plus GeoTIFF custom-CRS reconstruction (transform codes 15=polar-stereo / 17=equirectangular from numeric GeoKeys when no EPSG code exists) and geographic→pixel nearest-cell sampling for lunar DEM products.

## Flowsint pipeline-architecture patterns (see `references/flowsint-pipeline-patterns.md`)

Source-level read of reconurge/flowsint @ 1820569 — an OSINT graph tool whose architecture is a clean reference for any multi-source chaining pipeline: the **three-layer split** (pure schema types / one-external-system-each tools returning raw data / typed enrichers that own all side effects), **decorator auto-discovery** via os.walk with per-module import-error isolation + idempotent load flag, the **scan/postprocess two-phase contract** (gather phase has no I/O; persist phase has no network — each independently testable) with strict `extra="forbid"` params models and deferred vault-secret resolution, **Neo4j MERGE semantics keyed on (type, nodeLabel, sketch_id)** — label collisions are graph-correctness bugs, not cosmetics — plus soft-delete resurrection and batched idempotent re-runs. Also: declarative YAML templates as a first-class extension mechanism with an LLM generator gated by schema-in-prompt + fence-strip repair + `safe_load` + frozen Pydantic validation (LLM-writes-*config* beats LLM-writes-code), per-run JSON audit logs with input-keyed memoization and fail-fast, DockerTool wrapper quirks (`TERM=dumb`, diagnostic re-run on non-zero exit), test conventions for pipeline components, a recurring-bug-class checklist from their PR history (~8 naive-datetime fixes, IDOR, UTF-8 assumptions, tight healthcheck timeouts), and the anatomy of their embedded agent extension-builder skill (source-paths table + decide-before-code tree + refuse-list).

## Scheduling template (GitHub Actions)

- `on: schedule` cron staggered across a UTC window + `workflow_dispatch` for manual runs; `permissions: contents: write`; `environment:` with the HF token secret.
- After upload, commit+push only the status file with a retry loop (`git pull --rebase`, up to 3 attempts) so concurrent dataset workflows don't clobber each other's status commits.
- **Watchdog**: a daily job after all regular runs detects stale datasets from cron-derived periods, auto-retries transient failures (persistent state), and escalates persistent ones to idempotent GitHub issues — full pattern in skill `cron-pipeline-watchdog` (works for any scheduled pipeline, not just space data).

## Checklist before shipping a new pipeline

1. Script passes `python -m py_compile` (no test suite needed — validation lives in-step).
2. `check_dataset()` runs and PASSES on real fetched data, not just shape; no column >80% null without justification.
3. Row count printed for the status step.
4. If incremental: confirm dedup key is stable across source updates AND the existing-data floor guard is set.
5. License checked against the provider's policy page (not the upstream card) — see licensing ref.
6. Add to a domain collection/index so it's discoverable.
