---
description: "spacekit.js (typpo): browser 3D solar-system viewer on three.js; Orbit/Ephem run headless in Node and checked against astropy: planet presets are two-body, Saturn drifts to 1.5 AU by 1900"
source_repo: typpo/spacekit (MIT)
tested_version: "repo main @ aa93d3f (2026-04-07), package spacekit.js 0.1.0 with a committed build/spacekit.cjs.js loaded in Node 22.23.2 (no npm install: it failed with an ERESOLVE report); positions compared with astropy 8.0.1 builtin ephemeris in a uv Python 3.12 venv. No browser rendering was run"
verified_date: "2026-10-05"
---

# spacekit (typpo/spacekit)

A JavaScript library that draws a solar system in the browser with three.js: planets, asteroids and comets from orbital
elements, ephemeris tables, skyboxes, particle swarms (meteor showers), shape models. It is a **visualisation** tool, not an
ephemeris source: use `skyfield`, SpiceyPy or `brahe` when you need numbers (see `SKILL.md`).

## Facts

| Item | Value |
|---|---|
| Package | `spacekit.js`; npm `latest` is **0.1.1 (2023-11-07)**, while repo `package.json` on main says `0.1.0` (a TypeScript rewrite, last commit 2026-04-07). Pin and read which one you installed |
| Dependencies | `three` **0.135.0** (exact pin), `julian`, `postprocessing` |
| Build output | `build/spacekit.cjs.js`, `spacekit.esm.js`, `spacekit.js` (global `Spacekit`) are **committed** to git |
| Exports (cjs) | `Ephem, EphemPresets, EphemerisTable, GM, KeplerParticles, NaturalSatellites, Orbit, OrbitType, RotatingObject, ShapeObject, Simulation, Skybox, SkyboxPresets, SpaceObject, SpaceObjectPresets, SphereObject, Stars, StaticParticles, THREE, getSkyboxOrientationTransform` |
| Tests | `jest` in `test/` (Ephem, Orbit, EphemPresets, EphemerisTable, Coordinates, Math, Skybox); one pins the 'Oumuamua hyperbolic radius at 2.0249705285 AU |
| Examples | `examples/` has ~20 HTML demos (planet, jupiter, halleys_comet, roadster, hyperbolic, ephemeris_table, meteor-shower ...) |

## Headless use (run)

The Orbit maths needs no WebGL context. With the committed bundle:

```js
const S = require('./build/spacekit.cjs.js');
const orbit = new S.Orbit(S.EphemPresets.MARS, {});     // Orbit wraps an Ephem
const [x, y, z] = orbit.getPositionAtTime(2461318.5);   // Julian date -> AU, heliocentric ecliptic
```

`Ephem` itself has no position method (`get`, `set`, `copy`, `lock`); `Orbit.getPositionAtTime(jd)` dispatches to
elliptical, near-parabolic, hyperbolic, parabolic or ephemeris-table code.

## Accuracy of the planet presets (run, vs astropy builtin ephemeris)

The presets are **two-body Keplerian elements held fixed**. Mercury to Saturn use JPL osculating elements at JD 2458426.5
(2018-11-26); Earth uses the JPL "approximate positions" J2000 mean elements without their per-century rates. Distance from
the astropy heliocentric position, in AU:

| Planet | At its epoch | 2026-10-05 | 2040 | 1900 | Orbit radius |
|---|---|---|---|---|---|
| Mercury | 0.0000 | 0.0004 | 0.0011 | 0.0073 | 0.31-0.47 |
| Venus | 0.0000 | 0.0018 | 0.0046 | 0.0258 | 0.72 |
| Earth (EMB) | 0.0000 (J2000; 2018-11-26 gives 0.0006) | 0.0010 | 0.0013 | 0.0032 | 0.98-1.02 |
| Mars | 0.0001 | 0.0011 | 0.0026 | 0.0122 | 1.4-1.7 |
| Jupiter | 0.0003 | 0.0071 | 0.0069 | 0.0402 | 5.0-5.4 |
| **Saturn** | 0.0007 | **0.0856** | **0.3675** | **1.4878** | 9.2-10.1 |

Inner planets stay within a few thousandths of an AU around the present, which is fine for a picture (at 1 AU, 0.001 AU is
150 000 km). Saturn is not: Jupiter's perturbation makes Saturn's osculating elements drift, so by 2040 the dot is 0.37 AU
off and by 1900 it is 1.5 AU off. For historical or far-future scenes supply elements for that epoch (JPL Horizons) or use
an `EphemerisTable`.

Reference computation: `get_body_barycentric_posvel(..., solar_system_ephemeris='builtin')` minus the Sun, rotated to the
mean ecliptic J2000 with an obliquity of 84381.406". The builtin ephemeris is itself approximate (arcsecond-level for the
planets), far smaller than the errors above.

## Practical notes

- Use `EphemerisTable` (Horizons vector tables) for spacecraft and anything where two-body error matters.
- three.js is pinned at 0.135.0 (2021); do not mix it with another three.js version in the same page (spacekit
  re-exports its `THREE` so you can use the matching copy).
- Not run: browser rendering, the example pages, the jest suite, `npm install`, skybox assets, shape-model loading.
