---
description: "hf_dataset_utils internals from juliensimon/space-datasets (230 pipelines): retry budget, TAP clients, HEASARC HTTP-200 failures, MAST keyset pagination, LFS recovery, watchdog"
source_repos: juliensimon/space-datasets @ 5f886cd (clone %LOCALAPPDATA%\Temp\space-ds-dive, read in full this pass)
tested_version: clone @ 2026-09-12; HEASARC HTTP-200 failure block + Asterank targeted dv re-probed LIVE on this machine same day
verified_date: "2026-09-12"
---

# space-datasets Shared Library Internals (hf_dataset_utils)

Deep read of the shared library behind all 230 pipelines in `juliensimon/space-datasets` (~2,800 lines across
`scripts/hf_dataset_utils/`, `mast_tap.py`, `stale-checker.py`). Everything below was source-read from the clone;
the three items marked **[LIVE]** were re-probed on this machine 2026-09-12. Patterns are portable to any
scheduled data-pipeline project — see also skill `cron-pipeline-watchdog` (devops) for the watchdog pattern in isolation.

## fetch_with_retry — one retry helper, tuned budget, picky status set (`http.py`)

```python
RETRY_WAITS = (30, 60, 120, 240, 480)          # ~15 min of backoff + connect timeouts ≈ 21 min worst case
RETRY_STATUS = frozenset({403, 408, 425, 429, 500, 502, 503, 504})
```

- Origin (from the module docstring): between 2026-08-28 and 08-31 celestrak.org **black-holed TCP connections from
  GitHub runners for stretches of 6+ minutes**; every pipeline whose per-script retry loop gave up sooner failed.
  The budget was widened again after a 2026-09-08 outage outlasted the original ~12 min (run 34209051829 exhausted all attempts).
- **A long budget is only safe because of status pickiness**: non-retryable statuses (404, 401, 400) raise immediately —
  retrying a dead URL would burn the whole ~21 min and bury the cause under a timeout. 403 IS retried because CelesTrak
  transiently blocks runner IPs with 403 before allowing access again.
- The regression test (`scripts/tests/test_http_retry.py`) pins **both halves of that bargain**: the ladder is walked for
  transient failures (asserts exact sleep sequence `[30, 60]`), and skipped entirely for a status that will never recover
  (404 → zero sleeps, exactly one `requests.get` call). Sleeps are captured, not performed — "the real ladder is 7.5 minutes".

## VizieR TAP client (`tap/vizier.py`) — recno cursor pagination

- **No OFFSET in ADQL** — paginate with the `recno` pseudo-column: inject `recno > <last>` (before any ORDER BY,
  AND-ed into an existing WHERE or as a new one), PAGE_SIZE = 500,000.
- Error responses come back as **VOTable XML even when CSV was requested** — guard with `text.startswith("<?xml")` /
  `"<VOTABLE"` and hard-fail printing the first 500 chars (a silent parse of an error page is worse than a crash).

## HEASARC TAP client (`tap/heasarc.py`) — format fallback + HTTP-200 failures **[LIVE]**

- Format chain `text → csv → json`, each attempt retried up to 3× with exponential backoff (30 s base); the first
  parseable non-empty result wins. Default is **`FORMAT=text`** (pipe-delimited) — requesting CSV can return VOTable XML instead.
