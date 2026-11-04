---
description: "Concrete CSS, typography and access floors from hallmark's 39 KB gate list - the blank-page-at-rest reveal gotcha, transition/animation bans, focus-ring and tooltip timing, contrast thresholds with APCA numbers, layout traps (dvh not vh, minmax(0,1fr), sticky-sticky collision, overflow-x clip), honesty floors (no invented metrics, no fake-send forms, capture the real product instead of drawing it) - each as tell plus fix; static-checked by sloplint and live-run on Node 22"
source_repo: Nutlope/hallmark v2.0.0 (MIT) at main, 2026-11-04 - skills/hallmark/references/gates.md § 4 (+ scripts/sloplint.mjs run against its fixtures)
tested_version: "LIVE-RUN for the static tier on Node v22 (Windows): gate ids fire with line numbers as documented; render-tier gates (px/geometry claims measured in a browser) were NOT verified here - puppeteer-core and Chrome are absent, so treat those specific thresholds as source-read"
verified_date: "2026-11-04"
---

# CSS / access floors worth adopting from hallmark's gate list

The control architecture (tiers, guarded waivers, graded verdicts) is in
`../../../../software-development/verification-culture/references/tiered-gates-and-waivers.md`. This file keeps the **specific
tells and fixes** — each one either verified firing by `sloplint` here, or marked *render* (measured in-browser upstream, not here).

## The gotcha that ships a blank page (Floor, static)

> Gate 62: *"a reveal class setting `opacity: 0` or `visibility: hidden` that depends on JavaScript to show it, with no `.js`
> scoping, no self-running CSS animation and no `@starting-style`, so the page ships blank when a script fails."*
> Fix: visible by default; hide only under a `.js` class, or animate from visible with `@starting-style`.

Every scroll-reveal recipe in our creative/web skills should carry this. It is the CSS equivalent of swallowing an error.

## Motion bans (Floor, static — all four observed firing)

- No `transition: all`; **list transitioned properties**. Animating `width`, `height`, `top`, `left` is out → `transform`/`opacity`.
  (`FAIL 10a :78 transition: all on .card`, `FAIL 10a :96 @keyframes grow animates width`)
- A **focus ring must not fade in** — rings appear instantly (`FAIL 15`). Ring needs ≥3:1 against what it's drawn over, and
  removing the outline with nothing in its place is a Floor breach (26a).
- Any keyframe/transform transition requires a `prefers-reduced-motion: reduce` fallback (`FAIL 27`, fired here on a fixture that
  had motion and no block).
- Tooltips: hover delay **800–1000 ms**, focus delay **0** — equal delays are a Floor breach (gate 17), because keyboard users get
  punished for what mouse users tolerate.
- Auto-rotating content must pause on hover *and* focus, with a visible pause control past 5 s of motion (18).

## Contrast and colour mechanics (Floor; static half verified)

Gate 40: text/icon/focus-ring/field-edge under threshold against its **computed** background — body **4.5:1 or APCA Lc 60**;
large text, icons, rings and field edges **3:1 or Lc 45**. Gate 41: button text within 5% lightness / 0.05 chroma of its fill is
unreadable-by-construction; a dark panel that never swaps its text colour, or grey text on a coloured surface, fails the same way —
the fix is a paired ink token (`--color-accent-ink`). Gate 48: **no raw colour or `font-family` literal outside the token block**.

Pure absolutes are their own reflex family (measured firing as waivers): `#000`/`#fff` as page colour, and zero-chroma neutrals on a
page that has an anchor hue — tint toward it at chroma ≥ 0.005 (7a Floor / 7b + 22 Reflex).

## Layout traps (mix of static-verified and *render*)

