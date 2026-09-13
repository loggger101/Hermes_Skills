# Pyomo Formulations & Algorithms — measured from source + live execution

Everything below was verified against pyomo 6.10.2.dev0 (built from a fresh clone of Pyomo/pyomo,
main branch, 2026-09-12) with highspy 1.15.1 on Windows / Python 3.12. Counts are exact for the
stated test models; formulas generalize per the cited papers.

## Piecewise-linear → MIP reformulations (`pyomo/contrib/piecewise/transform/`)

All implement Vielma, Ahmed & Nemhauser (Operations Research 58(2), 305–315, 2010) — "Mixed-integer
models for nonseparable piecewise-linear optimization: unifying framework and extensions". The
modeling object is `PiecewiseLinearFunction` (`pyomo/contrib/piecewise/`):

```python
from pyomo.contrib.piecewise import PiecewiseLinearFunction, Triangulation
m.pw = PiecewiseLinearFunction(points=[0, 1, 3, 6, 9], function=lambda t: math.log(t + 1))
# also: points + simplices; tabular_data (value→point mapping); multivariate via scipy triangulations
z = m.pw(m.x)          # callable — returns the PWL value expression at x
```

Four construction modes (from the class docstring): (1) points + nonlinear function → triangulation
built automatically (Delaunay default; `Triangulation.OrderedJ1` required for incremental);
(2) simplices + function; (3) simplices + linear expressions per simplex; (4) tabular data.

**Measured component counts** — model: 1 continuous var, PWL over 5 breakpoints (4 segments),
transform applied via `TransformationFactory(name).apply_to(m)` (verified live):

| transform name | binaries | total vars | active constraints | structure observed in the transformed block |
|---|---|---|---|---|
| `contrib.piecewise.incremental` | **3** (= segments) | 9 | 9 | `delta[1..4]` (one per segment), `y_binaries[1..3]`, `substitute_var`; constraints: `sum(delta)=1`, `delta_i <= y_i`, `delta_{i+1} >= y_i` chains, x-reconstruction, value substitution |
| `contrib.piecewise.convex_combination` | **4** (= breakpoints) | 11 | 9 | implemented as GDP inner representation → big-M reformulation: `lambdas[1..5]`, one binary per breakpoint (reduced to n−1 effective), `convex_combo` (x = Σ λᵢxᵢ), `linear_func` (z = Σ λᵢyᵢ), XOR pick-a-piece |
| `contrib.piecewise.multiple_choice` | **4** (= breakpoints) | 14 | 23 | implemented as GDP outer representation → hull reformulation with disaggregated vars: per-disjunct copies of x and z, `disaggregationConstraints`, `pick_a_piece_xor` |

Rules of thumb (paper + measurements):
- **Incremental**: fewest binaries (n−1), smallest model — the default pick for univariate PWL.
  Requires ordered triangulation (`Triangulation.OrderedJ1`) in multivariate cases; simplices must be
  chained so T_i intersects T_{i+1} and shared vertices align.
- **Convex combination**: n binaries, tightest LP relaxation for convex/concave functions — use when
  the solver struggles with incremental's weaker bound on non-monotone data.
- **Multiple choice / hull (outer)**: disaggregated variables give the strongest formulation but the
  most constraints; Pyomo builds it by routing through `gdp.hull`/`gdp.bigm` transformations — you can
  inspect the generated GDP blocks (`_pyomo_gdp_hull_reformulation`, `_pyomo_gdp_mbigm_reformulation`)
  to audit exactly what was added.
- **Nested inner representation** (`contrib.piecewise.nested_inner_repn`): linearly many binaries in
  the explicit model, but only logarithmically many *effective* ones (up to variable substitution) — a
  binary tree of "which polytope" GDPs with local convex-combination multipliers. Use for very large n.

Pitfall: `apply_to` on these transforms rejects unknown kwargs (e.g. `keep_originals=False`) because
the transform config is a strict ConfigDict — pass nothing or only declared options.

## FBBT — feasibility-based bounds tightening (`pyomo/contrib/fbbt/`)

Two-pass interval propagation over the expression tree:
1. **Leaf→root**: propagate variable bounds up through each operator (interval arithmetic per node).
2. **Root→leaf**: use the constraint's own bound on its root expression to tighten children back down,
   iterating until fixed point or infeasibility detected (`FBBTException`).

Worked example from the module docstring, verified live: `x*y + z == 1` with x∈[−1,1], y∈[−2,2] →
pass 1 gives x·y ∈ [−2,2]; pass 2 uses root = exactly 1 ⇒ **z tightened to [−1, 3]** (live result:
`(lb=-1.0, ub=3.0)`). Import path trap: `from pyomo.contrib.fbbt.fbbt import fbbt` — the package
`pyomo.contrib.fbbt` has an empty `__init__.py`.

## GDPopt global solvers (`pyomo/contrib/gdpopt/`)

Solvers for Generalized Disjunctive Programming (logical/disjunctions over NLP). From module docstrings:

