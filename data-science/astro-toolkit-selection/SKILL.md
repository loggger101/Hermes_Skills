---
name: astro-toolkit-selection
description: "Space trajectory work: pick the method, then the library."
version: v1.0.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [astrodynamics, trajectory, tooling, trajectories, delta-v, mission-design]
    related_skills: [orbital-mechanics-data, optimization-modeling-pyomo, economicspace-pipeline]
---

<!-- round-57: space-mission-computation-paradigms (same starred-repo research) merged in as step 1 -->

## When to Use

- Deciding how to compute a trajectory, delta-v budget or transfer window: closed-form, propagation, convex optimization, global optimization or Monte Carlo — the cheapest method that answers the actual question at the accuracy it needs
- Choosing a library to propagate orbits, optimize a trajectory, simulate a launch vehicle or search a mission design space
- Cross-checking results between astrodynamics tools, or checking a tool's license before building on it

## What This Skill Does

Two decisions, in order. First the **method**: the five distinct ways to compute trajectories / delta-v / transfer windows (plus the optimization layer that consumes their numbers), which are NOT interchangeable — each answers a different question at a different cost/accuracy tradeoff. Then the **library** for that method (skyfield, brahe, nyx, OpenSCvx, CamPyRoS or pygmo), from a source-verified decision table with verified usage patterns and the unit and licensing gotchas.

# Space Computation: Method, Then Toolkit

The methods are the ones that show up in the user's `for-econ-space-pipeline` star list. Pick by what you actually need, not by which library is most impressive.

## Step 1: Pick the method

| paradigm | computes | accuracy | speed | use it for | example lib in the list |
|---|---|---|---|---|---|
| **Closed-form patched conics** | Δv budget, transfer time, launch window (phase angle), rendezvous geometry | low-med (two-body + SOI patches) | instant (analytic) | ranking many targets by reachability/cost; the economicspace default | hand-coded in `calc.py` (`asteroid_transfer_dv_km_s`) |
| **Numerical propagation** (RK4 / SGP4 / Gauss-Jackson) | precise state at any epoch, access windows, orbit determination | high (full force model) | fast-ish (per-step integration) | validating a closed-form number; exact phase angles; TLE-based passes | brahe (`propagators`, `integrators`), skyfield (DE ephemerides) |
| **Successive convexification** (SCvx / SCVX) | optimal thrust profile under constraints (fuel-optimal, time-optimal, LOS/obstacle) | high (solves the actual OCP) | slow (iterative NLP loop) | designing a specific maneuver's control law; low-thrust trajectory shaping | OpenSCvx (JAX + CVXPY) |
| **Parallel global multiobjective optimization** | Pareto front over many design variables, robustness under uncertainty | depends on inner model | very fast at scale (island model, GPU) | "what's the best mission given N uncertain parameters"; campaign sweeps | pygmo/pagmo (ESA), mesa (agent-based variant) |
| **6DOF forward-integration Monte Carlo** | dispersions of a launch/flight under stochastic inputs; heating, wind, slosh | high (full 6-DOF dynamics + stats) | slow (thousands of runs) | launch dispersion analysis, reliability, aeroheating — NOT interplanetary Δv | CamPyRoS (Cambridge) |
| **Declarative constrained optimization** (orthogonal layer — consumes the numbers above as coefficients) | optimal fleet/mission *selection* under budget/fleet/window constraints; piecewise-linear cost curves kept MIP-exact; global solutions of disjunctive ("either this transfer or that") structure | exact for LP/MIP/QP, rigorous b&b for convex GDP | fast (solver-internal); model build is the cost | "which subset of N candidates maximizes net value under K launches/yr" — the allocation problem closed-form Δv feeds but can't answer itself | Pyomo + HiGHS/Gurobi (`optimization-modeling-pyomo` skill: V2 solver idiom, piecewise MIP counts, GDPopt global solvers) |

### The core distinction: closed-form vs. numerical

