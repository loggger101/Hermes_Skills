---
name: astro-toolkit-selection
description: "Choose astrodynamics tools: brahe, nyx, OpenSCvx, skyfield."
version: v0.9.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [astrodynamics, trajectory, tooling]
    related_skills: [space-mission-computation-paradigms, orbital-mechanics-data]
---

## When to Use

- When working on: Choose astrodynamics tools: brahe, nyx, OpenSCvx, skyfield.

## What This Skill Does

| Job | Tool | Why | |---|---|---|


# Astrodynamics Toolkit Selection

Verified 2026-09 from source of duncaneddy/brahe, nyx-space/nyx, OpenSCvx/OpenSCvx, cuspaceflight/CamPyRoS, skyfielders/python-skyfield (clones were read-only; re-clone with `git clone --depth 1` if you need verbatim examples).

## Decision rule
| Job | Tool | Why |
|---|---|---|
| Propagate orbits / ephemerides of solar-system bodies + TLE sats | **skyfield** (MIT, pip) | Elegant, cached data files (`Loader`), no build step. Fastest path to positions/velocities. |
| Full astrodynamics in Python: propagators RK4/SGP4, orbit determination, frames/time/EOP, ICGEM gravity, relative motion, access windows — plus SBDB/Horizons/SPICE/Celestrak data clients | **brahe** (Rust core + py bindings) | One lib covers both catalog-fetching and dv math; ships benchmarks vs nyx for cross-checks. |
| High-fidelity validated propagation reference / cross-check target | **nyx** (AGPLv3, Rust) | Python pkg `nyx_space` is LIVE (`pip install nyx_space`, py≥3.11 — verified round 2; see references/optimization-toolkit.md). AGPL = copyleft blocker for anything shipped: use as reference/cross-check only, never link into proprietary code. |
| Optimize a trajectory under hard constraints (free final time, continuous dynamics + impulsive nodes) | **OpenSCvx** (`pip install openscvx`, JAX+CVXPY successive convexification) | `ox.State`/`ox.Control` → dynamics fns → `Problem.solve()`. Verified spacecraft examples: hohmann_transfer.py, let_transfer.py (Sun-Earth CR3BP low-energy), halo_orbit.py, proxops_cw.py. |
| 6DOF launch vehicle simulation w/ aeroheating + Monte Carlo dispersion | **CamPyRoS** (`pip install git+https://github.com/cuspaceflight/CamPyRoS.git`) | Full 6DOF, live wind data, variable mass/inertia. Stats module needs `ray` — on Windows it degrades to single-threaded (slow); plan around that. |
| Global multi-objective optimization of black-box mission objectives (e.g. profit vs delta-v Pareto) | **pygmo** (`conda install -c conda-forge pygmo`) | Island-model parallelism + BFE batch evaluation. **PyPI wheels are Linux-only — on Windows use conda-forge or build from source.** JOSS-reviewed; cite Biscani & Izzo 2020 if used in research. |

## Verified patterns
- OpenSCvx Hohmann (from examples/spacecraft/hohmann_transfer.py): planar 2-body Earth-centered, `mu=3.986e5 km^3/s^2`, impulsive dv at initial+final nodes via discrete dynamics (`v += dv; cost += ||dv||`), fixed half-period transfer time, scalar accumulated-cost state minimized at final node. Initial guess must avoid r≈0 (singular gravity).
- brahe: check `pyproject.toml` version before pinning; examples/ has Dawn/Ceres-class missions.
- skyfield: top-level import pulls most of the library — use submodules (`skyfield.api`, `skyfield.topos`) for speed in hot loops.

## Gotchas
- Units are the #1 bug source across all five: km vs m, deg vs rad, J2000 epoch conventions differ per lib. State units explicitly at every API boundary and unit-test against a known ephemeris (e.g. skyfield position of Earth on a fixed date).
- nyx AGPL = reference/cross-check only; don't plan builds around it (the Python pkg is live, but copyleft still blocks shipping).
- OpenSCvx needs JAX — CPU works but GPU strongly preferred for batched problems (`pip install openscvx[cvxpygen]` optional extra).
- CamPyRoS on Windows: runs WITHOUT ray via its bundled `ray_alt.py` serial shim (verified round 2 — see references/optimization-toolkit.md); Monte Carlo works single-threaded, just slow. Skip the stats module only if you need speed.

## References (verified API detail lives here)
- `references/brahe-api-reference.md` — brahe 1.7.0 full module map + live-run snippets (Horizons SPK fetch for any small body; Celestrak query builder; EKF/UKF/BLS estimation).
- `references/skyfield-api-reference.md` — skyfield **1.55 breaking changes** (load() contract), de430s.bsp 404 on both JPL mirrors, phase-angle trap with numbers, osculating-elements solver for independent element checks.
- `references/openscvx-patterns.md` — OpenSCvx core problem pattern (State/dynamics/Problem.solve), Hohmann example constants verbatim, autotuner class map.
- `references/catalog-data-sources.md` — astroquery async-first API map (SBDB `covariance=` flag; Horizons all-43-quantities bloat gotcha; NEODyS full 6×6 covariance), pds4_tools metadata-with-array, cumulus pvl/cmr-client, space-map binary ephemeris schema.
- `references/optimization-toolkit.md` — nyx-py (LIVE correction), pygmo2 UDA contract, mesa v3 two blockers (py≥3.12 + API rewrite), z3 FPRef/regex sorts, Pyomo dae/gdp/mpec, CamPyRoS ray_alt serial shim.
