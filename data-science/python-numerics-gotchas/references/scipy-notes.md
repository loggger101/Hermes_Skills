# SciPy 1.18.1 notes: what silently goes wrong (run live)

Source: [scipy/scipy](https://github.com/scipy/scipy) (BSD-3). Every line below was run on **scipy 1.18.1, numpy 2.5.2,
Python 3.14.6, Windows** (1.18.1 released 2026-08-21). Probe scripts were scratch files; each claim names the observed
output. Not covered: `ndimage`, `io`, `cluster`, `fft` internals, `scipy.special` accuracy tables.

## Removed or renamed names (hasattr checks on 1.18.1)

| Gone | Use instead | Notes |
|---|---|---|
| `integrate.trapz`, `simps`, `cumtrapz` | `trapezoid`, `simpson`, `cumulative_trapezoid` | `trapezoid([0,1,4], dx=1)` = 3.0, `simpson` = 2.6667 |
| `stats.binom_test`, `itemfreq`, `chisqprob` | `stats.binomtest`, `np.unique(return_counts=True)` | |
| `signal.cmplx_sort` | none | |
| `interpolate.interp2d` | `RegularGridInterpolator`, `griddata`, `make_interp_spline` | the name still exists but **raises `NotImplementedError: interp2d has been removed in SciPy 1.14.0`**, so `hasattr` says True |
| sparse `.A`, `.H` | `.toarray()`, `.getH()` | `csr_matrix(...).A` -> `AttributeError` |

Still present: `stats.mode`, `stats.bootstrap`, `monte_carlo_test`, `permutation_test`, `false_discovery_control`,
`optimize.milp`, `direct`, `interpolate.AAA`, `make_splrep`, `make_smoothing_spline`, `sparse.diags_array/eye_array/random_array`.
Submodules load lazily: `import scipy; scipy.cluster.vq` works without importing it first.

## optimize

- **`curve_fit` from a bad `p0` can return garbage with no warning.** `f = a*exp(-b*x)` on exact data, `p0=[1e3, -50]`
  returned `[-2.3e-13, -50.0]`, RMS residual **3e73**, a finite covariance matrix and no exception. Check the residual
  yourself, pass `bounds=`, and start from a physically sensible `p0`. With `bounds=([0,0],[10,10])` it recovered
  `[2.5, 1.3]`. `full_output=True` returns `(popt, pcov, infodict, mesg, ier)` (`ier` 2, "relative error between two consecutive
  iterates ...", on a good fit); the garbage fit above raised nothing, so `ier` alone is not a quality check.
- **`sigma` rescales, it does not weight absolutely, unless `absolute_sigma=True`.** With `sigma=100` everywhere the
  parameter errors were the same as with no sigma (`[0.0298, 0.0242]`); with `absolute_sigma=True` they became
  `[72.09, 58.64]`. Use `absolute_sigma=True` when `sigma` is a measured uncertainty.
- An unidentifiable parameter gives `pcov` full of `inf` plus an `OptimizeWarning`. `maxfev=3` raises
  `RuntimeError: Optimal parameters not found`; fewer points than parameters raises `TypeError: Improper input: func input
  vector length N=2 must not exceed func output vector length M=1`.
- `minimize` with no `method` picks one from the arguments (documented: BFGS, then L-BFGS-B with bounds, SLSQP with
  constraints). Observed messages: plain -> "Optimization terminated successfully" (2 iterations, 9 evaluations), bounds ->
  `CONVERGENCE: NORM OF PROJECTED GRADIENT <= PGTOL` (a success despite the wording), constraint -> "Optimization terminated
  successfully". Constraint form is `fun(x) >= 0` for `"ineq"`: `1.5 - x0 - x1` gave `[0.25, 1.25]`.
- `linprog` (HiGHS): `status` 0 optimal, 2 infeasible (`HiGHS Status 8`), 3 unbounded (`HiGHS Status 10`). Always branch on
  `res.status`, not on `res.x` being present.
  `milp(c, constraints=LinearConstraint(A, ub=...), integrality=[1,1], bounds=Bounds(0,10))` returned `[3, 1]`, fun -5.
- **`differential_evolution(workers=N)` on Windows (spawn):**
  - without an `if __name__ == "__main__":` guard the script **hung** (60 s timeout, process tree killed);
  - a `lambda` objective fails to pickle (`when serializing tuple item 0`): use a module-level `def`;
  - `workers>1` forces `updating="deferred"`, with `UserWarning: the 'workers' keyword has overridden updating='immediate'`;
  - guarded + top-level function worked (`maxiter=30` stopped early: `success False`).
  Serial, `tol=1e-8`, 3 dims: success after 5809 evaluations.

## integrate

- `solve_ivp` on a stiff ODE (`y' = -1000y + 3000 - 2000e^-t`, `rtol=1e-6`): RK45 **19,586** function evaluations (3,112
  steps), Radau 455, BDF 373, LSODA 259. Pick `LSODA`/`Radau`/`BDF` when RK45's step count explodes.
- Events: set `ev.terminal = True` and `ev.direction = 1`; the run stopped at `t = 2.5` with `status 1`,
  `t_events = [array([2.5])]`. `y0` must be 1-D (`solve_ivp(f, [0,1], 1.0)` -> `ValueError: y0 must be 1-dimensional`).
- `quad` on `1/sqrt|x|` over [-1, 1] returned `inf` with a divide-by-zero warning because the integrator evaluates `x=0`;
  `points=[0]` gave `4.0` with error 5.7e-14.

## sparse

- Prefer the `*_array` classes (`csr_array`); `csr_matrix` keeps the old matrix semantics. Measured differences:
  `A * A` is **elementwise** for arrays (`[[1,4],[9,16]]`) and matrix product for matrices (`[[7,10],[15,22]]`); use `@`
  for the product with arrays. `a.sum(axis=0)` is a 1-D `ndarray` shape `(2,)` for arrays and a `matrix` shape `(1,2)`
  for matrices; `a[0]` has shape `(2,)` vs `(1,2)`; `.todense()` returns `ndarray` vs `matrix`; `csr_array` accepts 1-D
  input (shape `(3,)`).
- **Constructors still return the legacy class:** `sps.diags([1,2], 0)` -> `dia_matrix`, `sps.eye(2)` -> `dia_matrix`;
  use `diags_array(..., offsets=0)` -> `dia_array`, `eye_array`, `random_array(shape, density=, rng=)` -> `coo_array`.
  Also `sps.diags` of an int list emits a `FutureWarning` about the output dtype being cast to float64.
- `hstack([array, array])` -> `csr_array`; mixing an array and a matrix still gave `csr_array`. `spsolve(csr_array(2I), ones)`
  returned `[0.5 0.5 0.5]` with no efficiency warning. Index arrays are `int32`.

## stats

- `ttest_ind` defaults to `equal_var=True` (Student): p 0.0015 vs Welch 0.0020 on unequal-variance samples. Use
  `equal_var=False` unless variances are known equal. The result has `.confidence_interval()`.
- NaN handling: default `nan_policy='propagate'` returned p `nan`; `nan_policy='omit'` returned 0.0968.
- `bootstrap((a,), np.mean, method="BCa", rng=1)` and `permutation_test(..., rng=0)` take `rng=`;
  `random_state=` is still accepted on 1.18.1 (no error), so old code keeps working but prefer `rng`.
- `stats.mode(x, axis=1)` returns arrays (`mode [1 3]`, `count [2 3]`) with `keepdims=False`; ties pick the smallest value;
  with no `axis` on 2-D input it works along axis 0 (`[1 1 2]`).
- `false_discovery_control([0.01, 0.02, 0.03, 0.5])` -> `[0.04 0.04 0.04 0.5]` (Benjamini-Hochberg adjusted p-values).

## signal, special, spatial

- **Order-12 Butterworth with `ba` output blows up:** `butter(12, 0.01)` then `lfilter` produced `max|y| = 5.8e39` on unit
  noise; `output="sos"` + `sosfilt` gave 0.27. Always `output="sos"` above order ~4 and use `sosfiltfilt` for zero phase.
- `special.logsumexp([1000, 1000])` = 1000.693; the naive `log(sum(exp))` overflows to `inf`. `comb(100, 50, exact=True)`
  returns the Python int, the default returns a float (`1.0089e29`).
- `cKDTree.query(points, distance_upper_bound=0.3)` (tested on `cKDTree`): a missing neighbour comes back as index `tree.n` (1000) with distance
  `inf`, which is a valid-looking index into a longer array. Mask with `np.isfinite(d)`.

## Quick selector

| Task | Reach for |
|---|---|
| Fit a model to data with uncertainties | `curve_fit(..., sigma=, absolute_sigma=True, bounds=)` and inspect residuals |
| Global optimum, cheap objective | `differential_evolution` (serial first) or `direct` / `shgo` |
| Linear / integer program | `linprog` / `milp` (HiGHS); big sparse -> OR-Tools or Pyomo (see the optimization skill) |
| Stiff ODE | `solve_ivp(method="LSODA" or "Radau")` |
| Large linear systems | `sparse.csr_array` + `sparse.linalg.spsolve` / `cg` / `gmres` |
| Filtering | `butter(..., output="sos")` + `sosfiltfilt` |
| Resampling-based CIs and tests | `bootstrap`, `permutation_test`, `monte_carlo_test` |
