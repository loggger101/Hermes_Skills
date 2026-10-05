# Animate.css 4.1.1: what the stylesheet really does (parsed live, three traps confirmed in Chrome)

Source: [animate-css/animate.css](https://github.com/animate-css/animate.css) (82.9k stars, last push 2024-07-29, so
effectively finished). npm `animate.css` **4.1.1**, installed with `npm install --prefix` on Windows and parsed with Node;
the trap checks ran in the in-app Chromium against a page served from `http://127.0.0.1`. The licence line inside the
CSS header says **MIT** while the repo README says **Hippocratic License**: check before shipping in a product with
ethical-use constraints. Not covered: the animate.style docs site, the `source/` build, and any JS wrapper.

## Package facts (counted from the files)

| File | Bytes | Class prefix | Notes |
|---|---|---|---|
| `animate.css` | 95,374 | `animate__` (`.animate__animated`, `.animate__fadeInUp`) | the default `main`/`style` entry |
| `animate.min.css` | 71,750 | `animate__` | same rules, minified |
| `animate.compat.css` | 70,607 | **none** (`.animated`, `.fadeInUp`, `.delay-2s`, `.fast`) | v3-style names, minified |

All three hold 97 `@keyframes`, 111 distinct classes, 835 `-webkit-` declarations (every keyframe is written twice,
`@-webkit-keyframes` plus `@keyframes`: the prefixed copies are dead weight for any browser since 2016) and exactly three
custom properties: `--animate-duration: 1s`, `--animate-delay: 1s`, `--animate-repeat: 1`. Every keyframe has a matching class
and vice versa. Keyframe families (count): fade 26, bounce 11, rotate 10, zoom 10, slide 8, back 8, flip 5, lightSpeed 4, plus
singletons (flash, pulse, rubberBand, shake x2, headShake, swing, tada, wobble, jello, heartBeat, hinge, jackInTheBox, roll x2).
**Use the compat file only for migrating v3 markup**: its bare names (`.fast`, `.slow`, `.infinite`, `.flip`, `.bounce`) collide
with any other framework or your own utilities.

## Tuning classes are multipliers of the variables

Every rule is emitted twice, a literal fallback then a `var()` version, so `animate.css` works without custom-property support.

- Speed: `animate__faster` = duration/2, `fast` = x0.8, `slow` = x2, `slower` = x3 (no class = 1s).
- Delay: `animate__delay-1s` .. `-5s` = `calc(var(--animate-delay) * N)`. Repeat: `animate__repeat-1/2/3` = `--animate-repeat * N`;
  `animate__infinite` sets iteration-count infinite.
- **Retune globally or per element with the variables, not by overriding the named class**: `:root { --animate-duration: 300ms }`
  shortens every animation and every `fast`/`slow` multiple of it; `style="--animate-delay: 150ms"` on one element re-bases its
  `delay-Ns` class. The speed/delay/repeat classes carry the selector `.animate__animated.animate__xxx` (two classes), so a
  plain `.animate__fadeIn { animation-duration: .2s }` loses to them.

## Three traps (all confirmed in Chrome with `--animate-duration: 60ms`, animations forced to their end with `finish()`)

1. **The end state is kept (`animation-fill-mode: both`) and the final keyframe overrides your own `transform`.** An element
   with `transform: rotate(45deg)` and class `animate__fadeInUp` computes `matrix(1, 0, 0, 1, 0, 0)` afterwards: the rotation is
   gone for good, not just during the animation. Same for any class that ends in `translate3d(0,0,0)`, `scale3d(1,1,1)`, etc.
   Fix: animate a wrapper element, or remove the animation classes on `animationend` so the element's own style applies again.
2. **A delayed entrance is invisible during its delay.** `fill-mode: both` applies the `from` keyframe at once, so
   `fadeIn` + `delay-1s` computed `opacity: 0` straight away. That is usually the intent, but it also means a hidden entrance
   still occupies layout and can be tabbed to: add `inert`/`aria-hidden` until it plays if the content matters.
3. **Exit classes do not remove the element.** After `animate__fadeOut` the button computed `opacity: 0`, `display: inline-block`,
   `visibility: visible`: it still takes space, stays in the tab order and keeps the accessibility tree entry (opacity does not
   change hit-testing; the click-through itself was not exercised, the pane had a 0x0 viewport). Remove or `hidden`-flag the
   node in an `animationend` handler: `el.addEventListener('animationend', () => el.remove(), { once: true })`.

Also remember to strip the classes before re-triggering: re-adding the same class on an element that already has it does nothing,
so the standard replay is remove class, force reflow (`void el.offsetWidth`), add class (or toggle through `animationend`).

## Reduced motion is built in, and has a naming trap

The shipped media query is `@media print, (prefers-reduced-motion: reduce)`:

```css
.animate__animated { animation-duration: 1ms !important; transition-duration: 1ms !important;
                     animation-iteration-count: 1 !important; }
.animate__animated[class*='Out'] { opacity: 0; }
```

- It collapses every animation to 1ms, one iteration, so `infinite` loops stop and `animationend` still fires (JS that waits
  for it keeps working). It also applies **when printing**.
- The `[class*='Out']` substring selector fixes exit animations (the element ends hidden). It is case-sensitive and matches **any
  class containing `Out`** on an `animate__animated` element: `layoutOutline` or `fadeOutro` would be forced to `opacity: 0` for
  reduced-motion users (the regex check: `Out` matches `layoutOutline`, not `layout`). Do not put your own `...Out...` class names on
  elements that also carry `animate__animated`.
- 41 keyframes are exits (`...Out...`) against 42 entrances, so the rule covers every exit; attention seekers (`pulse`, `shake`,
  `tada`) just become instant, which is the right outcome.

## When to use it, and what to use instead

- Good for: marketing pages and static sites with a handful of one-shot entrances where adding a dependency on JS is unwanted
  (class toggle + `animationend` is the whole API). Pair with `IntersectionObserver` for scroll-reveal.
- Not for: anything interruptible, spring-based, layout-aware or driven by state (use the Motion notes in
  `web-development/react-ecosystem/references/motion-14-notes.md`), or when 95 KB of CSS for three animations is the wrong
  trade: copy the two or three keyframes you need (each is 5 to 20 lines) instead of linking the file.
- Respect the existing `prefers-reduced-motion` and performance rules in `references/web-interface-guidelines-ui-checklist.md`;
  the keyframes set only `transform`, `opacity`, `transform-origin` and `visibility` (plus timing functions), so the
  animations stay compositor-friendly (property list collected from all 97 keyframes).
