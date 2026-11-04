---
description: "Measured cost/correctness behaviour of the Python vector-GIS stack on Windows/py3.14: R-tree build vs bulk sindex (8.07s vs 0.048s), numpy mask beating an index, rtree bounds/NaN error contract, save() removal, silent wrong answers from CRS axis order and read_file bbox, invalid-geometry area==0.0, WhiteboxTools API shape"
source_repo: Toblerity/rtree (MIT) + opengeos/WhiteboxTools-ArcGIS context; probed directly against PyPI releases rather than repo docs
tested_version: "LIVE RUN 2026-11-04 on Windows 11, isolated venv (`python -E`, uv-created CPython 3.14.7): rtree 1.4.1, shapely 2.2.0 (GEOS 3.14.1), geopandas 1.2.0, pyogrio 0.13.0, pyproj 3.8.0, numpy 2.5.4, pandas 3.1.0, whitebox 2.3.6 / WhiteboxTools v2.4.0 binary, folium 0.20.0"
verified_date: "2026-11-04"
---

# Spatial index and CRS behaviour — measured numbers

All figures are from a single probe session on the owner's Windows box in an isolated venv (see
`../../../software-development/python-craft/references/venv-isolation-and-pythonpath-windows.md` for why
isolation had to be forced). Timings are wall-clock `time.time()` deltas, best-of-runs where repeated.

## 1. Index construction cost dominates everything else

| Construction path | n=50,000 rectangles | Query time | Hits |
|---|---|---|---|
| `rtree.index.Index()` + per-row `.insert()` loop | **8.07 s** (also measured 8.40 s) | 3.22–3.36 ms | agrees with brute force |
| `GeoSeries.sindex` bulk build (STR packing) | **0.048 s** | 0.26 ms | identical hit set to numpy mask |

Building the geometry objects themselves was cheap by comparison: vectorized `shapely.box(x, y, x+0.02,
y+0.02)` over 50k coordinate arrays took **0.101 s**. So ~99% of the slow path is incremental insertion into
libspatialindex through ctypes, not geometry construction.

**Idiom:** construct all geometries vectorized, wrap in a GeoDataFrame, and let `.sindex` bulk-build. An
insert loop is only defensible for streaming data that cannot be held at once.

## 2. Brute force / vectorized mask comparison (why an index can lose)

Same 50k rectangles, same query window `(-18,-9,18,9)`:

| Method | Time | Hits |
|---|---|---|
| numpy boolean mask over coordinate arrays (`(x<=e)&(x+w>=minx)&...`) | **0.171 ms** (best of 3) | 503 |
| rtree index query, after paying the build | 3.36 ms | 503 |
| pure-Python loop over tuples (the naive baseline people measure against) | 19.5 ms | 533* |

\* different RNG draw; matched its own index result exactly (`agree=True` in both runs).

Break-even for the rtree build at this size is roughly **2,400 queries**. Also measured: 200 random
large windowed queries cost 1805.9 ms total (9.03 ms/query) because output volume dominated — selectivity,
not index structure, decides whether an index pays off.

## 3. rtree input contract and its misleading message

| Input | Result |
|---|---|
| `insert(id, (nan, 0.0, 1.0, 1.0))` | `RTreeError: Coordinates must not have minimums more than maximums` — **no mention of NaN** |
| `insert(id, (5, 5, 1, 1))` (min > max) | same `RTreeError` |
| query window with min > max (hit while generating random windows) | same `RTreeError`, raised from `get_coordinate_pointers` |
| `insert(id, ())` | `ValueError: Can only assign sequence of same size` |
| 3-D index via `index.Property(); p.dimension = 3` | works; query takes 6 floats and returns the id |

Because NaN is reported as a reversed-bounds problem, an agent that trusts the message will go looking for
swapped columns and never find the real cause. Check `np.isnan(...)` first whenever this error appears with
data from any pipeline that can produce missing values.

## 4. Persistence API (rtree 1.x)

- `Index.save(path)` **does not exist** in rtree 1.4.1 → `AttributeError: 'Index' object has no attribute 'save'`.
  Tutorials showing `idx.save("myindex")` are pre-1.0 and will crash.
- Persistent storage is chosen by the constructor: `index.Index(os.path.join(d, "spatial"))` created
  `spatial.dat` + `spatial.idx`; reopening with that same **basename** (no extension) returned all 20 rows.
