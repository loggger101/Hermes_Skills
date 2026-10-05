---
description: "plotly.py 7.1.0 for reports: HTML size (embedded JS 4.8 MB vs CDN 7.6 KB), JSON size, NaN handling, static export via kaleido 1.4 (needs Chrome), default browser renderer; run live"
source_repo: plotly/plotly.py (MIT)
tested_version: plotly 7.1.0 + kaleido 1.4.0 pip --target on Windows py3.14 with system Chrome present; one probe script
verified_date: "2026-10-05"
---

# plotly.py in scripts and pipelines

`plotly` 7.1.0 (2026-09-15, MIT, `>=3.8`) builds interactive figures (`plotly.express` for one-liners, `plotly.graph_objects` for control). The facts below matter when figures are produced by a script, a report job or an agent rather than a notebook.

## Output formats and their cost (measured)

| Call | Result |
|---|---|
| `fig.write_html(p, include_plotlyjs=True)` (default for full HTML) | **4,826,893 bytes** per file: the whole plotly.js bundle is embedded; works offline |
| `include_plotlyjs="cdn"` | 7,610 bytes; needs internet when opened and loads plotly.js from a CDN |
| `include_plotlyjs=False` | 7,357 bytes; you must load plotly.js yourself on the page |
| `fig.to_json()` for a 100,000-point line (normal floats) | 1,367,179 bytes (13.7 B/point): fine for an API response, heavy for a page with many traces |
| NaN and inf in `y=[1, nan, inf]` | serialised as `[1, null, null]`: gaps in the line; the infinity is silently dropped |
| `fig.write_image("a.png", width=600, height=400)` with `kaleido` 1.4.0 | worked in 1.7 s (17.6 KB PNG) on a machine with Chrome installed |

Rules: for a dashboard of many figures use one shared plotly.js (`"cdn"` or a local script tag) and per-figure fragments (`fig.to_html(full_html=False, include_plotlyjs=False)`);
a report that must open offline pays about 4.8 MB per embedded figure, so embed once or export PNG/SVG. Past tens of thousands of points use `go.Scattergl` (exists; WebGL) or downsample before plotting.

## Static export needs a browser (kaleido 1.x)

`kaleido` 1.x renders through a Chromium-family browser (its dependency `choreographer` drives it), rather than the bundled engine of 0.x. It worked here because Chrome is installed.
On a bare CI image or server `write_image` will fail until a browser is available (kaleido's docs describe `kaleido.get_chrome_sync()` to fetch one: not run here). Keep the export step separate and handle the failure
with a clear message; do not let a missing browser fail the data pipeline.

## Defaults that surprise in scripts

- `plotly.io.renderers.default` was `'browser'`: `fig.show()` **opens a browser tab**. In unattended jobs write files instead, or set `pio.renderers.default = "png"`/`"json"` deliberately.
- `px.line(data, x="a", y="zzz")` raises a clear `ValueError: Value of 'y' is not the name of a column in 'data_frame'. Expected one of ['a', 'b'] but received: zzz`.
- Default template is `plotly` (the familiar light grey grid); set a template explicitly (`plotly_white`, `simple_white`) for reports, and keep colour and contrast decisions with the `dataviz` guidance.

## Choosing against other tools in this repo

Interactive, shareable, zoomable: plotly. Publication-quality static figures: matplotlib/seaborn. Dashboards: Streamlit (`streamlit-dashboards`) or NiceGUI, both of which embed plotly figures.
For provenance, save the figure's JSON (`fig.write_json`) beside the data it was built from.