- **[LIVE, verified this machine]: query failures arrive as HTTP 200** with a plain-text `---- Messages ----` block whose
  content includes a line starting with `Failure:` (probed: `SELECT bogus_column FROM fermi_4fgl` → status 200, no XML).
  Left unguarded the text parser turns that into a **bogus one-column DataFrame that passes the non-empty check**, masking
  a hard query failure as a cryptic downstream KeyError. Guard = scan lines for `Failure:` prefix before parsing; treat it
  as deterministic (don't retry, move to next format).
- The pipe-text parser: skip separator lines (only dashes/pipes/spaces), trim values to header count, replace literal
  `"null"`/`"NULL"` with NA, then auto-detect numeric types **with a no-new-NaN guard** (`converted.isna().sum() == df[col].isna().sum()`).

## MAST TAP client (`mast_tap.py`) — keyset pagination + adaptive page size (JWST/HST/Kepler/GALEX)

Constraints learned from 4 missions (module docstring, all verified in code):
- Sync TAP **caps at 100K rows per request**; `dbo.caomplane` is wider and hits 504 at 100K — use 50K for it.
- JOIN between caomobservation and caomplane **times out server-side** — aggregate client-side after two separate fetches.
- Keyset pagination on the primary key (`ORDER BY id ASC` + `WHERE ... AND id > '<last>'`) is much faster than composite ORDER BY.
- On a 504, **halve the page size down to a floor of 5,000 and never ramp back up** — "bouncing between 50K and 25K wastes pages to 504s".
- Hand-rolled regex VOTable parser (`<TR>`/`<TD>`/`<FIELD name=`) is **~10× faster than astropy.io.votable** for wide, string-heavy rows and avoids the astropy dependency entirely.

## Upload path (`upload.py`) — rate-limit + broken-LFS recovery

- Skip `create_repo` when the repo already exists (avoids rate-limited calls during the busy morning window when many workflows run concurrently).
- Retry 429/5xx with capped exponential backoff: base 10 s, cap 300 s, max 10 attempts.
- **Broken LFS pointer recovery**: HF rejects a commit when an existing remote file has a broken LFS pointer (HTTP 400).
  Parse `Offending file: - <path>` from the error message, `api.delete_file(...)` on the remote, retry the upload once.

## Incremental updates (`incremental.py`) — three primitives + one guard rail

- `download_existing()`: `hf_hub_download` of `data/<file>`; returns None on ANY failure → caller falls back to full rebuild.
- `merge_dedup(existing, new, key, sort_by)`: `pd.concat` + `drop_duplicates(subset=key, keep="last")` (new wins) + stable sort.
- `append_by_date(existing, new, date_col, min_existing=100)`: replaces overlapping dates in existing data; **aborts with
  sys.exit(1) when existing < min_existing** — protects months of historical data from a bad small fetch overwriting it.

## Validation semantics (`validation.py` check_dataset)

- Hard fail (sys.exit 1): rows below `min_rows`; any expected column missing; ANY entirely-null column (skipped for empty frames — vacuous truth).
- Warnings (GitHub Actions `::warning::` annotations, don't block publish): critical-column null fraction > `max_null_pct` (default 5%);
  optional all-column sweep via `warn_all_nulls`; row-count drop vs previous run > `max_row_drop_pct` (20%) — promoted to hard fail with `fail_on_drop=True`, which is what incremental pipelines set, since data loss there is the real failure mode.

## Cleaning helpers (`cleaning.py`)

- `coerce_int` → nullable **Int64** (not int32) so NA survives; `coerce_numeric(errors="coerce")`.
- `clean_strings`: preserve existing NAs BEFORE `astype(str)` — otherwise pd.NA becomes the string `"<NA>"`; then replace
  `""/nan/None/<NA>` with pd.NA and cast to `"string"` dtype. Skip (with warning) if a listed column is already numeric or absent.
- `drop_mostly_null(threshold=0.95)` — for TAP wide schemas where optional fields are empty; run BEFORE validation so dropped columns can't trip the all-null gate.

## Pipeline context manager (`pipeline.py`) + status.json merge-conflict trick

`Pipeline(repo, pretty_name, description, tags, source_url, ...)` → `p.clean(df, numeric=..., integer=..., strings=...)`
→ `p.publish(df, filename, min_rows, ...)`: validate → write parquet (zstd/pyarrow) into a temp dir's `data/` subdir →
banner image download → **auto cross-links** (`crosslinks.py` inverts the central `DATASET_DOMAIN` registry and appends up to 4 same-domain siblings)
→ generate README card → upload → emit `rows=N` to `$GITHUB_OUTPUT`.

The workflow's status commit (see CLAUDE.md template): keys are **always written alphabetically** (`_rows` first, sorted inside; then per-dataset date keys).
Sorted ordering prevents merge conflicts between the ~50 concurrent daily-cron pushes that would otherwise all append at end-of-file.
Commit loop: `git pull --rebase || true`, `git checkout status.json` (discard local drift), update, `git diff --cached --quiet && break`, push with 3 attempts + reset on failure.

## Watchdog (`stale-checker.py`) — full pattern in skill `cron-pipeline-watchdog`

Daily at 21:00 UTC (after all regular workflows). Derives each dataset's expected period from its workflow cron expression
(dow≠* → weekly; month-limited → 366/n_months incl. `*/N`; dom digit → monthly; else daily), flags stale when
`today − last_success > period + GRACE_DAYS(1)` or never succeeded, then: GHA status success → repair status.json from run logs (regex the `--rows N` line out of `gh run view --log`); in progress → skip; failed → persistent retry-state machine (`data/retry-state.json`, MAX_RETRIES=2) before escalating to an **idempotent** GitHub issue (title-search for open `[watchdog] <name> pipeline failing` first). A NO_RETRY set exists for datasets where re-triggering is dangerous — `tle-history`, because Space-Track bans aggressive accounts.

## HF dataset-card frontmatter conventions (`readme.py`)

- Required: `license`, `pretty_name`, `language`, `description` (≤200 chars, Google-indexed), `size_categories` bucket computed from row count (n<1K … 1B<n<10B), `task_categories`, `tags` (4 mandatory: `space open-data tabular-data parquet` + domain + source names).
- **Multi-config repos need `default: true` on the primary config or `load_dataset()` fails** — always set it.
- YAML escaping order matters: backslashes BEFORE quotes; tags containing special chars get double-quoted; markdown table cells escape `|` → `\|`.

## License audit (full detail in `space-data-licensing-audit.md`)

The repo's own 2026-05-26 audit found **30 datasets mis-licensed** as cc-by-4.0 when upstream forbids commercial use
(ESA = CC BY-NC 3.0 IGO, WDC Kyoto no-commercial, SILSO CC BY-NC 4.0, AAVSO NC) and relicensed 89 total in commit e05a793.
Key rule: **the source license travels with the data — fetching ESA mission catalogs via VizieR/HEASARC mirrors does not strip the restriction.**
