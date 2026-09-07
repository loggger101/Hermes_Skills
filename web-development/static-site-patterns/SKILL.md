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

## Provenance & verification notes

- Source of truth for every pattern above: the clone at `%LOCALAPPDATA%\Temp\starred-dive\Front-End-Checklist\skills\<rule-name>\` (SKILL.md + references/rule.md). The repo ships 390 such rule skills — this file curates the ~15 that apply to a framework-free static site; for any other topic (a11y, SEO rules, security headers), grep its `skills/` dir directly.
- Front-End-Checklist is also distributed as an MCP server + CLI (`packages/mcp`, `packages/cli`) if machine-consumable QA checks are wanted later — see the survey note in `frontend-design/nicegui-app-builder/references/frontend-tooling.md`.
- The dashy clone (lissy93/dashy) demonstrates the same patterns at product scale: docker-compose deployment, config-as-YAML, and a fully static frontend with no framework.
