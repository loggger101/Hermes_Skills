---
name: python-numerics-gotchas
description: "Silent numpy/scipy/pandas/sympy/statsmodels traps."
version: 1.0.0
author: Hermes Agent (promoted from python-data-science references, live-run 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [numpy, scipy, pandas, sympy, statsmodels, dask, numerics, gotchas, migration]
    related_skills: [python-data-science, python-plotting, sql-for-data, duckdb-querying, bit-identity-float-pipelines, python-craft]
---

# Python numerics gotchas

## What This Skill Does

Holds the **measured failure modes** of the numeric Python stack on current versions (numpy 2.5, scipy 1.18, pandas 3.0, sympy 1.14, statsmodels 0.15, dask 2026.8; Python 3.14 on Windows), where a call "works" and returns a wrong or surprising answer. Each library has a reference of probes with the observed output, so you can check a result against a known behaviour instead of trusting memory of an older version.

## When to Use

- Upgrading or writing code against numpy 2, pandas 3 or recent scipy and a result changed without an error
- A fit, integral, regression or symbolic result looks plausible but you cannot say why it is right
- Porting numeric code from Linux to Windows (integer widths, spawn-based multiprocessing)
- Deciding whether dask is worth it for a dataset
- Not for the end-to-end modelling workflow (`python-data-science`), plotting (`python-plotting`), torch/CV libraries (`ml-cv-library-notes`) or SQL-engine work (`duckdb-querying`)

## Which reference

| Symptom or task | Library | Reference |
|---|---|---|
| Integer arrays wrap silently, `np.trapz`/`in1d` gone, `dtype="l"` is 32-bit on Windows, `copy=False` raises | numpy 2.5 | `references/numpy-2-notes.md` |
| `str` dtype and NaN semantics, chained assignment does nothing, read-only arrays, `datetime64[us]`, removed aliases | pandas 3.0 | `references/pandas-3-notes.md` |
| `curve_fit` returns garbage from a bad `p0`, `interp2d` raises, `differential_evolution(workers=)` hangs on Windows, sparse `*` | scipy 1.18 | `references/scipy-notes.md` |
| Float vs Rational, `==` is structural, `solve` return shapes, `lambdify` constants do not broadcast | sympy 1.14 | `references/sympy-notes.md` |
| No-constant R-squared, `add_constant` skipping, unseen-level `predict`, zero-event confidence intervals, ARIMA without a frequency | statsmodels 0.15 | `references/statsmodels-notes.md` |
| Is dask faster than pandas for this size, what `head()` reads, `meta` warnings | dask 2026.8 | `references/dask-notes.md` |

## Procedure

1. Name the library and version in play (`python -c "import numpy, pandas, scipy; print(numpy.__version__, pandas.__version__, scipy.__version__)"`). The references are pinned; a different major version needs a re-probe.
2. Open the matching reference and find the probe closest to your call; compare its observed output with yours.
3. Turn silent behaviour into a failure while you debug: run with `python -W error` (add `-W error::FutureWarning` for pandas), and wrap numpy code in `np.errstate(all="raise")`.
4. Check results rather than exit codes: recompute the residual after a fit, assert shapes and dtypes, and compare an independent route (for symbolic work, `sp.simplify(lhs - rhs) == 0`, not `==`).
5. When a trap is new, add a probe and its observed output to the library's reference with the version and date.

## Highest-value traps (details in the references)

- **numpy**: with NEP 50 a Python int takes the array's dtype, so `np.array([200], np.uint8) + 100` wraps to 44 with no warning (scalars warn, arrays do not); `uint64 + int64` becomes `float64`. On Windows `np.dtype("l")` and `np.long` are 4 bytes while `int` is 64-bit.
- **pandas 3**: the default string dtype is `str` with `nan` as missing, `.str.len()` becomes `float64` when any value is missing, and `df["a"][0] = 1` is a no-op (use `df.loc[...]`). Arrays from `to_numpy()` are read-only unless `copy=True`.
- **scipy**: `curve_fit` from a bad `p0` can return an RMS residual of 3e73 with a finite covariance and no error; `sigma` only rescales unless `absolute_sigma=True`; `differential_evolution(workers=N)` hangs on Windows without an `if __name__ == "__main__":` guard.
- **sympy**: a Python float leaks into an exact expression (`0.1 + 0.2`); `nsimplify` repairs float error silently; always `solve(..., dict=True)`; derive with sympy, then `lambdify(..., "numpy")` rather than retyping.
- **statsmodels**: `sm.OLS` without `add_constant` reports an uncentred R-squared (0.27 vs 0.66 on the same data); formula NaNs are dropped silently (`nobs` 190 of 200); `proportion_confint(0, 20)` normal is (0, 0), use Wilson.
- **dask**: at 4 million rows plain pandas (0.073 s) beat dask (0.091 s); choose dask for data that does not fit in memory, not for speed on in-memory frames, and measure first.

## Pitfalls

- Quoting a behaviour from these notes on a different version: they are dated snapshots (2026-10-05 for most), re-run the probe.
- Treating a clean exit as correctness: most traps here return a value and no error.
- Using seeded-sample or float-summation results as bit-identical across partition counts or hosts; verify with `bit-identity-float-pipelines` when that matters.

## Verification

- [ ] The library version in use matches the version a reference was probed on, or the probe was re-run
- [ ] Results were checked with an independent computation (residual, identity, second library) rather than by absence of errors
- [ ] `python -W error` run on the changed code path shows no new warnings
- [ ] Any new trap found was written back to the library's reference with version and date

## References

- `references/numpy-2-notes.md` - numpy 2.5.2 on Windows/py3.14: NEP 50 promotion and silent integer wraps, 32-bit `long` on Windows, removed names, `copy=False`, float32 `cumsum` stalls, json/np.load traps
- `references/pandas-3-notes.md` - pandas 3.0.6: default `str` dtype and NaN semantics, always-on Copy-on-Write and read-only arrays, `datetime64[us]`, removed names and aliases
- `references/scipy-notes.md` - scipy 1.18.1: removed names, `curve_fit` bad-`p0` garbage and `absolute_sigma`, `differential_evolution(workers=)` on Windows, `linprog`/`milp` status handling, sparse array vs matrix
- `references/sympy-notes.md` - sympy 1.14.0: Float vs Rational, structural `==`, `solve(dict=True)`, `CRootOf`, `lambdify` constant broadcasting, assumptions change simplification
- `references/statsmodels-notes.md` - statsmodels 0.15.0 on pandas 3: no-constant R-squared, silent `add_constant` skip, misleading `predict` error, degenerate proportion intervals, ARIMA without a frequency
- `references/dask-notes.md` - dask 2026.8.0 measured on 4M rows: not faster in memory, lazy semantics, `head()` reads one partition, `meta` warning, seeded sampling
