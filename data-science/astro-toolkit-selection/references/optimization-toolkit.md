---
description: "nyx-py / pygmo2 / mesa v3 / z3 / Pyomo / CamPyRoS — optimization & simulation toolkit"
source_repos: nyx-space/nyx (nyx-py), esa/pygmo2, mesa/mesa, Z3Prover/z3, Pyomo/pyomo, cuspaceflight/CamPyRoS
tested_version: clones @ 2026-09-05; versions from pyproject/stubs/release notes
verified_date: "2026-09-06"
---

# Optimization & Simulation Toolkit (round-2 deep dive)

Decision rule lives in skill `space-mission-computation-paradigms`; this file is the **what-exists** layer.
⚠️ Corrections to round-1 notes are marked — trust these over older memory entries.

## nyx-py — ⚠️ LIVE (round 1 said "disabled" — wrong) [SRC]
`pip install nyx_space`. Python ≥3.11; deps: numpy≥2.4, **polars**, plotly, scipy. AGPLv3 core still applies to the
Rust engine — fine for internal research, a copyleft consideration if you ship it.
- Modules (from `.pyi` stubs): `anise/` (MetaAlmanac, Aberration, Orbit, CelestialObjects, Frames), `mission_design`,
  **`monte_carlo`** (`MvnSpacecraft`, `StateDispersion`, `OrbitalElement`, `StateParameter` — launch dispersion is first-class),
  `orbit_determination`, `time`.
- Canonical workflow (examples/01_readme.py): ANISE `MetaAlmanac(dhall).process().load(bpc)` → build `AccelModels`
  (`point_masses=...`, `gravity_field=GravityFieldConfig(degree=50, order=50, filepath="EGM2008...gz")`,
  `solid_tides=SolidTides.earth_moon_system(...)`) → vehicle-dependent forces (`SolarPressure([frames], almanac, correction=Aberration("LT"))`,
  `Drag(Nrlmsise00Flags...)`) → `Propagator`.
- Orbit class has element-delta helpers: `add_sma_km/add_ecc/add_inc_deg/...` + diff methods — handy for perturbation studies.

## pygmo2 (JOSS-reviewed) [SRC]
- UDA contract is tiny: a pure-Python problem implements **`fitness(x)`** and **`get_bounds()`**; islands implement `run_evolve`.
  The `_patch_*.py` files in the package show exactly how Python objects get wrapped into the C++ core.
- Windows install note (unchanged from round 1): PyPI wheels are Linux-only → conda-forge or build.

## mesa v3.x — ⚠️ TWO BLOCKERS for this machine [SRC]
1. **`requires-python = ">=3.12"`** in pyproject; source uses PEP 695 generics (`class Agent[M: Model]:`) — won't even parse on Python 3.11 (this box). Install a 3.12+ interpreter before any mesa work.
2. **Full API rewrite vs every 2.x tutorial**: no more `Model.__init__(self, **kwargs)` + scheduler pattern.
   - Agent: action-based — `start_action(action)`, `should_interrupt(current, incoming)`, `interrupt_for(new_agent)`,
     `cancel_action()`, `is_busy()`; async `step`/`advance`; per-agent `rng`.
   - Model: event-driven time — `schedule_event(function, *, at=|after=, priority)`, `schedule_recurring(...)`,
     `run_model()`, `run_for(duration)`, `run_until(end_time)`; agent registry with removal hooks.

## z3 v5.2.0 (SMT solver) [SRC]
- Single-file Python API (`src/api/python/z3/z3.py`); 64 top-level classes. Notable sorts: **FPRef** (floating-point SMT),
  SeqRef+ReRef (sequences + regular expressions — monadic regex solver on by default since 5.1, `smt.seq.regex_monadic=true`),
  FiniteDomainRef, DatatypeRef.
- Workflow objects: `Solver`, `Optimize`, `Fixedpoint`, `Simplifier`, `Tactic`; results via `ModelRef`/`CheckSatResult`.
  Top-level convenience: `solve()`, `simplify()`, `prove()`.

## Pyomo — the unmentioned modules [SRC]
Standard pattern unchanged (`ConcreteModel` + `Var/Indexer` + `Constraint` + `Objective` + `SolverFactory`; Model class in
`core/base/PyomoModel.py`). The parts worth knowing exist:
- **`pyomo/dae/`** — differential-algebraic equations (trajectory work beyond OpenSCvx's SCP framing).
- `gdp/` generalized disjunctive programming; `mpec/` mixed-integer complementarity; `network/`; `repn/` (LP/MIP/NLP export);
  solver interfaces incl. pyros/pynumero under docs/explanation/solvers/.

## CamPyRoS — ⚠️ runs WITHOUT ray on Windows [SRC]
Round 1 said "stats module needs ray, Windows has issues". Correction: the package ships **`campyros/ray_alt.py`** — a serial
fallback shim whose `@remote` decorator just warns ("Ray was not available so multithread running will not work. Stats will take
a long time") and runs inline. Monte Carlo works on this box, single-threaded.
- Entry: `stats.StatisticalModel("settings.json").run_model(test_mode=False, debug=True, num_cpus=3)`; ray path uses `ray.init(num_cpus=N)`.
- Differentiators in source: `heating.py` (`TangentOgive`, `AeroHeatingAnalysis`), `aero.AeroData`, 6DOF core with variable mass/inertia.

## Cross-cutting gotchas
- nyx + pygmo both pull polars — one data layer for the whole optimization stack (see `polars-pymc-api-reference.md`, now at `data-science/python-data-science/references/`).
- Version pins matter: z3 5.x release notes change solver defaults; mesa 2→3 is a hard break; nyx requires numpy≥2.4 which some older stacks reject.
