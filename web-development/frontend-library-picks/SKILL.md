---
name: frontend-library-picks
description: "Pick CSS/icon/animation libs by weight and licence."
version: 1.0.0
author: Hermes Agent (promoted from static-site-patterns references, measured 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [css, icons, animation, postcss, licence, bundle-size, static-site, frontend-libraries]
    related_skills: [static-site-patterns, react-ecosystem, frontend-design, design-taste-frontend, static-site-seo, publish-site]
---

# Frontend library picks (non-React, static sites)

## What This Skill Does

Answers "which CSS framework, icon set, animation library or build helper" for plain HTML/CSS/JS sites with measured weight, licence and maintenance state, so a dependency is not added by habit. Every library was installed from npm and measured (file sizes, class counts, jsdom or Chromium runs). The React counterpart is `react-ecosystem`.

## When to Use

- Choosing a CSS kit, icon library, scroll or animation library for a static site, or auditing the one already in use
- Checking licence or attribution duties before shipping (Font Awesome, ScrollReveal, Preline, animate.css)
- Wondering whether a starred or old library is still maintained, or whether native CSS replaces it
- Setting up PostCSS, or formatting minified JS/CSS/HTML
- Not for site structure, CSP and build patterns (`static-site-patterns`), SEO (`static-site-seo`), visual design direction (`frontend-design`, `design-taste-frontend`), or React projects (`react-ecosystem`)

## Picks by need

| Need | Default | Weight / state | Reference |
|---|---|---|---|
| Tiny responsive CSS kit | **Pure.css 3.1.0** (`purecss`; `pure-css` on npm is a different 2022 package) | 15.7 kB min, 3.6 kB gzip, no JS | `references/pure-css-3-notes.md` |
| Material look | `@materializecss/materialize` 2.x (community fork) | CSS 20 kB gz + JS 34 kB gz; the original `materialize-css` is frozen at 1.0.0 (2018 release, last commit 2020) | `references/materialize-css-notes.md` |
| Full desktop-style UI framework | avoid for static pages: `@olton/metroui` 5.1.20 | CSS 1.48 MB, JS 0.92 MB, about 640 kB gz with icons; 54 MB npm tarball | `references/metro-ui-5-notes.md` |
| Tailwind component plugins | Preline 5.0.0 | licence is MIT plus a "Fair Use" licence; non-optional peer deps pull jQuery via `datatables.net-dt` | `references/preline-5-notes.md` |
| Icons, MIT, no attribution | **Tabler Icons 3.49.0** | 5,184 outline + 1,054 filled SVGs, `icons.json` searchable by meaning | `references/tabler-icons-3-notes.md` |
| Icons, brand logos | Font Awesome Free 7.3.1 | three licences in one package; SVG/JS icons are CC BY 4.0 and need attribution | `references/font-awesome-7-free-notes.md` |
| Ready-made CSS keyframes | animate.css 4.1.1 | 71.7 kB min, repo finished (last push 2024-07); licence line in CSS says MIT, README says Hippocratic | `references/animate-css-4-notes.md` |
| JS animation and timelines | Anime.js 4.5.0 | ESM, import by subpath: bundle is 118 kB (40.7 kB gz) | `references/animejs-4-notes.md` |
| Scroll-reveal | native CSS (`animation-timeline`) or IntersectionObserver; ScrollReveal 4.0.9 only for open-source use | GPL-3.0 unless a commercial licence is bought; frozen since 2022 | `references/scrollreveal-4-notes.md` |
| Build-time CSS transforms | PostCSS 8.5.x with autoprefixer, `postcss-nested`, cssnano | native CSS nesting replaces some plugins | `web-development/js-tooling-notes/references/postcss-8-notes.md` |
| Formatting minified JS/CSS/HTML | js-beautify 2.0.3 (whitespace only), Prettier 3 when the code must parse | CLI rewrites files in place with 2+ inputs | `web-development/js-tooling-notes/references/js-beautify-notes.md` |
| Statically checked CSS scoping | do not adopt `@css-blocks/core` 1.5.0 | dormant since 2022 and crashes on Windows | `references/css-blocks-notes.md` |

## Procedure

1. Name the need, take the default from the table, and open its reference for the measured facts.
2. Check licence before installing: GPL (ScrollReveal), CC BY attribution (Font Awesome SVG/JS), and Fair Use terms (Preline) each constrain a client or commercial site.
3. Budget the page: add CSS and JS gzip sizes and stay inside the project's performance budget; prefer per-module files (Pure) and subpath imports (Anime.js).
4. Re-check maintenance with `npm view <pkg> version time.modified deprecated --json` before committing, as the picks are a 2026-10 snapshot.
5. Ask whether native CSS does it (scroll-driven animation, nesting, custom properties) before adding a JS or PostCSS dependency.
6. Record the choice with the licence and measured weight in the project README or ADR.

## Pitfalls

- PostCSS: always pass `from` (otherwise autoprefixer cannot find your browserslist config), `await` async plugins, and use `postcss-scss` for `//` comments; the default parser keeps them without error.
- Anime.js v4 has no default export (`import anime from 'animejs'` fails); import `animate` and friends by name.
- js-beautify never reports syntax errors (exit 0 on broken code) and overwrites files in place with two or more inputs: run it on a clean git tree.
- Font Awesome: SVG minifiers that strip comments remove the attribution notice.
- Package names mislead: `purecss` not `pure-css`; `@olton/metroui` not `metro4`; `@materializecss/materialize` not `materialize-css`.
- Sizes and versions are 2026-10-05 snapshots; a legal reading of the licences is for you to confirm.

## Verification

- [ ] Licence for the chosen file types is recorded and compatible with the site
- [ ] Gzip weight of the added CSS and JS fits the performance budget
- [ ] The package is maintained, or its frozen state is a conscious choice
- [ ] Native CSS or an existing dependency was considered first

## References

- `references/pure-css-3-notes.md` - Pure.css 3.1.0 weight per module, no JS, licence, grid generator
- `references/materialize-css-notes.md` - frozen 1.0.0 vs maintained `@materializecss/materialize` 2.x: Material 3 tokens, sizes, formats
- `references/metro-ui-5-notes.md` - Metro UI 5.1.20 weight, global reset, undeclared dependencies, 54 MB tarball
- `references/preline-5-notes.md` - Preline UI 5.0.0 licence, peer-dependency pile, `autoInit` behaviour in jsdom
- `references/tabler-icons-3-notes.md` - Tabler Icons 3.49.0: 5,184 MIT icons, webfont weight, React barrel, `icons.json`
- `references/font-awesome-7-free-notes.md` - Font Awesome Free 7.3.1 delivery methods, three-licence package, v7 CSS
- `references/animate-css-4-notes.md` - animate.css 4.1.1 files, class prefixes, compat build, licence mismatch, confirmed traps
- `references/animejs-4-notes.md` - Anime.js 4.5.0 modular API, v3 migration traps, deterministic values
- `references/scrollreveal-4-notes.md` - ScrollReveal 4.0.9 GPL licence, frozen state, inline-style side effects, native replacements
- `skill_view(name='js-tooling-notes')` — PostCSS 8 and js-beautify moved there with Bun and standard/neostandard (round-251)
- `references/css-blocks-notes.md` - CSS Blocks 1.5.0: dormant, breaks on Windows, what it enforces
