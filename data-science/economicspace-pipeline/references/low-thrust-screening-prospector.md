---
description: "How Karmanplus/prospector screens asteroids for low-thrust reachability: tiered solvers, errors-must-point-low rule, Edelbaum + intercept bracket (formula run live), validation vs Dawn/Psyche/Hayabusa2/DART, pixi/conda-forge install"
source_repo: Karmanplus/prospector (Apache-2.0)
tested_version: README, docs/physics.md and docs/validation.md read via GitHub API @ main; Edelbaum/Hohmann formulas re-implemented and run locally; conda-forge platform lists queried from the anaconda.org API; prospector itself NOT installed or run (needs pixi)
verified_date: "2026-10-05"
---

# Low-thrust target screening (prospector's method)

Prospector (Apache-2.0, ~10 stars, Python + NiceGUI desktop app) answers: *which asteroids can a low-thrust spacecraft reach, and which are worth reaching?*
It is the same problem the economicspace pipeline prices with closed-form delta-v, so its structure is a useful design reference and external cross-check target.

## Design rule worth copying: which way the errors must point

- **Screening estimates undercharge delta-v on purpose.** The expensive mistake is discarding a reachable target, so every screen-stage number (Edelbaum element cost, escape estimate, impulsive Lambert cost) errs low. Screens **rank and bound; they never cull.** A more accurate stage decides.
- Past the screen the bias reverses: worst-case radiation for the Earth escape spiral, thrust derated by the operator duty cycle, ordinary optimisations for the date grid and the trajectory solve.
- Reading rule: **a screen number is a floor; a converged number is an estimate.** Where a quantity has an optimistic and a pessimistic form, the screen uses the optimistic and the pessimistic one gives diagnostics and the far end of the range.

## Tiers, cheapest first (each runs only on what survives the previous one)

