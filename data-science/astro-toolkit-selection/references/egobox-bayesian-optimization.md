---
description: "EGObox 0.38.0 (Rust EGO / Bayesian optimization with Python bindings Egor and Gpx), run live: README example reproduced, seed behaviour, evaluation count, Branin, surrogate behaviour"
source_repo: relf/EGObox (Apache-2.0)
tested_version: egobox 0.38.0 pip --target on Windows py3.14, run live; Rust crates egobox-ego 0.40.2 / egobox-gp 0.36.4 (crates.io, 2026-09-22) not compiled
verified_date: "2026-10-05"
---

# EGObox: Efficient Global Optimization (Bayesian optimization) in Rust, with a Python module

For **expensive, gradient-free** objectives (a mission simulation, a CFD run): fit a Gaussian-process surrogate (`Gpx`, a mixture of GPs), pick the next point by an acquisition criterion (expected improvement), evaluate, repeat.
`pip install egobox` (0.38.0, 2026-10-01, Python `>=3.10`) installed on Python 3.14 here with no compiler; Apache-2.0. Rust sub-crates: `egobox-doe`, `egobox-gp`, `egobox-moe`, `egobox-ego`.

```python
import numpy as np, egobox as egx
def f_obj(x: np.ndarray) -> np.ndarray:           # x has shape (n, dim); return shape (n, 1)
    return (x - 3.5) * np.sin((x - 3.5) / np.pi)
res = egx.Egor([[0.0, 25.0]]).minimize(f_obj, max_iters=20, seed=42).result
res.x_opt, res.y_opt, res.x_doe, res.y_doe         # result attributes
```

## Verified results

| Check | Result |
|---|---|
| README example (minimise on [0, 25], 20 iterations, seed 42) | `y_opt = -15.12510324`, `x_opt = 18.93522131`; a 250,001-point grid gives the truth `-15.125103` at `x = 18.9352`, so it found the global minimum in 0.0 s |
| Same call repeated | bit-identical `x_opt` and `y_opt` |
| Different seed (7) | `x_opt = 18.93523738`, `y_opt = -15.12510324`: same optimum to about 1e-5 in x |
| Cross-host note | the README quotes `x_opt = 18.93525454` for the same seed; this machine gave `18.93522131`. Optimum value agrees to 1e-8 but the argmin differs in the 5th decimal, so **do not hash `x_opt` across machines** (BLAS/threading differences); compare with a tolerance |
| Objective call pattern | 21 calls for `max_iters=20`: one batch of 5 points for the initial design of experiments (input shape `(5, 1)`), then one point per iteration (shape `(1, 1)`). The objective **receives 2-D arrays** and must return `(n, 1)` |
| Branin (2-D, true minimum 0.397887), bounds `[-5,10] x [0,15]`, 30 iterations, seed 1 | `y_opt = 0.39788747` at `x = (3.14174, 2.27483)` in 0.1 s |
| `Gpx.builder().fit(xt, yt)` on 5 points | predictions at the training points reproduce them exactly (`0, 1, 1.5, 0.9, 1`); `predict_var` returns shape `(n,)`; the variance at `x = 10` (outside the training range 0 to 4) was 0.415, i.e. uncertainty grows when extrapolating |
| `gpx.predict` on a 2-column input to a 1-D model | `ValueError: input x should be of shape (n, 1), got [1, 2]` |

Result object attributes: `x_doe`, `y_doe` (the evaluated design), `x_opt`, `y_opt`.

## Practical rules

- Use it only when each evaluation is costly; for cheap closed-form models (e.g. the economicspace per-row calculators) plain vectorised search or `scipy.optimize` is better (see `optimization-toolkit.md`, `python-data-science/references/autograd-notes.md` for gradient-based alternatives).
- Count evaluations (the initial DOE is extra), fix `seed`, and record bounds; the budget is `max_iters` plus the initial design.
- Bounds are a list of `[low, high]` pairs, one per dimension; constraints and mixed-integer variables are supported by the library (see its docs; not exercised here).
- Check the answer against a brute-force grid in low dimensions before trusting it on a high-dimensional objective.
- Rust crates: `egobox-ego = "0.40"` and `egobox-gp = "0.36"` (versions per crates.io) for embedding in Rust code; the cargo features (`blas`, `c-cobyla`, `c-slsqp`) are listed in the README.
