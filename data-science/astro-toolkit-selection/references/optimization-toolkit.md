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

## mesa — ⚠️ CORRECTED + LIVE-VERIFIED 2026-09-19 (PyPI 3.5.1 on Python 3.12) [LIVE]
Round 2 read **master** and reported "v4 API, two blockers". Live probes against the actual PyPI
release change that picture:

1. **"Two blockers" overstated**: `pip install mesa` → **3.5.1**, which already ships most of the v4
   surface on Python 3.12 (no PEP-695 parse issue — that's master/v4-alpha only, requires-python ≥3.12).
   Don't git-install for real work; PyPI is fine.
2. **The working idiom** (verified end-to-end):

```python
class Miner(mesa.Agent):
    def __init__(self, model, wealth=0):      # `model` positional arg still REQUIRED in 3.x
        super().__init__(model)
        self.wealth = wealth
    def step(self):
        self.wealth += int(self.random.randint(1, 3))

class Economy(mesa.Model):
    def __init__(self, n=5, **kw):            # pass seed via kw: Model(seed=N) warns (deprecated); use rng=int
        super().__init__(**kw)
        for _ in range(n): self.register_agent(Miner(self))   # v4-style registration on 3.5.1 ✓
    def step(self):
        self.agents.shuffle_do("step")         # ← AgentSet has NO .step(); shuffle().step() raises AttributeError
```

- Seeding: `Model(rng=7)` (int) is the non-deprecated path; **`rng=random.Random(7)` fails** — numpy
  SeedSequence wants int/sequence-of-ints. Same seed ⇒ identical agent draws (`self.random` replay verified).
- AgentSet API on 3.5.1: `select(fn)`, `do("step")`, `shuffle_do(...)`, `agg(attr, "sum"|"mean"|...)`,
  `groupby`, `sort`. Agent identity attr is **`unique_id`** — NOT `agent_id` (v2 name).
- ⚠️ **VERIFIED BUG: `mesa.batch_run()` silently returns `[]` when the DataCollector has only
  agent_reporters.** Root cause in 3.5.1 source: `DataCollector.collect()` appends to `_collection_steps`
  ONLY inside `if self.model_reporter:` — with no model reporters the list stays empty, and batchrunner's
  `data_collection_period=-1` path does `[recorded[-1]] if recorded else []`. **Fix: give the collector at
  least one model reporter** (e.g. `"n_agents": lambda m: len(m.agents)`). With that fix + `rng=[7]`,
  batch_run rows are correct and seeded runs reproducible (`iterations=` is deprecated → use `rng=[...]`).
- New in 3.x PyPI: `mesa.discrete_space` (Grid/HexGrid/VoronoiGrid, CellAgent) — spatial models with no
  external deps.

## z3-solver 5.1.0 (pip) — ⚠️ CORRECTED API NAMES vs round-2 source read [LIVE]
Round 2 read the repo's `src/api/python/z3/z3.py` at a newer revision and quoted names that **do not
exist in `pip install z3-solver` (5.1.0)**: no `RegExConst`, no `SeqVal`. What actually works (verified):

```python
import z3 as zz
# Float SMT: sort via Float64(), variables FP(name, Float64()); conversions take REAL EXPRESSIONS —
# fpRealToFP(RNE(), 0.1, ...) raises "Second argument must be a Z3 expression or real sort"; use RealVal("0.1")
one_tenth = zz.fpRealToFP(zz.RNE(), zz.RealVal("0.1"), zz.Float64())
g = zz.FP("g", zz.Float64()); s = zz.Solver()
s.add(g == (one_tenth + two_tenths), g != three_tenths)   # PROOF: IEEE double 0.1+0.2 != 0.3 -> sat ✓
# FP <-> bits: fpToIEEEBV(h); the BV constant ctor is BitVecVal (NOT BitVectorVal/BVVal):
s.add(h == one_tenth, zz.fpToIEEEBV(h) == zz.BitVecVal(0x3FB999999999999A, 64))   # sat ✓
# Regex: the pip-build API is Re()/InRe()/Union() (doctest pattern from z3.py L12061):
re = zz.Union(zz.Re("a"), zz.Re("b"))
zz.simplify(zz.InRe("c", re))   # False  ✓
# Optimize nonlinear: maximize(x*x) s.t. 0<x<5 -> sat, model eval x=319/64 (exact rational) ✓
# Module-level solve()/simplify()/prove() all present ✓; prove() prints "proved" and returns None
```

- `unknown` remains a real result class on hard nonlinear arithmetic — set timeouts (`s.set("timeout", ms)`);
  the general advice stands even though small test constraints solved instantly here.

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