**Closed-form patched conics** (what economicspace uses):

- Two-body Keplerian motion inside each body's sphere of influence; patch at the SOI boundary by transforming velocity into the new central body's frame and adding that body's heliocentric velocity.
- Δv from vis-viva differences between orbits; transfer time = half-period of the transfer ellipse (Hohmann) or a bi-elliptic variant for large radius ratios.
- Launch window / phase angle: wait until target is at `θ_launch = (ω_target − ω_transfer)·t_trans (mod 2π)`.
- **Strength:** instant, deterministic, bit-reproducible — ideal when you must rank thousands of asteroids and argue from exact float identity.
- **Weakness:** ignores third-body gravity inside SOIs, perturbations (J2, SRP), non-spherical bodies; the Δv is a budget estimate, not an executable trajectory.

**Numerical propagation**:

- Integrate `r̈ = −μ r/r³ + Σ(perturbations)` with RK4 / Gauss-Jackson / SGP4 (for LEO from TLEs). Deterministic given fixed step + seed.
- **Strength:** captures the real force model; gives exact positions for phase angles and access windows.
- **Weakness:** per-step cost; must be deterministic to stay reproducible (fixed timestep, consistent frame/units) — same discipline as any ML sim environment.

**Successive convexification** (OpenSCvx's paradigm):

- Reformulate a nonlinear optimal-control problem by linearizing dynamics around the current guess and adding trust-region / penalty terms so each subproblem is CONVEX; solve with CVXPY, iterate to convergence. JAX gives autodiff Jacobians + AOT compilation + vectorization/GPU.
- Specific techniques OpenSCvx implements: **free final time**, **fully adaptive time dilation** (a scalar `s` appended to the control vector so the solver can stretch/compress the timeline), **continuous-time constraint satisfaction** (arXiv 2404.16826 — constraints enforced between nodes, not just at them), **FOH/ZOH exact discretization**, **vectorized AOT-compiled multishooting**.
- **Strength:** solves the actual fuel/time-optimal control problem with hard constraints — the "right answer" for a single maneuver's thrust profile.
- **Weakness:** iterative (may not converge from a bad guess), heavy dep chain (JAX/CVXPY → GPU/CUDA), and it changes floats per solver version — incompatible with bit-identity pipelines unless fully isolated and pinned.

**Parallel global multiobjective optimization** (pygmo/pagmo):

- Wraps many algorithms (CMA-ES, differential evolution, PSO, NLP solvers) behind one interface; runs them across a **generalized island model** for massively parallel population-based search; supports multi-objective Pareto fronts and uncertainty quantification. JOSS-reviewed (Biscani & Izzo 2020).
- **Strength:** "optimize the mission over N uncertain parameters" at scale — exactly what a campaign sweep wants.
- **Weakness:** PyPI wheels are Linux x86_64 + aarch64 ONLY; on Windows you need conda-forge or source build (matters for this user's dual-host setup).

**6DOF forward-integration Monte Carlo** (CamPyRoS):

- Full 3-translational + 3-rotational dynamics, variable mass/inertia, aeroheating model, live wind data; stochastic analysis via Monte Carlo (Ray for parallelism on non-Windows). References NASA 6-DOF check-cases and the tangent-ogive heating program.
- **Strength:** launch dispersion / reliability / aeroheating — the atmospheric + rotational regime closed-form conics can't touch.
- **Weakness:** it's a *forward simulator*, not an optimizer; GPL-3.0; stale (last push Jul 2025); Windows stats module degrades to single-threaded without Ray.

### Measured ground truth from economicspace's own audit (research/starred-repos/)

Before deciding anything, the repo validated its closed-form estimator against a **numerical Izzo-Lambert porkchop oracle** (`orbital.py` + `probe_lambert.py`, 10,874 bodies):

- The closed-form outbound Δv is **optimistic by median +1.30 km/s (11.9%) on 86% of bodies**, worst at high inclination — the plane-change term overcharges (median 4.87%, up to ~25×) while transfer geometry undercharges, and the two errors partially cancel: correcting only the overcharge makes the model WORSE in every inclination band.
- The verdict was therefore NOT "wire brahe into calc.py": a fair cross-check target is exactly what this oracle already is — an independent numerical method used to bound the closed-form one's error, with both terms corrected together or not at all (the standing limitation stays documented rather than half-fixed).

### Decision guide for economicspace-style work

1. **"Rank every asteroid by net profit"** → closed-form patched conics + rocket equation (current `calc.py`). Keep it — instant and bit-reproducible.
2. **"Is that Δv number actually right?"** → cross-check with a numerical propagator (brahe or skyfield) on the same transfer; compare to known references (Earth→Moon ~9.4 km/s, Earth→Mars Hohmann ~5.6 km/s). Do NOT let it replace the ranking math — if it moves a float it's a regression, not a check.
3. **"What exact launch window / phase angle?"** → skyfield DE ephemerides or brahe Horizons/SPICE; validate `synodic_period_yr` against them.
4. **"Design the actual low-thrust thrust profile to get there"** → OpenSCvx (successive convexification). Isolate it: JAX/CVXPY deps + GPU will break bit-identity if they leak into the modules' import path.
5. **"What's robust across uncertain mineral content / Δv / price?"** → pygmo campaign sweep for a Pareto front; or mesa agent-based modeling only if you want emergent multi-agent market dynamics (not single-mission optimization).
6. **"How much does the launch disperse under wind/aero uncertainty?"** → CamPyRoS 6DOF Monte Carlo — but it's atmospheric, not interplanetary, and copyleft.

### Cross-cutting reproducibility rules (economicspace-specific)

- Any of these libs added as a dep goes into **both** `requirements.txt` AND `requirements-lock.txt`, pinned — numpy/JAX/CVXPY all pick kernels per-release and can move the last bit of `estimated_mass_kg`.
- Cross-check/optimizer libs must live OUTSIDE the four modules' import path or be gated, so they validate without changing committed numbers.
- Determinism: fixed timestep + consistent reference frame + pinned solver version for any numerical method you expose to a second host (`platform_check.py` gates it).

## Step 2: Pick the library

Verified 2026-09 from source of duncaneddy/brahe, nyx-space/nyx, OpenSCvx/OpenSCvx, cuspaceflight/CamPyRoS, skyfielders/python-skyfield (clones were read-only; re-clone with `git clone --depth 1` if you need verbatim examples).

| Job | Tool | Why |
|---|---|---|
| Propagate orbits / ephemerides of solar-system bodies + TLE sats | **skyfield** (MIT, pip) | Elegant, cached data files (`Loader`), no build step. Fastest path to positions/velocities. |
| Full astrodynamics in Python: propagators RK4/SGP4, orbit determination, frames/time/EOP, ICGEM gravity, relative motion, access windows — plus SBDB/Horizons/SPICE/Celestrak data clients | **brahe** (Rust core + py bindings) | One lib covers both catalog-fetching and dv math; ships benchmarks vs nyx for cross-checks. |
| High-fidelity validated propagation reference / cross-check target | **nyx** (AGPLv3, Rust) | Python pkg `nyx_space` is LIVE (`pip install nyx_space`, py≥3.11 — verified round 2; see references/optimization-toolkit.md). AGPL = copyleft blocker for anything shipped: use as reference/cross-check only, never link into proprietary code. |
| Optimize a trajectory under hard constraints (free final time, continuous dynamics + impulsive nodes) | **OpenSCvx** (`pip install openscvx`, JAX+CVXPY successive convexification) | `ox.State`/`ox.Control` → dynamics fns → `Problem.solve()`. Verified spacecraft examples: hohmann_transfer.py, let_transfer.py (Sun-Earth CR3BP low-energy), halo_orbit.py, proxops_cw.py. |
| 6DOF launch vehicle simulation w/ aeroheating + Monte Carlo dispersion | **CamPyRoS** (`pip install git+https://github.com/cuspaceflight/CamPyRoS.git`) | Full 6DOF, live wind data, variable mass/inertia. Stats module needs `ray` — on Windows it degrades to single-threaded (slow); plan around that. |
| Global multi-objective optimization of black-box mission objectives (e.g. profit vs delta-v Pareto) | **pygmo** (`conda install -c conda-forge pygmo`) | Island-model parallelism + BFE batch evaluation. **PyPI wheels are Linux-only — on Windows use conda-forge or build from source.** JOSS-reviewed; cite Biscani & Izzo 2020 if used in research. |

### Verified patterns

- OpenSCvx Hohmann (from examples/spacecraft/hohmann_transfer.py): planar 2-body Earth-centered, `mu=3.986e5 km^3/s^2`, impulsive dv at initial+final nodes via discrete dynamics (`v += dv; cost += ||dv||`), fixed half-period transfer time, scalar accumulated-cost state minimized at final node. Initial guess must avoid r≈0 (singular gravity).
- brahe: check `pyproject.toml` version before pinning; examples/ has Dawn/Ceres-class missions.
- skyfield: top-level import pulls most of the library — use submodules (`skyfield.api`, `skyfield.topos`) for speed in hot loops.

### Gotchas

- Units are the #1 bug source across all five: km vs m, deg vs rad, J2000 epoch conventions differ per lib. State units explicitly at every API boundary and unit-test against a known ephemeris (e.g. skyfield position of Earth on a fixed date).
- nyx AGPL = reference/cross-check only; don't plan builds around it (the Python pkg is live, but copyleft still blocks shipping).
- OpenSCvx needs JAX — CPU works but GPU strongly preferred for batched problems (`pip install openscvx[cvxpygen]` optional extra).
- CamPyRoS on Windows: runs WITHOUT ray via its bundled `ray_alt.py` serial shim (verified round 2 — see references/optimization-toolkit.md); Monte Carlo works single-threaded, just slow. Skip the stats module only if you need speed.

## Library → method map (the 17 repos)

| repo | paradigm(s) | notes |
|---|---|---|
| calc.py (economicspace, hand-coded) | closed-form patched conics + Tsiolkovsky rocket eq | the baseline; bit-identity discipline |
| duncaneddy/brahe | numerical propagation (RK4/SGP4), orbit determination, frames/time/EOP, **SBDB/Horizons/SPICE/Celestrak data** | MIT, pip-installable — top cross-check + catalog-enrichment pick |
| skyfielders/python-skyfield | DE ephemerides (numerical positions) | MIT, numpy-only dep |
| OpenSCvx/OpenSCvx | successive convexification (JAX+CVXPY) | Apache-2.0; heavy GPU dep chain |
| esa/pygmo2 | parallel global multiobjective (island model) | MPL-2.0; Linux wheels only on PyPI |
| cuspaceflight/CamPyRoS | 6DOF forward-integration Monte Carlo + aeroheating | GPL-3.0, stale Jul 2025 |
| mesa/mesa | agent-based modeling (emergent dynamics) | Apache-2.0; not single-mission optimization |
| nyx-space/nyx | high-fidelity propagation + trajectory opt + orbit determination | AGPLv3; the Python pkg `nyx_space` is live (pip, py≥3.11 — the old "disabled" note was wrong, see `references/optimization-toolkit.md`), but copyleft blocks shipping: reference/cross-check only |
| Pyomo/pyomo (mined 2026-09-12) | declarative constrained optimization layer over the above | BSD-3; HiGHS persistent interface live-verified on this box via isolated venv (`optimization-modeling-pyomo`) — allocation/selection problems, not trajectory math itself |

## References (verified API detail lives here)

- `references/brahe-api-reference.md` — brahe 1.7.0 full module map + live-run snippets (Horizons SPK fetch for any small body; Celestrak query builder; EKF/UKF/BLS estimation).
- `references/skyfield-api-reference.md` — skyfield **1.55 breaking changes** (load() contract), de430s.bsp 404 on both JPL mirrors, phase-angle trap with numbers, osculating-elements solver for independent element checks.
- `references/openscvx-patterns.md` — OpenSCvx core problem pattern (State/dynamics/Problem.solve), Hohmann example constants verbatim, autotuner class map.
- `references/catalog-data-sources.md` — astroquery async-first API map (SBDB `covariance=` flag; Horizons all-43-quantities bloat gotcha; NEODyS full 6×6 covariance), pds4_tools metadata-with-array, cumulus pvl/cmr-client, space-map binary ephemeris schema.
- `references/optimization-toolkit.md` — nyx-py (LIVE correction), pygmo2 UDA contract, mesa 3.5.1 LIVE-verified working idiom + silent batch_run bug (round-19 corrections to the old "two blockers" note), z3-solver 5.1.0 pip API names verified live (FP/regex/Optimize proofs), Pyomo dae/gdp/mpec, CamPyRoS ray_alt serial shim.
- `references/pykep-v3-notes.md` — pykep 3.0.1 (ESA): PyPI wheels are manylinux-only (cp311-313), so not pip-installable on Windows/macOS (conda-forge has pykep 3.0.0 for win-64/osx via pixi/mamba); API map for Lambert, Lagrangian/Taylor propagation, legs, trajopt (mga, sims_flanagan, ZOH), planets; fit vs brahe/OpenSCvx/pygmo.
- `references/egobox-bayesian-optimization.md` — EGObox 0.38.0 (pip, py3.14): Egor/Gpx run live (README example reproduced, argmin differs across hosts in the 5th decimal, 21 objective calls for 20 iterations, Branin 0.39788747).
- `references/hifitime-time-scales.md` — hifitime 4.3.1 (Rust + pip) run live and cross-checked against astropy 8.0.1: correct TAI/TT/TDB/GPST offsets, but a 1 s TAI->UTC error at leap-second boundaries, UTC `timedelta` ignoring the leap second; rules for safe use.
- `references/rebound-n-body-notes.md` — REBOUND 5.2.1 live-run (wheel OK on py3.14; `sim.G` in AU/yr/Msun is 39.4769, not 4pi^2) and REBOUNDx (sdist-only, needs a C compiler: failed here), Yarkovsky/radiation-force parameters, GPL-3.0 caveat, ASSIST pointer.
- `references/orekit-python-notes.md` — Orekit 13.1.9 from Python via `orekit-jpype` + pip-provided JDK (live-run on py3.14/Windows): import-after-`initVM` rule, SI/radian units, Kepler propagation verified, UTC/ITRF fail without orekit-data, data helpers.
- `references/spiceypy-notes.md` — SpiceyPy 8.2 (live-run on py3.14): empty-kernel-pool errors, `KernelPool` clears hand-set pool vars, 80-char kernel-pool strings silently truncated, SPICE's AU (149597870.6137 km) differs from the IAU value, asteroid NAIF ids (2000000 + number), kernel-free `conics`/`oscelt` cross-check.
- `references/spacekit-notes.md` — spacekit.js (typpo) 3D viewer: committed cjs bundle runs headless in Node (`new Orbit(EphemPresets.X, {})`), planet presets are fixed two-body elements checked vs astropy (Saturn 0.09 AU off today, 1.5 AU in 1900), npm latest 0.1.1 vs repo 0.1.0, three.js pinned 0.135.0
- `references/astropy-notes.md` — astropy 8.0.1 traps run (py3.12): numeric JD is UTC by default (TT differs 69.184 s), string UTC offsets rejected, `Time + float` assumes days, AltAz without location gives a misleading AttributeError, IERS auto-download defaults and far-future extrapolation, units/angle gotchas.
