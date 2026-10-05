---
description: "pykep 3 (ESA trajectory design): Linux-only PyPI wheels, API map (Lambert, Lagrangian propagation, legs, trajopt, planets), where it fits vs brahe/OpenSCvx/pygmo"
source_repo: esa/pykep (MPL-2.0)
tested_version: install availability checked via the PyPI JSON API (pykep 3.0.1); package NOT installed or run (no Linux/WSL/conda on this Windows box); API names read from the project's Sphinx source @ master
verified_date: "2026-10-05"
---

# pykep 3 / kep3

ESA's astrodynamics toolbox for interplanetary trajectory design: C++ core `kep3` plus the `pykep` Python package.
Version 3 (3.0.0 released 2026-05-23, PyPI 3.0.1) is a rewrite of the 2.x line; the old pykep is "no longer actively maintained".
It is the natural library for **Lambert arcs, gravity-assist chains, low-thrust legs and global trajectory
optimisation** (GTOC-style problems), and it integrates with `pygmo` for evolutionary search.

## Install reality (checked 2026-10-05)

| Route | Status |
|---|---|
| `pip install pykep` on **Windows / macOS** | **Fails**: PyPI 3.0.1 ships only `manylinux_2_28` wheels (cp311, cp312, cp313; x86_64 and aarch64). `pip download pykep --only-binary=:all:` for py3.11-3.13 and Python 3.14 win_amd64 found no distribution. Older 2.4-2.6 releases list cp36-cp38 wheels (including win_amd64), far too old for current Python |
| `pip install pykep` on Linux x86_64/aarch64, Python 3.11-3.13 | works per the wheel list. Declared dependencies: `numpy, scipy, matplotlib, sgp4, spiceypy, pygmo, heyoka==7.10.1`; `heyoka` is pinned exactly |
| conda-forge | README says conda-forge still serves the v1 line; v3 packages come once the API stabilises |
| Source build | recommended by the README for v3 development: conda env from `kep3_devel.yml`, then CMake with `-Dkep3_BUILD_PYTHON_BINDINGS=ON` (needs Boost, fmt, heyoka, xtensor) |

Practical consequence for a Windows machine: use WSL/Linux or a container for pykep 3, or choose a library that installs here
(`brahe`, `skyfield`, REBOUND; see `SKILL.md`). The exact `heyoka` pin plus `pygmo` (itself Linux-wheel-only on PyPI) makes a mixed
environment fragile, so give pykep its own venv.

## API map (names from the docs; not executed)

| Area | Objects |
|---|---|
| Time and elements | `pk.epoch`, anomaly conversions, equinoctial elements, `pk.planet` |
| Planet models (`pk.udpla`) | `keplerian`, `jpl_lp` (JPL low-precision), `vsop2013`, `tle`, `spice`, `de440s`, `cr3bp`, `null_udpla` |
| Lambert | `pk.lambert_problem` (multi-revolution solutions) |
| Propagation | `pk.propagate_lagrangian` and `propagate_lagrangian_grid` (Kepler via Lagrange coefficients); `pk.ta` Taylor-adaptive integrators on heyoka for Kepler, CR3BP, bicircular, zero-order-hold (ZOH) Keplerian/equinoctial/CR3BP/solar-sail dynamics, each with a variational version returning the state transition matrix |
| Legs | `pk.leg.sims_flanagan`, `zoh`, `zoh_ms`, `zoh_ms_py` |
| Trajectory optimisation (`pk.trajopt`) | direct: `sf_point2point`, `sf_pl2pl`, `sf_pl2pl_alpha`, `zoh_point2point`, `zoh_pl2pl`, `zoh_ss_point2point`; indirect (Pontryagin): `pontryagin_cartesian_mass/time`, `pontryagin_equinoctial_mass/time`; evolutionary encodings: `mga`, `mga_1dsm`, `pl2pl_N_impulses`; plus `primer_vector` |
| Utilities | flyby (gravity assist) helpers, constants, plotting (`pk.plot`) |

Design pattern: trajectory problems are exposed as `pygmo` user-defined problems, so a global optimiser (island model) can search the
encoding while a leg model supplies the physics. The `mga` encoding is the standard way to search launch window plus flyby sequences.

## Where it fits

| Task | Tool |
|---|---|
| Multi-flyby / Lambert-based mission search, GTOC-style, low-thrust leg design | pykep (Linux) |
| One solver for a single constrained transfer with free final time | OpenSCvx (`openscvx-patterns.md`) |
| Catalog access, EOP, propagation on Windows | brahe (`brahe-api-reference.md`) |
| Ephemerides and frames as ground truth | SpiceyPy (`spiceypy-notes.md`) |
| Global optimisation of any mission objective | pygmo (`optimization-toolkit.md`) |

MPL-2.0 is file-level copyleft: you can use pykep from proprietary code, but modifications to pykep's own files must be shared.
The docs warn that some tutorials use features not yet in the latest stable release, so match notebooks to your installed version.
