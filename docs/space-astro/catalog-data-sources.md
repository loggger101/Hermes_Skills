---
description: "astroquery + pds4_tools + cumulus — catalog/archive access for the small-body pipeline"
source_repos: astropy/astroquery (BSD-3), Small-Bodies-Node/pds4_tools, NASA-cumulus/cumulus
tested_version: clones @ 2026-09-05; astroquery async-first API, pds4 v1.5.dev0
verified_date: "2026-09-06"
---

# Catalog & Archive Data Sources (astroquery, pds4_tools, cumulus)

Companion to [brahe-api-reference.md](./brahe-api-reference.md): brahe does the ephemeris math;
this file covers **catalog metadata**, **archive products**, and NASA's data-service clients.
All facts source-read from clones (no agents).

## astroquery — 69 service modules, async-first API [SRC]

Clone layout: `astroquery/<service>/core.py` (NOT flat `<service>.py`). Every query method is now
`*_async(...)` with **keyword-only args**; sync wrappers exist but the docs target the async names.

### jplsbdb.SBDBClass — the pipeline's metadata workhorse
```python
from astroquery.jplsbdb import SBDBClass
d = SBDBClass().query_async("1 Ceres", id_type="search",   # 'spk' (SPICE kernel id) / 'desig' also valid
                            full_precision=True, phys=True,
                            covariance='mat',               # None | 'mat' | 'vec' | 'src'
                            close_approach=True, radar=True, virtual_impactor=False,
                            solution_epoch=False, neo_only=False, cache=True)
```
- Returns an `OrderedDict`. **The `covariance` flag is the sleeper feature**: full matrix (`'mat'`),
  upper-triangular vector (`'vec'`), or Cholesky square-root form (`'src'`) — orbital uncertainty
  straight from JPL, no separate fetch.
- `close_approach=True` + `radar=True` + `virtual_impactor=False/True` = impact-risk data in the same call.
- `solution_epoch=True` → orbit at the **JPL solution epoch** (not the MPC epoch) — matters when comparing solutions.

### jplhorizons.HorizonsClass — ephemerides / elements / vectors [SRC]
```python
from astroquery.jplhorizons import HorizonsClass
h  = HorizonsClass(id="433")   # Eros; or 'Ceres', SPK id, ...
eph  = h.ephemerides_async(start_time=..., stop_time=..., location='500@10')
elem = h.elements_async()      # refsystem='ICRF', refplane='ecliptic', tp_type='absolute'|'relative'
vec  = h.vectors_async(aberrations='geometric', delta_T=False)
```
- **GOTCHA (verified in source):** `quantities` defaults to `conf.eph_quantities` = **ALL 43 output quantities**.
  Request only what you need or every response bloats ~10x.
- Observation-constraint filters are first-class kwargs: `airmass_lessthan=99`, `solar_elongation=(0,180)`,
  `max_hour_angle=0`, `skip_daylight=False`, `refraction=False`.

### Other small-body-relevant services (verified class/method names) [SRC]
| Service | Class → key methods | Use |
|---|---|---|
| `mpc` | `MPCClass.get_observations_async(targetid)` — ALL reported obs; `get_ephemeris_async`, `query_objects_async(target_type=...)` (mission catalogs), observatory code lookups | raw observation archive, MPC ephemerides |
| `imcce.miriade` | `MiriadeClass.get_ephemerides_async(targetname, *, objtype='asteroid', epoch_step='1d')` | quick asteroid ephemeris (no auth) |
| `imcce.skybot` | `SkybotClass.cone_search_async(coo, rad, epoch, *, location='500', position_error=120)` | sky-survey cone search in arcsec |
| `solarsystem.neodys` | `NEODySClass.query_object(object_id)` | NEO risk/encounter data (ESA) |
| `solarsystem.pds` | `RMSNodeClass.ephemeris_async(planet)` | PDS Ring-Moon Systems Node — moon/ring ephemerides |
| `vizier` | `VizierClass.find_catalogs(keywords)`, `query_object_async`, `query_region_async`; builder props `columns/column_filters/ucd/catalog` | any CDS catalog; TAP gotcha: always `SELECT *` + recno pagination (see space-data-pipelines skill) |

## pds4_tools — reading PDS4 archive products [SRC]
```python
from pds4_tools.reader import pds4_read
product = pds4_read("file.pds", lazy_load=False, no_scale=False, decode_strings=True)
# product: StructureList (label + all data structures); .info(abbreviated=True), indexable by name/type
arr = product["data"]          # PDS_ndarray / PDS_marray — numpy arrays WITH a .meta_data attribute
```
- **Metadata rides with the array** (`PDS_ndarray.meta_data`) — spectral characteristics, display settings,
  field definitions survive into analysis without re-parsing labels.
- Full label object model available if needed: `Label`, `TableStructure`/`TableManifest` + `Meta_Field*`
  (Character/Binary/Delimited/UniformlySampled/Bit), `ArrayStructure`/`ArraySection`, plain-text and FITS header parsers.

## cumulus — NASA's PDS label parser + CMR client [SRC]
30-package monorepo; the two pipeline-relevant pieces:
- **`pvl`** — PDS (label) format parser: `pvlToJS(labelString)` / `jsToPVL(obj)`. JS, but it is the reference
  implementation of the label grammar that pds4_tools parses in Python.
- **`cmr-client`** — NASA CMR search/ingest API client with Launchpad token refresh; endpoints documented in its `API.md`.

## space-map export format — ready-made ephemeris shipping schema [SRC]
Full binary spec captured from the repo's docs/export-format: 24-byte common header + per-body 32-byte headers;
**float64 JD segment bounds, float32 Chebyshev coefficients**; Clenshaw evaluation recipe with a parent-chain walk
to SSB-relative km. Stated precision: sub-km for inner moons. If the pipeline ever needs to *ship* ephemeris data
instead of fetching it, this is the schema — don't invent one.

## Pipeline placement
SBDB (`covariance=` + physical params) → brahe Horizons SPK (ephemeris math) → pds4_tools (archive products).
astroquery's MPC/IMCCE services are fallbacks when JPL endpoints are down or raw observations are needed.
