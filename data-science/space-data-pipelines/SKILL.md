---
name: space-data-pipelines
description: "Build space/astro data pipelines with verified API gotchas."
version: v1.0.0
author: Hermes Agent (ported from starred-repo research; deep pass on juliensimon/space-datasets 2026-09-12)
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
