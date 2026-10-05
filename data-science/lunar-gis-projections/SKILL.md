---
name: lunar-gis-projections
description: "Lunar polar GIS: LPS projection, cap grids, COG rules."
version: 1.0.0
author: Hermes Agent (promoted from space-data-pipelines, nasa/aegis pass)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [lunar, gis, polar-stereographic, lgrs, geotiff, cog, openlayers, tiling, aegis]
    related_skills: [space-data-pipelines, open-data-catalog-sources, orbital-mechanics-data, astro-toolkit-selection]
---

# Lunar GIS projections

## What This Skill Does

Reproduces the lunar south-pole mapping math used by nasa/aegis and checks it with scripts that run without GIS software: the Lunar Polar Stereographic (LPS) projection, the LGRS grid labels, GeoTIFF custom-CRS reconstruction, cap-grid tiling for OpenLayers overlays and Cloud-Optimized GeoTIFF rules for browser serving. The projection was verified against the real `lgrs` 0.3.0 package to 5.8e-11 m.

## When to Use

- Converting lunar latitude and longitude to polar-stereographic metres, or back
- Reading a lunar GeoTIFF that has no EPSG code
- Tiling a lunar raster for a browser map, or serving it as a COG
- Generating or labelling LGRS grid cells
- Not for ephemerides or orbit propagation (`orbital-mechanics-data`) or fetching the data feeds (`space-data-pipelines`, `open-data-catalog-sources`)

## Quick Reference

```bash
python data-science/lunar-gis-projections/scripts/lps_projection_verify.py            # stdlib only, embedded oracle vectors
python data-science/lunar-gis-projections/scripts/lps_projection_verify.py --oracle   # also regenerates vectors from installed lgrs
python data-science/lunar-gis-projections/scripts/cap_grid_verify.py                  # 34 tiling invariants, exit code = failures
```

Both exit 0 on success. `references/lunar-gis-patterns-aegis.md` has the formulas, the GeoTIFF key tables and the grid-generation details.

## Lunar-surface GIS (see `references/lunar-gis-patterns-aegis.md`)

South-pole LPS projection math from nasa/aegis (AEGIS) — re-derived and **verified against the real lgrs 0.3.0 package to ≤5.8e-11 m** (`scripts/lps_projection_verify.py`, stdlib-only, exit-code gated). It covers:

- Exact constants: R=1737.4 km, K0=0.994, false E/N = 500000 m, and the -80° domain limit.
- lgrs API traps:
  - the constructor takes (latitude, longitude), in that order
  - `to_lps()` returns an object with `.easting`/`.northing`, not a tuple
  - PyPI needs Python ≥3.13
- GeoTIFF custom-CRS reconstruction: transform codes 15=polar-stereo / 17=equirectangular from numeric GeoKeys when no EPSG code exists.
- Geographic→pixel nearest-cell sampling for lunar DEM products.

Round-27 added the **cap-grid tiling invariants** from AEGIS's own GIS pipeline (`scripts/cap_grid_verify.py`, 34 live checks):

- Shared-z0/per-layer-depth pyramids.
- The odd-tile-count padding trap that makes layers jump when zooming out (re-derived numerically).
- COG compression rules for browser serving: **zstd is NOT decodable by geotiff.js/OpenLayers**, which is their own default.
- LGRS grid generation without ArcGIS via USGS `lgrs`, including a **verified internal inconsistency in AEGIS's legacy converter**. Its n==6 branch contradicts its docstring; the harness asserts both so an upstream fix flips loudly.


## Procedure

1. Run `lps_projection_verify.py` before relying on any ported projection code; it must report max error well under the 1 mm tolerance.
2. Pass coordinates to `lgrs` as (latitude, longitude) and read `.easting` and `.northing` from the returned object.
3. For a GeoTIFF without an EPSG code, rebuild the CRS from the numeric GeoKeys (transform code 15 polar-stereo, 17 equirectangular).
4. Tile with a shared z0 and per-layer depth, and run `cap_grid_verify.py` to confirm layers do not jump when zooming out.
5. Serve COGs without zstd compression: geotiff.js and OpenLayers cannot decode it.
6. Re-run both scripts after any upstream change; a flipped assertion means upstream fixed or broke something.

## Pitfalls

- Swapping latitude and longitude in the `lgrs` constructor.
- Treating `to_lps()` as returning a tuple.
- Using `lgrs` on Python older than 3.13 (the PyPI package needs 3.13 or later).
- Odd tile counts shifting layers between zoom levels.
- Trusting AEGIS's legacy grid converter: its n==6 branch contradicts its own docstring, and the harness asserts both.

## Verification

- [ ] Projection check passes with error under the stated tolerance
- [ ] Cap-grid check reports 0 failures
- [ ] Served COG opens in the browser viewer without a decoder error
- [ ] Domain limit (-80 degrees latitude) is enforced by callers

## References

- `references/lunar-gis-patterns-aegis.md` - LPS projection, GeoTIFF reconstruction, pixel sampling, traverse distance, LGRS labels, cap-grid z0 invariant, COG serving, grid generation, update notes
- `scripts/lps_projection_verify.py`, `scripts/cap_grid_verify.py` - the stdlib verification harnesses
