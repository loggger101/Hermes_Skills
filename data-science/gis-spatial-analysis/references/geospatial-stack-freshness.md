---
description: "PyPI distribution reality for the Python geospatial stack on Windows/Python 3.14+: which packages ship ABI-free vs per-minor-version wheels, free-threaded (cp314t) coverage, and the one whose analysis binary is not on PyPI at all"
source_repo: live PyPI JSON API (pypi.org/pypi/<pkg>/json), 2026-11-04; context repos Toblerity/rtree, opengeos/WhiteboxTools-ArcGIS, giswqs/geog-312
tested_version: "release metadata as fetched 2026-11-04: rtree 1.4.1, shapely 2.2.0, geopandas 1.2.0, pyogrio 0.13.0, whitebox 2.3.6, pint 0.26.2, folium 0.20.0 (galpy 1.12.1 checked in the same pass)"
verified_date: "2026-11-04"
---

# Geospatial stack freshness / wheel reality (Windows)

Checked against PyPI JSON on **2026-11-04**. This is about *installability*, which is where geospatial work
actually stalls — the API docs assume a working environment. Re-fetch before quoting; wheel coverage moves
with every CPython minor release.

| Package | Latest (2026-11-04) | Wheel shape | Consequence on Python 3.14 / Windows |
|---|---|---|---|
| `rtree` | 1.4.1 | **ABI-free platform wheels**: `py3-none-win_amd64`, `py3-none-win_arm64`, manylinux/musllinux/macOS, + sdist | installs on any CPython 3.x including free-threaded builds; libspatialindex is bundled in the wheel |
| `shapely` | 2.2.0 | per-minor-version wheels only: cp311–cp315 (incl. **cp314 / cp314t**), win_amd64 + win32 + win_arm64, + sdist | fine on 3.14 today; no `abi3`, so a *new* CPython minor waits on a new wheel — and building from sdist needs GEOS + a compiler |
| `pyogrio` | 0.13.0 | **cp311-abi3** win_amd64/mac/linux, plus explicit cp310 and cp314t builds, + sdist | abi3 covers 3.11+; free-threaded needs the dedicated `cp314t` asset. GDAL is vendored in the wheel |
| `geopandas` | 1.2.0 | pure Python (`py3-none-any`) + sdist | installs anywhere, but it is only as good as its I/O engine (pyogrio) and pyproj underneath |
| `whitebox` | 2.3.6 | pure Python wrapper (`py2.py3-none-any`) + sdist | **the analysis binary is not on PyPI.** First use downloads WhiteboxTools (~v2.4.0) from whiteboxgeo.com into site-packages — fails offline / read-only installs, and needs write permission there |
| `pint` | 0.26.2 | pure Python + sdist | no wheel risk (units library; pairs with the Rust `uom` notes in `rust-crate-picks`) |
| `folium` | 0.20.0 | pure Python (`py2.py3-none-any`) + sdist | renders offline HTML; tile layers still need network unless `tiles=None` |

Also fetched in the same pass, for astro work: **`galpy` 1.12.1 ships cp314 win_amd64 wheels** (so galactic-dynamics
work is installable on this box's Python without a compiler). This paragraph previously claimed ANISE
had no PyPI distribution and had to come from its Rust crate; **that was wrong (corrected
2026-11-05)**. `pip install anise-py` does return HTTP 404, but that only proves the *hyphenated guess*
is absent — ANISE publishes on PyPI under its plain project name, **`anise` v0.10.6** (requires-python
>=3.9, license **MPL-2.0**, homepage `nyxspace.com`, source `github.com/nyx-space/anise`), so the
Python binding installs directly with no Rust toolchain or maturin build. Rule worth keeping: **a 404 on
a guessed name is not evidence of absence** — check the plain project name, and record the license when
you cite a package (`anise` is MPL-2.0, not MIT).

## Practical rules from this table

1. Prefer packages with ABI-free or abi3 wheels when the target is "any Python" (`rtree`, `pyogrio`).
   Per-minor-version packages (`shapely`) are the ones that break on a fresh interpreter upgrade — check
   before promising an environment rebuild works.
2. A pure-Python wheel is not evidence of a self-contained tool: `whitebox` proves the wrapper installs while
   the actual binary arrives at first execution from a third-party host. Treat "pip install succeeded" as
   necessary, never sufficient — run one real tool call before trusting a pipeline step.
3. Free-threaded Python (cp314t) coverage is uneven: present for shapely/pyogrio here, absent elsewhere. If the
   plan involves `python3.14t`, verify per package rather than assuming ecosystem-wide support.
