# Library landscape for the economicspace pipeline

Curated from the user's GitHub star list `loggger101/lists/for-econ-space-pipeline`
(17 repos, pulled via GraphQL `user.lists -> items` on 2026-09-03). Maps each repo
to a stage of the **economicspace** asteroid-mining profitability pipeline and records
what is actually useful to wire in vs. what is a dead end.

## The pipeline it maps onto

economicspace = `C:/Users/Owner/OneDrive/Documents/GitHub/economicspace` (owner loggger101).
Four stages, hand off via CSVs on disk:

| stage | module | does |
|---|---|---|
| 1 catalog | `catalog.py` | build asteroid catalog from JPL SBDB + MP3C + SsODNet ssoBFT (parquet) + NEOWISE IR diameters/albedos |
| 2 mineral_value | `mineral_value.py` | price the minerals each body contains (+ densities) |
| 3 transportation | `transportation.py` | launch / propellant / dv-segment / ops costs; carries a literature-cited hardcoded dv segment table (GEO, Mars MOI, NEA->NRHO Oberth capture) |
| 4 calc | `calc.py` | rocket equation + cost cascade -> ranked profitability table. **Already hand-codes its own patched-conic / Hohmann dv** (`asteroid_transfer_dv_km_s(a_au,e,i_deg)`, canonical-unit heliocentric transfer, `synodic_period_yr`) |

Current deps: `requests pandas numpy yfinance tqdm pyarrow` (+ streamlit for the UI).
**None of the 17 starred repos are imported yet.** So this is a "what could plug in where"
survey. The hand-coded dv means an external astrodynamics lib is a **cross-check / enrichment**,
not a replacement -- and economicspace argues every release from bit-identity, so any new dep
must be added to BOTH `requirements.txt` AND `requirements-lock.txt` (pinned) or it can move a
float in the last bit.

## The 17 repos (verified via GitHub GraphQL, 2026-09-03)

| repo | lang | stars | license | open issues | pushed | maps to |
|---|---|---|---|---|---|---|
| mesa/mesa | Python | 3824 | Apache-2.0 | 78 | 2026-09-01 | (econ) agent-based modeling -- not a fit for deterministic ranking |
| Z3Prover/z3 | C++ | 12635 | MIT | 43 | 2026-09-04 | SMT theorem prover (Satisfiability Modulo Theories) -- constraint/feasibility solving, not needed for the ranking |
| Pyomo/pyomo | Python | 2519 | BSD-3-Clause (COIN-OR) | 348 | 2026-09-02 | algebraic modeling layer -> external solvers; calc.py already solves its own feedback loop |
| pola-rs/polars | Rust | 39639 | MIT | 2531 | 2026-09-04 | DataFrame engine -- redundant, pyarrow already in stack |
| pymc-devs/pymc | Python | 9735 | NOASSERTION (Apache-2.0) | 307 | 2026-09-03 | Bayesian inference -- optional uncertainty layer on prices/densities |
| CelestiaProject/Celestia | C++ | 2357 | GPL-2.0 | 134 | 2026-09-03 | 3D viz -- separate tool, copyleft if linked |
| esa/pygmo2 | C++ | 535 | MPL-2.0 | 37 | 2026-04-17 | parallel global+local optimization (island model) |
| OpenSCvx/OpenSCvx | Python | 60 | Apache-2.0 | 40 | 2026-08-27 | successive convexification, JAX backend -- research-grade trajectory opt |
| cuspaceflight/CamPyRoS | Jupyter | 35 | GPL-3.0 | 2 | 2025-07-27 | Cambridge rocket trajectory sim -- stale (Jul 2025), copyleft |
| duncaneddy/brahe | Rust | 96 | MIT | 6 | 2026-09-03 | **astrodynamics lib, Python bindings -- the clean cross-check candidate** |
| typpo/spacekit | JS | 582 | MIT | 12 | 2026-04-10 | JS 3D space viz -- separate tool |
| julie-dujardin/space-map | Python | 2 | AGPL-3.0 | 0 | 2026-09-02 | "Google Maps for the solar system" -- tiny, copyleft |
| nyx-space/nyx | Rust | 485 | AGPL-3.0 | 18 | 2026-09-02 | high-fidelity astrodynamics (Firefly Blue Ghost 1, CAPSTONE) -- **AGPL + Python pkg disabled** |
| Small-Bodies-Node/pds4_tools | Python | 26 | none detected | 14 | 2026-02-14 | read/display NASA PDS4 small-bodies data -- no license = legally risky to import |
| skyfielders/python-skyfield | Python | 1764 | MIT | 88 | 2026-08-07 | pure-Python ephemerides (DE421) -- only dep is numpy |
| juliensimon/space-datasets | Python | 11 | NOASSERTION | 0 | 2026-09-03 | 200+ auto-updated space/astro datasets on Hugging Face (NASA, NOAA, ESA, JPL, SpaceX) |
| astropy/astroquery | Python | 791 | BSD-3-Clause | 362 | 2026-09-03 | query online astronomy data (JPL Horizons, SIMBAD) -- catalog enrichment |

