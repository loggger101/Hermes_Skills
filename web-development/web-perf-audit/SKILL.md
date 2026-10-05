---
name: web-perf-audit
description: "Audit a built static site: perf script + UI checklist."
version: 1.0.0
author: Hermes Agent (promoted from static-site-patterns, Front-End-Performance-Checklist + Web Interface Guidelines)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web-development, performance, core-web-vitals, lighthouse, accessibility, ui-review, static-site, audit]
    related_skills: [static-site-patterns, static-site-seo, website-audit, frontend-library-picks, design-taste-frontend, dogfood]
---

# Web performance and UI audit

## What This Skill Does

Audits a built static site before it is published. A zero-dependency script (`scripts/perf_audit.py`) checks the 13 machine-checkable items of the Front-End Performance Checklist and prints `file:line: rule: message`; a triage table says which of the checklist's 40 items the script covers, which need a live measurement, and which numbers are out of date; a UI checklist (Vercel's Web Interface Guidelines) reviews accessibility, forms, animation and copy. The sections below hold the fixes the findings point to: responsive images and Core Web Vitals.

## When to Use

- A static or hand-authored site is about to ship and needs a performance pass
- LCP, CLS or page weight is poor and the cause is unknown
- A pull request touches images, fonts, scripts or `<head>` order
- A markup or JS review needs an accessibility, forms and motion checklist with `file:line` output
- Not for PWA, service worker, vanilla JS or CSS tooling (`static-site-patterns`), SEO and structured data (`static-site-seo`), or a whole-site written report (`website-audit`)

## Quick Reference

```bash
python web-development/web-perf-audit/scripts/perf_audit.py --root site/ site/   # exit 1 on findings, 2 when no HTML found
python web-development/web-perf-audit/scripts/perf_audit_verify.py               # planted-defect self-test, 20 checks
```

Thresholds are flags: `--max-page-kb 1500`, `--max-font-kb 300`, `--max-iframes 2`, `--max-data-uri 2048`. Rules: `img-dimensions`, `img-base64`, `img-lazy`, `script-blocking`, `css-after-js`, `style-in-body`, `iframe-count`, `font-format`, `font-display`, `font-preconnect`, `font-weight`, `not-minified`, `page-weight`. It is a static scan: no browser, no JS execution, no server headers.

## Procedure

1. Build the site, then run `perf_audit.py` on the output directory.
2. Fix `img-dimensions`, `script-blocking` and `font-*` findings first: they map to CLS, LCP and font swaps.
3. Apply the markup patterns below for images, the LCP candidate and layout shift.
4. Measure the live page (Lighthouse or WebPageTest) for what a static scan cannot see: headers, compression, TTFB and real LCP, INP and CLS.
5. Run the UI checklist (`references/web-interface-guidelines-ui-checklist.md`) on the changed markup and scripts.
6. Judge by current thresholds (TTFB 0.8 s, LCP 2.5 s, INP 200 ms, CLS 0.1), not the checklist's dated numbers; see the triage table.

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


## Pitfalls

- Treating a clean `perf_audit.py` run as a good score: it cannot see headers, compression, third-party scripts or real user timings.
- Lazy-loading the hero image; the LCP candidate gets `fetchpriority="high"` and a preload instead.
- Generating image variants per request rather than once in a build step.
- Copying the checklist's old numbers (3 s load, 1.3 s TTFB) as targets.
- Reading `font-preconnect` findings on remote font hosts as noise; a missing preconnect costs a round trip on the critical path.

## Verification

- [ ] `perf_audit.py` exits 0 on the built output, or each remaining finding has a written reason
- [ ] `perf_audit_verify.py` passes (20/20) if the script was changed
- [ ] Hero image has dimensions, `fetchpriority="high"` and a preload; below-fold images and iframes are lazy
- [ ] A live Lighthouse or WebPageTest run was compared against the current thresholds
- [ ] UI checklist findings were reported with `file:line`

## References

- `references/performance-checklist-triage.md` - the checklist's 40 items mapped to script rules or other tools, with dated numbers replaced by web.dev's current ones
- `references/web-interface-guidelines-ui-checklist.md` - Vercel's Web Interface Guidelines as an accessibility, forms, animation and copy checklist
- `scripts/perf_audit.py`, `scripts/perf_audit_verify.py` - the 13-rule static audit and its planted-defect harness
