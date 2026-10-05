# Tabler Icons 3.49.0: 5,184 MIT icons, the webfont weight, and the React barrel (measured from npm)

Source: [tabler/tabler-icons](https://github.com/tabler/tabler-icons) (21.9k stars, MIT, pushed daily). npm `@tabler/icons` **3.49.0** (SVG files and metadata),
`@tabler/icons-webfont` 3.49.0, `@tabler/icons-react` 3.49.0 (all published 2026-10-05; also `@tabler/icons-sprite` and `@tabler/icons-vue` at the same version), installed on
Node 22.23.2 / Windows with React 19; file sizes, `icons.json` and an SSR render were measured. Not covered: the sprite and Vue packages, the Figma kit, a browser render.
Compare the licence-heavy Font Awesome Free in `font-awesome-7-free-notes.md`.

## What is in it

- **MIT for everything**, so no per-SVG attribution comment (the two SVG files opened carry none) and no Pro tier.
- `icons/outline/` **5,184 SVGs**, `icons/filled/` **1,054 SVGs**. `icons.json` (1,947 KB, 194 KB gzip) has **5,184 entries**, each with `name`, `category` (**41 categories**, largest: System 784,
  Devices 363, Design 350, Arrows 333, Map 263, Document 209, Letters 214), `tags` (search keywords, e.g. `a-b-2`: `ab-test, split-test, experiment, ...`) and `styles` with the version that
  introduced it and its font codepoint: the file to search when an agent must find an icon by meaning. `tabler-nodes-outline.json`/`-filled.json` are the other metadata files (not opened).
- Every outline icon is 24 x 24, `fill="none" stroke="currentColor" stroke-width="2"` with round caps and joins (stroke width was 2 in all of the first 400 files checked); filled icons use
  `fill="currentColor"`. `outline/user.svg` is 433 bytes and starts with an invisible `<path stroke="none" d="M0 0h24v24H0z" fill="none"/>` bounding-box rect; its `class` is
  `icon icon-tabler icons-tabler-outline icon-tabler-user`. Because the stroke width is an attribute you can set `stroke-width` per use (or via CSS on the `svg`).

## Delivery options and weight

| Method | Package / file | Size |
|---|---|---|
| Inline or `<img>` SVG | `icons/outline/<name>.svg` | about 0.4 kB each |
| Web font (outline) | `dist/tabler-icons.min.css` | 213 kB (**37.7 kB gz**) + `fonts/tabler-icons.woff2` **507 kB** (woff 780 kB, ttf 1.8 MB) |
| Web font (filled only) | `dist/tabler-icons-filled.min.css` | 43 kB (8.2 kB gz) + `tabler-icons-filled.woff2` 73 kB |
| Weight variants | `tabler-icons-200.*`, `tabler-icons-300.*` | each the full set again: CSS 213 kB, woff2 about 520 kB |
| React components | `@tabler/icons-react` | one module per icon (6,246 files in `dist`), `sideEffects: false`, peer `react >= 16` |

A webfont of every icon costs ~545 kB of font plus the stylesheet even if a page shows three icons (outline and filled are separate fonts, each monolithic);
the CSS has **no `font-display`** (browser default, so text may swap in) and base rule `.ti{font-family:"tabler-icons" !important; ...}`, glyph classes are `.ti-user:before`
(5,247 of them) and the filled set is a separate font and stylesheet. Font URLs are relative (`./fonts/tabler-icons.woff2?v3.49.0`): keep `dist/` layout when copying.
For a handful of icons prefer inline SVG; for many icons in a framework app prefer the React package with named imports.

## React package behaviour (SSR via `renderToStaticMarkup`)

- Names: `IconUser`, `IconUserFilled`. The barrel exports **6,307 names (6,304 `Icon*`, 1,057 of them `*Filled`)** plus `createReactComponent`, `icons` and `iconsList`.
  `require('@tabler/icons-react')` took **96 ms** (3.6 MB CJS barrel); `sideEffects: false` lets bundlers tree-shake named imports (not bundled here), so import by name, never `import * as`.
- Default render: `<svg ... width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ... class="tabler-icon tabler-icon-user">`.
  Props that worked: `size={32}` (width and height), `stroke={1.5}` (stroke width), `color="red"` (stroke), `className`, `title="Profile"` (adds `<title>Profile</title>` child), `aria-label`.
  `IconUserFilled` renders `fill="currentColor" stroke="none"`.
- **No accessibility attributes by default**: nothing like `aria-hidden="true"` or `role="img"` was emitted. Decorative icons need `aria-hidden`, meaningful ones need `title`/`aria-label`.
- **Renames in v3 bite old code**: `IconCircleCheck` exists while `IconCheckCircle` is `undefined`; `IconHome`, `IconHome2`, `IconBrandTwitter`, `IconBrandX` and `IconSearch` all exist, so aliases are kept for many but not all
  names. Check with `typeof T.IconName` or search `icons.json` rather than guessing names.

## When to pick it

Good default free set when a project wants consistent 2 px outline icons with a filled variant, MIT licensing and a React package. For static sites ship the few SVGs you use. If the project is
already on Font Awesome Free, switching only pays when attribution handling or the Pro-only styles are a problem.
