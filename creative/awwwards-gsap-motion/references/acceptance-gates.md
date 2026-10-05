---
description: "Acceptance gates for motion-heavy pages: slopscan rule list, honest perf measurement (DPR, GPU, prod build), serve-don't-file://, fallback-payload check"
source_repo: agiwhitelist/auteur (MIT)
tested_version: README + reference/verify.md + scripts/slopscan.mjs read via GitHub API @ main, not run locally
verified_date: "2026-10-05"
---

# Acceptance gates for motion-heavy pages

A page that "looks done" in the editor is what every model ships. Done means three checks passed,
cheapest first: a deterministic linter, a screenshot journey, a numeric rubric. Distilled from
auteur's `reference/verify.md` and `scripts/slopscan.mjs`; the scripts themselves are not vendored
here, so the rules below are what to reproduce (or `npx skills add agiwhitelist/auteur` for the real linter).

## 1. Linter rules worth enforcing in code

FAIL (the build stops):

| Rule | Catches |
|---|---|
| `FONT_DEFAULT_SLOP` | Inter / Space Grotesk as the committed display or body face |
| `AI_GRADIENT` | the 250-290 degree purple-to-blue gradient |
| `GRADIENT_TEXT` | `background-clip: text` gradient headlines |
| `TRANSITION_ALL` | `transition: all`; it animates layout properties and hides what actually moves |
| `RAW_SCROLL_LISTENER` | `addEventListener('scroll')` driving animation; use ScrollTrigger / IntersectionObserver / CSS `animation-timeline` |
| `AUTOPLAY_SOUND` | audio or unmuted video that starts without a user gesture |

WARN (read each one, fix or accept in writing):

| Rule | Catches |
|---|---|
| `GLASS_CARD`, `CARD_CLONE_GRID` | glassmorphism cards and identical-card grids |
| `EM_DASH_COPY` | em-dash rhythm in copy (count `&mdash;` too; an entity dodges a naive regex) |
| `EYEBROW_EVERYWHERE` | a small-caps eyebrow label above every heading |
| `CREAM_DEFAULT` | the cream/beige "editorial" background reflex |
| `VIDEO_NO_POSTER` | `<video>` with no poster, so the hero is blank until decode |
| `WEBGL_NO_REDUCED_MOTION` | a WebGL canvas with no `prefers-reduced-motion` branch |
| `POINTER_NO_RAF` | pointer handlers doing work outside `requestAnimationFrame` |

Two habits that keep a linter honest:

- Suppression needs a reason: `/* allow: RULE_ID -- <10+ chars naming the design decision> */`. A bare suppression is itself reported.
- Quote the linter's final `Summary:` line in the report **after the last edit**. A remembered result is not a result.

## 2. Verify over HTTP, never `file://`

`fetch()` to a `file:` URL is blocked. A page that loads a glTF, HDRI, JSON or frame manifest silently
falls back to its poster, and a screenshot tool photographs an attractive page whose main scene never
booted. That is a false PASS. Any static server will do (`python -m http.server`, a 40-line `node:http`).

Screenshot at 390 / 768 / 1440 and read every frame. Also:

- `--full` page captures composite `position: fixed` and stuck `sticky` elements at their viewport position, so a fixed bottom nav shows mid-page. Judge those from viewport frames only.
- Console errors and "possibly blank" warnings are FAILs until explained.
- Run the reduced-motion journey as its own pass: it must be a watchable cut, not a blank canvas.

## 3. Perf numbers are only as honest as three settings

Every default flatters the page. State all three when you quote a number
(e.g. "minFps 57 at 4x CPU, 1440x900 @2x, production build").

| Setting | Wrong default | Why it matters |
|---|---|---|
| Pixels | DPR 1 (1.3MP) | fullscreen passes (bloom, DoF, grain) cost per pixel; DPR 2 is 5.2MP, so DPR 1 certifies 60fps on a page that stutters on a retina laptop. Scenes with no fullscreen pass measure the same at both, which is the correct result. |
| GPU | headless chromium | software raster; auteur measured 6 / 20 / 20 fps headless vs 53 / 53 / 54 headed. A headless number is a floor, not a verdict. |
| Build | dev server | HMR client and unminified bundles cost roughly 2x per frame. This errs toward false FAILs, which is how a good scene gets cut for nothing. |

Throttle the CPU (`Emulation.setCPUThrottlingRate`, rate 4) because jank hides at full speed. Assert:

- minFps >= 50 while scrolling the whole page
- no long task over 50ms (observe `longtask` via `PerformanceObserver`)
- WebGL context count flat across route changes (no "Too many active WebGL contexts"); swap textures, never remount
- audio off until a gesture, with a visible mute control, and the visual complete when muted
- poster or first frame paints inside the LCP budget

## 4. Numeric rubric

| Check | Threshold |
|---|---|
| Body contrast | >= 4.5:1 (large text 3:1), **measured in every state**: an error or stale view that dims its own text is the usual failure, and linters read the undimmed colour |
| LCP / CLS / INP | < 2.5s throttled / < 0.1 / < 200ms |
| Hero video / poster | <= 2MB / <= 300KB; sequence frames <= 150KB each at 1440w |
| Scroll-pattern families | <= 3 per page; exactly one peak scene at intensity >= 8 |
| Adjacent scenes | no two neighbours share a layout family |
| Background lightness | within +/-0.12 OKLCH L of the value committed before the build (a measured check that the built page matches its own art direction) |
| Keyboard, no-JS | tab order sane, focus visible, no traps, ESC closes overlays; content readable with JS off |
| Fallback payload | every degraded cut (reduced-motion, no-JS, no-WebGL) still carries the peak's information, checked at 390 too: a callout hidden by a mobile breakpoint deletes the payload while desktop screenshots look fine |

## 5. Method note: commit before you build

auteur's other transferable idea is a short written art direction committed before any markup: one
brand hue, a type system, a motion budget, named anti-references (the "house tells" of the category
that this page will break, at least two), and a target background lightness. The gates above then
check the build against that document instead of against taste. `design-taste-frontend` supplies the
dial-based version of the same idea.

## 6. Cross-route drift (multi-screen products)

A product fails differently from a page: each screen looks fine alone while a fourth button variant
appears on screen seven. Crawl every route (not a sample), read the computed styles the browser
actually painted, and fail on any control kind that exceeds its declared per-kind variant budget or
any control with no visible focus state.
