---
description: "polars + pymc API references — verified line-numbered facts from cloned sources"
source_repos: pola-rs/polars, pymc-devs/pymc (clones at %LOCALAPPDATA%\Temp\starred-dive\)
tested_version: clones @ 2026-09-05; polars lazy-first + join validate=; pymc sample() w/ nutpie auto-select
verified_date: "2026-09-05"
---

# Data Stack — API References (polars, PyMC)

Distilled from the 2026-09-05 deep-dive salvage report (`%LOCALAPPDATA%\hermes\output\starred-dive\data-engineering.md`),
which verified every fact against cloned source with file:line anchors. Re-check line numbers before quoting them — they drift between releases; the *facts* are what matter.

> **⚠️ 2026-09-14 update (round-22):** polars is at **2.0.0rc1** on PyPI (stable = 1.44.x). The v2
> release changes the default engine to streaming and breaks ~35 behaviors — read
> `polars-v2-engine-and-breaking-changes.md` before upgrading anything, and note that several facts in
> this file below were corrected by that pass (marked ⚠️-corrected).

## polars (Rust core, Python bindings)

**Design rule: lazy-first.** The lazy API is where query optimization and streaming
(larger-than-RAM) live (`docs/source/user-guide/lazy/using.md` in-repo). Eager works but you give up optimizer passes.

### Verified entry points & signatures (clone @ 2026-09-05)
| What | Where | Notes |
|---|---|---|
| `read_csv` / `scan_csv` | `py-polars/src/polars/io/csv/functions.py:74` / `:558` | scan_* = lazy entry; prefer for any pipeline > RAM or multi-step transform chain |
| `to_pandas` interop | `dataframe/frame.py:2479` | the pandas escape hatch — keep it at the boundary, not mid-pipeline |
| **modern group_by** | `dataframe/frame.py:7091`: `group_by(*by, maintain_order=False, **named_by)` | positional + named kwargs; old `.groupby()` alias still present (`:7409`) — use `group_by` in new code |
| **LazyFrame.join** | `lazyframe/frame.py:5822`: params incl. `how`, `left_on/right_on`, `suffix="_right"`, **`validate="m:m"`**, `nulls_equal`, `coalesce`; v2 adds semantics around `maintain_order`/`build_side` (see ⚠️ below) | `validate=` is the standout vs pandas — join cardinality validation catches fan-out bugs at query time, not in a 3 AM data review. **⚠️-corrected (round-22):** `maintain_order: Literal["none","left","right","left_right","right_left"]` and `build_side: Literal["auto","prefer_left","prefer_right","force_left","force_right"]` already exist in stable 1.44 — they are NOT v2-only APIs; what changed in 2.0 is that the default (streaming) engine no longer preserves left row order, making `maintain_order="left"` load-bearing |
| `collect()` | signature: `engine: EngineType = "auto", background, optimizations` | pluggable query engines + async/background collection (see `tests/unit/lazyframe/test_async.py`, `test_engine_selection.py`). **⚠️-corrected (round-22):** in 2.0 `"auto"` resolves to the STREAMING engine for lazy queries — row order is no longer guaranteed on unpivot/group_by/joins; escapes are per-query `engine="in-memory"`, process-wide `pl.Config.set_engine_affinity("in-memory")` / env `POLARS_ENGINE_AFFINITY`. Also new in 2.0: `collect_batches()` (streaming batches) and `pl.collect_all([lf1, lf2])` which merges plans with common-subplan elimination |

### Module layout worth knowing
`catalog/unity/` (lakehouse Unity Catalog client), `sql/` (**not an engine** — a 13-file Rust parser/resolver that translates SQL into expressions for the normal IR; every expression feature works from SQL and gets all optimizer passes, but also inherits v2 streaming/order semantics), `interchange/` (**⚠️-corrected round-22:** in 2.0 this now holds only `CompatLevel` — the DataFrame Interchange Protocol itself was removed along with `df.__dataframe__()`; use `.to_arrow()` / `.to_pandas()` for interop), `ml/torch.py` (unstable `PolarsDataset(TensorDataset)` bridge to torch), `datatype_expr/` (unstable `pl.dtype_of(col)` — lazily-referenced dtypes, e.g. as `map_batches(..., return_dtype=...)`).

### The idiom to internalize
```python
lf = pl.scan_parquet("...")            # lazy entry
out = (lf.filter(...)
        .join(other, on="id", how="left", validate="1:1")   # cardinality-checked join
        .group_by("key", maintain_order=True)               # order-stable when it matters
        .agg(pl.col("x").mean())
        .collect(engine="auto"))                             # or background=True for async
```

## PyMC (Bayesian probabilistic programming, Apache-2.0)

### Verified facts (clone @ 2026-09-05)
| What | Where | Notes |
|---|---|---|
| **`sample()`** | `pymc/sampling/mcmc.py:620`: `draws=1000, tune=None, chains/cores, random_seed, step=None, var_names, nuts_sampler: Literal["pymc","nutpie","numpyro",...]` | the one function to know; everything else is model-building around it |
| **nutpie** (Rust NUTS) | auto-selected when installed (`docs/source/installation`) | recommended companion install — big speedup over pure-Python NUTS; `pip install nutpie` and PyMC picks it up, no code change |
| `sample_posterior_predictive` | `pymc/sampling/forward.py:607` | posterior predictive checks belong in every fit report |
| convergence stats / model class | `pymc/stats/convergence.py` / `model/model.py:1680` | R-hat + ESS from the stats module; modern usage is the `pm.Model` context manager |

### Package layout
`distributions/`, `step_methods/`, `smc/`, `variational/` (ADVI), `gp/` (Gaussian processes, own guide notebook). In-repo learning path: `docs/source/guides/*.ipynb` — pymc_overview, model_comparison, posterior_predictive, GLM_linear, Gaussian_Processes.

### Use-case mapping for this owner's work
- **Uncertainty on pipeline outputs** (e.g., dv estimates with correlated errors) → hierarchical models + `sample()`; nutpie keeps it tractable.
- **Model comparison across candidate dynamics** → `model_comparison` guide workflow, not ad-hoc BIC math.

## Discovery indexes (no code — curated lists only)
- **oxnr/awesome-bigdata**: 867-line README spanning streaming (Kafka/Flink/Samza lineage), ML frameworks, storage engines. Use as a discovery index; most entries are links with one-liners.
- **DataExpert-io/data-engineer-handbook**: bootcamp structure — `beginner-bootcamp/` (Docker + Python 3.11+ prereqs, free end-to-end project list incl. Uber BigQuery pipeline), `intermediate-bootcamp/`, plus books/interviews/newsletters/projects files. Value = curated learning path, not code.
