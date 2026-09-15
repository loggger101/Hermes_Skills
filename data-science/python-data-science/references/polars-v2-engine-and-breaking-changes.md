---
description: "polars 2.0 (rc) engine architecture + every breaking change live-verified on polars==2.0.0rc1 — streaming-by-default, row-order semantics, OOC spilling internals, GPU beta"
source_repos: pola-rs/polars @ main commit 6a00e21 (cloned %LOCALAPPDATA%\Temp\polars-dive), pyproject version = 2.0.0rc1; PyPI stable at time of writing = 1.44.x, rc available as polars==2.0.0rc1
tested_versions: "live checks on polars 2.0.0-rc.1 (venv %LOCALAPPDATA%\Temp\polars-dive-venv) + API-surface probes on stable 1.44.2 (venv %LOCALAPPDATA%\Temp\polars-1x-venv)"
verified_date: "2026-09-14"
---

# Polars 2.0 — Engine Architecture & Verified Breaking Changes

Deep-dive of `pola-rs/polars` (MIT, ~39.6k stars) at the **2.0 release candidate**. This is not a
skill: it's general code knowledge — what the engine actually does under the hood and which 1.x → 2.0
behavior changes are real, each backed by either source file:line or a live execution on this machine.

**Companion files:** `polars-pymc-api-reference.md` (stable-API idioms) · `big-data-patterns.md`
(pattern selection). **Re-run the verification any time:** `references/polars-v2-verify.py` — 39 checks,
last full run 2026-09-14: **39/39 PASS** on polars 2.0.0-rc.1 (exit code = failure count).

## Version status (verified 2026-09-14 via PyPI JSON API)

| Channel | Version | Notes |
|---|---|---|
| Stable | **1.44.2** | what `pip install polars` gives you; the version in `big-data-patterns.md` (1.44.1) behavior still holds |
| Release candidate | **2.0.0rc1** | on PyPI as `polars==2.0.0rc1`; everything below verified against it live |

The repo's own upgrade guide is `docs/source/releases/upgrade/2.md` (1,743 lines). I read the whole
thing and then **executed every claim that was testable** — see `polars-v2-verify.py`. Two claims turned
out to be *less* new than they look (below); everything else held exactly.

## The one change that matters most: streaming is now the default engine

`LazyFrame.collect()` / `collect_async()` still say `engine="auto"`, but **`"auto"` now resolves to the
streaming engine** for lazy queries (it used to resolve to in-memory). Eager `DataFrame` ops are
unaffected. Consequences, all live-verified:

1. **Row order is no longer guaranteed anywhere it wasn't required.** `unpivot`, `group_by`, and joins
   can return rows in a different order than 1.x — including *left-hand join row order*, which nothing
   about the query looks like an order dependency on (check #3: default join returned LHS keys as
   `[a2, a4, a6, a0, ...]`). Fix: `sort()` explicitly or pass `maintain_order` where supported — for
   joins that's now `join(..., maintain_order="left")`.
2. **Escapes:** per-query `collect(engine="in-memory")`, process-wide
   `pl.Config.set_engine_affinity("in-memory")` (verified: plain `collect()` output then matches the
   in-memory engine exactly), or env var `POLARS_ENGINE_AFFINITY=in-memory`.
