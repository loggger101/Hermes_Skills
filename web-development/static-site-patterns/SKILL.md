---
name: static-site-patterns
description: "Static-site perf/UX: PWA installability + Core Web Vitals."
version: 1.0.0
author: Hermes Agent (curated from thedaviddias/Front-End-Checklist + lissy93/dashy)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web-development, static-site, pwa, core-web-vitals, vanilla-js, css]
    category: web-development
    related_skills: [static-site-seo, har-derived-api-client, design-taste-frontend]
---

# Static Site Patterns (framework-free)

## What This Skill Does

Concrete, copy-paste patterns for **vanilla HTML/CSS/JS static sites** — no framework required. Curated from thedaviddias/Front-End-Checklist's 390 agent-ready rule skills (each with verified code examples), filtered to what a hand-authored multi-page site actually needs: PWA installability, responsive images, Core Web Vitals fixes, and modern vanilla JS/CSS idioms. Complements `static-site-seo` (which covers SEO/structured-data/analytics/security-headers) — this skill is the **performance + UX** half.

## When to Use

- Building or auditing a static site with no build framework (hand-authored HTML pages).
- Making an existing static site installable as a PWA / work offline.
- Fixing Core Web Vitals (LCP, CLS) on image-heavy portfolio sites.
- Modernizing old vanilla JS (`var`-era code) to ES2015+ idioms without adding dependencies.

## The gap this fills: manifest yes, service worker no

A static site with `site.webmanifest` + icons but **no service worker** is not installable in most browsers — the manifest alone only gets you "Add to Home Screen" on some platforms. The three-piece set (all snippets below are vanilla JS, drop-in for a hand-authored site):

### 1. Manifest link + theme color (`<head>` of every page)

```html
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#0b1026">
<!-- Apple-specific: Safari ignores the manifest for these -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
```

### 2. Service worker — versioned precache + stale-while-revalidate (`sw.js` at site root)

Pattern from Front-End-Checklist `service-worker` rule (adapted to vanilla JS; the source uses TS):

```js
// sw.js — CACHE_VERSION bumps invalidate all caches on deploy
const CACHE_VERSION = 'v1';
const STATIC_CACHE = `static-${CACHE_VERSION}`;
const DYNAMIC_CACHE = `dynamic-${CACHE_VERSION}`;

const PRECACHE_URLS = [
  '/', '/portfolio-website.html',          // every hand-authored page (they are the app)
  '/style.css', '/site.js',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

// Activate: delete every cache that is not the current version pair.
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((k) => !k.endsWith(CACHE_VERSION)).map((k) => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

// Fetch: network-first for navigations (fresh content), cache fallback when offline;
// stale-while-revalidate for same-origin static assets.
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET' || !event.request.url.startsWith(self.location.origin)) return;

  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(() => caches.match('/offline.html')) // offline fallback page, precached
    );
    return;
  }

  event.respondWith(
    caches.open(DYNAMIC_CACHE).then(async (cache) => {
      const cached = await cache.match(event.request);
      const network = fetch(event.request).then((res) => {
        if (res.ok) cache.put(event.request, res.clone());   // keep fresh copy in background
        return res;
      }).catch(() => cached);                                 // offline: serve stale
      return cached || network;                                // SWR: instant + updated next visit
    })
  );
});
```

### 3. Registration (top of `site.js`)

```js
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js', { scope: '/' }).then((reg) => {
      reg.addEventListener('updatefound', () => {
        const nw = reg.installing;
        if (!nw) return;
        nw.addEventListener('statechange', () => {
          if (nw.state === 'installed' && navigator.serviceWorker.controller) {
            // a NEW version installed while the page was open — tell the user once
            console.info('New version available on next reload.');
          }
        });
      });
    });
  });
}
```

**Offline fallback page:** `offline.html` must be **fully self-contained** (inline `<style>`, no external CSS/JS) and included in `PRECACHE_URLS`. From the Front-End-Checklist `offline-fallback` rule.

## Responsive images without a build step

From `responsive-images` + `image-optimization` rules — all plain HTML:

