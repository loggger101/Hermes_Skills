# Anime.js 4.5.0: modular API, v3 migration traps, deterministic values (run in Node + jsdom)

Source: [juliangarnier/anime](https://github.com/juliangarnier/anime) (73k stars, MIT, pushed 2026-08-21). npm `animejs` **4.5.0**
(2026-08-17), installed with jsdom on Node 22.23.2 / Windows. About 50 probes with `autoplay: false` plus `.seek(ms)` so every value is
deterministic, no timers. Not covered: `waapi.animate` (jsdom has no `Element.animate`), `onScroll`/`ScrollObserver`, `createDraggable`, `createLayout`,
text splitting, the SVG helpers, real rendering. For React see `web-development/react-ecosystem/references/motion-14-notes.md`.

## Package facts

- ESM package (`type: module`, no dependencies, `sideEffects` only for `adapters`); `import { animate } from 'animejs'` works, and
  `require('animejs')` also worked on Node 22 (returned an object with 67 keys). **There is no default export**: the v3 line
  `import anime from 'animejs'` fails with `SyntaxError: The requested module 'animejs' does not provide an export named 'default'`.
- 67 named exports: `animate`, `createTimeline`, `createTimer`, `createAnimatable`, `createDraggable`, `createDrawable`, `createLayout`, `createMotionPath`,
  `createScope`, `onScroll`, `stagger`, `spring`, `eases`, `engine`, `utils`, `svg`, `text`, `waapi`, `splitText`, `scrambleText`, `morphTo`, plus helpers
  (`lerp`, `clamp`, `wrap`, `snap`, `mapRange`, `random`, `round`, ...).
- Subpath exports give tree-shaking: `animejs/animation`, `/timeline`, `/utils`, `/easings`, `/engine`, `/draggable`, `/scope`, `/svg`, `/text`,
  `/waapi`, `/layout`, `/events`, `/adapters/three`; a four-subpath import (`animate`, `stagger`, `createTimeline`, `spring`) loaded fine.
- Prebuilt bundles: `dist/bundles/anime.umd.min.js` **118 kB (40.7 kB gzip)**, `anime.esm.min.js` 118.7 kB (41.0 kB gzip) containing everything,
  so import by subpath for production. The package directory is 2.5 MB on disk.

## v3 to v4 traps (all hit in the run)

| v3 habit | v4 result |
|---|---|
| `import anime from 'animejs'; anime({targets, ...})` | no default export (`SyntaxError`); use `animate(targets, params)` |
| `anime.timeline()` | `createTimeline({ autoplay, defaults })`; `tl.add(target, params, position)`; `'+=100'` gap syntax works (500 + 100 + 500 gave `duration` 1100) and `.label('end')` exists |
| `easing: 'linear'` | **silently ignored**: `easing: 'linear'` at 500 ms gave 75 (the default curve) instead of 50. The key is `ease` |
| default easing | gives 75 of 100 at half time (the same value as `outQuad`, so the default is an ease-out); `inOutCubic` at 25 % time gave 6.25 |
| unknown ease name | no error; `ease: 'invalidEaseName'` behaved as linear (50 at half time) |
| `anime.random`, `anime.stagger` | `utils.random`, `stagger(100)` (per-target delay: 3 targets at 100 ms stagger and 400 ms duration gave `duration` 600) |
| `createSpring({...})` | prints `createSpring() is deprecated use spring() instead`; `spring({ stiffness, damping })` reported `duration` 628 and `settlingDuration` 1760 |
| `loop: true` | `duration` property becomes **1,000,000,000,000** and `iterationCount` `Infinity`: never compute with `.duration` of an infinite animation |

## Behaviour verified

- Plain objects: `animate({x:0}, {x:100, duration:1000, ease:'linear'})` at `.seek(250)` gave `x = 25`; `[10, 20]` from-to with `modifier: utils.round(0)` at
  333 ms gave `13`. Instance class is `JSAnimation`; `await animation` resolves after `onComplete` (ran once).
- DOM: `animate(el, { x: 200, rotate: 90, opacity: 0.5 })` wrote **one `transform` string** (`translateX(100px) rotate(50deg)` at 500 ms) and `opacity: 0.75`;
  the element's existing inline `transform: rotate(10deg)` was read as the **start value** (rotate went 10 to 90, so 50 at the half), and `x` is a
  shorthand for `translateX`. Other inline properties (`width: 100px`) were preserved. Animations compose from the element's *current* state:
  a second `animate` to `x: 100` started from 200.
- `utils.$('.box')` returns a plain Array of elements. Utilities: `lerp(0,10,.25) = 2.5`, `clamp(15,0,10) = 10`, `mapRange(5,0,10,0,100) = 50`,
  `snap(13,5) = 15`, `wrap(12,0,10) = 2`, `random(1,1) = 1`.
- `loop: 2` with `alternate: true` at 1500 ms of a 1000 ms animation gave 50 (second pass running backwards).
- `engine` defaults: `fps` **240**, `precision` 4 decimal places, `timeUnit` `'ms'`, plus `pauseOnDocumentHidden` and `useDefaultMainLoop`
  fields; lower `engine.fps` if 240 Hz updates are not wanted (setting it was not tested).

## Test-harness trap

A partial DOM shim breaks it. With **no DOM globals at all**, `animate({x:0}, {...})` ran in plain Node; with jsdom's `NodeList` copied onto
`globalThis` but not `HTMLCollection`, `animate` threw `ReferenceError: HTMLCollection is not defined` from `parseTargets`. In a jsdom test define
the whole family (`NodeList`, `HTMLCollection`, `HTMLElement`, `SVGElement`, `getComputedStyle`, `requestAnimationFrame`, `document`, `window`)
or none. For deterministic assertions use `autoplay: false` and `.seek(ms)`.

## Choosing it

Good for imperative, framework-free animation of DOM, SVG and plain objects with timelines and staggers, and for a static site that wants a
single small import per feature. Use CSS transitions or `animation-timeline` for simple effects (see `scrollreveal-4-notes.md`), and Motion
(`motion-14-notes.md`) when the UI is React and needs layout animation or gestures. Respect reduced motion yourself: the library has no switch,
so gate calls with `matchMedia('(prefers-reduced-motion: reduce)')` (no mention of reduced motion in `dist/modules`, checked by grep).