3. **SQL is affected too:** `SQLContext.execute(eager=True)` / `pl.sql(..., eager=True)` now collect
   through lazy → streaming. In rc1 even the *default* of `execute()` flipped to returning a LazyFrame
   (check #35). Keep in-memory: leave it lazy and `.collect(engine="in-memory")` yourself.
4. **`LazyFrame.profile()` was removed** — its per-node timings were designed for the sequential
   in-memory engine and would mislead under concurrency. No replacement yet in OSS (Polars Cloud has a
   Query Profiler).

Streaming internals (`crates/polars-stream/`, 177 Rust files): a **concurrent graph executor with
morsel-driven parallelism** — data moves between nodes as "morsels" through ring buffers sized by
`POLARS_DEFAULT_LINEARIZER_BUFFER_SIZE` / `..._DISTRIBUTOR_BUFFER_SIZE` / `..._ZIP_HEAD_BUFFER_SIZE`
(default 4 each, see `crates/polars-stream/src/lib.rs`). Node catalog (one file per op in
`src/nodes/`) includes the interesting ones: `group_by.rs`, `sorted_group_by.rs`, `joins/`,
`dynamic_slice.rs`, `top_k.rs`, `merge_sorted.rs`, `rle_id.rs`, plus explicit **fallback nodes**
(`in_memory_source/sink/map.rs`) — any op not implemented streaming falls back to the in-memory engine
for just that node, transparently. Correctness check #39: streamed vs in-memory group_by+agg results are
identical after sort on rc1.

## Out-of-core (OOC) spilling — real subsystem, still maturing

New crate `crates/polars-ooc/` implements **spill-to-disk for the streaming engine** (`Spillable` trait:
`estimate_byte_size()` / `spill()` / `unspill()`, all async). Design facts from source
(`memory_manager.rs`, `spill_file.rs`, `crates/polars-config/src/lib.rs`):

- Global `MemoryManager`: spills when `(usage + incoming_prefetch) − in_progress_spill > budget`;
  prefetches back up to a second (higher) threshold. Budgets: `POLARS_OOC_MEMORY_BUDGET_FRACTION`
  default **0.8** of RAM, or absolute `POLARS_OOC_MEMORY_BUDGET_MB`.
- Spill *candidate selection* is score-based with an explore term — constants in source:
  `EXPLORE_BEYOND_BEST_SCORE_THRESHOLD = 20.0`, at most `SPILL_FRAME_BATCH_SIZE = 256` candidates per
  attempt; eviction policies are pluggable (`LeastRecentSpillContext`, `MostRecentSpillContext`,
  `RandomSpillContext`).
- Concurrency: separate tokio semaphores for spill vs prefetch tasks, both default **64** parallel.
- On-disk layout (from the doc comment in `spill_file.rs`): `<spill_dir>/<pid>/spill-<ctx>-<uuidv7>.ipc` —
  per-process subdirs, UUIDv7 names, IPC format; a background cleaner thread deletes files on drop.
  Min spill size default **64 KB** (`POLARS_OOC_SPILL_MIN_BYTES`), drift threshold 4 MB.
- **Maturity caveat (verified):** the whole Python test suite for OOC is `@pytest.mark.skip`ped
  (`py-polars/tests/unit/ooc/test_ooc.py`) and it references a `POLARS_OOC_SPILL_POLICY=spill` env var
  that does NOT exist in the config surface — treat OOC as experimental, don't build pipelines on it yet.

## GPU support (Open Beta)

`pip install polars[gpu]` → RAPIDS **cuDF** backend (`cudf-polars-cu12` by default; pin
`cudf-polars-cu13` for CUDA 13). Requires NVIDIA Volta+ / compute capability ≥7.0, Linux or WSL2 — so
on this Windows box it's a WSL2-only story. Usage is just `q.collect(engine="gpu")`. Multi-GPU via
cudf-polars engine objects (as of cudf-polars 26.06): **RayEngine**, **DaskEngine**, **SPMDEngine** —
each usable as a context manager that tears down its resources (`docs/source/user-guide/gpu-support.md`).

## The verified breaking changes (1.x → 2.0)

Grouped from the upgrade guide; every row below was executed on rc1 by `polars-v2-verify.py` unless
marked *doc-only*. "Silent" = no error, results or schema change — these are the dangerous ones for a
bit-reproducibility discipline (the economicspace-style concern).

### Engines & execution
| Change | Silent? | Verified |
|---|---|---|
| `engine="auto"` → streaming for lazy; row order not guaranteed on unpivot/group_by/joins | **yes** | #1, #3 |
| `Config.set_engine_affinity` / `POLARS_ENGINE_AFFINITY` restore in-memory default | no (explicit) | #2 |
| `LazyFrame.profile()` removed (misleading under concurrency) | error | upgrade guide; API gone on rc1 |
| `pl.collect_all(iterable)` — takes a **list**, not varargs; combined plan gets CSPE (`CACHE`/`SINK_MULTIPLE`) | no | #5 live: shared subplan confirmed in `explain_all([q1,q2])` |
| `collect_batches()` / `collect_async()` present on LazyFrame (batched + async collection) | — | #6 |

### CSV reading (read_csv is now literally scan_csv().collect())
| Change | Silent? | Verified |
|---|---|---|
| Accepts a **list of sources**; gains `infer_schema_files`, `extra_columns`, `missing_columns` etc. | no | #7 |
| Loses `n_threads`, `batch_size`, `sample_size`, `rechunk` (call `.rechunk()` after) | error on kwarg | upgrade guide |
| `schema_overrides=[...]` must cover **every** column now → partial list raises `SchemaError` | error | #8 live: exact exception type confirmed (`polars.exceptions.SchemaError`) |
| `columns=[2,1,3]` returns requested order (was sorted) — check #9 got `['c','b','d']` | **yes** | #9 |
| Headerless auto column names start at `column_0` (was `column_1`) | **yes** | #10 |
| User-provided `schema=` matched **by name against the header**, not positionally; file order respected — check #11: positional matching used to silently swap values between columns of a reordered schema | **yes** | #11, #12 (`extra_columns="ignore"` works) |
| Multi-file scans infer schema from first **10 files only** (was all); type drift in file #11 now raises; `infer_schema_files=11` fixes it — check #13 reproduced the exact failure and fix | error at parse | #13 |

### Semantics that change results silently
| Change | Verified |
|---|---|
| Int64 + UInt64 supertype is now **exact `Int128`** (was lossy Float64) — dtype AND values change, no error | #16: schema check returned `Int128` |
| `is_in()` coercion strict: Int vs Float raises; explicit `.cast()` required. Bonus finding live: same-dtype `Series.is_in(Series)` now also warns "ambiguous, use implode" (issue pola-rs/polars#22149) — the 1.x idiom is deprecating | #17 + warning observed in harness output |
| `selector & pl.col(...)` no longer means column-set intersection; with compatible dtypes it silently becomes an **element-wise bitwise op** (check #18: shape went from (2,1) to (2,3)). Use `selectors.by_name("mask")` for set ops | #18 |
| `pl.datetime(...)`/`pl.repeat(...)` output column named after the leftmost argument (was literal "datetime"/"repeat") — can silently overwrite an existing column in `with_columns`; alias explicitly if you rely on the name | #19: got `['year']` |
| File-like scans no longer auto-rewind: `write_parquet(buf); read_parquet(buf)` now needs explicit `buf.seek(0)` (check #20 reproduced the "must contain a header and footer" ComputeError) | #20 |
| Zero-width frames preserve height; `pl.DataFrame()` is fixed-height 0 so `with_columns` of a longer Series raises ShapeError — build with `pl.DataFrame(height=N)` instead | #21 |
| `concat(how="horizontal")` no longer null-pads on unequal heights (raises); new `how="horizontal_extend"` = old behavior; `strict=False` now rejected for horizontal | #14: both paths executed |
| `explode()` default `empty_as_null=False`: an empty list → **zero rows** (was one null row) — row counts change wherever lists can be empty; `keep_nulls` unaffected | #15: 3 vs 4 rows reproduced |

### Removed casts / ops (all now hard errors, verified raising on rc1)
| Old behavior that died | Replacement (verified working) | Check |
|---|---|---|
| `cast(String → Date/Datetime/Time)` | `.str.to_date()` / `.to_datetime()` / `.to_time()` — #25 confirmed the error message names it | 25 |
| int ↔ categorical/enum casts (both directions) | `.cat.to(dtype)` / `.cat.physical()` | 26 |
| flat args where a list is expected (`list.gather(0)`, `str.contains_any("a")`) — the implicit implode shim is gone; note per-row indexing was never what that did: use `list.get(col)` for per-row, `concat_list` to keep list type | explicit `.implode()` / plain Python lists | 27 (got `[1, 4]` from `list.get`) |
| boolean ops between Boolean and Int (`bool & int` coerced) | cast explicitly first | 28 |
| struct→struct casts silently truncating field mismatches under default strictness | now raises; `strict=False` restores old truncation | 30 |
| `std()`/`var()` on Duration dtype | `.dt.total_microseconds().std()` (doc-only) | upgrade guide |

### API reshapes & removals (typed errors are the new DX — see "general knowledge" below)
- `melt(id_vars=, value_vars=)` → **`unpivot(index=, on=)`**; `with_row_count()` → `with_row_index()`
  with default column name now `"index"` (was `"row_nr"`) — both verified raising the typed removal
  error *and* the replacement working (#31, #32).
- Unknown Arrow extension types load as `pl.Extension(name, storage)` dtype instead of silently falling
  back to the storage type; recover with `.ext.storage()` (check #24: got
  `Extension('google:sqlType:integer', Int64)`, restored `Int64`). Env escape hatch
  `POLARS_UNKNOWN_EXTENSION_TYPE_BEHAVIOR=load_as_storage`.
- **DataFrame Interchange Protocol removed**: `df.__dataframe__()` gone; `polars.interchange` now holds
  only `CompatLevel`; `pl.from_dataframe()` accepts PyCapsule-interface objects only, no `allow_copy`.
  Use `.to_arrow()` / `.to_pandas()`. Verified: raises the typed `AttributeRemovedError` (#22).
- `shift(n=None)` is a hard error now (was deprecation warning + nulls) — #23.
- `list.to_struct(fields=...)`: fields required positional; `upper_bound`/`n_field_strategy` gone with
  errors that literally spell out the replacement list comprehension — #34 executed both sides.
- `Expr.hash(seed)` single-seed (multi-seed removed); hash values are only stable *within* a version,
  never across — don't persist them (#33).
- `pl.Categorical(ordering=...)` gone: categoricals are **always lexical** now; the silent trap is that
  `pl.Categorical("physical")` becomes a category-pool *named* "physical" rather than erroring. #29.
- ~70 more removals in the upgrade guide's table (line 1607) — each raises either
  `polars.exceptions.AttributeRemovedError` or `ArgumentRemovedError` **with the replacement named in
  the message**, which makes a 1.x→2.0 migration greppable: run your code, collect those two exception
  types, follow their hints.

## What I probed and found was NOT new (honest corrections)

- `join(maintain_order=..., build_side=...)` — the upgrade guide's example makes these look like v2
  additions, but **stable 1.44.2 already has both** in `LazyFrame.join`'s signature (probed live on a
  1.44.2 venv). What changed in 2.0 is *semantics* (default engine no longer preserves order), not the
  API surface. Don't date-gate these params to ">=2".
- `pl.dtype_of(col)` — also present in 1.x; it's an **unstable** `DataTypeExpr` feature: a lazily
  instantiated dtype you can reference by column name, e.g. as `map_batches(..., return_dtype=...)`.
  Verified working on rc1 (#36) but marked "may change at any point" in its own docstring — pin it off
  for anything durable.

## Rust architecture map (for the curious / future cross-checks)

Workspace = ~30 crates (`crates/`): `polars-core` (233 files), `polars-plan` (254, logical+physical IR +
optimizer passes), `polars-lazy`, **`polars-mem-engine`** (the classic in-memory executor, 30 files — it
shrank while streaming grew to 177: the center of gravity moved), **`polars-stream`**, **`polars-ooc`**,
`polars-io`/`polars-parquet`, `polars-sql` (only 13 files!), `polars-time`, `polars-ops`. Python side:
Rust extension `py-polars/src/polars/_plr.pyd` + a thin Python layer in `py-polars/src/polars/` with the
namespaces (`dataframe/`, `lazyframe/`, `expr/`, `series/`, `io/`, `sql/`, `catalog/unity/` — lakehouse
Unity Catalog client, new).

**SQL is not an engine.** From `docs/source/user-guide/sql/intro.md`: "There is no separate SQL engine
because Polars translates SQL queries into expressions" — the 13-file `polars-sql` crate is just a
parser/resolver (`resolver.rs`, `sql_expr.rs`, `subquery.rs`, `grouping_sets.rs`) that lowers to the same
IR everything else uses. Consequence: any expression feature works from SQL eventually, and SQL queries
get every optimizer pass for free — but also inherit 2.0's streaming/order semantics (above).

**Optimizer passes** (`docs/source/user-guide/lazy/optimizations.md`, table verified against source):
predicate/projection/slice pushdown run once; **simplify expressions and type coercion iterate to fixed
point**; join ordering runs once using cardinality estimates; cardinality estimation itself is 0..n times.
`POLARS_JOIN_SAMPLE_LIMIT` (default 10,000,000 rows) bounds the sampling behind those estimates.

## Key `POLARS_*` environment knobs (defaults from `crates/polars-config/src/lib.rs`)

| Var | Default | What it does |
|---|---|---|
| `POLARS_ENGINE_AFFINITY` | auto (=streaming for lazy in 2.0) | force `in-memory` to restore pre-2 behavior process-wide |
| `POLARS_MAX_THREADS` | (cores) | thread cap |
| `POLARS_IDEAL_MORSEL_SIZE` | **100,000 rows** | streaming morsel target size — the main parallelism-granularity knob |
| `POLARS_FORCE_ASYNC` | false | force async executor even when sync would do |
| `POLARS_NUMA_AWARE` / `NUMA_MOCK_REGIONS` | false/0 | NUMA-aware allocation (mock regions for testing) |
| `POLARS_DIRECT_IO` | false | bypass page cache (`O_DIRECT`, Linux) |
| `POLARS_FILE_READ_CONCURRENCY` | 32 | parallel file reads; `FILE_POSIX_FADVISE`-style hint var alongside |
| OOC family (see above) | budget fraction 0.8, min spill 64 KB, 64 parallel tasks each way | experimental spilling controls |

## Multiplexing: LazyFrame variables are PLANS, not data

The classic lazy-API trap, documented in `docs/source/user-guide/lazy/multiplexing.md` and reproduced
live (#5): storing a query result in a variable (`lf1 = lf.group_by(...)`) stores the **plan**; every
downstream branch that collects from it re-executes the whole subquery — expensive AND order-unstable
(the docs' own example shows two branches of one group-by returning different row orders). The fix is to
give polars all plans in one pass: `pl.collect_all([q1, q2])` (iterable!) builds a combined plan with a
single `SINK_MULTIPLE`, and the optimizer inserts **CACHE nodes** for shared subplans (common-subplan
elimination) — verified present in `explain_all`. This is also why 2.0's CSPE flag exists as an env var
(`POLARS_ALLOW_NESTED_CSPE`) at all: caching interacts with streaming node lifetimes.

## General code knowledge worth stealing from this repo

1. **Typed removal exceptions.** Polars ships `AttributeRemovedError` (subclass of AttributeError) and
   `ArgumentRemovedError` (subclass of TypeError), raised automatically when you touch a removed API,
   each carrying the replacement in its message ("use `LazyFrame.unpivot`, with `index` instead of
   `id_vars`..."). This turns any deprecation cycle into an *executable migration guide* — users just run
   their code and follow errors. Cheap to add to any library that removes things (verified live: #22, #31).
2. **Morsel-driven concurrent execution** with per-edge ring buffers + explicit in-memory fallback nodes
   is a clean pattern for "concurrent graph engine where some ops aren't ready yet" — the fallback is a
   node type (`in_memory_sink`), not an exception path, so plans stay uniform and debuggable.
3. **Spill design with budgets on both sides** (spill threshold + separate higher prefetch threshold)
   avoids thrash: you don't refill memory until usage drops below 0.9×budget even though you spilled at
   0.8× — hysteresis, same idea as disk-cache writeback thresholds. Score-based candidate selection with
   an explicit explore term (20.0) is a small but real anti-thrash measure against always-picking-the-
   single-best-scored frame.
4. **Versioning policy** (`docs/source/development/versioning.md`): semver; "undocumented = not public";
   bug fixes are explicitly *not* breaking changes (links xkcd 1172); an **"unstable"** API tier that may
   change without a major bump and can be surfaced with `pl.Config.warn_unstable(True)` — the same trick
   used for GPU/DataTypeExpr/OOC surfaces. Useful template for any project that wants fast-moving edges
   next to stable cores.
5. **Repo etiquette note (AI_POLICY.md, root of repo):** polars strictly forbids agents from interacting
   with their GitHub repo (issues/PRs/comments) and requires AI disclosure on human-filed PRs; drive-by
   AI PRs get closed. If this second brain ever produces a contribution there: human files it, discloses
   the tooling, no "good first issue" work via AI.

## What was surveyed but NOT distilled here

- `py-polars/tests/` (streaming/, ooc/, sql/ suites) — read for design facts above; test code itself is
  polars-specific QA harness, not portable knowledge beyond the OOC-maturity finding.
- `docs/source/user-guide/io/*` cloud surfaces (BigQuery, HuggingFace datasets, hive partitioning —
  enabled by default when `scan_parquet` gets a single directory) — noted for completeness; no unique
  pattern beyond "hive parsing is on-by-default for dir scans" which belongs in the big-data doc if ever
  needed.
- `pyo3-polars/` (separate pyo3 binding crate, not the main Python package) and `examples/datasets/`
  (TPC-H feather heads + foods CSVs — just fixtures).
