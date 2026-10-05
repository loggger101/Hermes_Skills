# Font Awesome Free 7.3.1: which delivery method costs what, licences, and the v7 CSS (measured from the npm package)

Source: [FortAwesome/Font-Awesome](https://github.com/FortAwesome/Font-Awesome) (77k stars; default branch `7.x`, pushed
2026-07-15). npm `@fortawesome/fontawesome-free` **7.3.1** installed and measured on Windows (sizes with Node `zlib` gzip, class
presence by regex over `css/all.css`, counts from `svgs/` and `metadata/icons.yml`). Not covered: Font Awesome Pro, Kits (the hosted
loader), rendering in a browser, the Sass sources.

## Licence: three licences in one package

`LICENSE.txt` and the banner of every CSS file say **Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT**. Which one applies depends
on the file type you ship: SVG and JS files (and so the SVG sprites and `all.js`) are the **CC BY 4.0 icons, which require
attribution**; the `webfonts/` files are OFL; CSS is MIT. Each `svgs/*.svg` carries the notice as a leading XML comment
(`<!--! Font Awesome Free 7.3.1 by @fontawesome ... License - ... (Icons: CC BY 4.0 ...) -->`, about 250 of the 497 bytes of
`user.svg`). Minifying SVGs with a tool that strips comments removes the attribution notice: keep it, or credit Font Awesome
elsewhere (a licence reading for you to confirm, not legal advice). npm lists the packages as `(CC-BY-4.0 AND OFL-1.1 AND MIT)`;
the tree-shakeable `@fortawesome/free-solid-svg-icons` as `(CC-BY-4.0 AND MIT)`.

## What is in "free" 7.3.1

- **2,001 solid + 273 regular + 609 brands = 2,883 SVG files** (`svgs/`, identical counts in `svgs-full/`), but
  `metadata/icons.yml` has only **1,980 icon entries**, 1,130 of them with aliases: renamed icons ship **as extra files**, so
  `user-circle` and `circle-user`, `home` and `house`, `times` and `xmark`, `cog` and `gear`, `search` and `magnifying-glass`,
  `twitter` and `x-twitter` all exist. The file count overstates the icon count; copy by name from `icons.yml`.
- **Pro-only styles have no CSS**: `.fa-light`, `.fa-thin`, `.fa-duotone`, `.fa-sharp` do not exist in the free `all.css`
  (checked by regex); copying Pro markup renders nothing. Free styles are `fa-solid`, `fa-regular`, `fa-brands`, with the
  `fas`/`far`/`fab`/`fa` short forms and `fa-classic` still defined.
- **There is no `.fa-sr-only` / `.sr-only` helper in the 7.3.1 CSS** (grep found none). Icon-only buttons need your own visually-hidden
  class or an `aria-label`.

## Delivery methods and their weight

| Method | Files | Transfer size (gzip) | Notes |
|---|---|---|---|
| Web font + CSS | `css/all.min.css` 90.3 kB (**22.7 kB gz**) + `webfonts/fa-solid-900.woff2` 119.5 kB, `fa-regular-400.woff2` 19.5 kB, `fa-brands-400.woff2` 115.4 kB (woff2 is already compressed) | ~23 kB + the fonts the page uses | a browser fetches a font file only once a glyph from it is drawn, so a solid-only page skips regular and brands |
| `css/fontawesome.min.css` + one style file | 71.6 kB (17.1 kB gz) + `solid.min.css` 0.6 kB | | same fonts; the v4 compatibility font (`v4-shims.min.css` 21 kB, `fa-v4compatibility.woff2` 4 kB) is only for old `fa fa-*` v4 markup |
| JS "SVG with JS" | `js/all.min.js` **1.6 MB (549 kB gz)**; `solid.min.js` 821 kB (262 kB gz); `fontawesome.min.js` core 88.6 kB | large | per the docs it replaces `<i>` with inline SVG at runtime and watches the DOM (not run here); needs `css/svg-with-js.min.css` (25.6 kB, 3.7 kB gz); avoid on content sites |
| SVG sprite | `sprites/solid.svg` 876 kB (250 kB gz), `regular.svg` 115 kB (31 kB gz), `brands.svg` 597 kB (224 kB gz) | | the whole sheet is fetched even for one icon; only worthwhile cached across many icons |
| Individual SVG inline or `<img>` | `svgs/solid/user.svg` 497 B | per icon | best for a handful of icons; no font, no FOIT, no JS |
| npm modules (`fontawesome-svg-core` 7.3.1, `free-solid-svg-icons` 7.3.1 at 5.1 MB unpacked, `react-fontawesome` 3.5.0, `vue-fontawesome` 3.3.3) | | tree-shaken per import | for React/Vue apps; import single icons, not the whole pack |

Rule of thumb for a static site using under about 15 icons: **inline SVG files**; for many icons across pages: web font CSS (23 kB gz) and
the woff2 files, cached; never the 1.6 MB `all.js`.

## v7 CSS details that bite

- **Relative font URLs.** `all.css` references `../webfonts/fa-solid-900.woff2` and the others: copy `css/` somewhere without
  a sibling `webfonts/` directory and every icon turns into a missing-glyph box. Keep the `css/` + `webfonts/` layout or rewrite the `url()`s.
- **`font-display: block`** on all ten `@font-face` blocks: icons are invisible (not replaced by a fallback) until the font arrives.
  Preload the used woff2 with `<link rel="preload" as="font" type="font/woff2" crossorigin>`.
- **Glyphs come from a custom property**: `.fa-user { --fa: "\f007"; }` and the base class draws `content: var(--fa)/""`
  (the `/""` is CSS alt text, giving the pseudo-element an empty accessible name, with an `@supports not (content: ""/"")`
  fallback). So CSS icons are silent to screen readers: add a text label for meaningful ones, and `aria-hidden="true"` is
  still the habit for decorative ones. Width is `var(--fa-width, 1.25em)` (a fixed 1.25em box by default; `fa-fw` still exists).
- Tuning is by variables: `--fa-family`, `--fa-style`, `--fa-display`, `--fa-width`, and animation variables
  (`--fa-animation-duration` default 2s for `fa-spin`, 1s for `fa-spin-pulse`).
- **Reduced motion removes spinners**: `@media (prefers-reduced-motion: reduce)` sets `animation: none !important` on `fa-spin`, `fa-beat`,
  `fa-pulse`, `fa-shake` and 14 more (18 animation classes in all). A `fa-spinner fa-spin` loading indicator then shows as a static glyph: pair it with
  visible "Loading" text.
- Old v5/v6 names still resolve through aliases (`fa-times`, `fa-home`, `fa-cog` all have rules), so v6 markup keeps working;
  prefer the canonical names in new code (`fa-xmark`, `fa-house`, `fa-gear`).
