---
description: "SVG rasterisation options actually checked on this Windows box (rsvg-convert, Inkscape, ImageMagick and resvg all absent; cairosvg absent while matplotlib is present; node exists but @resvg/resvg-js does not — plus the trap that `convert` resolves to Windows' disk converter, not ImageMagick), what Skia actually is per its own README versus how it reaches us (CanvasKit/WASM rather than a pip package), and homelab-svg-assets' licensing nuance: repository code MIT but every brand icon stays the vendor's trademark with end-user responsibility for brand-guideline compliance"
source_repo: google/skia + loganmarchione/homelab-svg-assets README/DISCLAIMER, 2026-11-04; local tool inventory probed live
tested_version: "tool inventory **probed live on this box** (Windows 11, git-bash); Skia and the icon set were read from source and not installed"
verified_date: "2026-11-04"
---

# Rasterising SVG here, and where brand icons actually stand legally

## What can turn an SVG into a PNG on this machine (measured)

Probed with `which` / importlib / node require — the results matter because most diagram-export advice assumes tools that are not installed:

| Tool | Status on this box |
| --- | --- |
| `rsvg-convert` | **absent** |
| Inkscape | **absent** |
| ImageMagick (`magick`) | **absent** — and note the trap below |
| `resvg` (CLI) / `@resvg/resvg-js` | **absent** / not installed in node_modules |
| Python `cairosvg` | **absent** (and with no pip on system Python it is a uv-venv install, plus its Cairo DLL dependency) |
| Python `matplotlib` | **present** — good for chart PNGs, but it does *not* rasterise arbitrary SVG input |

**The `convert` trap:** `which convert` succeeds here and points at `/c/WINDOWS/system32/convert.exe` — the Windows filesystem conversion utility, not ImageMagick. A script that tests availability with `command -v convert` will "find" it and then do something catastrophic-adjacent or simply fail in a confusing way. Always probe `magick` (ImageMagick 7) or check the resolved path before trusting `convert`.

Practical consequence: for faithful SVG→PNG of hand-authored diagrams, use **headless Chromium we already drive** — write the SVG into an HTML page sized to the target dimensions and capture it (`capture_screenshot()` in the browser tooling; see `skill_view(name='diagram-design')` export flow). That path is installed, renders CSS/fonts/text the way a browser does, and needs no admin rights. If a dependency-free batch pipeline becomes necessary (no browser), install **resvg** rather than wrestling with Cairo DLLs — it's a single binary/npm package with no system graphics stack.

## Skia: what its own README commits to

`google/skia` says only: *"Skia is a complete 2D graphic library for drawing Text, Geometries, and Images"*, pointing at skia.org for detail. That is the honest extent of a README-level claim — do not cite specifics from memory as if they came from the repo. What matters operationally is how Skia reaches us: **not** as a pip-installable package on Windows/CPython-3.14, but transitively (it is the 2D engine inside Chromium and Flutter) or explicitly via its **CanvasKit** WebAssembly build in browser-side work — i.e. when we render through headless Chromium above, Skia *is* the rasteriser underneath, which is exactly why that route matches what users see in a real browser. Treat "use Skia" as "render through a browser/CanvasKit", not "add a Python dependency".

## homelab-svg-assets: 600+ brand icons, and the licence does **not** cover them

Over **600 full-colour SVG icons of homelab software/products/brands**, normalised to one size — genuinely useful for dashboards and architecture diagrams (see `system-atlas`, `architecture-diagram`). Distribution is unusually broad: GitHub tree (`assets/`), npm **`@loganmarchione/homelab-svg-assets`**, Packagist, CDN usage, PHP/Hugo helpers — and a documented **Diagrams.net** route.

The important part is the licensing split, which its badge ("MIT") invites people to get wrong. From `DISCLAIMER.md`:

> The code in this repository created by Logan Marchione is licensed under the MIT License… **However, the SVG icons representing homelab-related software, products, and brands are the property of their respective owners.** …The inclusion of these icons/SVGs is intended solely for referential and informational purposes, to accurately identify the software, product, or brand. Usage of these icons/SVGs does not imply endorsement by or partnership with the respective owners… **It is the responsibility of the end-user** to ensure that their use of each icon/SVG complies with applicable trademark policies, licensing terms, and brand guidelines.

So: repository code MIT, artwork *not* MIT — referential/informational use only, no implied endorsement, fair use asserted but explicitly not guaranteed across jurisdictions. For this owner's public surfaces (portfolio site, published dashboards/diagrams) that means icons are fine for *identifying* a product in a diagram, and the safe practice is attribution plus never restyling a logo into something that reads as an endorsement or as our own brand mark — same class of care recorded for fonts and image assets elsewhere. The repo also documents icon addition/update/removal processes (additions require explaining your association with the brand), which tells you vendor takedowns do happen: pin the npm package version rather than hot-linking `main`, so a removal doesn't silently blank an icon in a published figure.
