# Popmotion 11.0.5: the framework-free ancestor of Motion, with identical spring numbers (run in Node)

Source: [Popmotion/popmotion](https://github.com/Popmotion/popmotion) (20k stars, repo pushed 2024-03-12, GitHub reports no licence; npm says MIT).
npm `popmotion` **11.0.5** (2022-08-15) and `motion` 14.0.0 installed side by side on Node 22.23.2 / Windows; about 35 probes in plain Node, no DOM.
Companion packages are equally frozen: `framesync` 6.1.2, `style-value-types` 5.1.2, `stylefire` 7.0.3 (2022), `@popmotion/popcorn` 0.4.4 (2022-04).
Not covered: `stylefire`/`styler` DOM output, `inertia` with bounds, the React `pose` ecosystem. Current animation work belongs in Motion:
`motion-14-notes.md` in this directory.

## Status and weight

Dormant since 2022 and superseded by Motion (same author; the overlap in primitives below is measured, the lineage itself was not checked here). Runtime dependencies: `framesync`, `hey-listen`,
`style-value-types`, `tslib`. `dist/popmotion.min.js` (UMD) is **15.6 kB (6.8 kB gzip)**; ESM entry `dist/es/index.mjs`, CJS `dist/popmotion.cjs.js`.
Export surface: 51 names (`animate`, `spring`, `keyframes`, `decay`, `inertia`, `mix`, `mixColor`, `mixComplex`, `interpolate`, `pipe`, `snap`, `wrap`, `clamp`,
`progress`, `distance`, `angle`, `cubicBezier`, `steps`, easing functions `easeIn/Out/InOut`, `circ*`, `back*`, `bounce*`, `anticipate`, `linear`, helpers `velocityPerSecond`,
`velocityPerFrame`, `degreesToRadians`, `radiansToDegrees`, `toDecimal`, `smooth`, `smoothFrame`, `attract`, ...).

## Generators are pure, so the maths is testable

`spring`, `keyframes` and `decay` return objects with `next(timeMs)` giving `{ value, done }`, no timers needed.

| Probe | Result |
|---|---|
| `spring({from:0, to:100, stiffness:100, damping:10, mass:1})` at 0, 100, 200, 400, 800, 1600, 3200 ms | 0, 34.03, 84.943, **115.312** (overshoot), 97.901, 100 (done), 100 |
| same parameters through **Motion 14's `spring({ keyframes:[0,100], stiffness:100, damping:10, mass:1 })`** | **identical numbers to the digit** (34.03, 84.943, 115.312, 97.901, 100) |
| popmotion spring settle time, stepping 10 ms | done at 1050 ms |
| `keyframes({from:0, to:100, duration:1000, ease:linear})` at 250/500/1000 | 25, 50, 100 |
| `keyframes({to:[0,50,100], offset:[0,.2,1], ...})` at 100/200/600 | 25, 50, 75 |
| `decay({from:0, velocity:1000, power:0.8, timeConstant:350})` at 100/500/2000 | 198.8, 608.3, 797.4 (asymptote about 800 = velocity x power) |

So code that only uses springs, keyframes and the maths helpers ports to Motion without changing a number. The Motion generator additionally
reports `calculatedDuration` (null for the 3-arg spring above) and has `retarget`/`velocity`.

## Driving it

- `animate({ from, to, duration, ease, onUpdate, onComplete, driver })` returns controls (`stop`). With a custom `driver: update => ({ start, stop })`
  you step time yourself: four 100 ms ticks of a 400 ms linear animation produced `[25, 50, 75, 100, 'done']`. This is the deterministic way to test it.
- With the default driver it ran in plain Node and finished a 100 ms animation in ~141 ms (framesync apparently schedules without a browser), so no DOM shim is needed for non-DOM values.
- Per the project's docs (not run here) `animate` also takes `type: 'spring' | 'keyframes' | 'decay'`, and `inertia` combines decay with a spring at bounds.

## Helper behaviour (matches Motion where it overlaps)

`interpolate([0,1,2],[0,100,50])(1.5)` = 75; `interpolate([0,10],[0,1])(20)` = 1 (clamped by default); `snap(10)(23)` = 20; `snap([0,50,100])(40)` = 50; `wrap(0,3,4)` = 1;
`clamp(0,1,2)` = 1; `progress(10,20,15)` = 0.5; `pipe(x=>x+1, x=>x*2)(3)` = 8; `distance({x:0,y:0},{x:3,y:4})` = 5; `velocityPerSecond(10, 16.667)` = 599.99;
`cubicBezier(.17,.67,.83,.67)(.5)` = 0.6275; `easeOut(.5)` = 0.75, `backOut(.5)` = 1.0656, `bounceOut(.5)` = 0.7187, `anticipate(.2)` = -0.0412 (it undershoots first).

## Traps

1. **`mix` is numeric only and takes three arguments.** `mix('#ff0000', '#0000ff', 0.5)` returned the garbage string `NaN#ff0000` (no error). Colours go through
   **`mixColor(a, b)(t)`** (`rgba(180, 0, 180, 1)`, gamma-corrected, not 127) and strings with numbers through `mixComplex('0px 0px', '10px 20px')(.5)` = `5px 10px`.
   In Motion 14 `mix(a, b)` is curried and accepts colours (see `motion-14-notes.md`): the same call sites do not port mechanically.
2. Easings are exported **functions** (`easeIn`, `circOut`, `backInOut`) and every probe passed functions; string names like Anime's `'outQuad'` were not tried.
3. Anything touching the DOM (`styler`, `stylefire`) is a separate, equally old package: do not start new code on it.

## Decision

Reading old code or porting it: keep the maths, swap `animate`/drivers for Motion's `animate` and the `mix` call sites for the curried form. New code: Motion
(React) or Anime.js 4 (`frontend-library-picks/references/animejs-4-notes.md`), never Popmotion.