| solver | file | exactness note from source |
|---|---|---|
| **LOA** — logic-based outer approximation | `loa.py` | "For nonconvex problems, LOA may not report rigorous dual bounds" |
| **GLOA** — global logic-based OA (with spatial b&b) | `gloa.py` | the global variant of LOA |
| **LD-SDA** — local-discrete search direction algorithm | `ldsda.py` | heuristic; norm choice for directions: L2 = 2n standard-basis dirs, Linf = 3ⁿ−1 sign combos |
| **RIC** — relaxation with integer cuts | `ric.py` | "not exact unless the NLP subproblems are solved globally" (nonconvex) |
| **LBB** — logic-based branch and bound | `branch_and_bound.py` | rigorous for convex disjunctive structure |

Registration: all in one factory; `GDPopt` is a dispatcher. The decomposition machinery lives in
`create_oa_subproblems.py`, `cut_generation.py`, `discrete_problem_initialize.py`,
`solve_discrete_problem.py` (the master problem), `nlp_initialization.py`.

## KKT transformation (`pyomo/core/plugins/transform/kkt.py`)

`TransformationFactory('core.kkt').apply_to(model)` — verified live output anatomy on
min x²−4x s.t. x≥1, x≥0: adds **`kkt.alpha[1]`, `kkt.alpha[2]`** (nonnegative multipliers: one per
constraint + one for the objective normalization) and a **stationarity constraint**
(`-alpha[2] - alpha[1] - 4 + 2*x == 0`). Multiplier retrieval helper:
`tf.get_multiplier_from_object(model, obj)` returns `(lower_mult, upper_mult)` pairs — this is how you
read shadow prices / sensitivity out of a solved model.

## MPEC complementarity (`pyomo/mpec/complementarity.py`)

`Complementarity(expr=complements(A >= 0, B))` encodes `min(A,B)=0`. Canonicalization rules from source:
- equality side → dropped (becomes the constraint itself); exactly **two finite bounds total** required;
- both sides unconstrained expressions is an error.
- `to_standard_form()` rewrites to `l1 ≤ v1 ≤ u2 OR l2 ≤ v2 ≤ u3` style with auxiliary vars + equality —
  deliberately adds more aux structure than strictly needed because a single condition can't see all the
  model's complementarity conditions at once.

## Stochastic programming layer (`pyomo/contrib/parmest/`, `scenariocreator.py`)

Scenario-based two-stage modeling without mpi-sppy: an "experiment" is a labeled Pyomo model with
suffixes `m.experiment_outputs` (what to record) and `m.unknown_parameters` (params to estimate);
`get_labeled_model()` returns it. Scenario sets are grouped by name; the experiment list drives batched
solves for parameter estimation / uncertainty quantification. For full two-stage SP with parallel
subproblems, Pyomo's documented path is **mpi-sppy** (separate repo) — Pyomo provides the modeling
objects, mpi-sppy the generic solvers.

## Design-of-experiments (`pyomo/contrib/doe/`)

`doe.py` + `grey_box_utilities.py`: Latin-hypercube-style sampling utilities for parameter sweeps on
Pyomo models (the reactor example in `examples/reactor_experiment.py` shows the labeled-model pattern).

## Solver interface architecture (`pyomo/contrib/solver/common/base.py`, 713 lines)

- **V2 contract**: every new-style solver implements exactly `available() / is_persistent() / solve(model, **kwds) -> Results / version()`; must declare a class-level
  `CONFIG` (subclass of `SolverConfig` / `BranchAndBoundConfig` / `Persistent*` variants).
- **Availability enum** (verified values): FullLicense=2, LimitedLicense=1, NotFound=0, BadVersion=−1,
  BadLicense=−2, NeedsCompiledExtension=−3; truthiness = value > 0. Use this instead of stringly-typed
  "is the solver there" checks — it distinguishes *present but wrong version* from *absent*.
- **Persistent solvers** (`Highs`, `GurobiPersistent`, SCIP persistent): keep a live in-memory model;
  Pyomo maintains `_pyomo_var_to_solver_var_map` / `_pyomo_con_to_solver_con_map` and, for mutable
  coefficients (params inside expressions), registers lazy update objects — e.g. HiGHS's
  `_MutableVarBounds`, `_MutableLinearCoefficient`, `_MutableObjective` each re-evaluate their Pyomo
  expression only when `update()` is called before the next solve. This is why persistent solves of a
  parametric family are fast: model rebuild cost is O(changed coefficients), not O(model).
- **Results** (V2, from `common/results.py`): flat ConfigDict — `termination_condition`,
  `solution_status`, `incumbent_objective`, `objective_bound`, `solver_name/version`, nested
  `timing_info` + `extra_info`. No `.problem_info` nesting.

## Testing pattern: MockMIP (`pyomo/solvers/mockmip.py`)

A "mock" solver whose `_execute_command` copies pre-recorded output files (named after the problem)
into place instead of running anything — recorded stdout → solver log, recorded `.sol/.soln` → solution.
This is how Pyomo tests every legacy wrapper's parsing without needing the commercial/external binary.
Portable idea: for any subprocess-based tool in your own projects, a mock executable that replays
fixtures keyed by input filename gives deterministic parse tests with zero external deps.
