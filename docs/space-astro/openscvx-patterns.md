---
description: "OpenSCvx patterns — State/Control/dynamics core loop, Hohmann constants, autotuners"
source_repo: OpenSCvx/OpenSCvx (JAX + CVXPY successive convexification)
tested_version: cloned repo @ 2026-09-05 (examples/spacecraft/hohmann_transfer.py read directly; not pip-run on Windows — JAX+CVXPY stack, verify before relying)
verified_date: "2026-09-05"
---

# OpenSCvx — Core Pattern & Verified Constants

Successive convexification for trajectory optimization. Install `pip install openscvx`
(JAX + CVXPY; heavy deps). Use it to **DESIGN a specific maneuver's thrust profile under hard
constraints** (see skill `space-mission-computation-paradigms` for when this is the right tool vs closed-form/propagation).

## The core loop (from `examples/spacecraft/hohmann_transfer.py`, read verbatim)

```python
import numpy as np, openscvx as ox
from openscvx import Problem

n = 15                      # collocation nodes
mu = 3.986e5                # km^3/s^2 (planar two-body Earth-centered)
R_E = 6378.0; r_leo = 250.0 + R_E
sidereal_day = 86164.0905   # s
r_geo = (mu * sidereal_day**2 / (4*np.pi**2))**(1/3)
a_transfer = 0.5*(r_leo + r_geo)
T_transfer = np.pi*np.sqrt(a_transfer**3/mu)     # fixed Hohmann half-period

position = ox.State("position", shape=(2,))
position.initial = np.array([r_leo, 0.0])
position.final   = np.array([-r_geo, 0.0])       # opposite side for half-period transfer
position.min = np.array([-1.5*r_geo]*2); position.max = np.array([1.5*r_geo]*2)
theta_guess = np.linspace(0.0, np.pi, n); radius_guess = np.linspace(r_leo, r_geo, n)
position.guess = np.stack([radius_guess*np.cos(theta_guess), radius_guess*np.sin(theta_guess)], axis=1)

velocity = ox.State("velocity", shape=(2,))
v_c1, v_c2 = np.sqrt(mu/r_leo), np.sqrt(mu/r_geo)
velocity.initial = [0.0, v_c1]; velocity.final = [0.0, -v_c2]
vmag = 2.0*max(v_c1, v_c2); velocity.min = [-vmag,-vmag]; velocity.max = [vmag,vmag]

cost = ox.State("cost", shape=(1))               # scalar accumulated ||dv|| — the objective
cost.initial = [0.0]; cost.final = [("minimize", 10.0)]   # "minimize" tuple = free final value to minimize
cost.min = [0.0]; cost.max = [10.0]

dv = ox.Control("delta_v", shape=(2,), parameterization="impulsive", nodes=[0, n-1])
dv_bound = 5.0; dv.min = [-dv_bound]*2; dv.max = [dv_bound]*2

r = ox.linalg.Norm(position)
dynamics = {                                   # continuous: two-body gravity, no thrust
    "position": velocity,
    "velocity": ox.Concat(-mu*position[0]/r**3, -mu*position[1]/r**3),
    "cost": 0.0,
}
eps_impulse = 1e-6                             # avoid NaN derivatives at dv=0 in the norm
dynamics_discrete = {                          # impulsive nodes: kick velocity, accumulate cost
    "position": position,
    "velocity": velocity + dv,
    "cost": cost + ox.linalg.Norm(dv + eps_impulse),
}

constraints = []
for s in (position, velocity, cost):
    constraints.extend([ox.ctcs(s <= s.max), ox.ctcs(s.min <= s)])   # box constraints as CTCS

time = ox.Time(initial=0.0, final=T_transfer, min=0.0, max=T_transfer)  # fixed time; Free(...) for free-final-time problems
problem = Problem(dynamics=dynamics, dynamics_discrete=dynamics_discrete,
                  states=[position, velocity, cost], controls=[dv],
                  time=time, constraints=constraints, N=n)
problem.discretizer.ode_solver = "Dopri8"      # high-order RK for the linearization
problem.settings.prp.dt = 10.0                 # proximal-relaxation step size knob
# problem.solve() -> results; load_results()/load_json() to persist
```

## Key API facts (from `openscvx/__init__.py` export list)
- **Expr algebra**: build dynamics from JAX-traceable expressions — `ox.Concat`, `ox.linalg.Norm`, arithmetic on States, indexing (`position[0]`).
- **Constraint types**: `ox.ctcs(...)` continuous-time inequality; `Equality`/`Inequality`; `Fixed`/`Free` for time endpoints.
- **Discretizers**: `LinearizeDiscretizeVectorize`, `DiscretizeLinearizeSparse`, ode solvers incl `"Dopri8"`.
- **Autotuners** (the interesting part — SCP hyperparameter management as first-class objects):
  - Proximal weight strategies: `ConstantProximalWeight` (hold λ_prox, drop λ_cost after `lam_cost_drop`), `RampProximalWeight`, `AdaptiveProximalWeight` (PTR-style with fixed virtual-penalty weights).
  - Acceptance-ratio autotuners: `AcceptanceRatioAutotuner` — four-bucket update on λ_prox.
  - Penalty methods: `AugmentedLagrangian(+Hyper/Spec)`, `PenalizedTrustRegionConfig`.
  - All take dict/YAML via their `*Spec` validators → config-driven runs without code changes.
- **Solvers**: CVXPY-backed (`CVXPyPTRSolver` visible in exports).

## Example catalog (examples/spacecraft/) — all read from clone
| File | What it demonstrates |
|---|---|
| `hohmann_transfer.py` | impulsive Δv at 2 nodes, scalar cost state = Σ‖dv‖, fixed half-period; analytic Weber comparison in `__main__` (LEO→GEO) |
| `let_transfer.py` | Sun–Earth CR3BP low-energy transfer |
| `halo_orbit.py` | halo orbit insertion/loitering |
| `proxops_cw.py`, `dual_deputy_inspection_cw.py` | proximity operations, CW-frame deputy inspection |
| `relative_loitering.py` | relative loitering around a target |
| `capstone/` | Capstone-style mission (multi-phase) |

## Gotchas
- **Reality check on the economicspace audit (verified 2026-09-07):** `research/starred-repos/SECOND-PASS.md` in that repo claims "OpenSCvx still has no orbital transfer example; the examples are robot arms, aircraft and abstract control." That is **wrong against live main**: `examples/spacecraft/` exists upstream (added 2026-08-22, commit f2ea6fc "Expand the example suite for the arXiv release") with hohmann_transfer.py, let_transfer.py, halo_orbit.py + proxops/inspection examples — confirmed via GitHub API contents listing AND our clone. The audit likely read a stale checkout or an older tag. Lesson (the repo's own rule): re-read before trusting a rejection; here the *rejection* was wrong in the other direction — capability exists that the audit said didn't.
- **Initial guess must avoid r≈0** — the two-body dynamics are singular at the origin; the example builds an arc that never crosses it. A bad guess = solver divergence, not an error message.
- `cost.final = [("minimize", bound)]` is the idiom for "free final value, minimize it" — a plain number pins it instead.
- Epsilon inside norms (`dv + 1e-6`) is load-bearing: JAX autodiff of `Norm(0)` produces NaN gradients that kill the linearization silently.
- Windows note: not pip-run in this environment (JAX+CVXPY install weight). Before shipping a maneuver design, run it once and diff against the analytic numbers printed by each example's `__main__` block — they're built-in oracles.
