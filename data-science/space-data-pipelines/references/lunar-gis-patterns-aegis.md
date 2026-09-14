---
description: "Lunar GIS patterns from nasa/aegis (AEGIS): LPS projection math, GeoTIFF custom-CRS reconstruction, lgrs-verified port"
source_repos: nasa/aegis (Artemis EVA Geographic Information System)
tested_version: clone @ 2026-09-13; lgrs 0.3.0 oracle on Python 3.13
verified_date: "2026-09-13"
---

# Lunar GIS Patterns (nasa/aegis — AEGIS, round-19 live verification)

AEGIS = NASA JSC's Artemis EVA planning tool (OpenLayers + Automerge CRDTs). It is a full app, not an importable library — the value here is its **lunar-surface math**, which no generic GIS stack does: non-Mercator per-mission CRS rendering over custom ellipsoids. AEGIS ships **no LICENSE file** (NASA JSC internal tool), so this doc records patterns and independently re-derived constants, not copied code.

## South-pole Lunar Polar Stereographic (LPS) — the core projection [VERIFIED]

AEGIS ports pinned Python `lgrs 0.3.0` (`LatLonPoint(...).to_lps()`) into TypeScript
(`src/utils/lgrs/southLps.ts`). Round-19 re-derived that math in a standalone script and checked it
against the **real lgrs 0.3.0 package** (PyPI, requires Python ≥3.13):

| Point | lat/lon | e_lps / n_lps (lgrs 0.3.0 oracle) | AEGIS-port math error |
|---|---|---|---|
| South pole | -90.0, 0.0 | 500000.0, 500000.0 | **0 m** (exact by construction) |
| Artemis Base Camp area | -84.5276, 0.0 | 500000.0, 665071.360549 | ≤ 3.49e-10 m |
| Shackleton rim (west) | -89.0, -13.9 | 492759.004189, 529259.506527 | ≤ 3.49e-10 m |

**Max error: 3.5e-10 m — sub-nanometer.** The port is verified as claimed by its own docstring
("verified by the lgrs 0.3.0 reference corpus"). Re-run any time with
`scripts/lps_projection_verify.py` (stdlib-only; oracle vectors embedded).

Constants (from AEGIS `src/utils/consts.ts`, cross-checked against lgrs output):

```python
MOON_MEAN_RADIUS = 1737.4e3   # m
K0               = 0.994      # central scale factor at the pole
FALSE_EASTING    = 500000     # m (pole sits exactly on this easting/northing)
FALSE_NORTHING   = 500000     # m
```

The projection itself is standard polar stereographic with origin latitude -90°, longitude 0°:

```python
scale    = (2 * K0) / (1 + sin(phi_o)*sin(phi) + cos(phi_o)*cos(phi)*cos(lam - lam_o))   # phi_o=-pi/2, lam_o=0
easting  = R * scale * cos(phi) * sin(lam)                 + FALSE_EASTING
northing = R * scale * (cos(phi_o)*sin(phi) - sin(phi_o)*cos(phi)*cos(lam - lam_o)) + FALSE_NORTHING
```

**Domain limit:** LPS is only valid to about **-80° latitude**; lgrs 0.3.0 raises `MalformedCoordinate`
below that (measured: lat=-75, lon=45 → rejected; AEGIS uses the same `-80` cutoff as its viewport
domain radius). For mid/high northern latitudes use Lunar Transverse Mercator zones instead — lgrs's
`Constraints` object routes between LPS/LTM automatically.

### lgrs 0.3.0 API facts (measured, not from docs)

- Constructor order is **`(latitude, longitude)`** — the reverse of most GIS libraries; passing
  `(lon, lat)` silently produces a MalformedCoordinate or wrong hemisphere.
- `to_lps()` returns an `LpsPoint` object with `.easting` / `.northing` attributes (NOT subscriptable).
- PyPI requires **Python ≥3.13** — on this box use the system Python 3.13 in a fresh venv, not uv's default 3.12.

## GeoTIFF custom-CRS reconstruction [SRC]

Lunar rasters carry **no registered EPSG code** (custom ellipsoids), so AEGIS rebuilds proj4 strings
from the numeric GeoKeys embedded in each GeoTIFF (`src/server/raster/projection.ts`):

- `ProjectedCSTypeGeoKey == 32767` → user-defined CRS: read parameters directly.
  - **Transform code 15 = polar stereographic** → `+proj=stere +lat_0=<ProjNatOriginLat> +lon_0=<ProjStraightVertPoleLong> +k=<ProjScaleAtNatOrigin>`
  - **Transform code 17 = equirectangular** → `+proj=eqc +lat_ts=<ProjStdParallel1> +lat_0=<ProjCenterLat> +lon_0=<ProjCenterLong>`
- Registered codes (`!= 32767`) pass through as `EPSG:<code>` and let proj4 fetch the full definition.
- Hard requirement: linear units must be metres (`ProjLinearUnitsGeoKey == 9001`), else error — no unit guessing.

This is the pattern to copy for **any** lunar DEM product (LOLA, LRO SDR) that predates EPSG registration of its CRS.

## Geographic → raster pixel [SRC]

`src/server/raster/coordTransform.ts`: proj4 transform geographic→projected, then
`(x - origin[0]) / res[0], (y - origin[1]) / res[1]`, **truncated to nearest cell** (no interpolation).
The y-resolution is commonly negative because projected northing increases upward while image rows
increase downward — the sign flip happens naturally in the division.

## Traverse distance [SRC]

Plain haversine with a **parameterized planet radius** (`src/utils/mapping/geoMath.ts`) — so the same
code serves Earth (6371e3) and Moon (1737.4e3). Nothing lunar-specific; great-circle only, no terrain.

## LGRS display labels [SRC]

`lgrs 0.3.0` owns coordinate display: grid zone + easting/northing digits at **10 m precision**
(`LGRS_DISPLAY_PRECISION_METERS = 10`). AEGIS's `dynamicGrid.ts` ports the labeling plus viewport-grid
render planning (base spacing 10 m, label targets tuned for screen pixels).

## When to use vs alternatives

- Needing LPS/LTM coordinates or lunar map products → **lgrs** (Python ≥3.13) is the reference; AEGIS's TS port is verified equivalent if you're already in a JS stack.
- Rendering non-Mercator per-mission CRS in OpenLayers with custom ellipsoids → study `projection.ts` + `coordTransform.ts`; QGIS/CesiumJS don't do this out of the box for lunar data.
- Collaborative geospatial editing (CRDT) → AEGIS uses Automerge; its seeder (`apollo14SeedData.ts`) shows document shape.