```html
<!-- 1. Modern format with automatic fallbacks (AVIF → WebP → JPEG) -->
<picture>
  <source srcset="hero.avif" type="image/avif">
  <source srcset="hero.webp" type="image/webp">
  <img src="hero.jpg" alt="..." width="1600" height="900">
</picture>

<!-- 2. Width descriptors + sizes: the browser picks per viewport/DPR -->
<img src="project-800w.webp"
     srcset="project-400w.webp 400w, project-800w.webp 800w, project-1600w.webp 1600w"
     sizes="(max-width: 600px) 100vw, (max-width: 1200px) 50vw, 800px"
     alt="..." width="800" height="600">

<!-- 3. Different crops per breakpoint -->
<picture>
  <source media="(max-width: 600px)" srcset="hero-square.webp">
  <img src="hero-wide.jpg" alt="...">
</picture>

<!-- Fixed-size assets (icons/logos): density descriptors instead of width -->
<img src="logo.png" srcset="logo.png 1x, logo@2x.png 2x, logo@3x.png 3x" alt="" width="200" height="50">
```

Rules that matter: **always set `width`/`height`** (kills CLS — see below); generate the `-400w/-800w/-1600w` variants once with a script (e.g. ImageMagick/sharp in a build step), not per request; keep the largest source for retina.

## Core Web Vitals, vanilla edition

**LCP (largest contentful paint)** — from `largest-contentful-paint` + `fetchpriority-attribute`:

```html
<!-- The hero image IS the LCP candidate: preload it in <head> and boost priority -->
<link rel="preload" href="/hero.webp" as="image" type="image/webp">
<img src="/hero.webp" alt="..." width="1600" height="900" fetchpriority="high">
```

Everything else below the fold gets `loading="lazy"` (images AND iframes — a lazy YouTube embed is the classic critical-path killer).

**CLS (cumulative layout shift)** — from `cumulative-layout-shift`:

- Every `<img>`/`<iframe>` carries explicit `width` + `height` (or CSS `aspect-ratio: 16/9`).
- Never inject content above existing content without reserving its space first.

**Performance budget for a static site** — from `performance-budget`, adapted away from bundlers to what a hand-authored repo can check with zero dependencies: total page weight per HTML file (HTML + linked CSS + JS + images) against a ceiling, enforced in CI or a pre-commit script:

```bash
# crude but effective budget check for a static repo (no deps):
for f in *.html; do du -cb "$f" css/*.css js/*.js assets/* 2>/dev/null | tail -1; done
```

## Vanilla JS modernization patterns

From `event-delegation` + `modern-array-methods` — the two highest-leverage upgrades for a hand-written site script:

**Event delegation** (one listener instead of N, and it survives dynamically added nodes):

```js
// BAD: one listener per item; breaks on items added later
document.querySelectorAll('.project-card').forEach((el) => el.addEventListener('click', onClick));

// GOOD: one listener on the container — works for current AND future children
const grid = document.getElementById('projects');
grid.addEventListener('click', (event) => {
  const card = event.target.closest('.project-card');   // handles clicks on inner icons too
  if (!card) return;
  onClick(card);
});
```

**Modern array/object methods** replacing `for`-loop idioms:

```js
const names    = projects.map((p) => p.title);                       // transform all
const visible  = projects.filter((p) => p.tag === 'astro');          // select subset
const first    = projects.find((p) => p.featured);                   // first match (or undefined)
const totalKb  = assets.reduce((sum, a) => sum + a.kb, 0);           // aggregate
const byTag    = assets.reduce((g, a) => ((g[a.tag] ??= []).push(a), g), {});  // group-by
const allItems = orders.flatMap((o) => o.items);                     // map + flatten one step
```

## CSS: dark mode and reduced motion without a framework

From `dark-mode-css` — semantic tokens, OS preference by default, optional manual override:

```css
/* Light values are the DEFAULT on :root */
:root {
  --color-surface: #ffffff;
  --color-text: #111827;
  --color-border: #e5e7eb;
}

/* Dark mode = redefine the SAME variables, nothing else changes in your CSS */
@media (prefers-color-scheme: dark) {
  :root {
    --color-surface: #0f172a;
    --color-text: #f1f5f9;
    color-scheme: dark;   /* native dark scrollbars/inputs too */
  }
}

/* Optional manual override beats the OS preference */
[data-theme="light"] { /* light values again */ }
[data-theme="dark"]  { --color-surface: #0f172a; color-scheme: dark; }
```

Toggle = `document.documentElement.setAttribute('data-theme', t)` + persist in localStorage.

From `reduced-motion` — mandatory for any site with ambient animation (starfields, parallax):

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## Optional build step: esbuild for bundle + minify

The skill's default is no build step. When a static site grows past a few script files, `esbuild` (Go, 0.28.2 on 2026-10-05,
installs as one native binary via npm) bundles and minifies JS and CSS in milliseconds without a framework or config file.

