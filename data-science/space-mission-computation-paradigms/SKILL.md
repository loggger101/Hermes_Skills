---
name: space-mission-computation-paradigms
description: "Choose trajectory method: closed-form vs propagation etc."
version: v0.9.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [trajectories, delta-v, mission-design]
    related_skills: [astro-toolkit-selection]
---

## When to Use

- When working on: Choose trajectory computation method: closed-form vs propagation.

## What This Skill Does

The five distinct ways to compute trajectories / delta-v / transfer windows that show up in the user's `for-econ-space-pipeline` star list. They are NOT interchangeable — each answers a different


# Space Mission Computation Paradigms

The five distinct ways to compute trajectories / delta-v / transfer windows that show up in the
user's `for-econ-space-pipeline` star list. They are NOT interchangeable — each answers a different
question at a different cost/accuracy tradeoff. Pick by what you actually need, not by which library
is most impressive.

## The five paradigms (and when each is right)

| paradigm | computes | accuracy | speed | use it for | example lib in the list |
|---|---|---|---|---|---|
| **Closed-form patched conics** | Δv budget, transfer time, launch window (phase angle), rendezvous geometry | low-med (two-body + SOI patches) | instant (analytic) | ranking many targets by reachability/cost; the economicspace default | hand-coded in `calc.py` (`asteroid_transfer_dv_km_s`) |
| **Numerical propagation** (RK4 / SGP4 / Gauss-Jackson) | precise state at any epoch, access windows, orbit determination | high (full force model) | fast-ish (per-step integration) | validating a closed-form number; exact phase angles; TLE-based passes | brahe (`propagators`, `integrators`), skyfield (DE ephemerides) |
| **Successive convexification** (SCvx / SCVX) | optimal thrust profile under constraints (fuel-optimal, time-optimal, LOS/obstacle) | high (solves the actual OCP) | slow (iterative NLP loop) | designing a specific maneuver's control law; low-thrust trajectory shaping | OpenSCvx (JAX + CVXPY) |
| **Parallel global multiobjective optimization** | Pareto front over many design variables, robustness under uncertainty | depends on inner model | very fast at scale (island model, GPU) | "what's the best mission given N uncertain parameters"; campaign sweeps | pygmo/pagmo (ESA), mesa (agent-based variant) |
| **6DOF forward-integration Monte Carlo** | dispersions of a launch/flight under stochastic inputs; heating, wind, slosh | high (full 6-DOF dynamics + stats) | slow (thousands of runs) | launch dispersion analysis, reliability, aeroheating — NOT interplanetary Δv | CamPyRoS (Cambridge) |

## The core distinction: closed-form vs. numerical

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

## Measured ground truth from economicspace's own audit (research/starred-repos/)

Before deciding anything, the repo validated its closed-form estimator against a **numerical Izzo-Lambert porkchop oracle** (`orbital.py` + `probe_lambert.py`, 10,874 bodies):
- The closed-form outbound Δv is **optimistic by median +1.30 km/s (11.9%) on 86% of bodies**, worst at high inclination — the plane-change term overcharges (median 4.87%, up to ~25×) while transfer geometry undercharges, and the two errors partially cancel: correcting only the overcharge makes the model WORSE in every inclination band.
- The verdict was therefore NOT "wire brahe into calc.py": a fair cross-check target is exactly what this oracle already is — an independent numerical method used to bound the closed-form one's error, with both terms corrected together or not at all (the standing limitation stays documented rather than half-fixed).

## Decision guide for economicspace-style work

1. **"Rank every asteroid by net profit"** → closed-form patched conics + rocket equation (current `calc.py`). Keep it — instant and bit-reproducible.
2. **"Is that Δv number actually right?"** → cross-check with a numerical propagator (brahe or skyfield) on the same transfer; compare to known references (Earth→Moon ~9.4 km/s, Earth→Mars Hohmann ~5.6 km/s). Do NOT let it replace the ranking math — if it moves a float it's a regression, not a check.
3. **"What exact launch window / phase angle?"** → skyfield DE ephemerides or brahe Horizons/SPICE; validate `synodic_period_yr` against them.
4. **"Design the actual low-thrust thrust profile to get there"** → OpenSCvx (successive convexification). Isolate it: JAX/CVXPY deps + GPU will break bit-identity if they leak into the modules' import path.
5. **"What's robust across uncertain mineral content / Δv / price?"** → pygmo campaign sweep for a Pareto front; or mesa agent-based modeling only if you want emergent multi-agent market dynamics (not single-mission optimization).
6. **"How much does the launch disperse under wind/aero uncertainty?"** → CamPyRoS 6DOF Monte Carlo — but it's atmospheric, not interplanetary, and copyleft.

## Cross-cutting reproducibility rules (economicspace-specific)

- Any of these libs added as a dep goes into **both** `requirements.txt` AND `requirements-lock.txt`, pinned — numpy/JAX/CVXPY all pick kernels per-release and can move the last bit of `estimated_mass_kg`.
- Cross-check/optimizer libs must live OUTSIDE the four modules' import path or be gated, so they validate without changing committed numbers.
- Determinism: fixed timestep + consistent reference frame + pinned solver version for any numerical method you expose to a second host (`platform_check.py` gates it).

## Library → paradigm map (the 17 repos)

| repo | paradigm(s) | notes |
|---|---|---|
| calc.py (economicspace, hand-coded) | closed-form patched conics + Tsiolkovsky rocket eq | the baseline; bit-identity discipline |
| duncaneddy/brahe | numerical propagation (RK4/SGP4), orbit determination, frames/time/EOP, **SBDB/Horizons/SPICE/Celestrak data** | MIT, pip-installable — top cross-check + catalog-enrichment pick |
| skyfielders/python-skyfield | DE ephemerides (numerical positions) | MIT, numpy-only dep |
| OpenSCvx/OpenSCvx | successive convexification (JAX+CVXPY) | Apache-2.0; heavy GPU dep chain |
| esa/pygmo2 | parallel global multiobjective (island model) | MPL-2.0; Linux wheels only on PyPI |
| cuspaceflight/CamPyRoS | 6DOF forward-integration Monte Carlo + aeroheating | GPL-3.0, stale Jul 2025 |
| mesa/mesa | agent-based modeling (emergent dynamics) | Apache-2.0; not single-mission optimization |
| nyx-space/nyx | high-fidelity propagation + trajectory opt + orbit determination | **AGPLv3 + Python pkg disabled** — blocker despite mission-proven |
