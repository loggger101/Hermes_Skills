# d3 7.9.0 headless: scales, shapes, layouts and the traps (run live in Node)

Source: [d3/d3](https://github.com/d3/d3) (ISC; v7.9.0, 2024-03-12 and still latest on npm). `npm i d3 jsdom` into a scratch
dir, Node 22.23.2 on Windows, run with `TZ=America/New_York` where time zones matter. About 80 calls in one ESM script; each line
below is an observed value. d3 computes numbers and path strings; it needs a DOM only for `select`, so for a static SVG
file the pure functions (`line`, `arc`, scales, `treemap`) are enough and `jsdom` covers the rest.

## Loading

- `import * as d3 from 'd3'` gave 577 exports; **`require('d3')` also worked** on Node 22 (require of an ES module), no
  `ERR_REQUIRE_ESM`. `require('d3/package.json')` fails with `ERR_PACKAGE_PATH_NOT_EXPORTED` (read the file by path instead).
- `d3.select('#c')` with no DOM -> `ReferenceError: document is not defined`. Give it an element:
  `d3.select(new JSDOM(html).window.document.querySelector('#c'))`. With jsdom, `append('svg')`, `selectAll().data().join()` and
  `attr` produced clean markup (`<svg width="100" height="50"><circle cx="0" r="5"></circle>...`), and re-joining with 2 items
  left 2 circles. `selection.transition()` constructs without error outside a browser but needs timers to animate.

## Scales

| Probe | Result |
|---|---|
| `scaleLinear([0,10],[0,100])(15)` | **150** (extrapolates); `.clamp(true)` -> 100 |
| `ticks(0, 1, 5)` | `[0, 0.2, 0.4, 0.6, 0.8, 1]` |
| `nice()` on `[0.13, 9.87]` | `[0, 10]` |
| `scaleLog([0, 10])(5)` | `NaN` (log domains cannot include 0; use `scaleSymlog`) |
| `scaleOrdinal(['a','b'])` on unseen keys | **grows its domain**: `o('x')='a'`, `o('y')='b'`, `o('z')='a'`, domain becomes `[x,y,z]`; set `.unknown(...)` or a fixed domain to stop it |
| `scaleBand(['a','b','c'],[0,90]).padding(0.1)` | `b` at 31.94, bandwidth 26.13, step 29.03 |
| `scaleTime` vs `scaleUtc` ticks | local midnight `Mon Jan 01 2024 00:00 GMT-0500` vs UTC midnight shown as `Dec 31 19:00 EST`: pick one, matching how the data was written |
| `interpolateViridis(0, .5, 1)` | `#440154`, `#21918c`, `#fde725` |
| `scaleQuantize([0,10], ['lo','mid','hi'])(6)` | `mid` |

## Format and time

- `format(',.2f')(1234567.891)` `1,234,567.89`; `'.3s'` on 1234567 -> `1.23M`; `'.1%'` on .256 -> `25.6%`; `'$,'` -> `$1,234`;
  `'~s'` on 1500 -> `1.5k`; `'.2r'` on .000123 -> `0.00012`.
- **Negative numbers use a real minus sign U+2212**, not `-`: `format(',')(-1234.5)` -> `−1,234.5` (`'(,'` gives `(1,234.5)`).
  Strip or `.replace('−','-')` before writing to CSV or feeding a parser.
- `format('abc')` throws `Error: invalid format: abc`.
- **`utcParse('%Y-%m-%d')('2024-02-30')` returned `2024-03-01`** instead of null: out-of-range days roll over. Validate dates
  yourself. `utcParse('%d/%m/%Y')('03/04/2024')` read 3 April.
- `isoParse('2024-03-01')` is UTC midnight (prints `Feb 29 19:00 EST` in a local zone). `utcMonth.range` from Jan 31 gave Feb 1, Mar 1, Apr 1.

## Arrays and CSV

- `extent([3, NaN, 1, undefined, 2])` -> `[1, 3]` (ignores NaN/undefined). **`max(['10','9'])` -> `'9'`** (string comparison) and
  `max([10, 9, '11'])` -> `'11'`: coerce first.
- `[10, 9, 1].sort()` -> `[1, 10, 9]` (lexicographic); `d3.sort([10,9,1])` -> `[1, 9, 10]`.
- `mean([])` and `median([])` -> `undefined`; `sum([])` -> 0; `quantile([1,2,3,4], .5)` -> 2.5. `cumsum` returns a `Float64Array`.
- `d3.group(...)` returns an **`InternMap`** (a Map, not an object); `rollup` too; `bin().thresholds(3)` on 1..10 -> bins `[0,5)` 4,
  `[5,10)` 5, `[10,15)` 1; default (Sturges) on `range(100)` -> 10 bins. `range(0, 1, 0.1)` has 10 items, last 0.9.
- Seeded randomness: `shuffler(randomLcg(42))([1..5])` -> `[3,4,5,1,2]`; `randomNormal.source(randomLcg(1))(0,1)` three draws
  `-0.6473, -1.3048, 1.8885`. Use `randomLcg` for reproducible figures.
- `csvParse` without a type function gives strings (`{a: "1"}`). **`autoType` turns `007` into the number 7**, an empty cell
  into `null`, `3.5` into a number, and `2024-01-01` into a `Date` at UTC midnight; pass `dtype` per column if IDs matter.
  Quoted commas and `""` escapes parse correctly across CRLF; `csvFormat` writes `,` for null and quotes `x,y`.

## Shapes (exact output)

`line()([[0,0],[10,20],[20,10]])` -> `M0,0L10,20L20,10`; `curveMonotoneX` -> cubic `C` segments; `area().y0(50)` closes with `Z`;
`arc()({innerRadius:0, outerRadius:10, startAngle:0, endAngle:Math.PI})` -> `M0,-10A10,10,0,1,1,0,10L0,0Z` (angle 0 points up);
`pie()([1,1,2])` start/end angles `[3.142, 4.712]`, `[4.712, 6.283]`, `[0, 3.142]` (the result array keeps input order, but the default sort-by-value
puts the largest slice at angle 0; `.sort(null)` gave `[0, 1.571]`, `[1.571, 3.142]`, `[3.142, 6.283]` in input order); `symbol(symbolCircle, 64)()` is two arcs of radius 4.514. **`line().defined(d => d[1] != null)` on
`[[0,0],[10,null],[20,10]]` gave `M0,0ZM20,10Z`**: isolated points become empty subpaths, so a one-point segment draws nothing
(add a `stroke-linecap: round` or draw circles for singletons).

## Hierarchy and layouts

- `hierarchy(...).sum(d => d.v ?? 0)` gave `value 6, height 2, 5 descendants`. `treemap().size([100,100]).padding(1)`:
  a -> (1,1)-(66,74), b -> (1,75)-(66,99), d -> (68,2)-(98,98). `pack().size([100,100])` for two equal leaves: centres
  (25,50) and (75,50), radius 25. `tree()` puts two children at x = 25 and 75, y = 100.
- `stratify` errors: a parent id with no row -> `Error: missing: z`; two rows with empty parent -> `Error: multiple roots`.
- `forceSimulation` is **deterministic** (two 200-tick runs on the same graph gave identical coordinates; d3 uses a fixed
  LCG). It cools in about **300 ticks** (`ln(0.001)/ln(1-0.0228)`); call `.stop()` then `.tick()` N times for server-side layout.
  `forceLink` **mutates your link objects** (string/number `source` becomes the node object) and throws
  `Error: node not found: zz` for an unknown id.

## Geo: the winding trap

`geoPath(equirectangular)` of the triangle `[[0,0],[10,0],[10,10],[0,0]]` returned the triangle **plus a second outline
around the whole globe** (`M-3.142,-1.571L0,-1.571...Z`): d3-geo wants exterior rings **clockwise**, the opposite of
GeoJSON RFC 7946, so a counter-clockwise ring is read as "everything except this". Fix: reverse the ring (`[...ring].reverse()` drew `M0,0L0.175,-0.175L0.175,0Z`, and `geoArea` fell from 12.55 to 0.0153). d3 has no
`geoRewind` (`typeof d3.geoRewind` is undefined); `@turf/rewind` is an external option, not tested. Other values: `geoMercator().scale(100)([180,0])` = `[314.16, 0]`,
`[0,89]` -> y -474.1; `geoDistance` London-New York x 6371 = 5570 km; `geoArea({type:'Sphere'})` = 4 pi = 12.566.

## Checklist for generating a chart file

1. Fix the time zone: `scaleUtc`/`utcFormat`/`utcParse` for data in UTC, and validate parsed dates.
2. Coerce numbers before `max`/`min`/`sum`, and `autoType` only on columns you inspected.
3. Pass `randomLcg` seeds and `.stop()` + manual ticks so repeated builds are identical (see `bit-identity-float-pipelines`).
4. Replace U+2212 minus signs if the text leaves the SVG.
5. Not covered: `d3-brush`/`zoom`/`drag` (browser events), `d3-contour`, `d3-sankey` (separate package), `d3-delaunay`, Observable Plot.
