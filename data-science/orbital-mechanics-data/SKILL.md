---
name: orbital-mechanics-data
description: "Orbital mechanics: delta-v, transfers, rendezvous, KSP/KRPC."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [orbital-mechanics, delta-v, Hohmann-transfer, rendezvous, KSP, KRPC, patched-conics, vis-viva]
    category: data-science
    related_skills: [python-data-science, python-craft]
---

# Orbital Mechanics for Data and ML

Practical orbital mechanics for data-driven and ML projects — the equations, patterns, and common mistakes that show up when you're computing trajectories, delta-v budgets, transfer windows, or interfacing with a simulator (KSP/KRPC, custom orbit sim). Focus on what you actually compute, not orbital mechanics as a physics course.

## When to Use

- Computing delta-v budgets for transfers (Hohmann, bi-elliptic, patched conics)
- Computing rendezvous / intercept trajectories (phase angles, lead angles, timing)
- Interfacing with Kerbal Space Program via KRPC (reading orbit data, issuing burns, simulating)
- Building a trajectory optimizer or launcher for an ML project (feature engineering from orbital state, reward shaping for a control policy)
- Working with orbital elements, state vectors, or patched-conic approximations

**Don't use** for high-precision astrodynamics (numerical integration of the full N-body problem, perturbations, numerical propagator fidelity). This is the analyst/engineer approximation layer — patched conics, two-body, Keplerian — which is what most game/sim/ML projects actually use.

## Two-Body Keplerian Motion

The baseline: a small body orbiting a much larger one, no perturbations, point masses. Good enough for most game/sim work.

### Vis-viva equation

The core equation. Relates speed, orbital radius, and semi-major axis:

```
v² = μ (2/r − 1/a)
```

- `v` — speed at distance `r` from the central body
- `μ` — gravitational parameter (G · M, in m³/s² or km³/s²)
- `r` — current distance from the central body
- `a` — semi-major axis (positive for elliptical, negative for hyperbolic)

Use it to compute the speed at any point in a Keplerian orbit. For a circular orbit, `r = a`, so `v = sqrt(μ/r)`.

### Circular orbit velocity

```
v_circ = sqrt(μ / r)
```

The speed of a circular orbit at radius `r`. Baseline for "how fast am I going" and "how much to change orbit."

### Escape velocity

```
v_esc = sqrt(2μ / r) = sqrt(2) · v_circ
```

Speed needed to escape (reach infinity with zero residual velocity). A burn that reaches `v_esc` puts you on a parabolic trajectory.

### Specific orbital energy

```
ε = v²/2 − μ/r = −μ/(2a)
```

Negative for bound (elliptical) orbits, zero for parabolic, positive for hyperbolic. Conserved in two-body motion. Useful for checking whether a burn achieved the intended orbit.

### Orbital period

```
T = 2π · sqrt(a³/μ)
```

Period of a Keplerian orbit with semi-major axis `a`. For circular, `a = r`.

## Orbital Elements

