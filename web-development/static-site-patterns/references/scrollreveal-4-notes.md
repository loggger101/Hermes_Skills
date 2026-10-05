# ScrollReveal 4.0.9: GPL licence, frozen since 2022, inline-style side effects (jsdom run) and the native replacements

Source: [jlmakes/scrollreveal](https://github.com/jlmakes/scrollreveal) (22.5k stars, last push 2024-04-05). npm `scrollreveal`
**4.0.9** (npm last modified 2022-06-26) installed and its `dist/scrollreveal.js` run inside jsdom with stubbed geometry; defaults, side effects
and licence read from the source and README. Not covered: real scroll-triggered timing. jsdom has no layout, so an element placed in
view never revealed (opacity stayed 0, `afterReveal` never fired); that part is **not verified**. No real-browser run of the library
(the in-app browser's document was hidden, which pauses animation timelines).

## Licence: GPL-3.0 unless you buy a commercial licence

npm lists `GPL-3.0`; GitHub shows no detected licence (`license: null`). The README says: **"For commercial sites, themes, projects, and
applications, keep your source code private/proprietary by purchasing a Commercial License"**; GPL 3.0 is for compatible open-source and
non-commercial use (copyright 2023 Fisssion LLC). Do not drop it into a client's proprietary site by habit.

## State of the project

Last release 2022, repo quiet since April 2024, no maintained successor. The code is small: `dist/scrollreveal.min.js` **16.6 kB
(5.8 kB gzip)**, runtime deps `miniraf`, `rematrix`, `tealight` (already inside the bundle). The `module` entry is `dist/scrollreveal.es.js`.

## API and defaults (read from the source)

`const sr = ScrollReveal()` is a **singleton** (a second `ScrollReveal()` returned the same instance). Methods: `reveal(target, options, interval)`,
`sync()`, `clean(target)`, `destroy()`, `delegate()`; `ScrollReveal.isSupported()` (needs CSS transform and transition support) and
`sr.noop`. When unsupported or misconfigured it returns a no-op object and removes the `sr` class instead of throwing.

Defaults: `delay: 0`, `distance: '0'`, `duration: 600`, `easing: 'cubic-bezier(0.5, 0, 0, 1)'`, `interval: 0`, `opacity: 0`,
`origin: 'bottom'`, `rotate: {x:0,y:0,z:0}`, `scale: 1`, `cleanup: false`, `container: document.documentElement`, `desktop: true`,
`mobile: true`, `reset: false`, `useDelay: 'always'`, `viewFactor: 0`, `viewOffset: {top,right,bottom,left: 0}`, and
`before/afterReveal`, `before/afterReset` callbacks. Misconfiguration is logged (`ScrollReveal.debug = true` prints
`Reveal failed.` with the reason, e.g. `Expected either an array or object literal`), not thrown.

## Side effects observed (jsdom)

- **`<html class="sr">` is added when the script loads**, before any `reveal()` call, and `document.body.style.height = '100%'` is set
  (source lines 66 to 72). The intended use is a CSS rule such as `.sr .reveal { visibility: hidden }` to avoid a flash; without JS the
  class is absent. `destroy()` did **not** remove the `sr` class.
- **`reveal()` rewrites the element's inline style.** An `<h1 style="color:red;transform:rotate(10deg)">` became
  `color: red; transform: matrix3d(0.9, 0, 0, 0, 0, 0.9, 0, 0, 0, 0, 1, 0, -40, 0, 0, 1); visibility: visible; opacity: 0;` and got `data-sr-id`.
  Your own inline `transform` is replaced by the generated matrix (the original is kept in the store and re-applied by `destroy()`/`clean()`).
  Revealing the same element twice re-generates the matrix (`-40` became `-10` for `distance: '10px'`). Animate a wrapper element rather than
  one that already carries a `transform`.
- `destroy()` restored the original `transform: rotate(10deg)` but left `visibility: visible; opacity: 0;` on the element in this run, and
  an element that never revealed stayed `opacity: 0`. Whether this also happens in a real browser for revealed elements was not checked:
  after `destroy()`, assert that content is visible.
- **No `prefers-reduced-motion` handling anywhere in the source** (zero occurrences): users who asked for less motion still get slides and fades.
  Wrap the call: `if (!matchMedia('(prefers-reduced-motion: reduce)').matches) sr.reveal(...)`, and make sure the "hidden until revealed"
  CSS is also skipped in that case.
- A hidden-until-JS rule is a risk for crawlers, print and JS failures; scope it to `.sr` as above.

## Native replacements (preferred for new work)

1. **CSS scroll-driven animation** (no JS):

   ```css
   @keyframes rv { from { opacity: 0; translate: 0 40px } to { opacity: 1; translate: 0 0 } }
   .rv { animation: rv linear both; animation-timeline: view(); animation-range: entry 0% entry 60%; }
   @media (prefers-reduced-motion: reduce) { .rv { animation: none } }
   ```

   In Chrome 152 `CSS.supports` answered true for `animation-timeline: view()`, `animation-timeline: scroll()` and
   `animation-range`, and the rule above produced a `CSSAnimation` on a `ViewTimeline` for the element. The animated values could not be
   sampled (the pane's document was hidden, so timelines had no current time), so check the visual result yourself and
   verify browser support for your audience, with the reduced-motion branch as the fallback.
2. **`IntersectionObserver`** (supported everywhere): add a class once the element intersects, `unobserve` it, and keep the
   transition in CSS with a reduced-motion override. About 10 lines, no licence concerns.

Use ScrollReveal only to maintain an existing page that already depends on it.
