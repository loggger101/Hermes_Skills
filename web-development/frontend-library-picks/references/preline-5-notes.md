# Preline UI 5.0.0 (Tailwind component plugins): licence, the peer-dependency pile, `autoInit` (run in jsdom)

Source: [htmlstreamofficial/preline](https://github.com/htmlstreamofficial/preline) (6.5k stars, pushed 2026-08-31). npm
`preline` **5.0.0** (modified 2026-08-21) installed with jsdom on Node/Windows; its `dist/preline.js` evaluated in jsdom against
hand-written `data-hs-*` markup, and the shipped `LICENSE`, `variants.css` and bundled agent skills read. Not covered: the paid
Preline Pro blocks, Tailwind compilation of the components, real-browser focus and animation behaviour (jsdom has no layout or
CSS transitions), the datepicker/datatable/select plugins (they pull third-party widgets).

## Licence: MIT plus a "Fair Use" licence (not plain MIT)

GitHub reports the licence as `NOASSERTION` and npm as `Licensed under MIT and Preline UI Fair Use License`. The `LICENSE` file
is the MIT text **followed by** the Preline UI Fair Use License: no use to build a product that directly competes with Preline UI,
no harmful or deceptive use, derivative templates/themes may be sold only if not marketed as competing products and credited
("Preline UI" plus a link to the repository), redistribution must carry **both** licences and a link back, and the author may
terminate the rights for non-compliance. For client work this is usually fine; for a UI kit, theme pack or page builder it is a
real constraint: read `LICENSE` before reusing the markup in a product that sells components.

## Install weight

- `npm install preline` pulls **non-optional peer dependencies** (the package has no `peerDependenciesMeta`): `@floating-ui/dom`,
  `apexcharts`, `culori` (+ `@types/culori`), `datatables.net`, `datatables.net-dt` (which brings **jQuery**), `dropzone`,
  `nouislider`, `vanilla-calendar-pro`. With npm 7+ they install automatically (43 top-level directories, 49 MB including jsdom in
  the test project); pnpm/yarn only warn and plugins that need them then fail at runtime. A site using only the accordion still receives all of this
  at install time (the browser cost depends on which scripts you actually include).
- `dist/` is 5.1 MB: `preline.js` (all plugins, 435 KB), one file per plugin (`accordion.js`, `collapse.js`, ...) in UMD and
  `.mjs`, and a `-non-auto` twin of each that does not self-initialise. Prefer importing the single plugin you use.
- Tailwind 4 wiring (README): `@source "./node_modules/preline/dist/*.js"; @import "./node_modules/preline/variants.css";`. `variants.css`
  imports 23 plugin variant files from `./src/plugins/...` (so the package's `src/` must stay installed) and declares
  `@custom-variant hs-success`, `hs-error`, `hs-dragged` and others. Colour themes are CSS (`theme.css`, 30 KB; nine named themes
  in the bundled skill: default, harvest, retro, moon, ocean, bubblegum, cashmere, autumn, olive).

## JS behaviour (dist/preline.js in jsdom)

- Loading it defines **29 `window.HS*` globals**: HSAccordion, HSCarousel, HSCollapse, HSComboBox, HSCopyMarkup, HSDataTable, HSDatepicker,
  HSDropdown, HSFileUpload, HSInputNumber, HSLayoutSplitter, HSOverlay, HSPinInput, HSRangeSlider, HSRemoveElement, HSScrollNav,
  HSScrollspy, HSSelect, HSStepper, HSStrongPassword, HSTabs, HSTextareaAutoHeight, HSThemeSwitch, HSToggleCount,
  HSTogglePassword, HSTooltip, HSTreeView, plus `HSStaticMethods` and `HSAccessibilityObserver`.
- `HSStaticMethods.autoInit()` wires everything found by class/data attribute. Results after real `click` events:
  - **Accordion** (`hs-accordion-group`): opening item 2 removed `active` from item 1 and added it to item 2 (the group is exclusive)
    and set `aria-expanded="true"` on the toggle. The panel's `hidden` class was still present 450 ms later: the height transition
    finishes on `transitionend`, which jsdom never fires, so this part is jsdom-limited.
  - **Collapse** (`hs-collapse-toggle` + `data-hs-collapse="#id"`): removed `hidden`, set `aria-expanded="true"`.
  - **Dropdown**: wrapper got `open`, the menu got `block`, toggle `aria-expanded="true"` (menu `hidden` removed).
  - **Overlay (modal)** (`data-hs-overlay="#id"`): the overlay got `open opened`, the trigger `aria-expanded="true"`, a backdrop element was
    created. A synthetic Escape `keydown` dispatched on `document` did **not** close it (not conclusive: the library may listen elsewhere); test Escape in a real browser.
- **Content added after load is not initialised.** A new `hs-accordion` appended to the body did nothing when clicked (checked
  400 ms later); after calling `HSStaticMethods.autoInit()` again it opened. In SPAs or fetched fragments, call
  `HSStaticMethods.autoInit()` after each insertion.
- The ARIA attributes (`aria-expanded`, `aria-controls`, `role=region`, `aria-labelledby`) were written by hand in the test page and the
  plugins only updated `aria-expanded`; whether they add missing ones was not tested, so copy complete blocks rather than bare class names.

## What to take from it

Good: Tailwind-native, headless-leaning plugins with plain data attributes, no framework requirement, 204 free blocks (README count).
Watch: the dual licence, the peer-dependency install, no auto-init for dynamic DOM, and heavy plugins (datatable, datepicker,
charts) that load third-party libraries. For React apps compare `web-development/react-library-notes/references/ariakit-notes.md` and `shadcn-cli-4-notes.md` there in
`web-development/react-ecosystem/`. The agent skills this repo ships are covered in
`software-development/skill-intake-and-release/references/vendor-shipped-skills-preline.md`.
