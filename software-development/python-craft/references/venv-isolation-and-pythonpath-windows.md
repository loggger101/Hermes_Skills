---
description: "Measured on this Windows box: an ambient PYTHONPATH shadows fresh venvs (imports resolve elsewhere), uv silently installs into a live Hermes agent env when VIRTUAL_ENV is given as an MSYS /tmp path, and how to force/verify true isolation with -E plus module __file__"
source_repo: local environment probe 2026-11-04 (uv 0.12.x/0.13.x behaviour + Hermes terminal env), not a starred repo
tested_version: "LIVE PROBE 2026-11-04, Windows 11: uv venv + `uv pip install`, CPython 3.14.7 (uv-managed) and 3.14.9 (Hermes-managed); observed PYTHONPATH=...hermes\\installs\\<id>\\environments\\<hash>\\venv\\Lib\\site-packages"
verified_date: "2026-11-04"
---

# Venv isolation on this box: PYTHONPATH shadowing and uv's silent fallback

Two environment facts here can silently invalidate any claim of the form *"I installed X version Y, so this
behaviour is about X"*, which makes them prerequisites for every library-probing session. Both were measured
on 2026-11-04 while probing the geospatial stack (see `../../../data-science/gis-spatial-analysis/references/spatial-index-and-crs-measurements.md`).

## Fact 1 — an ambient PYTHONPATH wins over your venv

The terminal environment exports:

```
PYTHONPATH=C:\Users\<user>\AppData\Local\hermes\installs\<install-id>\environments\<hash>\venv\Lib\site-packages
```

`sys.path` puts that directory **first**, ahead of the fresh venv's own `Lib\site-packages`:

```text
C:\...\hermes\installs\340facfedadc4505\environments\138.../venv/Lib/site-packages   <- PYTHONPATH, wins
C:\Users\Owner\AppData\Roaming\uv\python\cpython-3.14-windows-x86_64-none\python314.zip
...
C:\Users\Owner\AppData\Local\Temp\gis2            <- your venv root
C:\Users\Owner\AppData\Local\Temp\gis2\Lib\site-packages   <- what you actually installed into, last
```

Observed consequence: `import rtree, shapely, geopandas, pyogrio, pyproj, whitebox` all reported their
`__file__` inside the **Hermes-managed** site-packages, not the venv just created. Run with `-E` (ignore
PYTHONPATH) and the same interpreter raised `ModuleNotFoundError: No module named 'rtree'` — proving which copy
had been executing code all along.

## Fact 2 — uv silently retargets when VIRTUAL_ENV is an MSYS path

Passing a bash-style temp path makes native `uv` abandon the intended venv and pick an ambient one, **without
failing**:

```bash
cd "$TMPDIR" && uv venv gisvenv --python 3.14                      # created fine (relative name)
VIRTUAL_ENV="$PWD/gisvenv" uv pip install rtree shapely ...        # $PWD == /tmp/gisvenv   <-- MSYS form
# -> "Using Python 3.14.9 environment at: C:\...\hermes\installs\...\environments\<hash>\venv"
```

That log line named a **live Hermes agent runtime** (its site-packages contains
`__editable__.hermes_agent-0.0.0.pth`), and the install added 14 packages there (`+ pandas==3.1.0`, geopandas,
shapely, rtree, pyogrio, pyproj, folium, pint, whitebox + deps). Purely additive — every line was `+`, nothing
was replaced — but it is still a mutation of the agent's own environment made by accident, and instantiating
`whitebox.WhiteboxTools()` there also downloaded its analysis binary into that env's site-packages.

The same install with a **native** path targeted correctly:

```bash
uv venv "C:/Users/<user>/AppData/Local/Temp/gis2" --python 3.14
VIRTUAL_ENV="C:/Users/<user>/AppData/Local/Temp/gis2" uv pip install rtree shapely pyogrio geopandas
# -> "Using Python 3.14.7 environment at: C:\Users\<user>\AppData\Local\Temp\gis2"   (correct)
```

## Rules for probing libraries here

1. **Read uv's first line** (`Using ... environment at:`). It is the only trustworthy statement of where an
   install went; `+ pkg==ver` lines say nothing about destination.
2. **Always pass native paths** (`C:/Users/...`) to `uv`, and never build `VIRTUAL_ENV` from `$PWD` when cwd is a
   bash temp dir — MSYS `/tmp/...` forms are invisible to the native binary (this box has bitten on that before).
3. **Verify by import, not by log**: print `module.__file__` and `module.__version__`. Add `-E` to ignore ambient
   PYTHONPATH when you need true isolation, or unset it for the call: `env -u PYTHONPATH python ...`.
4. If a probe mutates an unintended environment, restore it: re-check what was added (`uv pip list` against the
   target venv), then uninstall exactly those names with `VIRTUAL_ENV=<native path> uv pip uninstall <names>` —
   and remember side-effect downloads that live inside site-packages (WhiteboxTools' binary) are removed with them.

## Why this matters beyond tidiness

Version-conflict debugging, "the docs say X but I measured Y", and reproducibility claims all assume you know
which copy of a library ran. On this box the default configuration breaks that assumption in both directions:
your install may not be where you think, *and* your import may not come from your venv even when it is.