## What is actually useful to wire in

### brahe -- the clean dv cross-check (top pick)
MIT, `pip install brahe`, JOSS peer-reviewed (arXiv 2601.06452), active (pushed 2026-09-03,
only 6 open issues). Rust core + Python bindings; clean reference frames / time handling /
propagators. Use it to **independently cross-check** the hand-coded patched-conic dv in
calc.py -- do NOT replace the ranking math with it (bit-identity discipline). Validate against
known references first: Earth->Moon ~9.4 km/s, Earth->Mars Hohmann ~5.6 km/s total.
Versioning is NumPy-style not strict SemVer; pin to a specific major.minor.patch during the
transitional deprecation window (their own guidance).

**Computational surface (from its `brahe-py` binding modules):** propagators + integrators
(RK4, SGP4), orbit determination/estimation, frames/time/EOP handling, Earth gravity models
(ICGEM), relative motion, access windows -- AND data clients for **SBDB, JPL Horizons, SPICE,
Celestrak, Space-Track**. That last point matters: brahe overlaps BOTH economicspace's catalog
data sources (stage 1) and its dv math (stage 4) in one MIT library. It also ships comparative
benchmarks against nyx, so it is a fair cross-check target.

## The different computational calculations (paradigms)

The list contains five genuinely different ways to compute trajectories/dv/windows -- not
interchangeable. Full decision guide lives in the `space-mission-computation-paradigms` skill;
summary here:

1. **Closed-form patched conics** (economicspace's own `calc.py`): analytic two-body + SOI
   patches -> instant, bit-reproducible dv budget + transfer time + phase angle. Right for
   ranking thousands of targets. Weakness: no third-body/perturbation fidelity.
2. **Numerical propagation** (brahe RK4/SGP4, skyfield DE ephemerides): integrate the real force
   model -> exact positions for phase angles/access windows; validates a closed-form number.
3. **Successive convexification** (OpenSCvx, JAX+CVXPY): linearize nonlinear OCP around current
   guess + trust-region/penalty terms so each subproblem is convex; iterate to convergence.
   Techniques: free final time, adaptive time dilation (`s` appended to control vector),
   continuous-time constraint satisfaction (arXiv 2404.16826), FOH/ZOH exact discretization,
   AOT-compiled multishooting. Solves the actual fuel/time-optimal thrust profile under hard
   constraints -- but iterative + heavy GPU dep chain (breaks bit-identity if it leaks in).
4. **Parallel global multiobjective optimization** (pygmo/pagmo): one interface over CMA-ES/DE/PSO
   + NLP solvers, run across a generalized island model for massively parallel population search;
   Pareto fronts + uncertainty quantification. Right for "best mission given N uncertain params."
   PyPI wheels are Linux x86_64/aarch64 only (Windows needs conda-forge/source).
5. **6DOF forward-integration Monte Carlo** (CamPyRoS): full 3-trans + 3-rot dynamics, variable
   mass/inertia, aeroheating, live wind; stochastic dispersion via MC (Ray for parallelism on
   non-Windows). Launch-dispersion/reliability regime -- atmospheric, NOT interplanetary dv.

**Rule of thumb:** closed-form to RANK, numerical propagation to VERIFY, convexification to DESIGN
a specific maneuver's control law, global optimization to find the robust optimum across
uncertainty, 6DOF Monte Carlo for launch dispersion. economicspace currently uses only (1); the
highest-leverage additions are (2) as a gated cross-check and (3)/(4) if it ever needs real
trajectory design or campaign-level uncertainty.

## Non-trajectory computational methods in the list

Beyond trajectory math, four repos carry distinct algorithms that could apply to economicspace's
economics/uncertainty side:

- **pymc** -- Bayesian inference via two specific engines: (a) **NUTS MCMC** (No-U-Turn Sampler,
  Hamiltonian Monte Carlo with adaptive step-size/path-length termination) for exact-ish posterior
  sampling of complex models; (b) **ADVI variational inference** (Automatic Differentiation Variational
  Inference, + mini-batch ADVI) for fast approximate posteriors on large data. Built on PyTensor
  (dynamic C/JAX compilation). Use to turn point estimates of mineral price / density into posterior
  distributions -> credible intervals on the profit ranking. Heavy dep chain; only if uncertainty is wanted.
- **Pyomo** -- an *algebraic modeling language*, not a solver: it formulates symbolic LP/MIP/NLP/MIQP
  models and hands them to external solvers (COIN-OR ecosystem). Relevant only if economicspace ever
  needs a constrained allocation problem (e.g. "which subset of asteroids maximizes profit under a
  launch-capacity budget") -- that's an MIQP, which calc.py's per-row rocket equation does not solve.
- **z3** -- SMT theorem prover / constraint solver (Satisfiability Modulo Theories): decides feasibility
  and finds models for logical constraints over integers/reals/arrays/bit-vectors. MIT license. Not a fit
  for the ranking, but useful if you ever need to *prove* an invariant or check that a set of mission
  constraints is jointly satisfiable (e.g. no feasible launch window exists under given bounds).
- **mesa** -- agent-based modeling: simulate many autonomous agents with local rules and observe emergent
  system behavior. The "econ" in the list name likely points here -- e.g. model a market of competing
  mining firms, or demand dynamics over time. NOT single-mission optimization; it's for studying how an
  aggregate outcome emerges from individual decisions.

**None of these four are imported by economicspace today**, and none replace its closed-form ranking.
pymc is the most likely future addition (uncertainty on prices/densities); Pyomo/z3/mesa are only
relevant if the project scope expands to constrained allocation, invariant proving, or market dynamics.

### skyfield -- precise ephemerides / phase angles
MIT, pure Python, **only binary dep is numpy** -> lowest-risk addition. DE421/DE430 planetary
positions at any epoch. Useful to compute exact launch-window phase angles and to validate the
`synodic_period_yr` approximation in calc.py against a real ephemeris.

### astroquery -- catalog enrichment (stage 1)
BSD-3-Clause, astropy-affiliated. Sub-packages for JPL Horizons, SIMBAD, NEOWISE, etc. Could
add sources to `catalog.py` beyond the current SBDB/MP3C/ssoBFT/NEOWISE set. Watch rate limits
on large catalogs (it's a query layer over web services).

### pymc -- optional uncertainty layer (stage 2)
Apache-2.0, Bayesian inference. If point estimates for mineral prices / densities should become
distributions with credible intervals on the profit ranking, this is the tool. Heavy dep chain
(pytensor/Aesara lineage) -- only add if the uncertainty question is actually wanted.

### space-datasets -- bulk data source (stage 1)
200+ auto-updated datasets on Hugging Face from NASA/NOAA/ESA/JPL/SpaceX/Wikidata. Could feed
catalog.py or mineral_value.py without per-source scraping. License shows NOASSERTION -- check
the actual dataset licenses before relying on it.

## Dead ends / blockers (do NOT import into the pipeline)

- **nyx** -- AGPLv3: linking/depending on it forces economicspace to be AGPL too; AND the Python
  package `nyx_space` is **temporarily disabled** (issue #311). Mission-proven (Blue Ghost 1,
  CAPSTONE) but wrong license + no working Python path for this project. Use brahe instead.
- **Celestia** -- GPL-2.0 copyleft; it's a standalone visualization app, not a library to link
  into a headless pipeline. Fine as a separate viewing tool only.
- **CamPyRoS** -- GPL-3.0 + stale (last push Jul 2025). Rocket trajectory sim; not worth the
  copyleft for what it adds over brahe/skyfield.
- **pds4_tools** -- no license detected -> legally risky to import directly. If PDS4 small-bodies
  data is needed, read the raw PDS4 products yourself rather than depending on an unlicensed wrapper.
- **space-map** -- AGPL-3.0 + only 2 stars; tiny and copyleft.
- **polars** -- MIT but redundant: pyarrow already in the stack for parquet (ssoBFT). Don't add a
  second DataFrame engine.
- **mesa / z3 / Pyomo / pygmo2 / OpenSCvx** -- modeling/optimization/constraint tools that don't
  fit a deterministic profitability ranking. calc.py already solves its own rocket-equation
  feedback loop; none of these are needed for the current model.

## Integration discipline (economicspace-specific)

- Any new dep goes into **both** `requirements.txt` and `requirements-lock.txt` (pinned), because
  numpy's SIMD kernels pick per-release and a minor bump can move `estimated_mass_kg` in the last
  bit -- which is what the whole ranking runs on.
- Cross-check libs (brahe, skyfield) should live OUTSIDE the four modules' import path or be gated,
  so they validate without changing committed numbers. A lib that changes a float is not a
  cross-check, it's a regression.
- `master.py` is generated by `build_master.py` from `modules/*.py`; never edit it directly. If a
  module gains an import, the build's `_MASTER_REQUIRED` / auto-install list must match.

## Concrete next steps per candidate (surveyed 2026-09-04)

Per-repo action items beyond "wire in" — what each would actually do here and at what scale:

| repo | concrete step | scale note |
|---|---|---|
| brahe | Gated cross-check script (research/ level): closed-form dv vs numerical per body + exact phase angles → comparison CSV that never feeds ranking math. Its SBDB/Horizons clients could also enrich stage 1 without new scraping code. | One-off validation run; pin version during their transitional deprecation window |
| skyfield | Quantify the synodic-window approximation: `synodic_period_yr` is a closed-form mean-motion ratio — compare against ephemeris-derived exact phase angles per body, report distribution of deltas (km/s and days). Feeds directly into documenting calc 1.19.2's window_phasing_au fix margin. | numpy-only; cheap enough to run on the full catalog once |
| astroquery | SDSS cross-survey at scale: manual spot check found ~34% albedo disagreement between surveys — turn it into a per-body provenance column for every body in the SDSS footprint, converting the 90.2%-albedo-assumed problem from population statistic to per-row uncertainty flags (natural input to the pymc layer). | Batch queries; cache results as CSV like other stage-1 data |
| pymc | Uncertainty layer on comp_* / price elasticities with engine selection: NUTS MCMC for a handful of load-bearing global constants (exact-ish posteriors, high cost); ADVI variational inference for per-body comp_* at ~1.5M-row scale (fast approximate). Both PyTensor-based; heavy dep chain — gated + pinned in both requirements files. | Do NOT run NUTS per body; that's the engine-selection trap |
| Pyomo (+ COIN-OR) | MIQP fleet-allocation study: "which subset of top-N candidates maximizes net value under N launches/yr and fleet bounds" — calc.py's per-row outputs are exactly the coefficient vector. One-off research script unless a result is promoted into stage 4. | BSD-3 (COIN-OR); solver choice matters more than modeling layer here |
| z3 | Invariant proofs for harness structure, one-time + re-run on schema changes: preflight covers every destination pair; mass-ledger identity over config space; window_phasing_au total across all seven destinations. Empirical checks catch data regressions; a proof catches the structural class calc 1.19.2 just fixed (a conditional naming one member of a set instead of asking the set). | MIT; no runtime cost — proofs run at build/verify time only |
| mesa | Market-dynamics sandbox: competing-firm agents against static saturation constants; stress-tests geo's role as the smallest in-space market (40,000 kg/yr anchor) from a fixed number into a process. Long-term research item, not pipeline work. | Agent-based emergent dynamics — different paradigm entirely |
| polars | Already evaluated: Parquet-instead-of-CSV for catalog measured 19.7 s → 2.1 s and DECLINED (changes Module 1's output contract; no measurable cell movement). Revisit only if the CSV writer itself ever becomes a bottleneck. | Closed, not deferred — see defect-classes ref "Measured and declined" |
