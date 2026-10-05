# Motion 14.0.0 (ex Framer Motion): springs, headless animation, React SSR output (run live)

Source: [motiondivision/motion](https://github.com/motiondivision/motion) (MIT, 33.8k stars). npm `motion` **14.0.0** (the
package `framer-motion` is the same version and is pulled in as a dependency, with `motion-dom` and `motion-utils`), Node 22.23.2
on Windows, React 19.3 and jsdom for the DOM parts. About 75 probes in three scripts; each value below is an observed
output. Not covered: scroll-linked animation (`scroll`, `useScroll`), drag gestures, layout animations, `Reorder`, and any
real browser rendering.

## Package surface

- `import ... from 'motion'` exposes **327 names**, `'motion/react'` **398**, `'motion/mini'` only `animate` and `animateSequence`.
  The vanilla entry leaks internals (`VisualElement`, `HTMLProjectionNode`, ...): import only the documented ones (`animate`, `spring`,
  `inertia`, `stagger`, `mix`, `interpolate`, `transform`, `clamp`, `progress`, `wrap`, `cubicBezier`, `steps`, `motionValue`, `hover`,
  `press`, `inView`, `scroll`, `frame`, `cancelFrame`, `delay`).
- Present in `motion/react` (all 24 checked): `motion`, `m`, `AnimatePresence`, `LazyMotion`, `domAnimation`, `domMax`, `MotionConfig`,
  `LayoutGroup`, `Reorder`, `useMotionValue`, `useSpring`, `useScroll`, `useTransform`, `useAnimate`, `useInView`, `useReducedMotion`,
  `useAnimationFrame`, `useVelocity`, `useMotionValueEvent`, `useDragControls`, `usePresence`, `useMotionTemplate`, `useTime`,
  `useFollowValue`. `motion.create(Component)` and `motion(Component)` are both functions.
- Easings exported as functions: `easeIn easeOut easeInOut circIn circOut backOut anticipate cubicBezier steps`. **There is no
  exported `linear` or `easeInOutCubic`**; pass `'linear'` as a string.

## Pure maths (no DOM)

| Call | Result |
|---|---|
| `mix(0, 100, 0.25)` | 25 |
| `mix('#ff0000', '#0000ff')(0.5)` | `rgba(180, 0, 180, 1)`: colours blend in a gamma-corrected space (sqrt of the mean of squares), **not 127** |
| `interpolate([0,1,2],[0,100,50])(1.5)` | 75; out-of-range input is **clamped by default** (`[0,10]`->`[0,1]` at 20 gives 1; `{clamp:false}` gives 2) |
| `interpolate([0,1],['0px','10px'])(.5)` / colours | `5px` / `rgba(180, 180, 180, 1)` for `#000`->`#fff` |
| `clamp(0,1,2)`, `progress(10,20,15)`, `wrap(0,3,4)` | 1, 0.5, 1 |
| `stagger(0.1)(i, 4)` for i = 0, 3 | 0 and `0.30000000000000004` (float noise; round before comparing); `{from:'last'}` index 0 -> 0.3; `{startDelay:1}` index 2 -> 1.2 |
| easings at 0.25 / 0.5 / 0.75 | `easeIn` .093 .315 .622; `easeOut` .378 .685 .907; `easeInOut` .129 .5 .871; `circOut` .661 .866 .968; `backOut` .797 **1.067** 1.058; `anticipate` **-.034** .5 .984 |

## Spring generator

`spring({keyframes:[0,100], stiffness:100, damping:10, mass:1})` sampled with `.next(t_ms)`: t=100 -> 34.03, 300 -> 112.44,
600 -> 100.23, 1000 -> 100.22, 2000 -> 100 and `done`. It settled at **1050 ms** (`calcGeneratorDuration` agrees) with a peak
of **116.3** (16% overshoot). The duration form `spring({keyframes:[0,1], visualDuration:0.4, bounce:0.25})` was done at 679 ms and was
at 1.026 at 400 ms (the *visual* duration is when it first reaches the target, not when it rests); `duration:500, bounce:0` never
exceeded 1 (critically damped). `inertia({keyframes:[0,0], velocity:1000, power:.8, timeConstant:700})` -> 0 at t=0, 408.4 at 500 ms,
done by 10 s. A `MotionValue` animated with `{type:'spring', stiffness:300, damping:30}` ran 24 updates to 100 with a max of 100.42.

