---
name: python-plotting
description: "Headless matplotlib/seaborn/plotly: output and traps."
version: 1.0.0
author: Hermes Agent (promoted from python-data-science references, live-run 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [matplotlib, seaborn, plotly, plotting, headless, kaleido, deterministic-output, charts]
    related_skills: [python-data-science, python-numerics-gotchas, streamlit-dashboards, nicegui-app-builder]
---

# Python plotting in scripts and pipelines

## What This Skill Does

Covers what an **unattended** plotting script (agent, cron job, CI, report build) runs into with matplotlib 3.11, seaborn 0.13.2 and plotly 7.1: windows that block, figures that differ byte-for-byte between runs, removed or deprecated calls, HTML files that are 4.8 MB each, and static export that needs a browser. Each library has a reference with the calls that were actually run and what they returned.

## When to Use

- A script that plots hangs, opens a window, or warns about glyphs, figures or deprecations
- Committed or diffed figures must be reproducible (PNG, SVG, PDF)
- Producing many figures or a report and the output size or time matters
- Choosing between matplotlib/seaborn (static, publication) and plotly (interactive, shareable)
- Not for deciding what to chart or how it should look (use the `dataviz` skill), the modelling workflow around the plots (`python-data-science`), or interactive dashboards (`streamlit-dashboards`, `nicegui-app-builder`)

## Choosing the tool

| Need | Use | Why |
|---|---|---|
| Publication-quality static figure, exact control | matplotlib | deterministic output is achievable (below) |
| Statistical plots from a DataFrame in few lines | seaborn 0.13.2 on matplotlib | latest release is 2024-01; `main` has unreleased fixes |
| Interactive, zoomable, shareable HTML | plotly | cost is file size (below) |
| Many figures on one page | plotly with one shared `plotly.js` | embedding it per figure is about 4.8 MB each |
| Dashboard around the figures | `streamlit-dashboards` or `nicegui-app-builder` | both embed plotly figures |

## Procedure

1. Headless first: set `MPLBACKEND=Agg` in the environment, or call `matplotlib.use("Agg")` before importing pyplot. Under the default `tkagg` on a Windows Python with Tk, `plt.show()` opens a window and blocks.
2. In loops close figures (`plt.close(fig)`), or build them with `matplotlib.figure.Figure`; more than 20 open pyplot figures raises a `RuntimeWarning`.
3. Make output reproducible when it is diffed or committed: PNG already is (drop the `Software` string with `metadata={"Software": None}`); SVG needs **both** `metadata={"Date": None}` and `rcParams["svg.hashsalt"] = "fixed"`; PDF needs `metadata={"CreationDate": None}`.
4. For plotly, write files instead of calling `fig.show()` (the default renderer is `browser`), choose `include_plotlyjs` deliberately (`True` 4.8 MB offline, `"cdn"` 7.6 KB, `False` 7.4 KB), and use `go.Scattergl` or downsample past tens of thousands of points.
5. Treat plotly static export (`write_image` through kaleido 1.x) as a separate step that needs a Chromium-family browser; a bare CI image fails there, so do not let it fail the data pipeline.
6. Before upgrading, run once with `python -W error::FutureWarning` to surface the seaborn 0.14 removals.

## Calls that no longer work (matplotlib 3.11 / seaborn 0.13.2)

| Old call | Result | Use |
|---|---|---|
| `plt.cm.get_cmap(...)` | `AttributeError` | `matplotlib.colormaps["viridis"]` |
| `plt.style.use("seaborn")` | `OSError` | `"seaborn-v0_8"` |
| `ax.boxplot(..., vert=False)` | deprecation warning, removed in 3.13 | `orientation="horizontal"` |
| `sns.barplot(..., palette=...)` without `hue` | FutureWarning, removed in 0.14 | also pass `hue=`, `legend=False` |
| `sns.lineplot(..., ci=95)` | FutureWarning | `errorbar=("ci", 95)` |
| `sns.distplot`, `kdeplot(shade=True)` | removed in 0.14 | `displot`/`histplot`, `fill=True` |
| `sns.FacetGrid(..., size=2)` | `TypeError` | `height=2` |
| `sns.heatmap(df.corr())` with string columns | `ValueError` | `df.corr(numeric_only=True)` |

## Pitfalls

- Missing glyphs: the default DejaVu Sans warns and renders boxes for CJK, emoji and symbols; pick a font that has them.
- `set_xticklabels` without fixed ticks warns; call `set_ticks` first.
- NaN and inf in plotly data are serialised as `null`: gaps appear and the infinity vanishes silently.
- seaborn 0.13.2 calls the matplotlib `vert` argument inside `boxplot`; matplotlib 3.13 removes it, so pin `matplotlib<3.13` or move to a seaborn that changed it (not tested).
- Version snapshots date from 2026-10-05; re-probe before relying on them for newer releases.

## Verification

- [ ] Script runs to completion with no display (`MPLBACKEND=Agg`) and exits
- [ ] Re-running produces byte-identical files for the formats you commit (compare hashes)
- [ ] `python -W error::FutureWarning script.py` is clean, or the warnings are recorded
- [ ] Plotly outputs are sized as intended (check the file size, not just that it opens)

## References

- `references/matplotlib-notes.md` - matplotlib 3.11.2 on Windows (about 35 checks): default `tkagg` backend, deterministic PNG/SVG/PDF recipes, removed `get_cmap` and `seaborn` style, `vert=` deprecation, glyph and figure-leak warnings, speed
- `references/seaborn-0-13-notes.md` - seaborn 0.13.2 on pandas 3 / matplotlib 3.11: 24 calls run, the deprecations that vanish in 0.14, calls that fail, updated quick reference
- `references/plotly-notes.md` - plotly 7.1.0 in scripts: HTML 4.8 MB embedded vs 7.6 KB CDN, JSON size, NaN handling, kaleido 1.4 static export needs Chrome, default browser renderer
