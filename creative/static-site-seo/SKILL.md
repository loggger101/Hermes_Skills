---
name: static-site-seo
description: "Static site SEO: JSON-LD, meta tags, analytics, CSP."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [static-site, SEO, JSON-LD, analytics, CSP, form-backend, serverless, meta-tags, sitemap, canonical]
    category: creative
    related_skills: [python-craft]

---

# Static Site Generation, SEO, and Analytics

Guide for building and maintaining static sites — generation patterns, SEO fundamentals (titles, descriptions, canonicals, sitemaps, JSON-LD), analytics (GA4, privacy-friendly alternatives), form backends, security headers, and the common mistakes that silently hurt discoverability or user trust.


## What This Skill Does

Static site SEO: JSON-LD, meta tags, analytics, CSP.

## When to Use

- Building or maintaining a static site (hand-authored HTML, generated HTML, or a static site generator)
- Improving a static site's search visibility (titles, descriptions, structured data, sitemaps)
- Adding analytics without degrading privacy or performance
- Wiring up a contact/registration form without a backend server
- Hardening a static site with security headers (CSP, HSTS, X-Frame-Options, etc.)

**Don't use** for dynamic sites with server-side rendering needs, authenticated user flows, or real-time data — that's a different architecture. Static sites are for content that can be pre-rendered and served as files.

## Generation Patterns

### Hand-authored HTML

Each page is a `.html` file, edited directly. Good for small sites (up to ~20 pages) where the content is stable and the layout is shared via a common header/footer snippet or a CSS file.

- Pros: no build step, no dependencies, what you edit is what ships.
- Cons: duplication (every page repeats the header/footer/nav), hard to keep consistent, tedious to update shared elements.

### Generated HTML (script → pages)

A script (Python, Perl, shell, whatever) owns the generated parts of the site and writes the `.html` files. Shared layout is in the generator, not copied across pages. Content can come from data files (JSON, CSV, YAML) or be inline in the script.

- Pros: consistent layout, easy to update shared elements across all pages, data-driven pages (one source → many pages).
- Cons: you edit the script or data, not the HTML directly; a rebuild is required after changes; the generator must be correct or pages are wrong.

### Hybrid

Some pages are hand-authored (rare one-off pages, landing pages with unique layouts), most are generated. The key is knowing which tool owns which page — if a generated page is edited directly, the next rebuild clobbers the edit. Document the ownership.

### Build idempotency

A rebuild should produce the same bytes as the previous rebuild if nothing changed. This is a useful property: it means you can rebuild freely without worrying about churn, and `diff` between builds tells you whether anything actually changed. If a rebuild changes timestamps or reorderings without a content change, you get false diffs and wasted deploys.

Watch for:
- Timestamps embedded in pages (last-modified dates, generation dates) that change on every rebuild. Either don't embed them, or derive them from content history, not the current time.
- Non-deterministic ordering (e.g., dict iteration order in older Python, unsorted directory listings) that changes the output.
- Random values baked into the page (cache-busting tokens, unique IDs) that change every build.

## SEO Fundamentals

### Title

Every page needs a unique, descriptive `<title>`. Format: `Page name — Site name` or `Page name | Site name`. Keep it under ~60 chars to avoid truncation in search results.

- Bad: `Home`, `Page`, `Untitled`
- Good: `CSF1R-ALSP — AspireCURES`, `Asteroid Mining Profitability Catalog — Economic Space`

The title is the single most important on-page SEO element. It tells search engines what the page is and appears in the search result.

### Description

Every page needs a `<meta name="description">`. 150–160 chars, descriptive, written for humans (it appears in search results). It's not a ranking factor directly, but it affects click-through — a good description gets more clicks.

- Avoid auto-generated descriptions that are just the first 160 chars of the page (often a nav item or a generic sentence).
- Avoid keyword stuffing.
- For pages with no good description, write one. A missing description usually defaults to something worse than a real one.

### Canonical

Every indexable page should have a `<link rel="canonical">` pointing to its preferred URL. This tells search engines which URL to index when the same content is reachable from multiple URLs.

```html
<link rel="canonical" href="https://www.example.com/csf1r-alsp" />
```

- Use the full absolute URL, including the protocol and domain.
- Point canonicals to the www (or non-www) version consistently — pick one and use it everywhere.
- For pages that are accessible from multiple paths, the canonical tells search engines which one to count.

### Clean URLs

- Use extensionless URLs where possible (`/csf1r-alsp` maps to `csf1r-alsp.html`). Cleaner, and matches how users type URLs.
- Serve a real 404 for unknown paths, not a 200 with "page not found" content (soft 404). Search engines treat soft 404s poorly.
- Redirect old URLs to current ones with a 301 (permanent) or 308 (permanent, preserves method). Don't leave dead URLs returning 200.

