---
name: astro-library-notes
description: "Astro libs: skyfield, astropy, SPICE, Orekit, pykep traps."
version: 1.0.0
author: Hermes Agent (promoted from astro-toolkit-selection references, live-run 2026-09/10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [astrodynamics, ephemeris, time-scales, skyfield, astropy, spiceypy, orekit, rebound, pykep, brahe, hifitime, spacekit]
    related_skills: [astro-toolkit-selection, orbital-mechanics-data, space-data-pipelines, economicspace-pipeline, bit-identity-float-pipelines]
---

# Astrodynamics library notes

## What This Skill Does

Per-library reference for ephemeris, time-scale and propagation libraries used in space work: what installs on Windows and Python 3.14, which calls silently give a wrong answer, and how to cross-check one library against another. It is the second step after `astro-toolkit-selection` has picked the method: that skill says *which* approach and library family, this one says *how that library behaves*. Every note was run live (or marked source-read) against a pinned version.

## When to Use

- Computing positions, phase angles, time-scale conversions or propagations with skyfield, astropy, SpiceyPy, hifitime, Orekit, REBOUND, pykep or brahe
- A result is off by seconds, hours or an AU and you need the known trap (leap seconds, JD scale, kernel truncation, AU definition)
- A library fails to install on Windows or Python 3.14 (pykep wheels, REBOUNDx, Orekit needing a JVM)
- Cross-checking a closed-form delta-v or ephemeris against an independent tool
- Not for choosing the method (`astro-toolkit-selection`), delta-v and transfer formulas (`orbital-mechanics-data`), fetching catalogs (`space-data-pipelines`), or the optimization stack (`astro-toolkit-selection/references/optimization-toolkit.md`)

## Which reference

| You need | Library | Reference | Known trap |
|---|---|---|---|
| Planet and satellite positions, no build step | skyfield 1.55 | `references/skyfield-api-reference.md` | `load()` contract changed in 1.55; de430s.bsp 404 on both JPL mirrors; no asteroids in any de-series kernel; phase-angle trap |
| Time scales, coordinates, units, IERS | astropy 8.0.1 | `references/astropy-notes.md` | numeric JD is UTC by default (TT differs 69.184 s); `Time + float` assumes days; AltAz without location gives a misleading error |
| Time scales in Rust or Python (`pip install hifitime`) | hifitime 4.3.1 | `references/hifitime-time-scales.md` | correct TAI/TT/TDB/GPST offsets but a 1 s TAI to UTC error at leap boundaries |
| NAIF/SPICE kernels and geometry | SpiceyPy 8.2 | `references/spiceypy-notes.md` | empty kernel pool errors; 80-char kernel-pool strings truncate silently; SPICE AU is 149597870.6137 km, not the IAU value |
| High-fidelity propagation (Java) | Orekit 13.1.9 via `orekit-jpype` | `references/orekit-python-notes.md` | import only after `initVM`; UTC/ITRF fail without orekit-data; pip-provided JDK works |
| N-body integration | REBOUND 5.2.1 (+ REBOUNDx) | `references/rebound-n-body-notes.md` | `sim.G` in AU/yr/Msun is 39.4769; REBOUNDx is sdist-only (needs a C compiler); GPL-3.0 |
| Lambert, Taylor propagation, trajectory legs (ESA) | pykep 3.0.1 | `references/pykep-v3-notes.md` | PyPI wheels are manylinux-only, so not pip-installable on Windows/macOS (conda-forge instead) |
| Propagation, frames, SBDB/Horizons/Celestrak clients | brahe 1.7.0 | `references/brahe-api-reference.md` | Horizons SPK recipe works for any small body; check version before pinning |
| 3D orbit viewer in the browser | spacekit.js | `references/spacekit-notes.md` | planet presets are fixed two-body elements (Saturn 0.09 AU off today, 1.5 AU in 1900) |

## Procedure

1. Settle the method first (`astro-toolkit-selection`); then open the matching reference and read its install and traps sections before writing code.
2. Pin the version and state units, frame and time scale at every API boundary; most errors here are km vs m, degrees vs radians, UTC vs TT vs TDB.
3. Cross-check an important number with a second library: astropy as truth for TAI/TT/TDB, SpiceyPy or skyfield for ephemerides, a numerical propagator for a closed-form delta-v.
4. When a result sits at a leap-second boundary, do not trust a single library; hifitime has a 1 s error there and `datetime` ignores the leap second.
5. On Windows prefer pip-installable options (skyfield, astropy, SpiceyPy, brahe, hifitime); budget for conda, a compiler or a JVM for the rest.
6. Record new traps in the owning reference with version and date.

## Pitfalls

- Mixing AU definitions: SPICE's AU differs from the IAU value, so a conversion through `astropy.units` will not match a SPICE distance exactly.
- Assuming the viewer's presets are ephemerides (`spacekit` presets are fixed elements, accurate only near their epoch).
- Treating a library import as an install check for the data it needs (kernels, IERS tables, `orekit-data`): the first real call downloads or fails.
- Copyleft: REBOUND and REBOUNDx are GPL-3.0; check before building on them.
- Results are 2026-09/10 snapshots on specific versions; re-run before quoting numbers on a newer release.

## Verification

- [ ] Library versions match the references, or the relevant probe was re-run
- [ ] Time scale, frame and units are stated and tested against a known value
- [ ] A second library or independent calculation confirms any headline number
- [ ] Data dependencies (kernels, IERS, orekit-data) are present or fetched explicitly

## References

- `references/skyfield-api-reference.md` - skyfield 1.55 breaking changes (`load()` contract), de430s.bsp 404 on both JPL mirrors, phase-angle trap with numbers, osculating-elements solver for independent checks
- `references/astropy-notes.md` - astropy 8.0.1: numeric JD is UTC by default, string UTC offsets rejected, `Time + float` assumes days, AltAz without location, IERS auto-download
- `references/hifitime-time-scales.md` - hifitime 4.3.1 cross-checked against astropy: correct scale offsets, 1 s TAI to UTC error at leap boundaries, UTC `timedelta` ignoring the leap second
- `references/spiceypy-notes.md` - SpiceyPy 8.2: empty kernel-pool errors, `KernelPool` clearing hand-set variables, 80-char truncation, SPICE AU vs IAU, asteroid ids
- `references/orekit-python-notes.md` - Orekit 13.1.9 from Python via `orekit-jpype` and a pip JDK: import-after-`initVM`, SI/radian units, Kepler propagation, orekit-data needs
- `references/rebound-n-body-notes.md` - REBOUND 5.2.1 live run, REBOUNDx build failure, Yarkovsky/radiation-force parameters, GPL-3.0, ASSIST pointers
- `references/pykep-v3-notes.md` - pykep 3.0.1: manylinux-only wheels, conda-forge route, API map for Lambert, propagation and legs
- `references/brahe-api-reference.md` - brahe 1.7.0 module map with live-run snippets: Horizons SPK fetch for any small body, Celestrak query builder, EKF/UKF/BLS estimation
- `references/spacekit-notes.md` - spacekit.js 3D viewer: headless Node bundle, fixed-element planet presets checked against astropy, npm facts