- Other index members worth knowing (from `dir()`): `add`, `bounds`, `clearBuffer`, `close`, `contains`,
  `count`, `deinterleave`, `delete`, `dumps`, `flush`, `get_bounds`, `get_size`, `intersection`,
  `intersection_v`, `leaves`, `loads`, `nearest`, `nearest_v`, `result_limit`, `set_result_offset`, `valid`.
- Legacy positional style `index.Index(None, interleaved=False)` is still accepted silently in 1.4.1 — do not
  use constructor style to infer a version.

## 5. Silent wrong answers (the expensive category)

| Trap | Measured behaviour |
|---|---|
| Self-intersecting polygon ("bowtie") | `is_valid == False`, `.area == **0.0**` with no exception; after `shapely.make_valid()` area is 0.5 |
| Malformed WKT (unclosed ring) | raises `GEOSException: IllegalArgumentException: Points of LinearRing do not form a closed linestring` (this one *is* loud) |
| `Transformer.from_crs("EPSG:4326","EPSG:32632")` fed `(lon, lat)` | returned `(1432864.45, -8468390.66)`; the same transformer fed `(lat, lon)` gave `(-5740793.34, 9102674.37)`. No warning either way |
| Same with `always_xy=True` and `(lon, lat)` → EPSG:3857 | `(-8238310.24, 4970071.58)` — correct-looking Web Mercator values |
| `gpd.read_file(gpkg, bbox=(-80,40,-70,45))` (x,y order) | **1 row** (correct) |
| `gpd.read_file(gpkg, bbox=(40,-80,45,-70))` (y,x order) | **0 rows**, silently |
| `.area` on lon/lat then naive deg²→m² (`111320**2*cos(lat)`) | 0.0144 deg² → ~135 km² for a box whose real land area is ~59 km² (>2x error). Use `pyproj.Geod(...).geometry_area_perimeter` or an equal-area CRS |
| `gpd.sjoin(boxes, points, predicate="within")` | **0 rows** — predicate reads left-to-right; `"contains"`/`"intersects"` returned the expected 2 pairs |

GeoPandas' GeoDataFrame read back from GeoPackage preserved `EPSG:4326`, geometry type and coordinates
(`POINT (-74.006 40.713)` round-tripped); first `to_file` in a fresh process cost ~4.6 s (driver warm-up).

## 6. WhiteboxTools from Python, 2.3.x reality

- Module-level tool functions are gone: `whitebox.breach_depression(...)` → `AttributeError`.
- `whitebox.whitebox_tools` is a **module**, so the old call form raises `TypeError: 'module' object is not callable`.
- Public surface of the package root: `Runner`, `WhiteboxTools`, `download_wbt`, `whitebox`, `whitebox_tools`.
- Correct usage is an instance: `w = whitebox.WhiteboxTools()` exposing **575** snake_case methods. Names are
  not always what intuition suggests — there is no `breach_depression`; the real names include
  `breach_depressions`, `breach_depressions_least_cost`, `fill_depressions_planchon_and_darboux`,
  `fill_depressions_wang_and_liu`.
- First instantiation printed: `Downloading WhiteboxTools pre-compiled binary for first time use ...` →
  fetched `WhiteboxTools_win_amd64.zip` from whiteboxgeo.com, decompressed into the package directory, then
  also began fetching testdata. Non-interactive (no prompt blocked). `w.version()` reported
  **WhiteboxTools v2.4.0 (c) Dr. John Lindsay 2017-2023**. Plan for that download in CI/sandboxed runs; it is a
  network dependency separate from pip, and it writes inside site-packages (read-only installs will fail).

## 7. Multiprocessing observation (reported as observed, mechanism not proven)

A `multiprocessing.Pool(2)` whose worker function closed over an rtree `Index` did **not complete within
90 s** under the Windows spawn start method (`subprocess.TimeoutExpired`; parent had already built the index).
Pickling a comparable small index standalone finished instantly and produced 583 bytes, so "indexes cannot be
pickled" is *not* supported by these observations. What is safe to say: do not hand a live index handle to
pool workers on Windows — rebuild per worker or pass coordinate arrays. Re-test before stating a cause.

## Reproduction recipe

```text
uv venv C:/Users/you/AppData/Local/Temp/gis2 --python 3.14        # native path, not /tmp/...
VIRTUAL_ENV="C:/Users/you/AppData/Local/Temp/gis2" uv pip install rtree shapely pyogrio geopandas
"C:/Users/you/AppData/Local/Temp/gis2/Scripts/python.exe" -E -c "import rtree,shapely;print(rtree.__file__)"
```

`-E` matters: without it an ambient `PYTHONPATH` can resolve these imports from a *different* environment.
Confirm with `module.__file__`, never with the install log alone.
