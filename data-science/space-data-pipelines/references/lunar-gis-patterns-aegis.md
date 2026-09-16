---
description: "Lunar GIS patterns from nasa/aegis (AEGIS): LPS projection math, GeoTIFF custom-CRS reconstruction, lgrs-verified port"
source_repos: nasa/aegis (Artemis EVA Geographic Information System)
tested_version: clone @ 2026-09-13 + GIS_data_conversion_pipeline read @ 2026-09-16; lgrs 0.3.0 oracle on Python 3.13
verified_date: "2026-09-16"
---

# Lunar GIS Patterns (nasa/aegis — AEGIS, round-19 live verification + round-27 pipeline pass)

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

## Cap-grid tiling for OpenLayers overlays — the z0 invariant [SRC + re-derived]

`GIS_data_conversion_pipeline/esri-to-aegis-lunar-southpole/common/tile_to_cap_grid.py` tiles any
lunar raster onto AEGIS's shared **south-pole cap grid** so it pixel-aligns with the NAC basemap in
OpenLayers. The pattern generalizes to *any* non-Mercator tiled overlay:

- **Shared z0, per-layer depth.** Every layer is cut on the same origin (`CAP_MIN = -931100 m` both
  axes) and the same `z0 resolution (12800 units/px)` — OpenLayers builds its pyramid as
  `z0_res / 2**z`, so alignment to the basemap requires identical z0. But each layer's **max zoom is
  per-layer**: `max_zoom = ceil(log2(z0_res / native_resolution))` (ceil picks the next-deeper rung,
  so a layer is never stored coarser than its source; 1 m/px → z14). There is deliberately no shared
  zoom clamp — a deeper layer "just works" in the app.
- **The padding trap ("layer jumps when you zoom out").** The cap is not an integer number of tiles
  wide, and `gdal raster tile` anchors at TOP-left with TMS Y-flip re-derived as `ceil(rows/2)` per
  level. Padding only to the next whole tile at max zoom fails: an odd row count re-rounds on the way
  up and walks the bottom row off CAP_MIN, shifting every coarser level north by up to a tile. The fix
  is padding the canvas to **`2**max_zoom` tiles = exactly one z0 tile of `256 * z0_res` metres**, so
  every level halves exactly and TMS row 0 sits on CAP_MIN at all zooms. This single choice is what
  makes bottom-left-anchored XYZ/TMS conventions interchangeable here — re-derived in
  `scripts/cap_grid_verify.py`.
- **Tile window + tight bbox.** Data extent → tile indices: X from the bottom-left anchor increasing
  east; Y (XYZ/top-down) anchored at the *padded* cap top. The emitted `tilemapresource.xml` carries a
  convention-independent data bbox = tile window snapped to the grid and clamped to the cap, so
  renderers only fetch tiles that were actually written instead of the whole cap.
- **CRS identity.** Cap profile: South Pole Stereographic on the Moon (2015) sphere — `IAU2000:30166`,
  `+proj=stere +lat_0=-90 +lon_0=0 +k=1 +a=1737400` (note: **no** false easting/northing and **no**
  K0=0.994 — this is the *app's* cap CRS, distinct from lgrs LPS which uses FE/FN = 500000 and k=0.994;
  both are legitimate lunar south-pole stereographics with different conventions). The full WKT SRS is
  written into each layer's tilemapresource.xml because GeoTIFF/GeoJSON drop custom CRS on the wire.

## Cloud-Optimized GeoTIFF for browser serving [SRC]

`common/geotiff_to_cog.py`: GDAL COG driver via `rasterio.shutil.copy` — tiling + overviews +
compression in one multi-threaded pass; served directly by OpenLayers' `ol/source/GeoTIFF` over HTTP
Range requests (no tile server). **Compression choice is the gotcha:**

| codec | lossless? | browser-decodable via geotiff.js/OpenLayers? | use for |
|---|---|---|---|
| deflate | yes | yes | default, universal |
| lzw | yes | yes (fast decompress) | large analytical rasters |
| zstd | yes | **NO** — not decodable by geotiff.js/OpenLayers | server-side only (their own docstring flags it; the script's *default* is still zstd, so override for web serving) |
| jpeg | no (~10–20x smaller) | yes | visual imagery |
| lerc | bounded-error | partial | DEMs where error bounds matter |

Rule of thumb: if a COG must render in the browser, pick deflate/lzw/jpeg — zstd's "best ratio" is
invisible to your users. Companion scripts: `raster_to_8bit.py` (float→uint8 with per-band scaling),
`inspect_geotiff.py` (dims/dtype/transform/bounds/CRS dump before any conversion).

## LGRS grid generation without ArcGIS [SRC]

`grid/generate_lgrs.py` + `convert_lgrs.py` replace a manual ESRI/ArcGIS export: the USGS
[`lgrs`](https://github.com/rbeyer/lgrs) package (`write_grid(bounds, precision_m, path_template, acc=True)`)
emits LGRS cells in Lunar Polar Stereographic metres; reproject cell corners to lon/lat (AEGIS reads
the file as EPSG:4326), keep per-cell `LGRS_ACC` + condensed halves (`Z4F3` → `L_coord=Z4`,
`R_coord=F3`; 100 m grids = 6-char ACC, 1 km = 5-char) and cell-centre northing in metres. The two
inputs (ESRI export vs generated GeoJSON) are interchangeable for the converter because both follow
the same contract: **vertex 0 of every ring = the cell's bottom-left corner** (AEGIS label anchor),
features ordered **row-major in metres** (northing then easting ascending). Row/column detection is a
pure scan over centre-Y steps (a new row begins when centY rises; the last point before a rise gets a
blank L_coord/R_coord — an AEGIS display requirement, not data loss). The converter itself is
stdlib-only on purpose: in and out are both WGS84 GeoJSON, so no geo stack needed.

**Verified internal inconsistency (legacy path only).** `clean_lgrs_coordinate`'s n==6 branch comment
says "keep last 4 chars, split 2 + 2" but the code does `[3:5] + [5:]` — the **last three** chars as a
2+1 split (`'AAQ9K7' → '9K'/'7'`, measured). The module docstring also promises "truncated to its last
four chars". The n==5 branch is self-consistent (last 2, 1+1), and the generated-GeoJSON path never
calls this function at all (it uses pre-split L/R coords) — so only raw ESRI exports hit it. Anyone
reusing `clean_lgrs_coordinate` on a real ArcGIS export should diff its output against one known-good
AEGIS grid before trusting either the code or the comment; `scripts/cap_grid_verify.py` asserts both
the code's actual behavior and that the discrepancy exists, so a future upstream fix flips it loudly.

## When to use vs alternatives

- Needing LPS/LTM coordinates or lunar map products → **lgrs** (Python ≥3.13) is the reference; AEGIS's TS port is verified equivalent if you're already in a JS stack.
- Rendering non-Mercator per-mission CRS in OpenLayers with custom ellipsoids → study `projection.ts` + `coordTransform.ts`; QGIS/CesiumJS don't do this out of the box for lunar data.
- Collaborative geospatial editing (CRDT) → AEGIS uses Automerge; its seeder (`apollo14SeedData.ts`) shows document shape.