The standard way to describe an orbit. From the six classical elements, you can compute position and velocity at any time (Kepler's equation, then transform to the reference frame).

| Element | Meaning |
|---|---|
| `a` | Semi-major axis — size of the orbit |
| `e` | Eccentricity — shape (0 = circular, 0<e<1 = elliptical, e=1 = parabolic, e>1 = hyperbolic) |
| `i` | Inclination — tilt of the orbit plane relative to a reference plane |
| `Ω` | Longitude of ascending node — where the orbit crosses the reference plane going up |
| `ω` | Argument of periapsis — angle from ascending node to periapsis, in the orbit plane |
| `ν` (true anomaly) | Position along the orbit, measured from periapsis |

### State vector → orbital elements (two-body)

Given position `r` and velocity `v` relative to the central body:

1. Specific angular momentum: `h = r × v`
2. Node vector: `n = K × h` (K is the reference Z axis, usually the central body's rotation axis)
3. Eccentricity vector: `e = (v × h)/μ − r̂` (points toward periapsis; magnitude = eccentricity)
4. `a` from vis-viva: `a = 1 / (2/r − v²/μ)`
5. `i = arccos(h_z / |h|)`
6. `Ω = arccos(n_x / |n|)` (quadrant from `n_y`)
7. `ω = arccos((n·e)/(|n||e|))` (quadrant from `n·e` sign and `e_z` sign)
8. `ν = arccos((e·r)/(|e||r|))` (quadrant from `r·v` sign)

Implementation needs care with quadrants — use `atan2`, not `acos` alone, for angles that can be in either half-plane.

### Orbital elements → state vector

1. Perifocal frame position/velocity (in the orbit plane, periapsis along P):
   - `r_peri = a(cos E − e) P + a√(1−e²) sin E Q`  (E = eccentric anomaly)
   - `v_peri = (−√(μ/a) sin E / √(1−e²)) P + (√(μ/a) cos E / √(1−e²)) Q`
2. Solve Kepler's equation `M = E − e sin E` for E given mean anomaly M (Newton's method or direct iteration).
3. Rotate from perifocal to the reference frame using the 3-1-3 rotation sequence (Ω, i, ω+ν).

For circular orbits (e=0), E = M = ν, and the perifocal frame degenerates (P/Q direction is undefined — pick any orthonormal basis in the orbit plane).

## Hohmann Transfer

The classic two-impulse transfer between two circular, coplanar orbits.

### Transfer orbit

An ellipse with periapsis at the inner orbit radius `r₁` and apoapsis at the outer orbit radius `r₂`:

```
a_trans = (r₁ + r₂) / 2
```

### Delta-v

```
v₁ = sqrt(μ/r₁)                              # initial circular speed
v_trans_peri = sqrt(μ · (2/r₁ − 1/a_trans))  # speed at periapsis of transfer
Δv₁ = v_trans_peri − v₁                       # burn to enter transfer (prograde at inner)

v₂ = sqrt(μ/r₂)                              # target circular speed
v_trans_apo = sqrt(μ · (2/r₂ − 1/a_trans))   # speed at apoapsis of transfer
Δv₂ = v₂ − v_trans_apo                        # burn to circularize (prograde at outer)

Δv_total = Δv₁ + Δv₂
```

For a transfer from outer to inner, reverse the burns (retrograde at outer, retrograde at inner).

### Transfer time

Half the period of the transfer orbit:

```
t_trans = π · sqrt(a_trans³ / μ)
```

The Hohmann transfer takes you from one circular orbit to another in `t_trans`, with two burns.

### When Hohmann is optimal

For two circular, coplanar orbits, Hohmann is the minimum-delta-v two-impulse transfer when the ratio `r₂/r₁` is below ~11.94. Above that, a bi-elliptic transfer (three burns, with an intermediate high apoapsis) can be cheaper.

## Bi-Elliptic Transfer

Three burns: raise apoapsis to a high intermediate radius `r_b`, circularize at the target, then (optionally) lower the intermediate. Useful when `r₂/r₁` is large.

```
a₁ = (r₁ + r_b)/2
a₂ = (r₂ + r_b)/2

Δv₁ = |sqrt(μ(2/r₁ − 1/a₁)) − sqrt(μ/r₁)|     # raise apoapsis
Δv₂ = |sqrt(μ(2/r_b − 1/a₂)) − sqrt(μ(2/r_b − 1/a₁))|  # at apoapsis, adjust to target
Δv₃ = |sqrt(μ/r₂) − sqrt(μ(2/r₂ − 1/a₂))|     # circularize at target
```

The benefit over Hohmann grows with `r_b` up to a point; very large `r_b` takes a long time and the advantage vanishes.

## Plane Changes

Changing inclination costs delta-v. The cost of a pure plane change (same speed, new direction) is:

```
Δv = 2v · sin(Δi/2)
```

where `v` is the current speed and `Δi` is the inclination change.

- Small plane changes are cheap; large ones are expensive (scaling with speed).
- Plane changes are cheapest at low speed (high altitude, slow orbit) — do them at apoapsis if possible.
- Combine plane changes with other burns where possible (burn at the node, combine with a transfer burn) — a pure plane change is almost never the best way to change inclination.

## Rendezvous and Intercept

Getting from "in a similar orbit" to "at the same point at the same time."

### Phasing — changing the orbital period to catch up or wait

If you're ahead of the target, raise your orbit (longer period, you slow relative to target). If you're behind, lower your orbit (shorter period, you catch up). The classic phasing orbit is a small elliptical adjustment that changes your period by a modest amount.

Phase angle `θ` = angle from you to the target (in the direction of motion). To close a phase angle `θ` in time `t`, you need a period change that makes you gain/lose `θ` radians over `t`.

For a small phase change via a phasing orbit:
- Compute the required period difference `ΔT` to close the phase gap in the available time.
- `Δv` for the phasing orbit is small (it's a small tweak to a near-circular orbit) — but it takes time.
- The trade-off: fast rendezvous costs more delta-v; cheap rendezvous takes more orbits.

### Launch windows and phase angles

For an interplanetary or intercept transfer, you need the target to be at the right place when you arrive. The phase angle at departure is:

```
θ_launch = (target angular rate − transfer angular rate) · transfer_time   (mod 2π)
```

Wait for the target to reach that angle before launching. For circular coplanar orbits, this is the "wait for the phase angle" launch window.

### Intercept cost

The cost to match up with a target in a different orbit is:
- Transfer delta-v (get to the target's orbit).
- Phasing/rendezvous delta-v (get to the target's position at the right time).
- Capture/insertion delta-v (match the target's velocity, if needed).

The rendezvous cost is often dominated by phasing if the orbits are close; by the transfer if they're far apart.

## Patched Conics

For multi-body trajectories (e.g., Earth → Moon, or interplanetary), patched conics approximate by:
1. In the sphere of influence (SOI) of body A, treat body A as the only gravitating body (two-body with A).
2. At the SOI boundary, patch to the two-body motion around body B.
3. The velocity relative to B at the patch point is the incoming velocity (relative to A) transformed to B's frame, plus B's own motion.

This is an approximation (ignores the third body's gravity inside the SOI, assumes instantaneous patch), but it's the workhorse for game/sim interplanetary work and is what KSP uses.

### Sphere of influence radius

```
r_SOI ≈ a · (m / M)^(2/5)
```

where `a` is the semi-major axis of the smaller body's orbit around the larger, `m` is the smaller body's mass, `M` is the larger. This is the Laplace sphere of influence approximation.

## Kerbal Space Program / KRPC

KRPC is a mod that exposes a programmable interface to KSP via a gRPC server. You can read orbital state, control the vessel, issue burns, and watch the simulation from outside.

### What KRPC gives you

- Vessel state: position, velocity, orbit (body, Keplerian elements, SOI), altitude, speed, heading, etc.
- Orbit predictions: future position, closest approach, intercept data.
- Control: throttle, steering, RCS, wheels, brakes, staging.
- Simulation time: current time, UT, orbital periods, transfer windows.

### Common patterns

- **Read the orbit, compute the burn**: read `vessel.orbit`, compute the required Δv for a transfer or maneuver, issue the burn at the right time.
- **Maneuver nodes**: KSP's maneuver node API gives you the planned burn (Δv vector, time, resultant orbit). Use it to plan transfers, then execute.
- **Timing burns**: burns should be timed to the orbital position where they're effective (prograde at periapsis for raising apoapsis, retrograde at apoapsis for lowering periapsis, etc.). A burn at the wrong time wastes Δv.
- **Reading encounter data**: `vessel.orbit.next_approaching_body` or closest approach data gives you target body, time to encounter, and relative velocity. Use this for rendezvous planning.

### Common KRPC mistakes

- Reading state at the wrong time (e.g., reading altitude before the vessel has an orbit established).
- Assuming the orbit is Keplerian when it's not (inside an atmosphere, or in a patched-conic transition region).
- Issuing control commands faster than the simulation can process (throttle the commands, wait for acknowledgment).
- Not accounting for the vessel's rotation/orientation when interpreting "up" or "prograde" — use the vessel's own reference frame, not the world frame, for control.

## Feature Engineering from Orbital State

For ML projects that use orbital state as input (e.g., a KSP control policy), common features:

- **State vector**: position, velocity in a consistent reference frame (body-centered inertial, or orbital frame).
- **Orbital elements**: a, e, i, Ω, ω, ν — compact description of the orbit.
- **Relative state to target**: position, velocity relative to the target body or vessel.
- **Phase angles**: angle to target, angle to the next maneuver node, angle to periapsis/apoapsis.
- **Time to event**: time to periapsis, time to apoapsis, time to encounter, time to maneuver node.
- **Delta-v to target**: computed transfer cost (Hohmann, patched conic) to the target orbit/body.
- **Energy / angular momentum**: specific orbital energy, specific angular momentum — invariants that summarize the orbit.

Watch for:
- **Circular orbit degeneracy**: for e=0, ω and the perifocal frame direction are undefined. Don't use ω as a feature for circular orbits without handling the degeneracy (e.g., use argument of latitude `u = ω + ν` instead, or the true longitude).
- **Reference frame consistency**: position/velocity in one frame, angular momentum in another — make sure everything is in the same frame before computing derived features.
- **Angles wrap**: true anomaly, phase angle, heading — all wrap at 2π. Use sin/cos of the angle as features, or a wrapped representation, to avoid the discontinuity at the wrap.

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Using vis-viva with wrong `a` (sign or value) | Wrong speed, wrong delta-v | Check `a` sign: positive for elliptical, negative for hyperbolic; recompute from state if unsure |
| Plane change at high speed | Large, unexpected delta-v | Move plane change to low-speed point (apoapsis); combine with other burns |
| Phase angle ignored in transfer | Miss the target, arrive at empty orbit | Compute phase angle at departure; wait for the right launch window |
| Treating KSP orbits as full N-body | Discrepancies between prediction and reality | KSP uses patched conics + simplifications; treat predictions as approximate |
| Angle wrap in features | Discontinuity at 0/2π breaks ML model | Use sin/cos, or wrap features consistently |
| Reference frame mismatch | Derived features nonsense (angular momentum wrong sign, etc.) | Keep everything in one consistent frame; document which frame |
| Circular orbit ω/Ω degeneracy | Undefined or noisy features for circular orbits | Use argument of latitude or true longitude; handle e≈0 specially |
| Burns at wrong orbital position | Waste Δv, wrong orbit achieved | Burn prograde at periapsis to raise apoapsis; retrograde at apoapsis to lower periapsis; align burn with the desired effect |
| SOI patch assumed more precise than it is | Intercept prediction off | Patched conics are approximate; add margin to intercept plans |

## Orbit Simulation for ML Training

When you're building a custom orbit simulator as the environment for an ML agent (KSP_pipeline's `orbit_sim.py` pattern) — the simulation needs to be fast, deterministic, and correct enough to train on.

**Simulation choices for ML:**
- **Patch conics, not N-body:** for ML training, the simulation should be fast and deterministic. Full N-body integration is expensive and non-deterministic in practice (floating-point sensitivity). Patched conics (two-body within each SOI, patch at the boundary) is the standard approximation and what KSP itself uses.
- **Fixed time step:** a fixed-step integrator is deterministic given the same seed. Variable-step integrators are more accurate but harder to make deterministic. For ML, determinism matters more than high precision — you want the same seed to produce the same trajectory.
- **Two-body inside each SOI:** within a body's sphere of influence, the orbit is a two-body Keplerian orbit around that body. This is fast to compute (closed-form position/velocity from orbital elements) and deterministic.
- **Patch at SOI boundaries:** when the vessel leaves one body's SOI and enters another's, patch the state. The velocity relative to the new body is the incoming velocity (relative to the old body) transformed to the new body's frame, plus the new body's own motion.

**What the sim needs to provide for ML:**
- **State:** position, velocity (in a consistent frame), which body's SOI the vessel is in, orbital elements relative to the current body.
- **Controls:** thrust direction, thrust magnitude (or throttle), RCS, staging — whatever the agent can command.
- **Step:** advance the simulation by one time step given the current state and controls. Return the new state, any events (SOI transition, encounter, etc.), and whether the step was valid.
- **Determinism:** same seed, same initial state, same control sequence → same trajectory. This is essential for reproducibility and for shared random numbers in evolution.

**Feasibility checks the sim should support (KSP_pipeline's `checks.py` pattern):**
- Is the current state feasible? (in orbit, not crashed, not out of fuel, etc.)
- Is a proposed maneuver feasible? (enough fuel, thrust direction valid, not inside a body, etc.)
- Pre-checks before the agent acts — filter out obviously infeasible actions so the agent doesn't waste evaluation on them.

**Common sim defects for ML:**
- Non-determinism (floating-point order, variable-step integrator, thread scheduling) — same seed gives different trajectories, fitness is irreproducible.
- Incorrect patching at SOI boundaries — trajectory is wrong after the first SOI transition, and the error compounds.
- Units inconsistency (km vs m, seconds vs game-time units) — the sim produces numbers in the wrong units, and the agent learns the wrong thing.
- Missing events (SOI transitions, encounters, crashes) — the sim doesn't tell the agent when something important happened, and the agent can't learn from it.
- Drift (energy not conserved, orbit degrades over time) — the sim is wrong in a way that's hard to see from individual steps but visible over many steps.

**Verification:**
- Compare the sim's trajectories to a trusted reference (KSP itself, a high-precision integrator, or closed-form two-body solutions) for a set of test cases.
- Check invariants (energy conservation in two-body regions, correct SOI patching) over long trajectories.
- Check determinism (same seed → same trajectory) across multiple runs.

## Feature Engineering for KSP Neuroevolution

The KSP_pipeline pattern: evolve neural networks that control a spacecraft in orbit. The features the network sees determine what it can learn.

**State features:**
- Position and velocity relative to the current body (in a consistent frame — typically body-centered, in orbital or local frame).
- Orbital elements (a, e, i, Ω, ω, ν) — compact description of the orbit, useful for high-level decisions.
- Altitude, speed, heading — intuitive low-level features.
- Which body is the current primary, which SOI the vessel is in.

**Target features (when rendezvousing with or transferring to something):**
- Relative position and velocity to the target (body, vessel, orbit).
- Phase angle to the target (angle in the direction of motion).
- Time to periapsis, time to apoapsis, time to encounter.
- Delta-v to target (computed transfer cost) — a high-level feature that tells the agent how much it needs.

**Control features:**
- Current throttle, current thrust direction (or the agent's last commanded direction).
- Fuel remaining, stage state — resources the agent needs to manage.
- Time to next event (periapsis, apoapsis, SOI boundary) — timing information.

**Features to be careful with:**
- **Circular orbit degeneracy:** for e≈0, ω and the perifocal frame are undefined. Don't feed ω directly to the network for near-circular orbits — use argument of latitude (u = ω + ν) or true longitude instead, or handle e≈0 specially.
- **Angle wrap:** true anomaly, phase angle, heading — all wrap at 2π. Use sin/cos of the angle as features (two features that don't wrap) rather than the raw angle (one feature that jumps from 2π to 0).
- **Reference frame:** keep everything in one consistent frame. Position and velocity in body-centered inertial, or in the orbital frame, but not mixed. Angular momentum, cross products, and dot products only make sense in a consistent frame.
- **Scale:** features with very different scales (altitude in km, fuel in kg, time in seconds) can make neural network training harder. Normalize or scale features to a similar range, or let the network learn the scaling (but give it a chance).

**Reward shaping for KSP:**
- The reward should reflect what you want the agent to do (reach orbit, rendezvous, minimize fuel, etc.).
- Sparse rewards (success/failure only) are simple but slow to learn from — the agent gets no signal until it succeeds or fails.
- Dense rewards (reward for progress toward the goal — getting closer to the target orbit, reducing the phase angle, etc.) give the agent more signal but can be gamed (the agent optimizes the reward, not the goal, if the reward is misspecified).
- A common pattern: sparse reward for the actual goal + dense reward for progress that's aligned with the goal (and can't be gamed without also making progress).

## KRPC Read/Write Patterns

KRPC exposes KSP's state and control over a gRPC connection. The KSP_pipeline pattern for using it.

**Reading state:**
- Connect to the KRPC server (KSP must be running with KRPC installed and the server started).
- Read `vessel.position`, `vessel.velocity`, `vessel.orbit` (body, apoapsis, periapsis, inclination, eccentricity, semi-major axis, etc.), `vessel.surface_altitude`, `vessel.flight()` (dynamic data: speed, heading, vertical speed, etc.).
- Read the current vessel, the current body, the list of bodies, the simulation time.
- Read maneuver nodes (`vessel.control.desired_heading`, `vessel.auto_pilot` state, etc.) if the agent is using them.

**Writing control:**
- Set `vessel.control.throttle`, `vessel.control.gear`, `vessel.control.rcs`, `vessel.control.staging`.
- Set the throttle direction: `vessel.control.throttle = 1.0` for full thrust, `0.0` for none. Direction is set via the vessel's orientation (`vessel.auto_pilot.reference_frame`, `vessel.auto_pilot.target_direction`, or direct control).
- Use `vessel.auto_pilot` for controlled burns (engage, target a direction, disengage) — this is higher-level than raw throttle and direction.
- Stage: `vessel.control.activate_next_stage()` to fire the next stage (separation, engine ignition, etc.).

**Timing and throttling:**
- Don't issue control commands faster than KSP can process them. Throttle the commands — wait for acknowledgment, or issue at a fixed rate.
- Read state at a stable rate (don't read inside a tight loop without a sleep — you'll swamp the connection).
- A common pattern: read state, compute the desired action, issue the action, sleep for the time step, repeat. The sleep rate is the control frequency.

**Maneuver nodes:**
- KSP's maneuver node system gives you a planned burn: the Δv vector, the time to the node, the resultant orbit.
- Read maneuver nodes from `vessel.control.nodes`.
- Use them to plan transfers (read the node's Δv, time it, execute the burn at the right time).
- The agent can use maneuver nodes as a high-level interface (plan a transfer with a node, then execute it) or ignore them and control directly.

**Common KRPC mistakes:**
- Connecting to the server before KSP is ready (server not started yet) — connection fails.
- Reading state before the vessel has an orbit (on the launch pad, in the atmosphere) — orbit data is invalid or absent.
- Assuming the orbit is Keplerian when it's not (in the atmosphere, in a gravity turn, near a SOI boundary) — orbital elements are approximate or undefined.
- Issuing commands without checking feasibility (throttle when there's no engine, stage when there's nothing to stage) — KSP handles it, but the agent learns inefficiently.
- Not accounting for the vessel's orientation when interpreting directions — "prograde" in the vessel's frame vs. the world frame are different. Use the right reference frame for the control.

## Patched Conics in Practice

The patched-conic approximation in detail — what it gives you, where it breaks.

**The approximation:**
- Within a body's SOI, the vessel orbits that body in a two-body Keplerian orbit (the body is the central mass, the vessel is the satellite, no other bodies matter).
- At the SOI boundary, the vessel's orbit patches to the next body's two-body orbit.
- The patch: the velocity relative to the new body = the velocity relative to the old body (at the patch point) transformed to the new body's frame + the new body's velocity relative to the old body.

**What it gets right:**
- Interplanetary transfers (Earth → Mars, etc.) — the spacecraft spends most of its time in heliocentric space, with brief patches at Earth's and Mars's SOIs. The approximation is good.
- Moon transfers (Earth → Moon) — the same pattern, smaller scale.
- Most KSP gameplay — KSP uses patched conics, so a patched-conic sim matches the game.

**What it misses:**
- The gravity of other bodies inside the SOI (the Moon's gravity affects things inside Earth's SOI, if you're close to the Moon). This is the third-body problem, and patched conics ignores it.
- The transition region near the SOI boundary — the patch is instantaneous, but in reality the transition is gradual.
- Perturbations (non-spherical bodies, atmospheric drag, solar radiation pressure) — patched conics assumes point masses and no perturbations.
- N-body effects (Lagrange points, complex multi-body dynamics) — patched conics can't represent these.

**When patched conics is good enough:**
- Most interplanetary and cislunar transfers (the economicspace and KSP use cases).
- When you need speed and determinism (ML training, large-scale prospecting).
- When the bodies are far apart relative to their SOIs (the approximation is better when the SOIs don't overlap much).

**When you need more:**
- When third-body effects matter (operating near the Moon's SOI boundary while Earth is close, Lagrange-point navigation).
- When high precision is required (real mission design, not game/sim).
- When the bodies are close enough that their SOIs overlap or the transition matters (some moons of giant planets, close binaries).

**The economicspace use case:**
- Cislunar prospecting: which asteroids or lunar positions are profitable to reach from Earth, given delta-v costs, mineral content, and transport economics.
- Patched conics is the right approximation: the transfer is Earth SOI → heliocentric/translunar → target SOI, with patches at the boundaries. The delta-v cost is computed from the patched-conic transfer.
- The prospecting model adds economics on top of the orbital mechanics: mineral prices, transport costs, demand, accessibility. The orbital mechanics gives the delta-v; the economics gives the profit.

## Economic Prospecting with Orbital Mechanics

The economicspace pattern: use orbital mechanics to compute the delta-v cost of reaching asteroids and lunar positions, then layer economics (mineral prices, demand, transport costs) to compute profitability.

**The prospecting workflow:**
1. ** enumerate targets:** asteroids (by orbit class — NEO, Main Belt, etc.), lunar positions (poles, peaks of eternal light, etc.), and other cislunar locations.
2. **Compute delta-v to each target:** from Earth (or from a lunar base, or from a staging point), using patched conics. The delta-v is the cost to reach the target and (optionally) return.
3. **Assess accessibility:** how hard is the target to reach? (delta-v, launch window frequency, rendezvous complexity, stay time if it's a fast-rotating body, etc.)
4. **Assess resource content:** what minerals are there, in what concentration, how much total, how hard to extract.
5. **Compute transport economics:** cost to get the material back to market (delta-v, transit time, infrastructure needed).
6. **Compute profitability:** resource value minus delta-v cost minus transport cost minus extraction cost. Rank targets by profitability.

**Delta-v as the core orbital mechanics input:**
- The delta-v to reach a target determines the transportation cost (fuel, staging, time).
- The delta-v to return determines whether the target is worth it (you need to get the material back to market).
- Delta-v budgets are computed from patched conics (Hohmann transfers, rendezvous, plane changes, capture).
- A target with low delta-v from Earth and high mineral value is high-profitability. A target with high delta-v and low value is not.

**The economics layer:**
- Mineral prices (market price per unit mass of each mineral — platinum group metals, titanium, helium-3, water, etc.).
- Demand (is there a market for this mineral, and how much?).
- Extraction cost (how hard is it to get the mineral out of the target — concentration, processing, equipment).
- Transport cost (delta-v to return, transit time, infrastructure).
- Infrastructure requirements (do you need a base, a refinery, a depot — and what does that cost?).

**Prospecting as a data pipeline:**
- The prospecting computation produces a catalog: targets, their orbital parameters, delta-v costs, resource estimates, economic assessment, profitability ranking.
- This is a data pipeline (enumerate → compute → assess → rank) that produces a data artifact (the catalog, typically a CSV or similar).
- The pipeline can be re-run when inputs change (new mineral prices, new targets discovered, new orbital data).

**Verification:**
- Check delta-v computations against known references (Hohmann transfer costs for Earth-Moon, Earth-Mars, etc.).
- Check that the delta-v is consistent across the catalog (same target, same starting point → same delta-v; same target from different starting points → plausible differences).
- Check the economics for sanity (a target that's profitable only because its delta-v is negative, or because its resource content is absurdly high, is a bug).

## Verification Checklist

Before trusting an orbital computation:

- [ ] Vis-viva uses the correct `a` and `μ` (right body, right units)
- [ ] Delta-v burns are applied at the right orbital position (periapsis/apoapsis/node as intended)
- [ ] Plane changes are timed to low speed or combined with other burns
- [ ] Phase angle is accounted for in rendezvous/intercept planning
- [ ] State vectors and orbital elements are in a consistent reference frame
- [ ] Circular orbit degeneracy handled (ω, perifocal frame)
- [ ] Angles wrapped consistently (sin/cos features, or wrapped representation)
- [ ] For KRPC: orbit data read at a stable time, control commands throttled, maneuver nodes used for planning
- [ ] Patched-conic interplanetary estimates treated as approximate (not high-precision)
- [ ] Units consistent throughout (km vs m, s vs sec, km³/s² vs m³/s² for μ)
