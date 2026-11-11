---
name: gis-spatial-analysis
description: "Vector GIS + ArcGIS: indexes, CRS traps, verified picks."
version: 0.1.0
author: Hermes Agent (mined from starred repos, 2026-11-04)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [gis, spatial, vector, geopandas, rtree, shapely, crs, pyogrio, whitebox]
    related_skills: [lunar-gis-projections, space-data-pipelines, python-data-science, sql-for-data, duckdb-querying]
---

# GIS Spatial Analysis (Python vector stack)

Load for vector geospatial work: spatial indexes, joins between geometry sets, CRS/axis-order
questions, GeoPackage I/O, or choosing among rtree / shapely / GeoPandas-pyogrio / WhiteboxTools.
Raster-on-a-disk specifics (COG overviews, projections of planetary bodies) live in
`lunar-gis-projections` and `space-data-pipelines`; this skill is about *vector* analysis cost and
about the places where the stack returns a plausible number instead of an error.

Everything measured below ran on Windows 11 in an isolated venv (`python -E`, so ambient
`PYTHONPATH` could not leak in — see `../../software-development/python-craft/references/venv-isolation-and-pythonpath-windows.md`)
on 2026-11-04: rtree 1.4.1, shapely 2.2.0 (GEOS 3.14.1), geopandas 1.2.0, pyogrio 0.13.0,
pyproj 3.8.0, numpy 2.5.4, pandas 3.1.0, whitebox 2.3.6 (WhiteboxTools v2.4.0 binary), folium 0.20.0.

## What This Skill Does

Puts measured cost and correctness behaviour behind Python vector-GIS choices: which spatial-index
construction path to use (and when an index is the *wrong* answer), how the stack fails silently on CRS axis
order, invalid geometry and unprojected area, the real rtree 1.x / whitebox 2.3.x API shapes, GeoPackage and
File-Geodatabase I/O without proprietary software, and wheel/installability reality for this stack.

## When to Use

- Building or reviewing code that intersects/filters many geometries, joins two vector layers, or writes
  GeoPackage/Shapefile/File Geodatabase output
- A spatial query returns nothing, an area looks wrong, a projection gives nonsense, or an index build is slow
- Choosing between rtree / shapely vectorized ops / numpy mask / SQL (DuckDB) for a geospatial filter
- Setting up the geospatial stack on Windows/Python 3.14+ and needing to know what actually has wheels

Not for: raster COG/pyramid mechanics or planetary projection specifics (`lunar-gis-projections`,
`space-data-pipelines`), or non-GIS numeric work (`python-data-science`).

## The five rules that actually matter

1. **Never build a spatial index with an `insert()` loop.** 50,000 rectangles cost **8.07 s** via
   `rtree.index.Index()` + per-row `.insert()`, versus **0.048 s** to bulk-build the same data as
   `GeoSeries.sindex` (STR-packed) — a measured 167x difference, and both returned identical hits.
   Build from all geometries at once: `gdf = gpd.GeoDataFrame(geometry=geoms, crs="EPSG:4326"); si = gdf.sindex`.

2. **An R-tree is not automatically a win.** For axis-aligned predicates over rows already in numpy
   arrays, a vectorized mask answered in **0.171 ms** (50k rects) while the built index took 8 s to
   construct and then needed 3.36 ms per query — break-even was around *2,400 queries*. Reach for an
   index when you need many selective queries on large data or true geometry intersection; reach for
   a mask/`numpy` (or DuckDB/GIS SQL) for one-shot bbox filters.

3. **Bounds must be normalized in every dimension — and the error message lies about NaN.**
   `insert()` *and* query both raise `RTreeError: Coordinates must not have minimums more than maximums`
   when min > max, including when a coordinate is **NaN** (measured: NaN produced that same reversed-bounds
   message, never anything mentioning NaN). Sanitize with `np.nanmin/max` or drop the row; if you see that
   error and no obviously inverted extent, hunt for NaN. Inserting an empty bounds sequence gives
   `ValueError: Can only assign sequence of same size`.

4. **Invalid geometry yields plausible wrong numbers silently.** A self-intersecting "bowtie" polygon
   reports `is_valid == False` but `.area == 0.0` with no exception; after `shapely.make_valid()` the area is
   0.5. Check validity before trusting any area/union/intersection figure (malformed WKT, by contrast, does
   raise: `GEOSException IllegalArgumentException`).

5. **Axis order is silent and wrong-answer-prone.** `Transformer.from_crs("EPSG:4326","EPSG:32632")` uses the
   CRS's own axis order (lat, lon). Fed `(lon, lat)` it returned `(1432864.45, -8468390.66)` where the correct
   answer for that input is `(-5740793.34, 9102674.37)` — no warning at all. Pass **`always_xy=True`** on every
   transformer. Same trap in I/O: `gpd.read_file(path, bbox=...)` wants `(minx, miny, maxx, maxy)`; passing the
   lat/lon order returned **0 rows silently** (1 row for correct order).

## Unprojected-area trap

`.area` on lon/lat geometry is square *degrees*. For a ~Manhattan-sized box, `shapely.area` gave 0.0144 deg^2;
converting with the usual `111320**2 * cos(lat)` produced **~135 km² against a real land area of ~59 km²** — over
2x out from one formula, because that naive scaling ignores both ellipsoidal and parallel-length effects. Use
`pyproj.Geod(ellps="WGS84").geometry_area_perimeter(...)` or reproject to an equal-area CRS first.

## sjoin reads left-to-right

`gpd.sjoin(left, right, predicate=P)` evaluates `left_geometry P right_geometry`. With boxes on the left and
points inside them on the right: `predicate="within"` returned **0 rows** (a box is not within a point), while
`"contains"` and `"intersects"` each returned the expected 2. If a spatial join comes back empty, flip or
change the predicate before assuming missing data.

