---
description: "dask 2026.8.0 DataFrame: when it helps (not at 4M rows), laziness, head() semantics, meta warnings, determinism; measured on this machine"
source_repo: dask/dask (BSD-3-Clause)
tested_version: dask 2026.8.0 + pandas 3.0.6 + pyarrow, pip --target on Windows py3.14 (300 MB); one 4,000,000-row synthetic frame, default threaded scheduler, no `distributed` cluster
verified_date: "2026-10-05"
---

# dask DataFrames: when and how

`dask` 2026.8.0 (2026-08-24, BSD-3-Clause, Python `>=3.10`, classifiers to 3.14; `distributed` 2026.8.0 for clusters) splits a dataset into partitions and builds a lazy task graph that runs in parallel (threads by default) and can spill past RAM.
`dask.dataframe` is the pandas-like API; the query-planning optimiser is the default in this version (`dataframe.query-planning` was unset, meaning default).

## Measured (4,000,000 rows: int key with 1,000 values, float, 5-letter category)

| Operation | pandas | dask (8 partitions, threaded) |
|---|---|---|
| `groupby("k").v.mean()` | **0.073 s** | 0.091 s; results equal (`allclose`) |
| parquet read + `v.sum()` | n/a | 0.092 s |
| `len(ddf)` | n/a | 0.003 s (4,000,000) |
| `sort_values("v").head(3)` | n/a | 0.196 s |

**At this size plain pandas was faster than dask** (graph building and scheduling overhead). Dask earns its keep when the data does not fit in memory, when many files need parallel reading, or when you have many cores/a cluster and operations that parallelise;
for an in-memory frame of a few million rows start with pandas (or polars, see `polars-pymc-api-reference.md`) and measure before switching.

## Behaviours worth knowing

- `dd.from_pandas(pdf, npartitions=8)` returns a lazy `DataFrame`; nothing computes until `.compute()` (or `len`, `.values`, `.head()`...). `ddf.known_divisions` was `True` here (sorted index known), which makes `.loc` and joins cheaper; unknown divisions (e.g. after many operations) make index-based work expensive.
- **`ddf.head(n)` reads only the first partition** (`(3, 3)` shape came back instantly): do not use `head()` to judge the whole dataset; it is not a random sample.
- **`map`/`apply` without `meta` raises a `UserWarning`** while dask guesses the output dtype by running the function on fake data (guessed `float64` here); pass `meta=` explicitly to avoid wrong inference and double evaluation.
- `sample(frac=0.01, random_state=1)` repeated twice gave the same count (40,000), so seeded sampling is reproducible; verify on your own pipeline when bit-identity matters (`bit-identity-float-pipelines`), because partition counts and thread scheduling can change floating-point reduction order.
- `len(ddf)` triggers a real computation (it was fast here because the data was in memory); `.compute()` on a large result materialises it in the client process: aggregate first.
- Default scheduler is threads (right for NumPy/pandas code that releases the GIL; use processes or `distributed` for pure-Python work).

## Rules

1. Choose partition size by memory, about 100 MB per partition as a starting point, not by core count alone; too many tiny partitions make overhead dominate.
2. Persist (`ddf.persist()`) a reused intermediate result; avoid recomputing the same graph several times.
3. Prefer parquet with column pruning and filters (`dd.read_parquet(path, columns=[...], filters=[...])`).
4. Provide `meta`; keep operations column-wise; avoid `apply(axis=1)` over rows.
5. Use the dashboard/`distributed` only for real parallel workloads; for a single machine the threaded scheduler needs no setup.
