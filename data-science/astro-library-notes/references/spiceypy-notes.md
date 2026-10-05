---
description: "SpiceyPy 8.2 notes: kernel-load discipline, error classes, 80-char kernel-pool truncation, SPICE's own AU, asteroid NAIF ids"
source_repo: AndrewAnnex/SpiceyPy (MIT)
tested_version: spiceypy 8.2.0 (CSPICE N0067) pip-installed on Windows py3.14 into a scratch dir; kernel-free functions run live, kernel-dependent flow from the project docs (no .bsp/.tls downloaded)
verified_date: "2026-10-05"
---

# SpiceyPy notes (NAIF SPICE in Python)

SpiceyPy wraps NAIF's C toolkit (CSPICE) with ctypes/Cython. It is the reference implementation for
ephemerides, frames and time, and the thing to cross-check `skyfield` and `brahe` against. Function
docstrings link to the NAIF C docs, and the NAIF-authored "Lessons" are in the project docs
(`lessonindex.rst`); the Python docs are intentionally abridged, so the NAIF C docs are the real reference.

Install: `pip install spiceypy` (8.2.0 on 2026-10-05; wheels for CPython 3.10-3.14, Linux/macOS/Windows, x64 and arm).
conda-forge also ships it. No kernels are bundled.

## Nothing works until kernels are loaded (verified live)

With an empty kernel pool, SPICE raises, it does not return a default:

```text
spice.str2et("2026-10-05")                         -> SpiceNOLEAPSECONDS   (needs an LSK, e.g. naif0012.tls)
spice.spkezr("EARTH", 0.0, "J2000", "NONE", "SUN") -> SpiceNOLOADEDFILES   (needs an SPK, e.g. de440s.bsp)
```

Minimum kit for "where is X at UTC date D": an LSK (leap seconds, `.tls`) plus an SPK covering X and
its observer. Add a PCK (`.tpc` / binary `.bpc`) for body radii and orientation, and an FK for frames.
All of these are on `naif.jpl.nasa.gov/pub/naif/generic_kernels/` (`lsk/`, `spk/planets/`, `pck/`).
Fetch them once, outside the pipeline, and pin file names in the repo; a 30MB planetary SPK should
not be re-downloaded per run.

```python
import spiceypy as spice

with spice.KernelPool("meta.tm"):                     # furnsh + guaranteed kclear
    et = spice.str2et("2026-10-05T00:00:00")          # UTC string -> ephemeris time (TDB seconds past J2000)
    state, lt = spice.spkezr("EARTH", et, "J2000", "NONE", "SUN")   # km, km/s; lt = one-way light time s
```

`KernelPool` calls `kclear()` first, so **it deletes any variables you set in the kernel pool by hand**
and hides kernels loaded before the `with`. Use plain `furnsh` / `unload` if you rely on either.

Errors are Python exceptions: `SpiceyError` subclasses, one class per SPICE error code
(`SpiceNOLEAPSECONDS`, `SpiceNOLOADEDFILES`, `Spice1NODATAFORBODY`, ...). Catch the specific class;
the message carries the full NAIF diagnostic. `spice.failed()` stays False in normal use.

## Gotchas verified live

1. **Kernel-pool strings longer than 80 characters are silently truncated.** A text-kernel value of
   79 chars stored as 79; 81 and 200 chars both stored as 80, no error. Long paths in a meta-kernel's
   `PATH_VALUES` or `KERNELS_TO_LOAD` therefore turn into "file not found" (or load the wrong file)
   far from the cause. Keep kernel paths short (relative paths, a short `PATH_SYMBOLS` root) and use the
   `+` continuation inside `KERNELS_TO_LOAD`; the raw pool stores the pieces separately (a value split
   across two quoted strings read back as lengths 61 and 60).
2. **SPICE's AU is not the IAU AU.** `spice.convrt(1.0, "AU", "KM")` returns `149597870.6136889`, but the
   IAU 2012 constant is `149597870.700`. The 87 m difference is 6e-10 relative, harmless alone but it
   breaks bit-identity comparisons against code using the IAU value. Convert with an explicit constant
   and say which one.
3. `spice.conics(elts, et)` and `spice.oscelt(state, et, mu)` need no kernels and round-trip cleanly
   (an Earth-like orbit, `elts = [rp, ecc, inc, lnode, argp, m0, t0, mu]`, gave back `rp = 147099586.259 km`,
   `ecc = 0.0167`). They are an independent two-body check on hand-coded orbital math. Angles are radians,
   distances km, `mu` in km^3/s^2.
4. Times are **ET (TDB seconds past J2000)**, not UTC. Convert with `str2et` / `et2utc`, never by
   adding days to a Julian date.

## Small bodies

Asteroid NAIF ID = `2000000 + permanent asteroid number` (Ceres = 2000001; docs `naif_ids.rst`).
SPICE has built-in names for a few (live: `bodn2c("CERES")` = 2000001, `"PALLAS"` = 2000002, `"VESTA"` = 2000004,
`"BENNU"` = 2101955); `bodn2c("2000001")` raises `NotFoundError`; use `bods2c`, which accepts either a name or a numeric string (live: both give 2000001).
For anything else, load the body's SPK and list the ids it covers with `spice.spkobj`.
The planetary SPKs (`de440s.bsp` etc.) contain **no asteroids**. To get one, generate a small-body SPK from
JPL Horizons (SBDB's API or `brahe`'s Horizons client, see `brahe-api-reference.md`), then `furnsh` it next to
the planetary SPK so its position can be taken relative to `SUN` or `EARTH`.

## Where SpiceyPy fits among the astro tools

| Need | Use |
|---|---|
| Authoritative ephemeris, frames, light time, instrument geometry; mission-grade cross-check | SpiceyPy |
| Quick "where is body X" with a friendlier API and automatic kernel download | `skyfield` (note its de430s download problem in `skyfield-api-reference.md`) |
| One library for catalogs, propagation and SPICE kernels | `brahe` |

Cite both SpiceyPy (Annex et al. 2020, JOSS 5(46), 2050, doi:10.21105/joss.02050) and the SPICE toolkit
(NAIF credit page) in published work.
