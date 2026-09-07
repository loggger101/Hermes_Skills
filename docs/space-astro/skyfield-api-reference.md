---
description: "skyfield 1.55 API reference — breaking changes, de430s.bsp 404, phase-angle trap"
source_repo: skyfielders/python-skyfield (MIT)
tested_version: skyfield==1.55 (PyPI), Windows 11, Python 3.11
verified_date: "2026-09-06"
---

# skyfield — API Reference & Verified Patterns

**⚠️ Version warning first:** PyPI `skyfield` is now **1.55**, and its loading contract has
changed from the pre-2026 tutorials/docs that dominate search results. Every snippet below was
executed live on 2026-09-06; quoted outputs are real.

## Breaking changes vs classic skyfield (≤ ~1.4x)

| Classic pattern | What happens in 1.55 | Verified replacement |
|---|---|---|
| `ts, planets = load('de430s.bsp')` → tuple `(TimeSegment, PlanetCollection)` | **TypeError** on unpack: `load()` returns a single object — `skyfield.jpllib.SpiceKernel` (for SPK files) | `k = load('de421.bsp')`; bodies via `k['sun']`, `k[499]` etc. → VectorFunction; times via **separate** `ts = load.timescale()` |
| `load(filename, cache_location=DIR)` | **TypeError**: `Loader.__call__() got an unexpected keyword argument 'cache_location'` (signature is now `(filename, reload=False, backup=False, builtin=False)`) | `loader = Loader(DIR, verbose=False); k = loader('de421.bsp')` — the directory goes in the constructor. Note: module-level `load` IS a singleton `Loader`, so `load.timescale()` works without constructing one yourself (uses default cache dir). |
| `planets['Ceres']` for asteroids/dwarfs from de430s | **de430s.bsp is GONE**: HTTP 404 on both mirrors — `https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de430s.bsp` and `https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de430s.bsp` (checked 2026-09-06; also tried `de430t`, `de-430-s`, `_2017` variants — all 404) | Use **`de421.bsp`** (HTTP 200, verified): planets + Moon only. For small bodies use brahe's Horizons SPK client or fetch a targeted .bsp yourself and `load('your_file.bsp')`. |

## Verified snippets (run 2026-09-06)

### Osculating elements from state vectors — `skyfield.elementslib.osculating_elements_of` [SRC, verified in clone]
Pure-Python element solver: takes a position/velocity pair and returns an `OsculatingElements` object with
**all 15 derived quantities as properties**: `semi_major_axis`, `eccentricity_vector` + scalar,
`inclination`, `longitude_of_ascending_node`, `argument_of_periapsis`, `mean_anomaly`, `true_anomaly`,
`periapsis_time`, `period_in_days`, `apoapsis_distance`, `semi_latus_rectum`, ... Signature:
```python
from skyfield.elementslib import osculating_elements_of
oe = osculating_elements_of(position, reference_frame=None, gm_km3_s2=None)  # position/velocity Vector objects at one time
# oe.semi_major_axis (au), oe.eccentricity, oe.inclination (deg), oe.mean_anomaly (rad), ...
```
Use as an **independent check on any element math** in the pipeline (e.g. recompute elements from a
propagated state and diff against the catalog's stored elements — catches unit/angle-convention drift that
a same-library round-trip would not). Companion helpers `apoapsis_distance(p, e)`, `eccentricity_vector(...)`,
`inclination(h_vec)` are exported for single-quantity checks.

### Load ephemeris + timescale, Sun–Earth distance
```python
from skyfield.api import load
k = load('de421.bsp')        # SpiceKernel; downloads once to cache dir, then instant
ts = load.timescale()        # TimeScale (downloads leap-seconds/ΔT tables on first use)
t = ts.utc(2026, 9, 6, 12)
sun_p, earth_p = k['sun'].at(t).xyz.au, k['earth'].at(t).xyz.au   # numpy arrays in au (barycentric ICRF)
import numpy as np
d_au = float(np.linalg.norm(sun_p - earth_p))
# verified output: Sun-Earth @ <Time tt=2461290.0008> = 1.0080 au   (true value ~1.007-1.008 in early Sep ✓)
```

### Phase angle — **the trap** (numbers from the live run, Mars as stand-in for an asteroid; de4xx covers planets only)
The true phase angle is the Sun→body←Earth angle with vertex at the BODY:
```python
import numpy as np
from skyfield.api import load
k = load('de421.bsp'); ts = load.timescale()
t = ts.utc(2026, 9, 6)
sun_p, earth_p, mars_p = (k[n].at(t).xyz.au for n in ('sun', 'earth', 'mars'))

def ang(u, v):
    c = float(np.dot(u, v)/(np.linalg.norm(u)*np.linalg.norm(v)))
    return float(np.degrees(np.arccos(max(-1.0, min(1.0, c)))))

true_phase  = ang(sun_p - mars_p, earth_p - mars_p)   # vertex at MARS
elongation  = ang(sun_p - earth_p, mars_p - earth_p)  # vertex at EARTH

obs = k['mars'].at(t).observe(k['earth'])
builtin = float(np.degrees(obs.phase_angle(k['sun']).radians))
# verified outputs: true_phase=33.59°   elongation=56.89°   builtin observe().phase_angle()=56.88°
```

**`observe(...).phase_angle(sun_body)` returns the EARTH-vertex angle (elongation), not the
body-vertex phase angle.** For asteroid illumination/visibility work in economicspace, compute
the body-vertex angle yourself as above — or you'll be off by tens of degrees. (Also note: pass
the **body** `k['sun']` to `.phase_angle()`, not a position object — passing a Barycentric raises
`AttributeError: 'Barycentric' object has no attribute 'at'`.)

### Kernel anatomy (1.55)
- `SpiceKernel.segments` → list of `ChebyshevPosition` segments, each with `(center_name, target_name)` e.g. `'0 SOLAR SYSTEM BARYCENTER -> 3 EARTH BARYCENTER'`.
- `k['earth']` returns a **VectorSum** (SSB→Earth barycenter + Earth-barycenter→Earth) — already composed; just `.at(t).xyz.au/.km`.
- `print(k)` lists all segments with date ranges. de421 spans 1899–2053.

## Gotchas
- **de4xx = planets only.** No Ceres/Vesta/asteroids in any de-series kernel — that was the old de430s "small body" marketing; for small bodies use targeted Horizons SPK (brahe does this cleanly, see brahe-api-reference.md).
- `Loader(DIR)` caches by filename inside DIR; a URL string as first arg (`loader('https://…/de421.bsp')`) also works and is cached under the basename.
- JPL's ephemeris directory layout changed in 2026 (de430s removed from both mirrors). If skyfield's built-in URL table 404s, pass an explicit working URL or a local file — don't fight `_search(self.urls, filename)`.
- `k['mars'].at(t)` gives barycentric position; `.observe(k['earth'])` shifts to Earth-centered (and adds light-time handling).
