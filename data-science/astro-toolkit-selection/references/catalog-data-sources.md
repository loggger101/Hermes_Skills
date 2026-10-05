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

## astroquery — 58 service subpackages in the 0.4.11 release (69 in repo main), async variants carry the real signatures [SRC + RUN 2026-10-05]

Clone layout: `astroquery/<service>/core.py` (NOT flat `<service>.py`). **Run on the released package (PyPI `astroquery` 0.4.11, installed in a Python 3.12 venv, 2025-09-20 release):** `pkgutil` finds **58** service subpackages (the clone of main read on 2026-09-05 had 69, so main is ahead of the release). For the JPL services the plain methods are generated wrappers: `HorizonsClass.ephemerides`, `elements`, `vectors` and `SBDBClass.query` show the signature `(self, *args, **kwargs)`, while the `*_async(...)` variants hold the real **keyword-only** parameters (`ephemerides_async(*, airmass_lessthan=99, ..., refsystem='ICRF', ...)`, `query_async(self, targetid, *, id_type='search', neo_only=False, ...)`). Read parameters from the `_async` signature. **Not every service follows that pattern**: `Simbad` in 0.4.11 is TAP-based (`query_object(object_name, *, wildcard, criteria, get_query_payload, async_job, verbose)`, `query_tap(query, *, maxrec=10000, async_job, ...)`, **no `query_object_async`**), so check the class before assuming. Importing `astroquery.gaia` printed a Gaia-archive maintenance notice on stdout.

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
| `solarsystem.neodys` | `NEODySClass.query_object(object_id, *, orbital_element_type="eq"\|"ke", epoch_near_present=0)` → dict with **`COV`: full 6×6 covariance matrix**, `COR` correlation (Keplerian), `KEP` + `EQU` state vectors (au/deg; equinoctial = higher precision per docstring), `MAG` H+G, `MJD`. One HTTP call per object — scope to the top-N of a ranking, never 1.5 M rows [SRC] | **orbit-quality uncertainty as an error bar rather than a U cutoff** (the open modelling decision in economicspace); University of Pisa service, not ESA |
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

**Run 2026-10-05 (pds4-tools 1.4 on Python 3.14.6 + numpy 2.5.3, synthetic PDS4 product).** It installs and imports with
numpy 2. A hand-made label (`Product_Observational` with an `Array_2D`, 3 x 4, `SignedLSB2`) and a 24-byte data file read as follows:

| Case | Result |
|---|---|
| Plain read | `product[0].data` dtype `<i2`, shape `(3, 4)`; `StructureList` has one structure with id `image` |
| `scaling_factor 0.5` + `value_offset 10` | **scaling is applied by default and the dtype becomes float64**: `[10.0, 10.5, 11.0, 11.5]`; `no_scale=True` returns the raw `<i2` `[0, 1, 2, 3]` |
| `SignedMSB2` label over the same bytes | values `[0, 256, 512, 768]`: the label's declared byte order is honoured, so a wrong `data_type` gives plausible-looking garbage rather than an error |
| `meta_data` on the array | keys include `Axis_Array`, `Element_Array`, `axes`, `axis_index_order`, `local_identifier`, `offset` |
| `lazy_load=True` | returns a `PDS_ndarray` of the right shape |
| Data file missing | `OSError: Unable to read data from file ...` |
| Data file shorter than the label says (6 of 24 bytes) | **`ValueError: cannot reshape array of size 3 into shape (3, 4)`**: a raw numpy error that does not name the file or the label |
| Unknown `data_type` (`Bogus99`) | `ValueError: itemsize cannot be zero in type` (cryptic) |
| `IEEE754LSBSingle` over 24 bytes | `ValueError: cannot reshape array of size 6 into shape (3, 4)` |
| Path containing a non-ASCII folder name | works |

So: validate file sizes against the label (`rows x cols x itemsize`) before reading, and treat byte-order and scaling declarations in
the label as load-bearing. Tables (`Table_Binary`, `Table_Character`) were not exercised.

## cumulus — NASA Earth-science cloud ingest framework; two reusable packages [SRC + `@cumulus/pvl` RUN 2026-10-05]

`nasa/cumulus` is **not** a planetary-data tool: it is the "Cumulus Framework", an AWS-based data ingest, archive,
distribution and management system for NASA EOSDIS Earth-science streams (a monorepo of about 30 `@cumulus/*` packages,
Apache-2.0). Two packages are reusable on their own:

- **`@cumulus/pvl`** (npm 22.4.3, modified 2026-10-03) exports `pvlToJS`, `jsToPVL`, `parseValue`, `models`. **It is not a
  full PDS3/PVL grammar.** The same inputs run through it and through Python `pvl` 1.3.2:

  | PVL input | `@cumulus/pvl` | Python `pvl` 1.3.2 |
  |---|---|---|
  | `SOLAR_LONGITUDE = 120.5 <deg>` (unit) | **error** `Failed to parse value` | `[120.5, "deg"]` |
  | `D = 16#FF#` (based number) | **error** | `255` |
  | `S = {A,B,C}` and `Q = (1,2,3)` | **error** | frozenset / `[1, 2, 3]` |
  | multi-line quoted string | **error** | `"line one line two"` |
  | `NOTE = "he said ""hi"""` (doubled quote) | error | error (`LexerError`) |
  | `A = 1 /* trailing comment */` | value becomes the *string* `"1 /* trailing */"` | `1` |
  | `OBJECT = IMAGE ... END_OBJECT` | stored under the key `OBJECT` with `identifier: IMAGE` | `{"IMAGE": {...}}` |
  | `D2 = 2004-003T12:00:00` (day of year) | text string | parsed datetime |
  | `B = NULL` | the string `"NULL"` | `None` |
  | missing `END` | accepted | accepted |
  | duplicate keys | both kept in `store` | both kept |

  Other JS facts: it returns a model object (`{store: [[key, value]...], type: 'ROOT'}`), not a plain object, and
  `jsToPVL({A: 1})` on a plain object throws `TypeError: pvlObject.toPVL is not a function` (it expects its own model).
  So the earlier "reference implementation of the label grammar" description was wrong. For PDS3 labels use Python `pvl`;
  for PDS4 (XML) use `pds4_tools` (above). `@cumulus/pvl` is only safe for simple `KEY = value` metadata files.
- **`@cumulus/cmr-client`** — NASA CMR search/ingest API client with Launchpad token refresh; endpoints documented in its
  `API.md` (source-read; not run).

## space-map export format — ready-made ephemeris shipping schema [SRC]

Full binary spec captured from the repo's docs/export-format: 24-byte common header + per-body 32-byte headers;
**float64 JD segment bounds, float32 Chebyshev coefficients**; Clenshaw evaluation recipe with a parent-chain walk
to SSB-relative km. Stated precision: sub-km for inner moons. If the pipeline ever needs to *ship* ephemeris data
instead of fetching it, this is the schema — don't invent one.

Details verified from `docs/export-format/` (2026-09-07):

- **Validity-window rule**: every file carries `start_jd`/`end_jd` (float64 TDB; ±Infinity = unbounded). Consumers must
  *hide* bodies outside the window rather than propagate — SGP4 files are bounded to `min(epoch) − 14d … max(epoch) + 14d`;
  Keplerian/parabolic get Infinity (mathematical solutions); short-arc fits are "not trustworthy far out".
- **Elements payload** (format byte 0): columnar, zero-copy typed arrays; sub-format `Keplerian|Parabolic|SGP4`; file-level
  bytes for source provider (`horizons/sbdb/celestrak/spice`) and id type — one provider per zone/part is pipeline-enforced.
- **Secular-drift columns** `om_dot`/`w_dot` (deg/day): populated by a numerical mean-element fit so small moons capture
  J2/J4 nodal regression + apsidal precession without shipping Chebyshev coefficients; propagation = linear drift from epoch.
- **Chebyshev payload** (format byte 1): per-(zone, time-chunk) gzipped `.bin.gz`; zones split into a coarse always-loaded set
  (`major` planets/dwarfs/barycenters + `major_asteroids` ~15 perturbers incl. Psyche/Vesta/Pallas) and per-parent moon zones with
  density-scaled chunk cadence (Saturn's shepherds at 0.125 y chunks).
- **Object IDs**: `{prefix}-{numeric}` (`spkid-`, `naif-`, `norad_satcat-`); compound ids for SBDB moons; per-point flags carry
  NEO/PHA bits from SBDB.

### space-map embed SDK (`spacemap` on npm, 0.1.8, 2026-10-04) [SRC, not run]

The repo also publishes a browser SDK for embedding its solar-system map (three.js; `createMap({container})`, flat maps,
surface panoramas, a system diagram). Facts from its README and package template:

- MPL-2.0 code; **data and imagery keep their sources' terms**, and the credit line it draws cannot be removed.
- Imagery is ranked: **open** (default, any use), **non-commercial** (needs `includeNonCommercial: true`; for example the Uranus
  map and the Huygens panorama of Titan; without the flag Uranus renders as a flat colour), and **site-only** (never reaches the SDK).
- Units are km and degrees. Bodies use export ids: `naif-399` (Earth), `spkid-20000004` (Vesta), `norad_satcat-25544` (ISS).
- Load as one ES module from the jsDelivr CDN (`.../spacemap@0.1.8/dist/spacemap.js`) or an IIFE build; versions are immutable,
  so pin one and add an `integrity` sha384 digest. From npm it needs `three` (^0.183) as a peer dependency.
- No key and no quota "for now"; releases 0.1.5-0.1.8 in two days (2026-10-03/04) added `setPinnedBodies`, a map-less
  distance/position call, and an attribution-bar fix: the API is moving fast.
- The browser SDK is not a data library: for numbers use the export format above or the tools in `SKILL.md`.

## Pipeline placement

SBDB (`covariance=` + physical params) → brahe Horizons SPK (ephemeris math) → pds4_tools (archive products).
astroquery's MPC/IMCCE services are fallbacks when JPL endpoints are down or raw observations are needed.
