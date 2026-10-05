# Front-End Performance Checklist: which of its 40 items an agent can check, and which numbers are dated

Source: [thedaviddias/Front-End-Performance-Checklist](https://github.com/thedaviddias/Front-End-Performance-Checklist) (17.4k stars, MIT, last push 2025-03-23; README of 693 lines,
**40 checklist items** in HTML, CSS, Fonts, Images, JavaScript and Server sections, each tagged high/medium/low priority, plus link lists of tools and articles). It is the
sibling of the Front-End Checklist this skill is curated from. The README is a human checklist, so the useful work was turning the machine-checkable items into a script and
re-checking its fixed numbers against current guidance.

## The script: `scripts/perf_audit.py`

Zero-dependency Python 3 scanner for a built static site: `python scripts/perf_audit.py --root site/ site/` prints `file:line: rule: message` per finding and exits 1 on any finding
(2 when no HTML is found). Thresholds are flags: `--max-page-kb 1500`, `--max-font-kb 300`, `--max-iframes 2`, `--max-data-uri 2048`. Its harness `scripts/perf_audit_verify.py`
(registered in `tools/run-self-tests.py`) builds one clean site that must pass and one site with every defect planted, and asserts that each of the **13 rules fires**
(`img-dimensions`, `img-base64`, `img-lazy`, `script-blocking`, `css-after-js`, `style-in-body`, `iframe-count`, `font-format`, `font-display`, `font-preconnect`,
`font-weight`, `not-minified`, `page-weight`), that fixing the defects returns exit 0, and that the threshold flag changes the verdict. Run on the repository's own HTML
templates it reported only `font-preconnect` (a Google Fonts stylesheet with no `fonts.gstatic.com` preconnect) in `creative/architecture-diagram/templates/template.html` and the diagram examples. It is a static scan: it does not
run a browser, execute JS, or see server headers.

## Item triage

| Checklist item (priority) | Where it is handled |
|---|---|
| Minified HTML (m); Minification of CSS (h) and JS (h) | `not-minified` heuristic for local CSS/JS (many short lines); minify with esbuild, see the esbuild section of `SKILL.md` |
| CSS before JavaScript (h) | `css-after-js` |
| Minimize iframes (h) | `iframe-count` |
| Prefetch / dns-prefetch / prerender (l) | not checked; use `preconnect` only for origins that are certainly used |
| Concatenation (m), Embedded CSS (h) | **dated under HTTP/2/3**: the checklist itself says "not always valid for HTTP/2"; many small files are fine, but `style-in-body` still flags `<style>` in `<body>` |
| Non-blocking CSS (h), CSS critical (h), Unused CSS (m), Stylesheet complexity (h) | not scripted: Lighthouse/Coverage, or `stylelint` (see the CSS lint section of `SKILL.md`) |
| Webfont formats (m) | `font-format` (woff2 required in each `@font-face`) |
| `preconnect` for fonts (m) | `font-preconnect` |
| Webfont size < 300 kB (m) | `font-weight` (local font files referenced from CSS, `--max-font-kb`) |
| Prevent invisible text (m) | `font-display` (missing `font-display` in an `@font-face`) |
| Images optimization / format / vector vs raster (h/m) | not scripted: see "Responsive images without a build step" in `SKILL.md` |
| Image dimensions (m) | `img-dimensions` |
| Avoid Base64 images (m) | `img-base64` (data URI over 2048 bytes) |
| Lazy loading (m), Responsive images (m) | `img-lazy` (more than 3 images and none lazy), plus the `SKILL.md` section |
| Non-blocking JavaScript (h) | `script-blocking` (`<script src>` in `<head>` without `defer`/`async`/`type=module`) |
| No JavaScript inside the body (m) | not checked: **contested**, inline scripts are fine when small and critical |
| Optimized/updated libraries (m), Dependency size (l), JS profiling (m) | not scripted (`npm outdated`, bundle analysis, DevTools) |
| Service Workers (m) | `SKILL.md` PWA section has a versioned precache template |
| HTTPS (h), HTTP cache headers (h), GZIP/Brotli (h), same protocol (h), reachable files (h), minimize requests (h), CDN (m), cookie size (m) | server or live-site checks, not in a static scan: use `curl -I`, Lighthouse, or a link checker (`tools/check-links.py` style) |
| Page weight < 1500 kB (ideally < 500 kB) (h) | `page-weight`: HTML + local CSS/JS/images/fonts it references, per page (remote assets are not measured) |

## Numbers that are dated against current guidance (fetched from web.dev on 2026-10-05)

| Checklist | Current web.dev guidance | Use |
|---|---|---|
| Time To First Byte < 1.3 s | **TTFB 0.8 s or less is "good"**, greater than 1.8 s is poor | target 0.8 s |
| Page load time < 3 s | no single load-time number; Core Web Vitals are the metrics: **LCP 2.5 s or less, INP 200 ms or less, CLS 0.1 or less** (75th percentile of real users) | judge by LCP/INP/CLS, as in the "Core Web Vitals, vanilla edition" section of `SKILL.md` |
| Page weight < 1500 kB / 500 kB | no official figure; it is a budget | keep as a configurable budget (`--max-page-kb`) |
| Webfont < 300 kB | a budget, not a standard | keep as `--max-font-kb`; one woff2 variable font is usually far below it |
| Cookies <= 4096 bytes each, <= 20 per domain | the 4096-byte figure is the common per-cookie limit; the 20 per domain is a conservative figure (browsers allow more) | informational only |

## How to use it

Run `perf_audit.py` on the built output before publishing, fix `img-dimensions`/`script-blocking`/`font-*` findings first (they map to CLS, LCP and font swaps), then measure the live page with
Lighthouse or WebPageTest for the items a static scan cannot see (headers, compression, TTFB, real LCP). The link and tool lists in the upstream README (WebPageTest, PageSpeed Insights,
Lighthouse, sitespeed.io, GTmetrix, SpeedCurve...) are the useful part to keep: each is a hosted or CLI measurement tool; none was run here.