```bash
npm i -D --save-exact esbuild          # exact pin: it is a 0.x project and minors can change behaviour (per its own docs)
npx esbuild src/main.js --bundle --minify --sourcemap --target=es2017 --outdir=dist --metafile=dist/meta.json
```

Live-checked (Windows, Node 22) on a 3-file sample:

- Whole run 52 ms. Unused exports are tree-shaken: `export function unused()` did not appear in the 123-byte `app.js`.
- A `import "./style.css"` in JS makes esbuild write `app.css` **next to** `app.js`; it is not injected into the page, so add a `<link rel="stylesheet" href="app.css">` yourself.
- `--target=es2015` lowered `??` and `?.` (the `??` count in the output went to 0); with no target they pass through untouched.
- For old browser targets (`--target=chrome90`) CSS nesting (`.a { &:hover {} }`) was lowered to `.a:hover {}`; with the default target it is left as written.
- `--metafile` writes an input/output size graph you can feed to esbuild's bundle analyzer when asked "why is this big".
- **It does not type-check.** `const x: number = "not a number"` in a `.ts` file built with exit code 0 and the types were just stripped. Run `tsc --noEmit` separately if you use TypeScript.

Keep the output committed or built in CI; do not make the site depend on a build the author's machine alone can run.

## CSS: property ordering and lint (use stylelint, not csscomb)

CSScomb (`csscomb/csscomb.js`) sorts properties into a configured order, but it is stale: npm `csscomb` 4.3.0 was
last published 2022-06 and the repo's last push is 2023-01. Live-tested (Node 22, Windows, config `sort-order`):

- the API (`new Comb(cfg).processString(css)`, which returns a **Promise**) sorted plain CSS, `@layer` and `@container` blocks correctly;
- **CSS nesting throws** a parse error (`.d { &:hover { ... } }` -> "Please check validity of the block starting from line #1"), and the same error aborted a whole modern stylesheet at the nested rule;
- the `csscomb file.css` CLI exited 0 and left the file unchanged here, with and without `-c`: a silent no-op is worse than an error, so do not trust it in CI.

Use stylelint, which is maintained and understands nesting, `@layer`, `@container` and modern colour functions:

```bash
npm i -D stylelint stylelint-config-standard stylelint-config-recess-order    # 17.16 / 40.0 / 7.8 on 2026-10-05
echo '{"extends":["stylelint-config-standard","stylelint-config-recess-order"]}' > .stylelintrc.json
npx stylelint "**/*.css"          # report; add --fix to rewrite
```

`recess-order` supplies the property ordering (position, then box model, then typography...) that csscomb was used for;
`standard` adds style rules. On a nested/`@layer` test file it reported 6 problems (blank line before at-rules,
`display` before `color`, `oklch(70% 0.1 200)` wanting `200deg`, one-declaration-per-line, `position` before `inset`) and
`--fix` rewrote 5 of them, leaving the single-line-block rule for hand edit. Lint at build/CI, not as a pre-commit rewrite of
files you did not touch.

For whitespace-only reformatting of JS/CSS/HTML (legacy or broken files, minified code, HTML with server-side template tags), `references/js-beautify-notes.md` holds the js-beautify 2.0.3 run: the CLI **rewrites files in place when given two or more files or a glob, with no `--replace`**; syntax errors exit 0 with garbage output and there is no `--check`; TypeScript and JSX come out mangled; `.editorconfig` needs `--editorconfig`. Prettier is the choice for TS/JSX or a CI format gate.

If a Materialize (Material Design CSS) look is requested, `references/materialize-css-notes.md` explains that the starred Dogfalo repo is frozen at 1.0.0 (2018) and the maintained line is `@materializecss/materialize` 2.x, with the measured size, icon-font and grid-markup (`col s12` became `s12`) migration traps.

For icons, `references/font-awesome-7-free-notes.md` compares Font Awesome Free 7.3.1 delivery methods by measured size (web font CSS 23 kB gz, 1.6 MB `all.js`, 250 kB solid sprite, 497 B inline SVG), flags the CC BY attribution comment inside each SVG, the relative `../webfonts/` path, `font-display: block`, the missing `sr-only` helper and reduced-motion handling that freezes spinners.

For Tailwind component plugins, `references/preline-5-notes.md` covers Preline UI 5.0.0: the MIT-plus-Fair-Use licence, the non-optional peer-dependency pile (jQuery via datatables.net), and measured `HSStaticMethods.autoInit()` behaviour, including that DOM added after load is not initialised until `autoInit()` runs again.

