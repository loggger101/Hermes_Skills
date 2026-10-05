---
description: "matplotlib 3.11.2 on Windows/Python 3.14 measured: default backend is tkagg, deterministic PNG/SVG/PDF recipes, removed get_cmap and 'seaborn' style, missing glyph warnings, vert deprecation, figure-leak warning, speed"
source_repo: matplotlib/matplotlib (PSF-based licence)
tested_version: "matplotlib 3.11.2 + numpy 2.5.3 in the Python 3.14.6 venv used for seaborn, Windows 11 (Tk available). Two scripts, about 35 one-call checks, warnings forced on, Agg backend. Interactive backends, animations, 3D axes and LaTeX text were not exercised"
verified_date: "2026-10-05"
---

# matplotlib 3.11.2: what an unattended script runs into (run)

## Backend and headless use

- `matplotlib.get_backend()` returned **`tkagg`** both before and after `import matplotlib.pyplot`, on this Windows Python that ships Tk. A script that
  calls `plt.show()` under that default opens a window and blocks. For agents, cron and CI: set `MPLBACKEND=Agg` in the environment, or call
  `matplotlib.use("Agg")` **before** importing pyplot. Under Agg `plt.show()` returns `None` quietly in this version.
- Creating more than 20 pyplot figures without closing them raised `RuntimeWarning: More than 20 figures have been opened`. Use `plt.close(fig)` /
  `plt.close("all")` in loops (or build figures with `matplotlib.figure.Figure` directly, which pyplot does not track).

## Size, speed

- `figsize=(3, 2)` at `dpi=100` gave a 300 x 200 PNG; `dpi=300` gave 900 x 600. `savefig.dpi` defaults to `figure` (so it follows `figure.dpi`, 100).
- A 1 000 000-point scatter (marker size 1) saved to PNG in **0.4 s** (35 KB); a 100 000-point line to SVG in about 0 s, 224 KB. Rasterise dense plots; SVG size grows with point count.

## Deterministic output (for diffing or committed figures)

| Format | Byte-identical after a 1.2 s gap? | What it takes |
|---|---|---|
| PNG | yes | already deterministic; the default metadata includes `Software: Matplotlib ...`, drop it with `metadata={"Software": None}` if you want no version string |
| SVG | **no** by default; **no** with only `metadata={"Date": None}` | needs **both** `metadata={"Date": None}` and `matplotlib.rcParams["svg.hashsalt"] = "fixed"` (element ids use a hash); then identical. The file contains a `<dc:date>` and ids like `figure_1`, `patch_1` |
| PDF | **no** by default | `metadata={"CreationDate": None}` makes it identical (two saves within the same second can look identical by accident) |

## API removals and warnings

| Call | Result |
|---|---|
| `plt.cm.get_cmap(...)` and `matplotlib.cm.get_cmap(...)` | **AttributeError: module 'matplotlib.cm' has no attribute 'get_cmap'**; use `matplotlib.colormaps["viridis"]` |
| `plt.style.use("seaborn")` | `OSError: 'seaborn' is not a valid package style ...`; the name is **`seaborn-v0_8`** (works) |
| `ax.boxplot(..., vert=False)` | `MatplotlibDeprecationWarning: vert: bool was deprecated in Matplotlib 3.11 and will be removed in 3.13`; use `orientation="horizontal"` (clean). The same warning appears from inside seaborn 0.13.2 |
| `ax.set_xticklabels(["a","b","c"])` without fixing ticks | `UserWarning: set_ticklabels() should only be used with a fixed number of ticks`; call `set_ticks` first or use a `FixedLocator` |
| Title with CJK, emoji, `✓`, `é` using the default DejaVu Sans | saves, but warns `Glyph 128640 (ROCKET) missing from font(s) DejaVu Sans` and the same for CJK (the glyphs render as boxes); `é` is fine. Choose a font that has the glyphs (`font.family` list, Noto, Segoe UI Symbol) or avoid those characters |
| `fig.set_layout_engine("constrained")` | works (`ConstrainedLayoutEngine`) |

## Habits

1. `MPLBACKEND=Agg` and `plt.close(fig)`; save with an explicit `dpi=`.
2. For reproducible artefacts, strip dates and Software metadata, and pin `svg.hashsalt` for SVG.
3. Replace `get_cmap`, `vert=`, and `seaborn` style names now; the `vert` warning says removal in 3.13.
4. Check fonts when the text may contain non-Latin characters or symbols; warnings are not errors, the output is just wrong.

Not run: interactive backends, `animation`, 3D, mathtext/LaTeX, `savefig(bbox_inches="tight")` with long labels, multithreaded figure creation.
