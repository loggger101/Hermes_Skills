# Metro UI 5.1.20 (`@olton/metroui`): a 1.5 MB CSS / 0.9 MB JS framework with a global reset (measured, jsdom run)

Source: [olton/metroui](https://github.com/olton/metroui) (7.1k stars, MIT, default branch `dev`, pushed 2026-02-01). npm
`@olton/metroui` **5.1.20** (modified 2025-10-19) installed with jsdom; its `lib/metro.js` evaluated in jsdom, `lib/*.css` measured and
grepped. The older package `metro4` stops at `5.0.0-rc0` (2024-05): use the scoped name. Not covered: visual rendering, the component docs, the NuGet
package, the paid "SUPPORT PACK" (priority email support only, per the README; code stays MIT).

## Weight (the main finding)

| File in `lib/` | Bytes | Gzip |
|---|---|---|
| `metro.css` | **1,481,825** | 210,547 |
| `metro.js` | **919,303** | 243,624 |
| `icons.css` | 392,894 | 187,932 |
| `metro.all.css` / `metro.all.js` | 1,874,718 / 919,303 | not measured |

About 20,000 CSS rules and 8,243 `--custom-property` references. Together about 640 kB gzip for the CSS, JS and icons before any page content: far beyond
a static page's budget (compare Font Awesome's 23 kB CSS in `font-awesome-7-free-notes.md`). The npm tarball is **54 MB** because `package.json` has no `files`
whitelist (it ships `examples/`, `fails/`, `temp/`, `CLA.docx`, `source/`); a project with jsdom came to 79 MB in `node_modules`. The README badge says
"Dependencies: none", yet the package declares **nine runtime dependencies** (`@olton/dom`, `html`, `model`, `router`, `hooks`, `guardian`, `farbe`, `datetime`, `string`); the
prebuilt `lib/` bundle does not need them, importing from `source/` does (`main` is `source/index.js`).

## What the CSS does to your page

- The first rule is `*{margin:0;padding:0;box-sizing:border-box}`; then `html{... scroll-behavior:smooth}` and
  `body{line-height:1.5; overflow-x:hidden; min-height:100vh; display:flex; flex-direction:column; justify-content:flex-start; ...}`.
  **`body` becomes a column flex container and every element loses its margin and padding**, so adding the stylesheet to an existing page re-lays it out. Scope it or
  load it only on pages built for it.
- `prefers-reduced-motion` appears **once** in 1.5 MB, `prefers-color-scheme` **never**: dark mode is class-based (215 `.dark…` selectors), so
  following the OS needs your own script.
- One `@font-face` in `metro.css` and no `url(...)` references at all (the regex found none); icons come from the separate 393 kB `icons.css`.

## JS behaviour (jsdom)

- Loading `lib/metro.js` creates `window.Metro` with **204 keys** (`version` 5.1.20, `utils`, `colors`, `dialog`, `storage`, `cookie`, `template`, `hotkeys`, `init`, ...)
  and prints an ASCII-art banner comment at the top of the file.
- It **auto-initialises on load**: `<div data-role="accordion">` came back with classes `accordion marker-on` and the `data-role` kept; the `<html>` element got
  `touchable-device`. No `Metro.init()` call was needed for markup present at load (dynamic content was not tested).
- `components.md` lists 167 component names (`accordion`, `calendar-picker`, `cookie-disclaimer`, `countdown`, `chat`, `cube`, `audio-player`, ...), many of which are one-off widgets a
  site will never use; the prebuilt `lib/` files are single bundles, so the full set always ships (importing from `source/` is the only route to a subset, not tried here).

## Verdict

Use it only to match an existing Metro-style product or when a large, all-in-one component set with one script tag is the explicit requirement. For a
new static site take a small CSS base, native elements and one library per feature. If you do adopt it: pin `5.1.x`, self-host `lib/`, scope or wrap the global reset, and add your own `prefers-color-scheme` and reduced-motion handling.
