# Materialize CSS: the starred repo is frozen at 1.0.0; the maintained line is `@materializecss/materialize` 2.x

Source: [Dogfalo/materialize](https://github.com/Dogfalo/materialize) (38.8k stars, MIT). Facts from the GitHub API and npm, then
both packages installed and measured (file sizes, a jsdom run of the bundles) on Node/Windows. Not covered: a real-browser
render, Sass builds, the docs site, accessibility testing with a screen reader.

## Which one is maintained

| | Dogfalo `materialize-css` | Community fork `@materializecss/materialize` |
|---|---|---|
| npm version | **1.0.0** (npm last modified 2022-06) | **2.4.0** (npm last modified 2026-09-24) |
| Repo state | last release 2018-09-09; last commit on the default branch (`v1-dev`) 2020-06-01 ("patreon june"); 789 open issues; the repo's `pushed_at` is later, so do not read it as activity | active (`materializecss/materialize`, site materializeweb.com) |
| Design language | Material Design 1 | Material 3 tokens: `:root` holds `--md-source`, `--md-ref-palette-*`, `--md-sys-color-*` (1,282 custom properties), and an `@media (prefers-color-scheme: dark)` block flips them |
| Module formats | UMD global `M` only (`main: dist/js/materialize.js`), no types, **no dependencies** | ESM (`.mjs`), CJS (`.cjs.js`), UMD, `materialize.d.ts`, `exports` map; **depends on `@js-temporal/polyfill`** |
| Sizes (min / gzip) | CSS 141.8 kB / 21.6 kB, JS 181.1 kB / 42.9 kB | CSS 125.9 kB / 20.3 kB, JS 138.4 kB / 33.9 kB |

New work should not start on 1.0.0 (frozen for six years, jQuery-era patterns). If a Materialize look is wanted, use the fork,
and still treat both as large for what they give: a 20 kB-gzip stylesheet plus 34 to 43 kB of JS.

## Measured facts that apply to both

- Neither stylesheet has any `@font-face`, and v1's `dist/fonts/` directory in the npm tarball is **empty**. The `.material-icons`
  class only styles a ligature; the **Material Icons font must be loaded separately** (Google Fonts link or self-hosted woff2), or icons
  render as literal text like `home`. Self-host it for privacy/CSP-sensitive sites.
- Both ship a Normalize-style reset against bare elements (`html { line-height: 1.15 }`, `body { margin: 0 }`, rules on `a`, `h1-h6`,
  `p`, `ul`, `table`, `label`, `input`, `button`, `img`), so adding it to an existing page restyles unclassed markup.
- Neither stylesheet contains `prefers-reduced-motion` handling; ripples, modals and sidenav transitions always animate.
- `window.M` is the whole JS API (v1: 22 components incl. `Materialbox`, `Parallax`, `Pushpin`, `TapTarget`, `ScrollSpy`;
  v2: 23 exports that add `Button`, `Cards`, `Forms`, `TextField`, `Waves` and drop Materialbox/Parallax/Pushpin/TapTarget). `M.AutoInit()` initialises every component it finds.

## Migration traps (v1 to v2, found by running both bundles in jsdom)

1. **Grid markup changed.** v1: `<div class="row"><div class="col s12 m6">`. v2's stylesheet has `.row .s12` and no `.col.s12` rule
   (a v1 grid copied over loses its columns): v2 columns are `<div class="row"><div class="s12 m6">`. Check every `col` class.
2. **`M.toast(...)` is gone in v2** (`M.toast is not a function`); v2 exposes a `Toast` class (`new M.Toast({...})`). Options were also
   renamed; read `materialize.d.ts` before porting.
3. **v2's `M.version` string says `2.3.3` inside the 2.4.0 package.** Do not use it to detect the installed version; read package.json.
4. **v2 `AutoInit()` threw `TypeError: Cannot read properties of undefined (reading 'trim')` in jsdom when the page held a
   `<select>`**, while v1 initialised the same page (jsdom added `.select-wrapper`). Cause not isolated (may be jsdom-specific): if a
   v2 page dies in `AutoInit`, initialise components one by one to find the failing one.
5. `.waves-effect` rules exist in v1's CSS (12 mentions) but not in v2's, which handles ripples in a JS `Waves` class instead.
6. v1's modal got `tabindex` but **no `role="dialog"` or `aria-modal`** in the DOM after `open()`; add them yourself or use the native
   `<dialog>` element. (Not checked for v2: its modal did not render an overlay in jsdom, so the behaviour test was inconclusive.)

## Decision

For a new static site, prefer a smaller or class-free base (see `SKILL.md` here for Core Web Vitals cost) and use native `<dialog>`,
`<details>` and CSS custom properties. Keep Materialize only when matching an existing Materialize product or when the user asks
for Material look explicitly; then install the fork and self-host the icon font.
