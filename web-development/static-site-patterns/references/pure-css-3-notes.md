# Pure.css 3.1.0 (`purecss`): the small responsive CSS kit, measured from the npm package

Source: [pure-css/pure](https://github.com/pure-css/pure) (23.7k stars, BSD-3-Clause, pushed 2026-10-05; GitHub shows the licence as `NOASSERTION`, the
`LICENSE` file is a Yahoo! BSD licence). npm **`purecss` 3.1.0** (2026-09-28; `pure-css` on npm is a different, 2022 package: install `purecss`), installed on Node 22 / Windows;
`build/*.css` parsed with Node, `HISTORY.md` read, `generateGrids()` called. Not covered: a browser render and the docs site. This is the smallest
framework in this directory's CSS-framework set; compare `materialize-css-notes.md` (21 kB gz CSS + 34 to 43 kB JS) and `metro-ui-5-notes.md` (about 640 kB gz).

## Weight

| File in `build/` | Bytes | Gzip |
|---|---|---|
| `pure-min.css` (everything) | 15,719 | **3,591** |
| `pure.css` | 26,207 | 5,983 |
| `grids-responsive-min.css` | 14,280 | 1,975 |
| `forms-min.css` | 7,075 | 1,447 |
| `menus-min.css` | 2,325 | 758 |
| `base-min.css` (Normalize 8.0.1) | 2,229 | 967 |
| `buttons-min.css` / `grids-min.css` / `tables-min.css` | 1,810 / 1,894 / 1,006 | 756 / 577 / 478 |

No JavaScript, no icons, no fonts, no custom properties, no `prefers-color-scheme`, no `prefers-reduced-motion` (nothing animates). Per-module files let you ship only
what a page uses; `pure-nr*.css` are the "no reset" builds (24.4 kB unminified versus 26.2 kB, they drop the Normalize layer), `base-context.css` scopes the reset inside `.pure-context`.

## Components (class names read from the CSS)

- **Grids**: `.pure-g` is a flex row-wrap container (`display:flex; flex-flow: row wrap; align-content: flex-start`), `.pure-u` is `inline-block`. Fraction
  units use denominators **1, 2, 3, 4, 5, 6, 8, 12, 24** (90 base classes such as `.pure-u-1-3`, `.pure-u-5-24`). Responsive classes (`grids-responsive.css`, 270 of them)
  are prefixed per breakpoint: `sm` at `min-width: 35.5em`, `md` 48em, `lg` 64em, `xl` 80em, `xxl` 120em, `xxxl` 160em (the file also holds a 240em block with no unit classes), e.g. `.pure-u-md-1-3`.
  It is mobile-first: classes without a prefix apply at every width. The responsive file is 14.3 kB of the 15.7 kB bundle, so
  skip `grids-responsive` if you only need fixed fractions.
- **Buttons**: `.pure-button`, `-primary`, `-active`, `-disabled`, `-hidden`, `-selected`, `.pure-button-group`. **Forms**: `.pure-form`, `-stacked`, `-aligned`, `.pure-control-group`, `.pure-controls`,
  `.pure-input-rounded`, `.pure-input-1-2` etc.; a `@media only screen and (max-width: 480px)` block restyles inputs and the submit button for phones.
  **Menus**: `.pure-menu`, `-horizontal`, `-scrollable`, `-fixed`, `-allow-hover`, `-has-children` (CSS dropdowns driven by hover; keyboard and touch behaviour were not tested). **Tables**: `.pure-table`
  with `-bordered`, `-horizontal`, `-striped`/`-odd`.
- The reset is **Normalize.css 8.0.1** (`html{line-height:1.15}`, `body{margin:0}`), far gentler than the "zero all margins" resets in the heavier frameworks.

## Version history that matters

- **3.0.0 (2022-10-26)**: dropped IE and the `font-family` hack from grids; browserslist became `> 1%`; check a layout that relied on old browsers.
- **3.1.0 (2026-09-28)**: CSS **unchanged** from 3.0.0 apart from banner comments; the build moved from Grunt to ESM npm scripts, Rework was removed, and
  `require('purecss').generateGrids(...)` was added. Contributing now requires **Node 26+ and npm 12+** (`.nvmrc`); consuming the built CSS does not.
  Releases publish from GitHub Actions with npm provenance.
- `generateGrids([1,2,3], {})` returned CSS beginning `.pure-u-1, .pure-u-1-1, .pure-u-1-2, .pure-u-2-2, ... { display: inline-block; letter-spacing: normal; word-spacing: normal; vertical-align: top; ... }`:
  the `letter-spacing`/`word-spacing` resets are leftovers of the old inline-block grid and are harmless with `.pure-g` flex parents.

## Gaps to plan for

No dark mode, no focus-ring design beyond browser defaults (check contrast and `:focus-visible` yourself), hover-driven menus, no JS components (modal, tabs, accordion: use native
`<dialog>` and `<details>`), and no spacing utility classes. Right fit: a documentation or marketing page needing a
grid, forms and tables in under 4 kB gzip. Wrong fit: an app UI that needs components or theming.
