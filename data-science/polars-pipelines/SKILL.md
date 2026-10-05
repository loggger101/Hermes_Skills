---
name: polars-pipelines
description: "polars 2.0, big-data patterns, PyMC on Windows."
version: 1.0.0
author: Hermes Agent (promoted from python-data-science references, live-verified 2026-09/10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [polars, duckdb, parquet, lazy, streaming, big-data, pymc, bayesian, pipelines]
    related_skills: [python-data-science, duckdb-querying, python-numerics-gotchas, sql-for-data, bit-identity-float-pipelines, space-data-pipelines]
---

# polars pipelines and big-data patterns

## What This Skill Does

Holds the verified knowledge for dataframe pipelines that outgrow pandas: polars' lazy-first idioms, the polars 2.0 engine change and its 35-odd breaking behaviours (re-runnable as a 39-check harness), duckdb and parquet patterns cross-checked against pandas on a 200k-row fixture, and what running PyMC on Windows without a compiler actually does.

## When to Use

- Building or upgrading a polars pipeline (especially across the 1.44 to 2.0 boundary)
- Choosing between duckdb, polars lazy, pyarrow and pandas for a dataset of a million rows or more
- A join, group-by or unpivot returns rows in a different order after an upgrade
- Running PyMC or nutpie on Windows, or choosing sampler and cores
- Not for the general modelling workflow (`python-data-science`), SQL-only ad-hoc work (`duckdb-querying`), or pandas/numpy gotchas (`python-numerics-gotchas`)

## Which reference

| Question | Reference | Key fact |
|---|---|---|
| Polars idioms, `scan_*` entry points, join `validate=` | `references/polars-pymc-api-reference.md` | lazy-first; `group_by` not `groupby`; `validate="1:1"` catches m:n fan-out at plan time |
| Upgrading to polars 2.0 | `references/polars-v2-engine-and-breaking-changes.md` | `engine="auto"` now resolves to streaming; row order is not guaranteed unless requested; escape with `collect(engine="in-memory")`, `pl.Config.set_engine_affinity("in-memory")` or `POLARS_ENGINE_AFFINITY`; `LazyFrame.profile()` removed |
| Re-checking those claims | `references/polars-v2-verify.py` | 39 checks, exits with the failure count (77 means skipped on stable) |
| Which engine for which job | `references/big-data-patterns.md` | duckdb for ad-hoc SQL over files and windows; polars lazy for repeatable ETL; column-pruned parquet reads; stay in pandas under about 1M rows |
| Re-running the pattern checks | `references/big-data-patterns-verify.py` | writes its own CSV fixtures and cross-checks against pandas |
| PyMC `sample()`, nutpie, Windows behaviour | `references/polars-pymc-api-reference.md` (PyMC section) | no C++ compiler falls back to the slower path; `cores=2` needs an `if __name__ == "__main__":` guard and was slower for a tiny model; nutpie is a separate install |

## Procedure

1. Check versions first (`pl.__version__`; stable was 1.44.x and 2.0 was at rc2 when verified).
2. Write pipelines lazy: `scan_parquet`/`scan_csv`, expressions, `collect()` at the end; keep `to_pandas()` at the boundary.
3. Put cardinality guards on every join (`validate=`), and give joins and group-bys an explicit `maintain_order` or a `sort()` where downstream code depends on order.
4. Before moving to 2.0, run `references/polars-v2-verify.py` in a venv with the rc and read the breaking-changes list; pin the version meanwhile.
5. Pick the engine by job with the decision table in `big-data-patterns.md`; measure on your data before switching from pandas.
6. For PyMC: guard the entry point, start with `cores=1`, record `pytensor.config.cxx`, and compare a posterior against a closed-form fit before trusting it.

## Pitfalls

- Treating streaming as a drop-in: join output order changed even where nothing looks order-dependent.
- Relying on the old `.groupby()` alias or removed casts; in 2.0 many are typed hard errors.
- File-like parquet round trips in memory need an explicit `.seek(0)` between write and read in the rc.
- Parallel PyMC chains on Windows re-import the script per worker and pay the import time each (about 4.5 s).
- Line numbers in the source-anchored tables drift between releases; the facts are what matter.

## Verification

- [ ] Polars version in use matches the reference, or the harness was re-run on it
- [ ] Every join has `validate=` and row order is explicit where it matters
- [ ] Results were cross-checked against pandas or duckdb on a sample
- [ ] Any PyMC fit was compared to a closed-form baseline

## References

- `references/polars-pymc-api-reference.md` - polars lazy-first idioms and entry points with the 2.0 corrections, join `validate=`; PyMC `sample()` and nutpie, plus the Windows no-compiler run
- `references/polars-v2-engine-and-breaking-changes.md` - polars 2.0 engine architecture (streaming default, spilling, GPU beta) and every breaking change live-verified
- `references/polars-v2-verify.py` - the 39-check harness for the 2.0 claims
- `references/big-data-patterns.md` - duckdb, polars lazy joins, parquet row-group control and incremental dedup, executed on a 200k-row fixture and cross-checked against pandas
- `references/big-data-patterns-verify.py` - the harness that re-runs those patterns end to end