## API-shape traps found by probing (not from docs)

- **rtree 1.x removed `Index.save()`** — calling it raises `AttributeError`. Persistence is constructor-based:
  `index.Index("myidx")` writes `myidx.dat` + `myidx.idx`; reopen with the same basename (no extension).
  `.flush()`, `.close()`, `.dumps()`, `.loads()` exist on the index.
- **Legacy positional kwargs still work**: `rtree.index.Index(None, interleaved=False)` is accepted silently in
  1.4.1 — so constructor style tells you nothing about the installed version; read `rtree.__version__`.
- **whitebox python 2.3.x has no module-level tool functions.** `whitebox.breach_depression` raises
  `AttributeError`, and `whitebox.whitebox_tools` is now a *module*, so calling it raises
  `TypeError: 'module' object is not callable`. Use `w = whitebox.WhiteboxTools()` (575 snake_case methods) —
  note names differ from intuition, e.g. **`breach_depressions`** (plural), `fill_depressions_wang_and_liu`.
  First instantiation auto-downloaded the WhiteboxTools binary from whiteboxgeo.com non-interactively and
  reported `WhiteboxTools v2.4.0`; that download is a network dependency to expect on first use in CI/sandboxes.

## Don't share live index handles across processes

A `multiprocessing.Pool(2)` whose worker closure captured an `rtree` Index did not finish within 90 s
(spawn start method), while pickling an equivalent small index standalone completed instantly (583 bytes).
Do not pass a built handle into workers: rebuild per worker, or hand workers plain coordinate arrays and let
each build what it needs.

## Tool picks for this stack

| Need | Pick | Why / caveat |
|---|---|---|
| one-shot bbox filter on in-memory rows | numpy mask, or Duckdb/SQL | measured faster than building any index (rule 2) |
| repeated selective queries on vector data | `GeoSeries.sindex` (bulk) | STR packing; never an insert loop |
| geometry predicates beyond bbox (`dwithin`, true overlap) | shapely 2.x vectorized + sindex prefilter | `shapely.box/points/buffer` accept numpy arrays directly |
| file I/O, GeoPackage, bbox pushdown | pyogrio (GeoPandas default engine) | fast; but bbox axis order silently returns nothing (rule 5) |
| terrain/hydro morphology at scale | WhiteboxTools via `WhiteboxTools()` instance | binary auto-downloads; plural tool names |
| interactive map artifact, offline HTML | folium (`tiles=None` for airgapped) | 50 markers rendered to a self-contained 26.7 KB page |
| headless PNG from vector data + named geoprocessing tools, **no GDAL/QGIS/Qt** | `rustgis` (Session/Layer) | measured: GeoJSON in, 31.7 KB PNG out with no display; 43-tool dict catalog by id — see reference |

## Esri formats without an ArcGIS license

The starred ArcGIS/ArcPy material (awesome-arcgis, Packt's *Python for ArcGIS Pro*, WhiteboxTools-ArcGIS) all
assumes a licensed proprietary platform. Most data-exchange needs do **not** require it: pyogrio 0.13.0 reads
*and writes* Esri File Geodatabase through GDAL's `OpenFileGDB` driver with no Esri software installed — measured
writing `sample.gdb` (real `a0000000N.gdbtable` members) and reading it back with 2 rows, `EPSG:4326`, geometry
intact. ESRI Shapefile write works too (`s.shp/.shx/.dbf/.prj/.cpg`).

- Trap: **Int64 fields silently downgrade.** Writing an integer column produced
  `RuntimeWarning: Field v of type Integer64 will be written as a Float64. To get Integer64, use layer creation
  option TARGET_ARCGIS_VERSION=ARCGIS_PRO_3_2_OR_LATER`. A warning that changes your data types — pass the LCO or
  accept float ids (and never key joins on them).
- Driver discovery is `pyogrio.list_drivers()` / `list_drivers_details()` / `detect_write_driver()`; there is **no**
  `pyogrio.drivers` attribute in 0.13.0 (`AttributeError`).
- Still genuinely ArcGIS-only: arcpy tooling, `.mxd`/`.aprx` projects, and enterprise geodatabase connections —
  for those the license gate is real; do not promise a workaround.

## References

- `references/spatial-index-and-crs-measurements.md` — every number above with its probe recipe, plus the
  multiprocessing observation and how to re-run it.
- `references/rustgis-headless-binding-notes.md` — RustGIS's Python binding run live: the headless Session/Layer
  surface, PNG render without a GUI, machine-readable tool catalog, and its property-vs-method / optional-extras
  traps (2026-11-11).
- `references/geospatial-stack-freshness.md` — PyPI wheel reality for this stack on Python 3.14/Windows
  (which packages ship cp314 win_amd64 wheels vs pure-python/sdist), from live PyPI JSON, 2026-11-04.
- `references/arcgis-pro-project-and-arcpy-patterns.md` — the Esri-side layout read from a book-code repo:
  what a real `.aprx` chapter carries (file-.gdb as multi-file binary composite + shapefile sidecar sets =
  cloud-sync hazards, keep canonical geodata single-file), TIGER/Line `tl_<yr>_<st>_<layer>` naming with
  FIPS layer codes, and the GEOID join-without-spatial-join idiom (hierarchy encoded in the identifier;
  cursor-side SQL filters; prefix-LIKE fragility when trailing code widths vary) plus arcpy's capability map
  (AGOL item mgmt, print-layout automation, .tbx script tools). Source-read — arcpy needs an ArcGIS Pro install.
