---
description: "REBOUND + REBOUNDx N-body notes: install reality on Windows (rebound wheel yes, reboundx sdist-only), units/G gotcha, Yarkovsky and radiation-force parameters, ASSIST pointer"
source_repo: dtamayo/reboundx (GPL-3.0), hannorein/rebound (GPL-3.0), matthewholman/assist (GPL-3.0)
tested_version: rebound 5.2.1 cp314 win_amd64 wheel installed and run (integrator, restart and Horizons tests added in the hannorein/rebound review); reboundx 5.1.0 install attempted and failed (no compiler); reboundx docs read via GitHub API @ main
verified_date: "2026-10-05"
---

# REBOUND / REBOUNDx for small-body dynamics

REBOUND (Rein et al.) is the N-body integrator (WHFast, IAS15, Mercurius, TRACE, ...). REBOUNDx adds extra
physics as forces and operators attached to a running simulation. For asteroid work the relevant effects are
the **Yarkovsky effect**, radiation pressure + Poynting-Robertson drag, general relativity, gravitational harmonics, and
mass modification. All three packages here are **GPL-3.0**: fine for analysis, but linking them into a shipped
closed-source product is a license problem (same class of caveat as nyx's AGPL in `SKILL.md`).

## Install reality (verified on Windows, Python 3.14)

| Package | Result |
|---|---|
| `pip install rebound` (5.2.1) | OK: a prebuilt `cp314-cp314-win_amd64` wheel (449 KB) |
| `pip install reboundx` (5.1.0) | **Fails**: `error: Microsoft Visual C++ 14.0 or greater is required`. No binary wheels exist for it at all: `pip download reboundx --only-binary=:all:` found no distribution for `win_amd64` or `manylinux2014_x86_64`. It is source-only, so every platform needs a C compiler (MSVC Build Tools on Windows, gcc/clang elsewhere) |
| `pip install assist` (1.2.3) | **Cannot be installed here**: PyPI holds only `assist-1.2.3.tar.gz` (61.5 KB sdist, no wheel for any platform), it needs a C compiler (none on PATH), and it pins `rebound<5.0.0,>=4.4.11`, while the REBOUND wheel above is 5.x. REBOUND 4.x Windows wheels stop at cp312 (4.6.0). See the ASSIST section below |

Plan accordingly: on a machine without a compiler, either install the Build Tools / use WSL or Linux, or fall back to
core REBOUND with your own perturbation in a Python or C force callback.

## Core REBOUND, verified

```python
import rebound
sim = rebound.Simulation()
sim.units = ("AU", "yr", "Msun")
sim.add(m=1.0)
sim.add(m=3.0e-6, a=1.0)
sim.add(m=0.0, a=2.7, e=0.08)          # massless test particle
sim.integrator = "whfast"; sim.dt = 0.01
e0 = sim.energy(); sim.integrate(100.0)
```

100 yr WHFast run: relative energy error `4.5e-15`; the test particle stayed at `a = 2.700001`, `e = 0.080000`.

Two gotchas seen in that run:

- **`sim.G` in `("AU","yr","Msun")` is 39.4769264, not 4 pi^2 = 39.4784176** (a 3.8e-5 relative difference), because REBOUND converts
  its own G into the requested unit system. If your reference code uses `G = 4*pi^2` (or the Gaussian gravitational
  constant), periods disagree at the 1e-5 level and a bit-identity comparison fails. Set `sim.G = 4*math.pi**2`
  explicitly when you need that convention (and print `sim.G` in any run you want to reproduce).
- `sim.N_active` printed `18446744073709551615` (the unsigned wrap of -1) when no particle was marked as massless-test only;
  it means "all particles active". Use `sim.N` for the count.

## Integrator choice, restarts and units (REBOUND 5.2.1, run live)

**WHFast needs a small enough fixed step for eccentric orbits; IAS15 adapts.** Sun + Jupiter-like planet + a test particle at a = 1.2 AU, e = 0.9
(perihelion 0.12 AU), 20 yr, compared against IAS15 as reference (the particle is scattered to a = 5.31 AU, e = 0.9766 in that run):

| Integrator | Result vs IAS15 |
|---|---|
| WHFast dt = 0.05 yr | garbage: a = -14.6 AU (unbound), position error 43 AU |
| WHFast dt = 0.01 yr | garbage: a = -91 AU, position error 33 AU |
| WHFast dt = 0.001 yr | da/a = 1.2e-2, position error 0.33 AU |
| WHFast dt = 0.0001 yr | da/a = 1.1e-4, position error 3.5e-3 AU (0.067 s) |
| IAS15 (adaptive; dt settled near 0.36 yr in the earlier quiet case) | reference, about 1 ms here |

For a nearly circular case (e = 0.01) the same WHFast dt = 0.01 gave a position error of only 1.3e-4 AU. Rule: for e above about 0.5 or any close encounter use IAS15
(or MERCURIUS/TRACE for planetary systems with encounters), and for WHFast set dt to a small fraction of the **pericenter** passage time, not of the period.
A diverging or unbound result at large dt is the usual symptom, not a code bug. Energy error alone is not a valid check for a massless test particle (it contributes zero
energy); compare orbital elements or positions against a reference run.

**Time stepping:** `sim.integrate(1.0)` with WHFast dt = 0.07 ended at exactly `t = 1.0` (the last step is shortened); `exact_finish_time=0` ended at `t = 1.05`
(a whole number of steps).

**Restarts are bit-identical (relevant to `bit-identity-float-pipelines`).** `sim.save_to_file(fn)` at t = 5, reload with `rebound.Simulation(fn)`, integrate on to t = 10: the
final positions and velocities were **exactly equal** to an uninterrupted run (IAS15, this machine). `save_to_file(fa, interval=1.0, delete_file=True)` builds a
`Simulationarchive`; snapshots land on step boundaries (times 0, 1.062, 2.164, 3.1, 4.12, 5.0 for interval 1.0), and restarting from snapshot 3 reproduced the final state. Bit-identity is
host-specific: it was shown on one machine, not across CPUs or builds.

**Units:** a fresh `Simulation()` has `units` = all `None` and `G = 1`; `P` for `a = 1` around `m = 1` is `2*pi`. If you never set `sim.units` and read lengths as AU and masses as Msun, times are in
"year/2pi" and a 100 "yr" run is 15.9 real years. `sim.add("Ceres", date="2026-01-01 00:00")` queries NASA Horizons over the network and prints
"Searching NASA Horizons ..." to stdout; it returned a = 2.7609 AU, e = 0.0801, and set the sim's units to `{'length': 'au', 'mass': 'msun', 'time': 'yr2pi'}`. Pin `sim.units`
before adding Horizons bodies and expect network access and stdout noise in pipelines.

## REBOUNDx pattern (source-read, not run)

```python
import rebound, reboundx
sim = rebound.Simulation()                 # set up as usual
rebx = reboundx.Extras(sim)                # attach once
gr = rebx.load_force("gr"); rebx.add_force(gr)
gr.params["c"] = 63241.08                   # speed of light in YOUR sim units (AU/yr: 299792.458 km/s * 31557600 s / 149597870.7 km)
mm = rebx.load_operator("modify_mass"); rebx.add_operator(mm)
sim.particles[0].params["tau_mass"] = -1000 # per-particle parameters work like a dict
```

Effects are **forces** (add acceleration) or **operators** (modify state between steps). Every effect documents its
effect parameters, particle parameters and an example notebook on the docs `effects` page. Parameters are in simulation
units; passing `c` in the wrong unit system is the usual silent error.

### `yarkovsky_effect` (asteroids)

Two variants selected per particle by `ye_flag`: `0` = full thermal model, `1` = simple outward drift, `-1` = simple inward drift.

| Scope | Parameter | Needed for |
|---|---|---|
| effect | `ye_lstar` (stellar luminosity), `ye_c` (light speed) | both; `ye_stef_boltz` for full |
| particle | `particles[i].r` (physical radius), `ye_body_density`, `ye_albedo`, `ye_flag` | both |
| particle | `ye_rotation_period`, `ye_emissivity`, `ye_thermal_inertia`, `ye_k` (0 to 1/4), `ye_spin_axis_x/y/z` | full only |

Based on Veras et al. 2015 and 2019; the implementation paper is listed as "in prep." in the docs, so cite the
Veras papers plus Tamayo et al. 2020 (MNRAS 491, 2885) for REBOUNDx itself. The semi-major-axis drift rate from this
effect is exactly the quantity an asteroid-family age or transport study (for example a belt-gradient analysis) needs
to model, rather than assume.

### `radiation_forces`

Radiation pressure plus Poynting-Robertson drag (Burns et al. 1979). Only particles with `beta` set (radiation to
gravity force ratio) feel it; effect parameter `c`; the source is particle 0 unless one has `radiation_source` set.

## Related

`matthewholman/assist` (ASSIST, "ephemeris-quality integrations of test particles", built on REBOUND; source-read, see the next section)
is the tool when an asteroid's position must match Horizons; REBOUND/REBOUNDx are for idealised or population dynamics. Cross-check against `nyx` / `brahe`
(`optimization-toolkit.md`, `brahe-api-reference.md`).

## ASSIST (matthewholman/assist 1.2.3, source-read, not run)

GPL-3.0, 47 stars, last push 2026-06-21. Read from the repo (`assist/*.py`, `docs/forces.md`, README) and PyPI metadata plus HTTP
HEAD requests on the JPL files; **nothing below was executed**, because it cannot be installed on this machine (row above).
To run it you would need Python <= 3.12 (REBOUND 4.x wheel), a C compiler for the sdist, and the data files.

What it is: REBOUND's IAS15 integrator with the force field of an ephemeris-grade small-body integrator: Sun, Moon, planets and
16 massive asteroids positioned from JPL DE440/441, Earth J2-J5 and Sun J2 harmonics, Einstein-Infeld-Hoffmann GR, and the
Marsden (1973) non-gravitational model; first-order variational equations are included for orbit fitting. Use it when a
test particle must match JPL Horizons; plain REBOUND is for idealised or population dynamics.

Data (sizes from `Content-Length`): `de440.bsp` 119.8 MB, `sb441-n16.bsp` (asteroid perturbers) 645.7 MB,
`linux_p1550p2650.440` (ASCII-derived planets, smaller date range) 102.3 MB. README says "almost 1 GB" for the planets plus asteroid pair.
`Ephem(planets_path, asteroids_path)` auto-detects SPK vs ASCII-derived format; with no planets path it looks in
`ASSIST_DIR` for `de441.bsp`, `de440.bsp`, `linux_m13000p17000.441`, `linux_p1550p2650.440` in that order.

Python API as read:

```python
import assist, rebound, numpy as np
ephem = assist.Ephem("data/de440.bsp", "data/sb441-n16.bsp")   # ephem.jd_ref default 2451545.0
earth = ephem.get_particle("Earth", 0)                          # names: Sun..Pluto, Moon, Ceres, Vesta, ... (ids 0-26)
sim = rebound.Simulation()                                      # add the test particle, set sim.t relative to jd_ref
ex = assist.Extras(sim, ephem)                                  # switches sim to units ("au","day","massist"), default_plane "frame"
ex.particle_params = np.array([4.99e-13, -2.90e-14, 0.0])       # A1, A2, A3 in au/day^2; write-only; must be a numpy array
ex.integrate_or_interpolate(t)                                  # use instead of sim.integrate
```

Source-level traps:

- **`Ephem` paths are encoded with `.encode("ascii")`**: a data directory with a non-ASCII character (an accented user name, for
  instance) raises `UnicodeEncodeError` before the C library is reached. Keep the files in a plain ASCII path.
- `ex.forces` returns a fresh list: `ex.forces.remove("EARTH_HARMONICS")` has no effect. Copy, remove, then assign
  (`f = ex.forces; f.remove(...); ex.forces = f`). Names: SUN, PLANETS, ASTEROIDS, NON_GRAVITATIONAL, EARTH_HARMONICS,
  SUN_HARMONICS, GR_EIH (all on by default), GR_SIMPLE and GR_POTENTIAL (off). The C side is a bitfield (`^=` flips a bit).
- `gr_eih_sources` defaults to the Sun only; set it to 11 (Sun, Moon, nine planets) for close planetary encounters, at a cost in speed.
- `particle_params` raises `AttributeError` on read. `ex.detach(sim)` is needed before the simulation can be garbage collected.
- The package prints `WARNING: python module and libassist have different version numbers` when the shared library and the
  Python module differ (the module string in the repo read 1.2.0 while PyPI is 1.2.3).
- `import assist` is light; `assist.Extras` imports numpy lazily on first access.

Cross-check against `nyx` / `brahe` (`optimization-toolkit.md`, `brahe-api-reference.md`).

## celmech (analytic and semi-analytic celestial mechanics on top of REBOUND)

`shadden/celmech` (GPL, Hadden, Tamayo and Hernandez; arXiv 2205.10385; PyPI 1.5.8, 2026-06-25) builds Hamiltonian models of planetary systems: Poincare variables and canonical transformations (`poincare.py`, `canonical_transformations.py`, `lie_transformations.py`),
secular and resonant models (`secular.py`, `resonances.py`, `multiplanet_hamiltonian.py`, `numerical_resonance_models.py`), disturbing-function expansions (`disturbing_function.py`), Poisson series, and symplectic maps; it takes initial conditions from a REBOUND simulation.
Use it for resonance widths, secular evolution and averaged dynamics that are too slow to integrate directly.

**Install reality:** the PyPI release is **sdist only** (`celmech-1.5.8.tar.gz`, no wheels), it compiles its own C library (`libcelmech`, loaded with `ctypes` at import), and it requires `reboundx>=4.0.0` (also sdist-only, see above) plus `exoplanet-core`, `pytensor`, `mpmath`, `sympy`, `rebound`.
On Windows without MSVC it is therefore not installable via pip (same cause as REBOUNDx); use Linux/WSL or conda/pixi, and treat the dependency stack (pytensor, exoplanet-core) as heavy. Not installed or run here.