| Tier | What it accounts for | Cost |
|---|---|---|
| `edelbaum` | orbital elements only, no dates; whole catalogue vectorised in NumPy | seconds for the population |
| `lambert` | real dates and positions, impulsive burns; only ever a **seed**, its delta-v is never displayed or ranked | one transfer, instant |
| `simsflanagan` | the real low-thrust solve (PyKEP 3's Sims-Flanagan leg, with its own derivatives) | seconds per solve |
| transfer grid | that solve sampled over departure date x flight time (8x8 grid about 9 s) | the surface the app draws |
| `spiral` / launch | the Earth escape flown properly; prices the departure speed the cruise treats as free | |

Escape and cruise are planned together because they trade against each other, and a mission may fly by a planet with the two legs solved as one.
Planets are in the target population too (Mars is reachable "like any other"; arriving means matching its orbit, not capture).

## The element screen (formula run locally)

Two closed-form strategies bracket the true optimum and the screen takes the **minimum**:

- `spiral_dv`: continuous-thrust arc changing size and plane together (Edelbaum) plus a first-order eccentricity term, RSS-combined; a conservative ceiling a low-thrust vehicle can essentially fly.
- `intercept_dv`: ballistic Hohmann out to the cheapest meeting point (perihelion, aphelion or the 1 AU crossing), then one match burn with the plane change riding on it at the slow local speed; impulsive, so an optimistic floor. It exists to rescue eccentric, Earth-approaching orbits the spiral over-charges.

```text
edelbaum_dv = sqrt(v0^2 + vf^2 - 2 v0 vf cos(pi/2 * di))       v = sqrt(mu/a) circular speed, di in radians
eccentricity_dv ~ v_c(af) * |de|                                  leading-order approximation
```

The `pi/2` factor is the signature of a continuous plane change: spreading a tilt around the orbit costs about 1.57x more than one optimally placed burn.

Numbers from re-implementing the formula (mu_sun = 1.32712440041279e11 km^3/s^2, AU = 149597870.7 km; Earth treated as a circular 1 AU orbit with v = 29.785 km/s):

| Target (a AU, i deg) | Edelbaum (circular-to-circular + plane) | `abs(v0 - vf)` (no plane change) | Planar Hohmann (impulsive) |
|---|---|---|---|
| Ceres-like (2.77, 10.6) | 13.640 km/s | 11.889 | 11.182 |
| Vesta-like (2.36, 7.1) | 11.397 | 10.397 | 9.947 |
| Mars-like (1.524, 1.85) | 5.819 | 5.658 | 5.596 |
| Bennu-like (1.126, 6.03) | 5.073 | 1.716 | 1.714 |

Checks that passed: with `di = 0` the formula equals `abs(v0 - vf)` exactly; a pure 10 degree plane change at 1 AU costs 8.140 km/s by Edelbaum vs 5.192 km/s for a single burn (ratio 1.568, close to pi/2).
Takeaway for a near-Earth target such as Bennu: the 6 degree inclination, not the 0.13 AU of altitude change, dominates the low-thrust cost (5.07 vs 1.71 km/s).
These are circular-orbit simplifications (no eccentricity term, no real dates), meant as floors; prospector's own intercept term can come in lower for eccentric orbits.

## Validation against flown solar-electric missions (their `docs/validation.md`)

Run as the app runs it (transfer grid over the launch window, then cruise from the best cells), real engines/masses/dates:

| Mission | Flyby, flown vs tool | Propellant, flown vs tool | Direct (no flyby) from same cell |
|---|---|---|---|
| Dawn (Mars to Vesta, 2007) | 17 Feb 2009, 542 km vs 13 Feb 2009, 500 km | 247 kg vs 224 kg | 307 kg (flyby saves 83 kg) |
| Psyche (Mars flyby, 2023) | 15 May 2026 vs 19 May 2026 (higher, gentler turn) | 1,085 kg load (cruise + 20 months orbit ops) vs 783 kg | 1,240 kg (more than the tank) |
| Hayabusa2 (Earth swing-by) | 3 Dec 2015, 3,090 km vs 30 Nov 2015, 2,531 km | 24 kg vs 22 kg | 33 kg |
| DART (direct impactor) | none | 55 m/s hydrazine vs 5 kg xenon (0.26 km/s) | n/a (engine was a tech demo; only geometry compares) |

The search is never told where the mission flew and still finds the same encounters within days and a few hundred to a thousand km. The tool lands **below** flown propellant where the flown mission had
outages and pointing constraints, and **above** it where the model adds constraints the mission lacked, so the sign is expected. The Psyche result flipped (direct cheaper than any Mars flyby) when an
outdated 2021 design mass (2,608 kg, 922 kg xenon, 280 mN) replaced the flown figures (2,747 kg, 1,085 kg, 240 mN): **vehicle inputs can reverse the conclusion**, so source them from the flown record.
Cost on a 24-core machine: flyby grids 294-378 s vs 110-220 s for direct; only 9 to 49 grid cells closed per mission and only at long flight times.

## Install reality (pixi, conda-forge)

The README insists on **pixi, not pip or uv**: the solvers (PyKEP, PyGMO) are not installable from PyPI on macOS and Windows. Queried from the anaconda.org API on 2026-10-05, conda-forge carries
`pykep` 3.0.0, `pygmo` 2.19.8 and `heyoka` 7.13.0 for `win-64`, `osx-64`, `osx-arm64`, `linux-64`, `linux-aarch64` and `linux-ppc64le`. (This corrects the pykep README's statement that conda-forge only serves the v1 line;
see `astro-toolkit-selection/references/pykep-v3-notes.md`.) Pixi is not installed on this machine; the first launch downloads a few hundred MB plus the JPL small-body catalogue, and optional target characterisation caches about 1.3 GB.

Config-as-YAML (engines, vehicles, missions, studies) lives in an untracked `configs/` directory seeded from `examples/configs`; heavy work runs as detached subprocesses that write a status file the app polls (no threads, no task queue).

## What to take for economicspace

- Adopt the **errors-point-low** discipline for any screening stage in the ranking, and document which direction each term errs.
- Keep a **closed-form floor** (Edelbaum/Hohmann) beside the real solver and treat disagreement in the wrong direction (screen above solve) as a bug.
- Cross-check a few well-known targets against flown missions (the four above) before trusting a vehicle model; mis-sourced vehicle masses can flip a flyby decision.
