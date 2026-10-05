---
description: "deck.gl 9.4.0 (WebGL2/WebGPU large-scale data visualization): lockstep packages, layers/views model, basemap pairing, what works in Node vs browser (checked), pitfalls"
source_repo: visgl/deck.gl (MIT)
tested_version: npm metadata (all @deck.gl/* at 9.4.0, 2026-09-05; luma.gl 9.4.2, loaders.gl 4.5.2); @deck.gl/core and @deck.gl/layers 9.4.0 installed (63 MB) and layers instantiated in Node 22; no browser rendering was run
verified_date: "2026-10-05"
---

# deck.gl: GPU data visualization layers

deck.gl maps **data** (usually an array of JSON objects) to a stack of **layers** (scatterplot, arc, path, polygon, icon, text, hexagon/heatmap aggregations, 3D mesh, tiles) viewed through **views** (map, first-person, orthographic).
It targets WebGL2/WebGPU (via luma.gl) for large datasets, with built-in picking, filtering and cartographic projections. MIT.

## Packages and versions (npm, 2026-10-05)

| Package | Version |
|---|---|
| `deck.gl` (umbrella: pulls `core`, `layers`, `geo-layers`, `aggregation-layers`, `extensions`, `mesh-layers`, `json`, `react`, `widgets`, `mapbox`, `maplibre`, `google-maps`, `arcgis`, `carto`) | 9.4.0 (2026-09-05) |
| `@deck.gl/core`, `layers`, `react`, `geo-layers`, `aggregation-layers`, `mapbox`, `google-maps`, `widgets` | all **9.4.0** |
| `@luma.gl/core` / `@luma.gl/engine` (rendering layer) | 9.4.2 (`^9.4.0` required) |
| `@loaders.gl/core` | 4.5.2 (`^4.4.3` required) |
| `maplibre-gl` | 6.12.0 |
| `react-map-gl` | 8.1.3 (the React wrapper for MapLibre/Mapbox basemaps) |

**Pin every `@deck.gl/*` package to the same exact version** (they are released in lockstep; the umbrella package pins them all to `9.4.0`). Mixing minors is a common source of cryptic layer errors.

## Checked in Node (no browser)

```js
import { ScatterplotLayer } from '@deck.gl/layers';
const layer = new ScatterplotLayer({ id: 'pts', data, getPosition: d => d.position, getRadius: d => d.r, radiusScale: 100, getFillColor: [255, 140, 0] });
```

- Layers are plain objects and can be constructed and inspected without WebGL: `layer.id === 'pts'`, `ScatterplotLayer.layerName === 'ScatterplotLayer'`, `layer.props.radiusScale === 100`, `layer.props.data.length === 2`. A layer constructed **without an `id`** gets its class name as id (`ScatterplotLayer`), so two such layers collide: always set unique ids.
- `ScatterplotLayer.defaultProps` lists the knobs (`radiusUnits`, `radiusScale`, `radiusMinPixels`, `radiusMaxPixels`, `lineWidthUnits`, ...), useful for generating or validating layer specs.
- `new Deck({...})` in Node throws `ReferenceError: document is not defined`: rendering needs a browser (or a headless browser/GL context). For server-side images use a headless browser screenshot, not Node alone.
- Not run: any rendering, picking, basemap integration, or the React bindings.

## Choosing and pairing

| Need | Use |
|---|---|
| Millions of points/arcs/trips over a map or abstract plane | deck.gl layers |
| React app | `@deck.gl/react` (`<DeckGL>`), with `react-map-gl` + `maplibre-gl` for the basemap |
| Existing Mapbox/MapLibre/Google Maps map | `@deck.gl/mapbox`, `@deck.gl/maplibre`, `@deck.gl/google-maps` (overlay or interleaved) |
| Quick prototype without a build | the script-tag flavour (from the README) |
| Simple charts | plotly / recharts (see `react-ecosystem/references/awesome-react-map.md`); deck.gl is for spatial and very large data |
| Globe/satellite views of space data | Cesium-based approaches (see `frontend-design/nicegui-app-builder/references/frontend-tooling.md`, gods-eye-view) or deck.gl's `GlobeView` |

## Practical rules

- Provide `getPosition` accessors returning `[lng, lat]` (or `[lng, lat, alt]`); swapped axis order is the usual "nothing appears" bug.
- Use binary/typed-array attributes for very large data and avoid re-creating the `data` array each render (change detection is by reference); use `updateTriggers` when an accessor's behaviour changes.
- Set `radiusUnits`/`widthUnits` (`meters`, `pixels`, `common`) deliberately; defaults differ per layer.
- WebGL2 is required in browsers; check `navigator.gpu`/WebGL support in your target environments and test on the lowest-end device that matters.