For scroll-reveal effects, `references/scrollreveal-4-notes.md` says why not to reach for ScrollReveal 4 (GPL-3.0 with a paid commercial licence, frozen since 2022, rewrites inline `transform`, ignores `prefers-reduced-motion`) and gives the native CSS `animation-timeline: view()` and `IntersectionObserver` replacements.

For framework-free JS animation, `references/animejs-4-notes.md` covers Anime.js 4.5.0 (subpath imports, deterministic `.seek()` testing) and the v3-to-v4 traps: no default export, `easing:` silently ignored in favour of `ease:`, infinite loops report a 10^12 ms duration, and a partial DOM shim throws in `parseTargets`.

For scoped, conflict-free CSS, `references/css-blocks-notes.md` records that LinkedIn's CSS Blocks is dormant (npm 2022), crashes on Windows (`process.getuid`), and changed its state syntax; it lists the strict rules it enforced and the maintained alternatives (CSS Modules, `@scope`, `@layer`, stylelint).

`references/metro-ui-5-notes.md` measures Metro UI 5.1.20 (`@olton/metroui`) for the "all-in-one CSS framework" question: 1.48 MB CSS, 0.92 MB JS, a global reset that makes `body` a flex column, class-based dark mode, auto-init on load; the README's "no dependencies" badge versus nine declared runtime deps.

For a CSS build step, `references/postcss-8-notes.md` runs PostCSS 8.5.29 with autoprefixer, postcss-nested, cssnano, preset-env, postcss-scss and postcss-cli: always pass `from` (autoprefixer cannot find browserslist without it), the default parser silently swallows `//` comments into selectors, postcss-nested 8 is ESM-only, warnings-only CLI exit codes, and that none of it is needed for a current-browser target.

When a lightweight CSS framework is wanted, `references/pure-css-3-notes.md` has Pure.css 3.1.0 measured (all modules 3.6 kB gzip, no JS, 7 `em` breakpoints, Normalize-only reset); it is the small end of the scale against the Materialize and Metro UI notes.

`references/tabler-icons-3-notes.md` is the MIT alternative to Font Awesome: 5,184 outline + 1,054 filled icons, searchable `icons.json` (tags, 41 categories), a 545 kB-per-font webfont versus 0.4 kB inline SVGs, and `@tabler/icons-react` renders with no default `aria-hidden` and renamed icons (`IconCircleCheck`, not `IconCheckCircle`).

To audit a built site against the machine-checkable items of the Front-End Performance Checklist, run `python scripts/perf_audit.py --root site/ site/` (13 rules: image dimensions, blocking scripts, CSS-after-JS, font format/display/preconnect/size, inline `<style>` in body, base64 images, iframes, unminified assets, page weight; exit 1 on findings; planted-defect harness `scripts/perf_audit_verify.py`). `references/performance-checklist-triage.md` maps the checklist's 40 items to script rules or other tools and replaces its dated numbers with web.dev's current ones (TTFB 0.8 s, LCP 2.5 s, INP 200 ms, CLS 0.1).

## UI/UX code review (beyond performance)

For a full accessibility/forms/animation/copy/dark-mode audit of site markup and JS, use `references/web-interface-guidelines-ui-checklist.md` — Vercel's Web Interface Guidelines ported verbatim with the clickable `file:line` output format. It complements this skill's Core-Web-Vitals section (which covers loading/rendering) by covering interaction quality; pair both when running a site audit.

For class-toggle CSS animation without a JS library, `references/animate-css-4-notes.md` holds the parsed facts for animate.css 4.1.1 (97 keyframes, `--animate-*` variables, the compat build's bare class names) and three Chrome-confirmed traps: the end state overrides your own `transform`, exits leave the node in layout and tab order, and the built-in reduced-motion rule force-hides any `*Out*` class.

## Provenance & verification notes

- Source of truth for every pattern above: the clone at `%LOCALAPPDATA%\Temp\starred-dive\Front-End-Checklist\skills\<rule-name>\` (SKILL.md + references/rule.md). The repo ships 390 such rule skills — this file curates the ~15 that apply to a framework-free static site; for any other topic (a11y, SEO rules, security headers), grep its `skills/` dir directly.
- Front-End-Checklist is also distributed as an MCP server + CLI (`packages/mcp`, `packages/cli`) if machine-consumable QA checks are wanted later — see the survey note in `frontend-design/nicegui-app-builder/references/frontend-tooling.md`.
- The dashy clone (lissy93/dashy) demonstrates the same patterns at product scale: docker-compose deployment, config-as-YAML, and a fully static frontend with no framework.