| Tell | Fix | Status here |
| --- | --- | --- |
| Hero sized in `vh` | `dvh`/`svh` (mobile chrome makes `100vh` taller than the screen) | 6a Floor, static |
| Image-bearing grid track on bare `1fr`; display head without `overflow-wrap: break-word; min-width: 0` | `minmax(0, 1fr)`; `break-word`, **never** `anywhere` | 50 Floor, static |
| Two `position: sticky; top: 0` elements (section head sliding under the nav) | second gets `top: var(--banner-height)`; z-order tokens keep nav above | 56 Floor, static |
| Horizontal scroll / `100vw` widths | `overflow-x: clip` on `html` **and** `body`; `width: 100%` | 34 Floor (geometry half = *render*) |
| Card inside a card | one containment layer | 4 Floor, static (`FAIL 4 :127 card nested in card`) |
| Raw `padding/margin/gap` where a `--space-*` token exists | the token; off-scale allowed ≤3 as optical nudges | 24a Floor / 24b Reflex |
| Running prose outside **45–75ch**, or rendered lines ~88 chars over three lines | `max-width: 65ch`; a two-sentence lede may sit from 28ch | 25 Reflex (*render* half) |
| More than three font families; Inter/Roboto/Lato/Poppins as the display face | display + body + one outlier, from theme or its fonts list | 37 / 1 Reflex, static (`WAIVED 1 :42 display font "inter"`) |
| Mono-as-costume: monospace on labels/captions/meta when neither display nor body is mono and content isn't code | body face, one step smaller, normal case | 64 Reflex, static (fired here) |
| `text-wrap: balance` missing on h1/h2-level heads | add it | F3 Finish (`WARN … no text-wrap: balance`) |

## Access & asset floors (static)

Emoji standing in for an icon is Floor (30a); two icon libraries on one page is a Reflex with a narrow brand-mark guard (30b);
decorative `<svg>`/`<canvas>`/CSS-art needs `aria-hidden="true"` **or** a label — "hide it or name it" (33). A broken image, or a
library photo without its credit on the page, is Floor; a paid-stock hotlink reports as WARN only (76).

## Honesty floors — these are not aesthetic rules

- **46a Floor:** an invented metric, testimonial, logo wall or case-study count. Fix: *"the user's number, a text slot, or nothing."*
  (`FAIL 19 :141 placeholder name: "Jane Doe"` fires from the same family.)
- **70 Floor — the fake send:** a form that prints "Sent / You're on the list" with no request behind it. Fix: empty `data-endpoint`
  and **no success state until wired**; the handoff names the endpoint. Same rule our plan/sketch notes argue for, stated as a ship-blocker.
- **84 Reflex — the fake product:** drawing a mock of a product that exists and could be run (a URL, a dev server, a project in the
  folder). Fix: *"run it, put it in a telling state and capture it"* with their `capture.mjs` or the OS. That is our `dogfood` skill's
  thesis expressed as a lint rule; *render* half unmeasured here.
- **Copy tells (19 Floor),** static and observed firing on buzzwords: placeholder names, startup clichés, *seamless / robust / empower /
  supercharge / elevate / effortless / unlock / unleash / next-generation / world-class*, the rebuttal cadence ("Not a feature. A platform.")
  three or more times, "quietly trusted by", filler openers, and a stock second action beside the primary (*Learn more*, *Get started*,
  *Book a demo*). Fix: *"say what the product does, in its own nouns."* Their list also bans **em/en dashes** — flag that as *their* house
  rule (it collides with normal technical prose), unlike the buzzword bans which are quality claims.

## Anti-slop composition tells worth knowing even without the tool

The eyebrow before a heading (54 Floor, `FAIL 54 :66 eyebrow "01 · The tour" before <h2>`); tracked-caps labels ≤15 px or letter-spacing
past 0.03em (67 Floor); template punctuation — middle-dot meta strings `A · B · C`, arrow glued to link text, decorative status dots
(63 Floor); the AI nav/footer shapes unnamed in the stamp (42); three equal icon-above-heading tiles and thick coloured card stripes (3);
purple→blue or cyan-on-dark gradients anywhere including `background-clip: text` (2a Floor) and a framework's default palette as tokens —
Tailwind indigo-500 / violet-600 / slate-900 (74 Reflex); the drawn illustration past icon size where a photo belonged (80 *render*);
the counting device of 24+ identical marks standing for a quantity (82 *render* — set the number in type).

## What was **not** verified here

Every px/geometry threshold (hero centring, section gaps at 1440, dead-band size, contrast against computed backgrounds) lives in the
render tier and needs puppeteer-core + Chrome; on this box `--render` reported *"render tier not run"* while still exiting 0. Treat those
numbers as upstream-asserted, adopt them by running the tool, and never quote them as locally measured.
