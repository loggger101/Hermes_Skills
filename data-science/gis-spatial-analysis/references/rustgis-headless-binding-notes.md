# RustGIS from Python — what `pip install rustgis` actually gives you

Repo: `opengeos/RustGIS` (created 2026-10-10, ~2.6k stars within a month of launch, Apache-2.0,
`rustgis.app`). A GIS written in pure Rust — desktop app, WASM web app, CLI where every GUI action is also a
scriptable command id, and 1000+ GeoLibre/Whitebox-style tools.

Everything below was **run** here on Windows with `pip install rustgis` (v0.6.0) in a Python 3.14 venv,
2026-11-11. Wheels are `cp312-abi3-win_amd64` / `-win_arm64`, `requires_python >=3.12` — abi3, so they load on
every Python from 3.12 up including 3.14.

## The headless surface is small and it works without GDAL, QGIS or a display

`import rustgis` exposes only `Session`, `Layer` and `RustGISError` as real API (plus leaked typing/os names).
Measured end-to-end on a hand-written GeoJSON with a Point and a Polygon:

- `s = rustgis.Session()`; `layer = s.add_geojson(path)` -> returns a **Layer** object directly.
- `s.layer_names` -> `['GeoJSON']`; the layer reports `fields()`, `count()`, `bounds()`, `filter()`,
  `select()/selected`, `style()`, and exports via `to_geojson()` / `to_geopandas()` / `to_file()`.
- **`s.to_png(width=320, height=240)` returned a real PNG (31,682 bytes) with no GUI and no display.** That is the
  interesting capability: map images for reports/agents from a headless process, no Qt, no browser.
- `s.tools()` returns **43 tools as plain dicts** — `{id, name, params:[{kind,label,name,required}], summary,
  toolbox}` (e.g. `polygonToLine`, `checkGeometry`, `repairGeometry`). Because the catalog is machine-readable
  and each entry has an `id`, a tool run is data rather than code: enumerate -> pick by id -> dispatch.
- Session also carries `commands`, `run`/`run_tool`, undo/redo, project save/load (`project_json`, `.rgis`),
  basemap/center control, and `add_tiles` / `add_pmtiles` for raster/pyramid sources.

## Traps measured (not guessed)

- **The widget layer is an optional extra.** Touching the map widget raises
  `ImportError: rustgis.Map needs anywidget: pip install "rustgis[jupyter]"`. The message names the fix, but note
  it fires on *attribute access*, not import — so a script that only wants headless data can still die if it does
  `from rustgis import *`-style probing or checks for `Map`. Keep to Session/Layer when running unattended.
- **Property vs method is inconsistent.** Some accessors are plain attributes returning lists (`layer_names`) and
  calling them raises `TypeError: 'list' object is not callable`; others need the call. Probe with
  `[n for n in dir(obj) if not n.startswith('_')]` plus one guarded read before writing a loop against this API.
- Extras declared by the wheel metadata: `[geopandas]`, `[jupyter]` (anywidget), `[qt]` (pyside6), `[test]`.
  There are **no console entry points** in the Python distribution — the CLI lives in the app, not the wheel. If
  you need `rustgis-cli`, that is a different install than `pip install rustgis`.
- `Layer(path)` / `Layer(name, path)` do not construct usable layers standalone (`TypeError: missing 1 required
  positional argument: 'layer'`; passing strings then dies inside on `_find_layer`). Layers come *from* a Session —
  add data through the session and take the returned object.

## Where it fits against this skill's Python stack

- It does **not** replace GeoPandas/Shapely for analysis: there is no predicate/join engine here comparable to
  `sjoin`/shapely vectorized ops, and geometry repair comes as named tools (`repairGeometry`) rather than library
  calls you compose.
- It does offer, in one self-contained wheel with no GDAL runtime: GeoJSON load/export, optional GeoPandas bridge,
  tile/PMTILE sources, symbology/project state, undo history and headless PNG rendering. For 'produce a map image
  or run a named geoprocessing tool inside an agent sandbox', that is a materially lighter dependency than the
  GDAL/QGIS stack.
- The repo ships its own `skills/` directory — third starred project this pass to vendor SKILL.md files next to
  code (see `docs/starred-repos-ledger.md`). Treat those as upstream docs, not as skills to import blind: the
  ledger's intake rule is verify-then-port.