### Robots

- `<meta name="robots" content="index, follow">` is the default — you don't need to declare it.
- Use `noindex` for pages that shouldn't be in search (admin pages, thank-you pages, staging, duplicate content).
- Use `nofollow` on a page if you don't want search engines to follow its links (rarely needed on static sites).
- `robots.txt` disallows crawling of paths — different from `noindex` (which tells search engines not to index a page they've already found). Use `noindex` for pages you want hidden, `robots.txt` for paths you want crawlers to avoid entirely.

### Sitemap

A `sitemap.xml` tells search engines which pages exist and when they were last modified.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.example.com/</loc>
    <lastmod>2026-08-13</lastmod>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://www.example.com/csf1r-alsp</loc>
    <lastmod>2026-08-13</lastmod>
  </url>
</urlset>
```

- Include all public, indexable pages.
- `lastmod` should reflect the actual last content change, not a bot date that moves on a schedule. A stale `lastmod` is misleading; a `lastmod` that moves without a content change defeats the purpose.
- Keep it up to date — a sitemap that lists pages that no longer exist, or omits pages that do, is worse than no sitemap.

### Hreflang (for multi-language)

If the site has multiple language versions, use `hreflang` to tell search engines which version to show to which audience.

```html
<link rel="alternate" hreflang="en" href="https://www.example.com/page" />
<link rel="alternate" hreflang="es" href="https://www.example.com/es/page" />
<link rel="alternate" hreflang="x-default" href="https://www.example.com/page" />
```

## Structured Data (JSON-LD)

JSON-LD is a machine-readable block that tells search engines what the page is about — an organization, an article, a medical condition, a product, an event, etc. It's placed in a `<script type="application/ld+json">` in the `<head>`.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "MedicalCondition",
  "name": "CSF1R-related adult-onset leukoencephalopathy with axonal spheroids and pigmented glia",
  "description": "A rare neurological disorder caused by mutations in the CSF1R gene...",
  "url": "https://www.example.com/csf1r-alsp",
  "keywords": "CSF1R-ALSP, BANDDOS, leukoencephalopathy"
}
</script>
```

### What to mark up

- **Organization** (homepage): name, url, logo, sameAs (social profiles), knowsAbout (what the org covers).
- **WebPage / MedicalWebPage**: url, name, description, about (the condition), dateModified, author, publisher.
- **MedicalCondition**: name, description, meSH terminology if applicable, epidemiology, treatment, related conditions.
- **Article / ScholarlyArticle**: headline, datePublished, dateModified, author, citation, keywords.

### Validation

Test structured data with Google's Rich Results Test or the Schema.org validator. Verify that:
- The JSON is valid (parseable).
- The types are correct (you're not marking up a page as a Product when it's a MedicalCondition).
- Required properties are present.
- URLs in the structured data match the actual page URLs.

### Common mistakes

- Duplicate structured data across pages that shouldn't be duplicated (e.g.,Organization on every page is fine; marking every page as a different MedicalCondition when it's not is wrong).
- Inconsistent data between the visible page and the structured data (title in JSON-LD doesn't match the `<title>`).
- Marking up content that isn't visible on the page (search engines may penalize this).
- Missing `@context` — every JSON-LD block needs `"@context": "https://schema.org"`.

## Analytics

### Google Analytics 4 (GA4)

GA4 is the current Google analytics product. It's script-based, event-driven, and consent-sensitive.

- Install via the GA4 measurement script in the `<head>`.
- Use `gtag.js` or Google Tag Manager. For a static site, `gtag.js` is simpler.
- Consent mode: GA4 should respect user consent for cookies. Load the script conditionally, or use consent mode to tell GA4 whether the user has consented.
- Key metrics: sessions, pageviews, engagement time, conversions (events you mark as conversions).

Pitfalls:
- Loading GA before consent (in many jurisdictions, this is a compliance issue).
- Not marking meaningful events as conversions (you get traffic data but not goal data).
- Duplicate GA tags (two scripts loading, double-counting).
- Testing in production and polluting real data — stub the GA loader in test/localhost.

### Privacy-friendly alternatives

- **GoatCounter**: lightweight, privacy-friendly, self-hostable or hosted. Script-based, no cookies by default. Good for personal sites and small projects.
- **Cloudflare Web Analytics**: cookieless, server-side analytics from Cloudflare. Good alongside GA4 as a cookieless complement.
- **Plausible**: privacy-friendly, cookieless, lightweight. Hosted or self-hosted.

When choosing:
- GA4 gives the most depth (funnels, cohorts, attribution) but is heavier and consent-sensitive.
- Cookieless alternatives give less depth but are simpler, lighter, and more privacy-friendly.
- Using both (GA4 + a cookieless option) is common — GA4 for depth, cookieless for a consent-free baseline.

### What to track

For a content site:
- Pageviews (by page path).
- Engagement time / time on page.
- Scroll depth (how far users read).
- External link clicks (do users click through to references?).
- Form submissions (did the contact/registration form fire?).

For a site with a form:
- Form start (page view of the form).
- Form submit (the POST).
- Form success (redirect to thank-you).
- Form abandonment (page view without submit).

## Form Backends (static sites)

A static site has no server — form submissions need a backend somewhere. Options:

### Serverless functions (Cloudflare Pages Functions, Netlify Functions, Vercel serverless)

A function receives the POST, does the work (save to a store, forward to a CRM, send an email), and returns a response. The form POSTs to the function's URL.

- Pros: runs server-side, can access secrets (CRM tokens, API keys) without exposing them to the client, can do server-side validation, can save to a KV/DB.
- Cons: requires a platform that supports functions; cold starts (usually minor for form handlers); timeout limits.

### Third-party form services (Formspree, Getform, Formsubmit, etc.)

The form POSTs to the service's URL; the service forwards to email or stores submissions.

- Pros: zero backend to maintain, works with any static host, often includes spam protection.
- Cons: vendor lock-in, rate limits, less control over what happens to the data.

### Mailto (bad idea)

`action="mailto:..."` — opens the user's email client. Unreliable, no server-side processing, no spam protection, no logging. Don't use it for anything real.

### Design considerations for form backends

- **Fail open vs. fail closed**: a form backend that fails should decide what to do. Fail-closed = submission lost. Fail-open = submission saved somewhere safe (KV, file) but CRM/email might not fire. For patient registrations or anything high-stakes, fail-open with a backup store is usually right — losing a submission is worse than delaying a CRM write.
- **Spam protection**: honeypot fields (invisible to humans, filled by bots), time traps (instant submissions are suspicious), CAPTCHA (Turnstile, reCAPTCHA) — but a CAPTCHA failure should never silently drop a submission; it should fail open or offer a fallback.
- **Timeouts**: a slow backend (CRM token grant, network hiccup) shouldn't leave the user waiting indefinitely. Return the redirect early, hand the slow work to a background mechanism (`context.waitUntil()` on Cloudflare, or a queue).
- **Duplicate submissions**: nothing de-duplicates a form by default. A user who clicks twice submits twice. De-duplication requires a client-side guard (disable the button after submit, time-trap stamp) and/or server-side de-dup by some identifier (submit timestamp + IP + fingerprint).
- **Data minimization**: don't send more than you need. Email in the key name is a leak (key names are enumerable); put sensitive data in the value, not the key.

## Security Headers

### Content Security Policy (CSP)

CSP tells the browser what resources the page is allowed to load. It's a strong defense against XSS and data exfiltration.

```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self';
               script-src 'self' https://gc.zgo.at;
               style-src 'self';
               img-src 'self' data:;
               font-src 'self';
               connect-src 'self' https://formspree.io https://loganmedwardsastrophy.goatcounter.com;
               form-action https://formspree.io;
               base-uri 'self'" />
```

- `default-src 'self'` — only load from same origin by default.
- `script-src` — where scripts can load from. Be specific; `'unsafe-inline'` and `'unsafe-eval'` weaken CSP.
- `style-src` — where styles can load from.
- `img-src` — images. `data:` allows base64 images.
- `font-src` — fonts.
- `connect-src` — fetch/XHR/WebSocket destinations.
- `form-action` — where forms can submit.
- `base-uri 'self'` — prevents `<base>` tag injection.

Pitfalls:
- CSP that's too restrictive breaks the site (missing a domain for an analytics script, a font, an image). Test CSP in report-only mode first (`Content-Security-Policy-Report-Only`), watch the console for violations, then enforce.
- CSP that's too loose (`'unsafe-inline'` everywhere) is not really a CSP. Start restrictive and relax only what's needed.
- CSP meta tag in HTML is fine for static sites; header-based CSP (set by the host) is stronger (can't be removed by injected HTML). Use the host header when available.

### HSTS (HTTP Strict Transport Security)

Tells browsers to only connect over HTTPS for a period. Set as a header (`Strict-Transport-Security: max-age=...; includeSubDomains`). Prevents downgrade attacks. Only set if the site is fully HTTPS and all subdomains are too.

### X-Frame-Options

Prevents the page from being embedded in an iframe (clickjacking defense). `DENY` or `SAMEORIGIN`. Set as a header.

### X-Content-Type-Options

`nosniff` — prevents the browser from MIME-sniffing responses. Set as a header. Prevents some content-type confusion attacks.

### Referrer-Policy

Controls how much referrer information is sent with requests. `strict-origin-when-cross-origin` is a reasonable default — sends the full URL for same-origin, origin only for cross-origin, nothing for downgraded requests.

## Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Missing or duplicate titles | Search results show "Home - " or the same title on every page | Unique, descriptive titles per page |
| Auto-generated descriptions from page start | Description in search results is a nav item or generic sentence | Write real descriptions; don't auto-pull the first 160 chars |
| Canonicals missing or pointing wrong | Duplicate content signals, wrong URL indexed | Canonical on every indexable page, pointing to the preferred absolute URL |
| Sitemap with wrong lastmod | Search engines think pages haven't changed (or changed when they haven't) | Derive lastmod from content, not a bot date |
| JSON-LD missing @context or wrong type | Structured data ignored or misinterpreted | Every block has @context; type matches the page content |
| GA loaded before consent | Privacy compliance issue | Load GA conditionally on consent; use consent mode |
| Form backend swallows failures | Submissions lost with no trace | Fail-open with backup store; log failures; timeouts on backend calls |
| CSP too loose or too tight | No real protection, or site broken | Start restrictive, test in report-only, relax only what's needed |
| Soft 404 (200 for missing page) | Search engines confused about what exists | Real 404 for unknown paths |
| Hand-edited generated page | Edit clobbered on next rebuild | Document which tool owns which page; edit the tool or data, not the HTML |
| Rebuild churn (timestamps, non-det order) | False diffs, wasted deploys, misleading lastmod | Idempotent builds; no live timestamps; deterministic ordering |
| Key names leak sensitive data (form backend) | Enumerable keys expose submissions | Put sensitive data in values; prefix keys by type; don't embed emails in key names |

## Serverless Form Backends in Practice

A real pattern from aspirecures: a Cloudflare Pages Function receives the POST, saves a backup to Cloudflare KV, creates a Zoho CRM Lead, and redirects to a thank-you page.

**The fail-open pattern with backup store:**
- KV is the safety net — if Zoho is down or unconfigured, the submission is still saved and the visitor still reaches the thank-you page.
- The handler should not depend on the CRM being available to complete the user's journey.
- Setup: KV namespace bound as `SUBMISSIONS`, Zoho env vars (`ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN`).

**Token management:**
- ⚠️ Per-submission token mint is a latent failure mode: `zohoToken()` runs a full `refresh_token` grant on each call, so a credential with an hour of life is used exactly once. This fails precisely when the org succeeds — a newsletter send, conference, or press mention produces the burst that trips Zoho's rate limit on how many access tokens a refresh token may mint in a window.
- Fix: cache the token in the same KV namespace under a reserved key, with `expirationTtl` set from Zoho's own `expires_in` minus a safety margin. KV is eventually consistent, so an occasional miss just mints fresh — harmless. Prefix keys to separate the token cache from submissions.

**Timeouts and async:**
- ⚠️ The handler awaiting KV write → Zoho token grant → Zoho create before redirecting leaves the visitor watching a spinner on a submitted form. A slow/hanging Zoho causes retries, which produce duplicate leads (the resubmitted `form-ts` is the original render time, so the 3s trap doesn't catch it).
- Fix: return the redirect immediately and hand the Zoho work to `context.waitUntil()`, with `AbortSignal.timeout()` on both fetches. Failures already fail open and are logged — the visitor just stops paying for the backend latency.

**Key naming and data minimization:**
- ⚠️ Embedding the email in the KV key (`${received_at}_${email}_${uuid8}`) makes key names enumerable — anyone who can list the namespace learns every registrant's email and signup time without reading a single value. On a rare-disease site, the mere fact that someone registered is sensitive.
- Fix: put the email in the value only, give keys a type prefix (`sub:<ts>:<uuid>`, `sys:zoho-token`) so submissions and the token cache can be listed apart. Server-side length-cap `Email` and free-text fields — both unbounded, and an oversized email pushes the key past KV's 512-byte limit, which throws and silently costs that submission its backup copy (Zoho still gets it).

**Spam protection:**
- Honeypot field: hidden from assistive tech (`hidden` + `aria-hidden="true"` + `tabindex="-1"`) so a screen-reader user cannot trip it and lose their registration.
- Time trap: 3-second minimum between form render and submit; instant bot autofills are silently dropped. Fails open on clock skew and for no-JS visitors.
- CAPTCHA (Turnstile/reCAPTCHA): only if spam appears. A CAPTCHA failure must never silently drop a submission (a false positive could be a real patient), and a siteverify outage must fail open. A complete Turnstile integration exists in git history — resurrect it, don't rebuild.

**De-duplication:**
- Nothing de-duplicates a form by default. A user who clicks twice submits twice.
- Client-side: disable the button after submit, or stamp the form with a render timestamp that the time trap checks.
- Server-side: de-dup by some identifier (submit timestamp + IP + fingerprint) if duplicates are a real problem.

**Privacy and consent:**
- The form itself should have real `<label for>` pairs, `autocomplete` on identity fields, `<fieldset>`/`<legend>` on every radio and checkbox group, and a consent line linking the Privacy & Waiver.
- `Last_Name` falls back so Zoho's required field is never empty.

## Automated Content Feeds

A real pattern from aspirecures: a weekly GitHub Action fetches new papers (Europe PMC + PubMed) and trials (ClinicalTrials.gov), has Claude vet + summarize each, writes JSON to `/data/research/`, and renders it into the disease pages.

**Pipeline structure:**
```
config.json → fetch_curate.mjs (CI) → data/research/<slug>.json → render.pl → <page>.html
              │  Europe PMC + PubMed (articles) + ClinicalTrials.gov (trials)
              │  structural validation + retraction screen
              └─ Claude: strict relevance gate + plain-language summary
```

**Design properties:**
- Append-only: nothing is ever removed; retractions are flagged, trial statuses refreshed in place.
- Safe-fail: a failing run changes nothing.
- The curation step is gated behind an API key (`ANTHROPIC_API_KEY` repo secret) — with it unset, the job runs green but skips curation. Two free operations inside the curation function (refresh trial statuses from CT.gov, recheck retractions) are also switched off behind the key check today.

**Cost control:**
- Hard cap per run: 300k tokens / 200 curations, so a runaway is impossible.
- Estimated ~$40–70/yr on the current weekly cadence + 14-day window, billed pay-as-you-go through the API Console, cannot draw on a Claude subscription.
- The model ID is in the code (`fetch_curate.mjs:47`), not config — a trial run can override it from the CI config with no code edit. Sonnet 5 via the Batch API is ~70% cheaper than Opus 4.8 for this workload (independent classifications, no latency requirement, cron-committed).
- The Batch API is this workload's textbook case: up to 100k requests, most complete within an hour, 24h worst case. Requires a refactor (submit → poll → collect) — not a config flip.

**Date and freshness management:**
- ⚠️ `generated` stamped unconditionally on every run rewrites all JSONs and re-dates all pages with no content change — exactly the churn pattern that defeats the point of a "new commit means something changed" signal.
- Fix: bump `generated` only when a page actually gained an item or had a status/retraction change.
- A disease page's date should be the *later* of the feed `generated` date and the page's own content history (git content date), not short-circuited on the feed date. Otherwise landing editorial copy on a page leaves it telling search engines the page hasn't changed since the last feed curation.

**Per-page configuration:**
- Per-page `max_fetch` overrides — six of nine pages exceed the default 30 on a fully indexed fortnight (MS 78, HD 76, FTD 47, LBD 32, FRDA 31); only one page has an override today.
- An override also raises that page's *trial* fetch, which is pure waste on pages whose trials are all gate-rejected and, being unstored, are re-gated every run.

**Manual backfill:**
- Manual curation passes stay the freshness mechanism until the API key is set. The reusable method: drive the real `fetch_curate.mjs` from a scratch driver.

## Generated HTML with Scripted Builds

A real pattern from aspirecures: Perl generators produce the site's pages from a shared shell, content data, and per-page build scripts. The key engineering property is that the generators are idempotent and marker-guarded.

**The generator architecture:**
- A shared shell (`tools/shell.pl`) owns the common layout — header, footer, nav, mobile menu, CSS includes, GA snippet, consent banner.
- Per-page build scripts (`build-home.pl`, `build-about.pl`, `build-disease-pages.pl`, `build-contact.pl`, `build-legal-pages.pl`, `build-partner.pl`) own the page-specific content and inject it into the shell.
- Partials (`tools/partials.pl`) own reusable sections — the consent banner, the GA loader, the mobile menu script.
- Data files feed the generators: `data/research/*.json` (research feed), `data/ads/slots.json` (ad inventory), `data/featured/` (hand-curated cards).

**Marker-guarded sections:**
- Generated sections are wrapped in HTML comments that mark their boundaries: `<!-- ac-... -->` ... `<!-- /ac-... -->`.
- A generator re-applies its sections on every run, replacing whatever is between its markers.
- This means a generated page can be re-run freely without clobbering hand-authored sections that live outside the markers.
- The markers also document which tool owns which section — read the comments and you know what to edit.

**Idempotency in practice:**
- A rebuild produces the same bytes as the previous rebuild if nothing changed.
- `verify.sh` confirms this: run the generators twice and the second run changes zero bytes.
- This matters for CI and for confidence — you can rebuild without worrying about churn, and a diff between builds tells you whether anything actually changed.

**The rebuild order is a source of truth:**
- The generators must run in the right order, or a later generator clobbers an earlier one's output.
- aspirecures documents the exact rebuild order in MAINTENANCE.md; running the generators out of order ships feed-less, rail-less disease pages.
- `verify.sh` fails on out-of-order rebuilds (it checks that the ad rail matches `slots.json`, that the research feed is present, etc.), so the wrong order can't ship — but it can waste a rebuild.

**Content edits flow through the generators:**
- To change page text, edit the copy in the page's `build-*.pl` script, re-run it, then run `perl tools/dedash.pl *.html` (the dedash pass normalizes dash characters).
- Editing the `.html` directly works once but is clobbered on the next rebuild — the generator is the source of truth, the HTML is the output.
- Hand-authored pages (`thank-you.html`, `404.html`, `member-site-homepage-1.html`) are exceptions — they're not generated, so they're edited directly. They're documented as hand-authored so nobody tries to regenerate them.

**Images and immutable assets:**
- Images live in `assets/images/`. Add a new image under a new name, point the `src`/`srcset` at it, remove the old file.
- Don't re-encode over an existing filename — `_headers` serves `/assets/images/*` as `immutable, max-age=31536000`, so returning visitors keep the old bytes for a year.
- `verify.sh` fails on an image that nothing references (orphaned asset) and on a referenced image that doesn't exist (Broken image).
- The hero video (`assets/video/hero.mp4`) is served immutable for a year too — when the bytes change, bump the `$VID` parameter in `build-home.pl` so returning visitors get the new file.

**SEO generation (the Perl SEO toolchain):**
- `tools/schema.pl` emits all JSON-LD for every indexable page (Organization on the homepage, MedicalCondition + MedicalWebPage on disease pages, Article/ScholarlyArticle for research items). Owned by `schema.pl`, not `seo.pl` — the README was stale on this for a while.
- `tools/seo.pl` owns the robots meta, canonicals, noindex, and copyright year.
- `tools/gen-sitemap.pl` generates `sitemap.xml` with per-page `<lastmod>`.
- `tools/pagedate.pl` is the shared date-precedence engine behind both `schema.pl`'s `dateModified` and `gen-sitemap.pl`'s `<lastmod>` — it walks git history to find the last commit that changed real content, skipping date-only commits. (The history here is instructive: two generators had duplicated the logic while each claiming it was shared, and a date-correction commit landed a content change (robots meta) in the same commit that re-stamped dates, which made the stamp stale the instant it landed. The lesson: content first, then re-run the date generators and commit the dates separately.)

**The research feed's render step:**
- `tools/research/render.pl` reads `data/research/<slug>.json` and renders the curated research + trials into the disease pages, inside marker-guarded sections.
- The feed is append-only (nothing removed; retractions flagged, trial statuses refreshed in place).
- `render.pl` is idempotent — a second run changes nothing if the JSON didn't change.

**Ad rail rendering:**
- `tools/render-ads.pl` reads `data/ads/slots.json` and renders the ad/sponsorship cards into disease pages that have slots assigned.
- Currently only two pages have slots (an unpaid nonprofit-partner card + a house "Register" card); the other seven render nothing.
- `render-ads.pl --check` verifies the ad rail matches `slots.json` (no dead links, no double-booked pages, headline length, blocklisted copy, theme values, dash style, card counts). Run by `verify.sh`.

**Dedash pass:**
- `perl tools/dedash.pl *.html` normalizes dash characters across all HTML files after a rebuild.
- Run with the glob — running it on a subset leaves the others untouched and the site inconsistent.

## Content Governance for Medical/Scientific Sites

A real pattern from aspirecures: medical content on a rare-disease site carries governance requirements that don't show up on a normal static site.

**Copy authorship and voice:**
- Copy is written in the owner's voice (we/our), never the visitor's.
- Medical copy is carried verbatim from the source and is not paraphrased without the medical partner's sign-off (Heidi, in this case).
- This is a governance constraint on the generators: the build scripts are where copy lives, and they're reviewed for medical accuracy before shipping.

**Editorial firewall for the research feed:**
- The automated feed fetches candidates (papers, trials) and has Claude vet each for on-topic relevance before summarizing.
- The relevance gate is strict — off-topic candidates are dropped, not summarized.
- The summary is plain-language (patient-readable), not academic. The feed is citation content, not medical advice.
- Retractions are flagged, not removed — the record stays, with a retraction notice.

**YMYL / E-E-A-T considerations:**
- Medical content has no author or reviewer byline by default (a decision, not an oversight — `schema.pl` deliberately emits no `lastReviewed` because that would claim a clinical review nobody performed).
- Adding a reviewer byline is a decision that needs a name attached before it can be built.
- For a rare-disease site, the fact that content is curated (feed + manual backfill + medical review) is a trust signal; making that visible is worth doing, but only if accurate.

**Ad/sponsorship governance:**
- The ad framework (`ADS-FRAMEWORK.md`) has editorial firewall rules: sponsors don't get to influence disease-page content, the research feed, or the medical copy.
- The ad rail is separate from the research feed (different sections, different markers, different renderers).
- Kill criteria compare carded pages against rail-free pages in the same period — two disease pages must stay ad-free permanently as a baseline (the holdout pair).
- The holdout is documented but was (at the time of the TODO) enforced by nothing — `ads-lint.pl` doesn't know about it. The fix: read a `holdout` array from `slots.json` and make `ads-lint.pl` ERROR if any unit's `pages` names a holdout page.

**Sponsorship/packaging:**
- The sponsor kit (`SPONSOR-KIT.md`) is the commercial pack: rate card, creative spec, vetting checklist, ad-ops runbook.
- Rate-card figures are blank until the owner fills them — nothing is sold until the figures are set and counsel reviews the disclosure wording.
- Click measurement: a decision to make before promising sponsors anything measurable. Options: JS-free placement-only, inline GA4 click event, or a first-party redirect through the existing Cloudflare function.

## External Link Integrity for Citation-Heavy Sites

A real pattern from aspirecures: the site carries 404 distinct external URLs (261 doi.org, 84 clinicaltrials.gov, 58 pubmed, 1 partner), and a dead one would sit there indefinitely. `verify.sh` only checks local refs.

**Why HTTP status checks lie on these hosts:**
- PubMed answers `203` behind a cookie gate — would do so for an invalid PMID too.
- ClinicalTrials.gov is a SPA that returns `200` for anything.
- 42 DOIs answer `403` from publisher bot-walls (JAMA, Wiley, OUP, ACS) while resolving perfectly in a browser.
- So status codes are misleading — check IDs through the APIs instead.

**The API-based check method:**
- DOIs: resolve through the DOI API / CrossRef, or check that the DOI resolves to a real article page (not just a 403).
- NCT IDs: check through the ClinicalTrials.gov v2 API — 84/84 valid records.
- PMIDs: check through PubMed's `esummary.fcgi` — 58/58 valid records.
- This is the reusable method: resolve IDs via the APIs, not via status codes.

**Where to put the check:**
- NOT in `verify.sh` — 400+ network calls would make CI slow and flaky, and rate-limit false failures would block the weekly feed job (verify.sh gates it).
- A separate on-demand script, run quarterly, is the right shape.
- The script should be idempotent and safe-fail — a failure to check one URL shouldn't block the rest.

**Monitoring cadence:**
- Quarterly is reasonable for a site whose content changes weekly at most (the feed) plus occasional manual edits.
- More frequent if the site is heavily citation-dependent and the citations are to unstable sources.
- The check should produce a report (dead links, resolved links, API errors) that someone acts on.

## Dark Mode and Accessibility in Static Sites

The website(Primary) portfolio pattern: dark theme, system preference respect, keyboard navigation, skip link, semantic HTML.

**Dark mode implementation:**
- CSS custom properties for the theme tokens (background, foreground, muted, accent, border, card).
- `prefers-color-scheme: dark` media query to switch the theme.
- Respect `prefers-reduced-motion` for animations (marquee, fade-in, transitions) — provide a static fallback.
- The theme should be set by CSS, not by JavaScript (no flash of wrong theme on load).

**Accessibility basics that matter:**
- Skip link (`<a class="skip-link" href="#main">`) as the first focusable element.
- Semantic HTML: `<nav>`, `<main>`, `<header>`, `<footer>`, `<section>`, proper heading hierarchy (one `<h1>`, sequential `<h2>`/`<h3>`).
- `<label for>` on form inputs, `<fieldset>`/`<legend>` on grouped inputs.
- Alt text on images (including decorative images — use `alt=""` for decorative, not missing alt).
- Focus styles (don't remove `:focus` without a replacement).
- Keyboard-navigable interactive elements (buttons, links, form controls — everything that's clickable should be focusable and activatable by Enter/Space).

**Things that are hard to machine-check:**
- The visual result of transitions and animations (a harness running with `document.visibilityState === 'hidden'` never composites, so `requestAnimationFrame` never fires).
- Native button activation from Enter/Space on a focused button (synthetic key events deliver keydown/keyup but no click).
- Whether a page actually looks right (machine checks can prove it loads clean, not that it looks good).

## GoatCounter and Privacy-Friendly Analytics

The website(Primary) pattern: GoatCounter for lightweight, privacy-friendly pageview tracking.

**GoatCounter setup:**
- Script: `<script async data-goatcounter="https://<your-counter>.goatcounter.com/count" src="https://gc.zgo.at/count.js"></script>`.
- No cookies by default — privacy-friendly out of the box.
- Self-hostable or hosted. Good for personal sites and small projects where GA4 is overkill.
- CSP: add `https://gc.zgo.at` to `script-src` and the counter URL to `connect-src` if needed.

**When GoatCounter is the right choice:**
- Personal site, small project, internal tool — you want pageviews without the GA4 weight and consent complexity.
- You want a cookieless complement to GA4 (GA4 for depth, GoatCounter for a consent-free baseline).
- You don't need funnels, cohorts, attribution — just "who visited what, roughly how many."

**When it isn't:**
- You need conversion funnels, cohort analysis, attribution, or integration with ad platforms.
- You need to track events beyond pageviews (button clicks, form steps, scroll depth) — GoatCounter can do some of this but GA4 is more capable.

**Cloudflare Web Analytics as a complement:**
- Cookieless, server-side, from Cloudflare. Good alongside GA4 as a consent-free baseline.
- Requires the Cloudflare dashboard (no client script needed if the site is on Cloudflare).
- Counts pageviews and bot filtering — less depth than GA4, simpler, privacy-friendly.

## Formspree and Third-Party Form Services

The website(Primary) pattern: a personal portfolio form that posts to Formspree.

**Formspree setup:**
- The form POSTs to `https://formspree.io/f/<form-id>`.
- Formspree forwards submissions to email (and/or stores them in their dashboard).
- CSP: add `https://formspree.io` to `form-action` and `connect-src` as needed.
- Free tier available; paid tiers for more submissions, custom routing, etc.

**When a third-party form service is the right choice:**
- A static site that needs a working form with zero backend maintenance.
- Low-to-moderate submission volume (within the service's free/standard tier).
- You're okay with vendor lock-in and the service's rate limits.

**When it isn't:**
- You need server-side processing beyond forwarding to email (CRM integration, complex validation, custom storage).
- You need to keep submissions in your own storage (privacy, control, compliance).
- Submission volume exceeds the service's tier — a serverless function or your own backend is more cost-effective.

**Comparison with a serverless function (Cloudflare Pages Function pattern):**
- Third-party service: zero backend, vendor handles spam protection, simpler setup, vendor lock-in, less control.
- Serverless function: you control the backend, can integrate with your own CRM/storage, can fail-open with a backup store, more setup, more control.
- For a personal portfolio form: Formspree is fine. For a patient registration form: a serverless function with KV backup and CRM integration is better (fail-open, data control, compliance).

## Single-Page Portfolio vs Multi-Page Site

The website(Primary) pattern: a single-page portfolio with anchor navigation (#about, #projects, #resume, #coursework, #contact).

**Single-page portfolio:**
- One HTML file, anchor navigation within it.
- Good for a personal site with a small number of sections.
- Simpler to build and maintain (one file, one set of assets).
- SEO: each section can have its own structured data, but the page is one URL. Section-specific indexing is limited.
- Shareability: sharing a section means sharing the URL with the anchor — works, but less clean than a dedicated URL.

**Multi-page site:**
- Each section is a separate URL (and usually a separate HTML file or generated page).
- Better for SEO (each page is indexable, has its own canonical, its own structured data).
- Better for shareability (each section has a clean URL).
- More to maintain (more files, more generators or more hand-authored pages).

**When to use which:**
- Single-page: personal portfolio, small number of sections, the whole story fits on one scrollable page.
- Multi-page: larger site, sections that benefit from dedicated URLs (disease pages, project pages, blog posts), SEO matters per-section.
- The portfolio site (website(Primary)) is single-page; aspirecures is multi-page (each disease is its own page). Different sites, different choices.

## Verification Checklist

Before deploying or declaring a static site healthy:

- [ ] Every page has a unique, descriptive `<title>`
- [ ] Every page has a `<meta name="description">` (real, not auto-pulled)
- [ ] Canonical URLs are present and point to the preferred absolute URL
- [ ] Sitemap lists all public pages with correct `lastmod`
- [ ] 404 is a real 404, not a soft 404
- [ ] JSON-LD is valid, has `@context`, and matches the page content
- [ ] Analytics loads correctly and respects consent (if consent-gated)
- [ ] Form backend is verified working end-to-end (submission saves, forwards, redirects)
- [ ] Form backend fails open with a backup store; failures are logged
- [ ] CSP is in place and tested (report-only → enforce); no violations in console
- [ ] HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy headers set (if host supports)
- [ ] No hand-edited generated pages that will be clobbered on rebuild
- [ ] Rebuild is idempotent (same bytes when nothing changed)
- [ ] External links resolve (local link check at minimum; external link rot monitored if citation-heavy)