## `animate()` outside a browser

- **In plain Node `animate(0, 100, {onUpdate})` never runs**: with no `requestAnimationFrame`, 0 updates and no `onComplete` after
  500 ms (and an `await` on it ends in "unsettled top-level await"). With a shim installed **before** `motion` is imported
  (`globalThis.requestAnimationFrame = cb => setTimeout(() => cb(performance.now()), 16)`) it produced 5 updates over 0.1 s,
  monotonic, first 18-25, last 100, then `onComplete`. Load the shim from a separate first import: ES module imports are hoisted.
- `animate(0,1)` returns controls with `play pause stop cancel complete finished then time speed duration state attachTimeline`;
  `await animate(...)` resolves.
- **A bad easing string throws asynchronously**: `animate(0, 1, {ease: 'nonsense'})` returned normally, then the next frame raised
  `Error: Invalid easing type 'nonsense'` as an **uncaught exception** that `try/catch` around `animate()` cannot see. Validate easings
  against a fixed list.
- DOM targets need real DOM globals: `animate('#x', ...)` -> `ReferenceError: document is not defined`; with jsdom but only
  `document` set -> `NodeList is not defined`, then `Element is not defined`. Copy `document, Element, HTMLElement, SVGElement, NodeList,
  Node, getComputedStyle` (and `window`, `navigator`) from the jsdom window. With those, `animate(el, {opacity:1, x:50}, {duration:.05})`
  ended at `opacity 1`, `transform translateX(50px)` even though jsdom has **no `Element.animate`** (WAAPI): the JS fallback drove it;
  `animate('.c', {opacity:.5}, {delay: stagger(.02)})` set both targets to 0.5. `motion/mini` (the WAAPI-only build) **threw
  `No valid elements provided` for the same jsdom element even with all those globals set**; jsdom has no `Element.animate`, the exact check that
  failed was not isolated. Use the full `animate` in tests.

## React server-render output (`renderToStaticMarkup`)

| Element | HTML |
|---|---|
| `motion.div initial={{opacity:0,x:-20}} animate={{opacity:1,x:0}}` | `<div style="opacity:0;transform:translateX(-20px)">`: the **initial** values are rendered, so the first paint is the start state |
| `style={{x:10,y:20,scale:1.5,rotate:45,opacity:.5}}` | `opacity:0.5;transform:translateX(10px) translateY(20px) scale(1.5) rotate(45deg)` (fixed order x, y, scale, rotate) |
| `initial={false} animate={{opacity:1,x:5}}` | `opacity:1;transform:translateX(5px)`: skips the entrance, renders the end state |
| `initial="hidden"` on a `motion.ul` with `variants` | the child `motion.li` inherits `opacity:0` through the variant label |
| `motion.path d=... pathLength={0.5} initial={{pathLength:0}}` | `pathLength="1" stroke-dashoffset="0" stroke-dasharray="0 1"` (draws nothing until animated) |
| `MotionConfig reducedMotion="always"` with `initial x:0` | `style="transform:none"` |
| `AnimatePresence` around an element with `exit` | the child renders normally on the server |
| `LazyMotion strict` with `m.div` | `<div></div>`; with `motion.div` it throws `You have rendered a motion component within a LazyMotion component. This will break tree shaking. Import and render a m component instead` |

Practical consequence: when text should be visible without JavaScript, do not use `initial={{opacity: 0}}` on it; server HTML ships
the hidden state. Use `initial={false}` or animate transforms only.
