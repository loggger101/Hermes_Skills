---
name: space-data-pipelines
description: "Build space/astro data pipelines with verified API gotchas."
version: v0.9.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pipelines, parquet, huggingface, api-gotchas]
    related_skills: []
---

## When to Use

- When working on: Build space/astro data pipelines with verified API gotchas.

## What This Skill Does

Every pipeline is ONE script following the same shape: 1. **Fetch** — HTTP to public API/file; set `timeout=`, sleep between sequential calls.


# Space Data Pipelines

Pattern for self-maintaining public space/astronomy datasets, distilled from the `juliensimon/space-datasets` repo (230+ auto-updating HF datasets, 108 GitHub Actions workflows). Use when ingesting NASA/JPL/VizieR/HEASARC/CelesTrak sources into clean tabular data that refreshes on a schedule.

## One script per dataset (6 steps)
Every pipeline is ONE script following the same shape:
1. **Fetch** — HTTP to public API/file; set `timeout=`, sleep between sequential calls.
2. **Transform** — pandas: type coercion, snake_case rename (`distance_au` not `dist`), derived columns.
3. **Validate** — gate with `check_dataset(df)` BEFORE upload: min rows, expected columns present, null thresholds per column, row-count trend vs last run (catches silent source breakage).
4. **Write** — `df.to_parquet(path, compression="zstd")` + README dataset-card frontmatter.
5. **Upload** — HF via huggingface_hub; local test = script fails at upload but parquet is already written to temp dir first.
6. **Status** — update status.json with date + row count per key.

## Update strategies
- Full rebuild: re-fetch entire source (single file or small sources).
- Incremental: download existing parquet, fetch 7–14 day window, `pd.concat` + `drop_duplicates(keep="last")`; fall back to full rebuild if no prior data exists. Best for append-only streams (TLEs, flares, Kp index).

## Verified source API gotchas
| Source | Gotcha |
|--------|--------|
| VizieR TAP | Always `SELECT *`; check real CSV headers with curl first — column names differ from docs. **No OFFSET** — paginate via `recno`. |
| HEASARC TAP | Use `FORMAT=text` (pipe-delimited). `FORMAT=csv` returns VOTable XML instead. |
| SIMBAD TAP | Query the `basic` table only — JOINs with other tables fail. Use `OR` chains, not `IN (...)`. No `regexp()`. |
| CelesTrak | 500s are common and it black-holes TCP connections from CI runners for minutes at a time. Never hand-roll retries — use one shared retry helper that rides out ~12 min; tune the wait budget in ONE place, not per script. |
| GFZ Kp API | Unreliable — prefer NOAA SWPC endpoint. |
| Space-Track | Authenticated cookie session. Be extremely conservative (a daily pipeline should make exactly 2 requests/day: login + one query). GP history returns only TLEs *generated* that day, not a snapshot — forward-fill for backfills. Accounts get banned for aggressive use. |

## Asterank mining-economics endpoint (verified live)
`http://www.asterank.com/api/asterank?query={}&limit=<N>&offset=<M>`
Returns ~600K asteroids, each with: `profit`, delta-v fields, spectral type (`spec`=SMASSII, `spec_B`=Bus-DeMeo, `spec_T`=Tholen), diameter + sigma, albedo, rotation period, GM, full orbital elements (a,e,i,om,w,ma,q,ad,per,n,t_jup,moid). Page it with limit/offset. The single best free source for asteroid *mining economics* — directly feeds a space-economics analysis pipeline.

## Scheduling template (GitHub Actions)
- `on: schedule` cron staggered across a UTC window + `workflow_dispatch` for manual runs.
- After upload, commit+push only the status file with a retry loop (`git pull --rebase`, up to 3 attempts) so concurrent dataset workflows don't clobber each other's status commits.

## Checklist before shipping a new pipeline
1. Script passes `python -m py_compile` (no test suite needed — validation lives in-step).
2. `check_dataset()` runs and PASSES on real fetched data, not just shape.
3. Row count printed for the status step.
4. If incremental: confirm dedup key is stable across source updates.
5. Add to a domain collection/index so it's discoverable.
