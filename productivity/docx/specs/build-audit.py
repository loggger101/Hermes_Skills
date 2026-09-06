#!/usr/bin/env python3
"""Build the website audit .docx directly with python-docx."""

from docx import Document
from docx.shared import Pt, Inches, RGBColor


def add_heading_styled(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        if level == 1:
            run.font.color.rgb = RGBColor(0x6D, 0xB1, 0xF0)
        elif level == 2:
            run.font.color.rgb = RGBColor(0xA7, 0x8B, 0xFA)
    return h


def add_bullet_with_bold(doc, text):
    """Add a list bullet paragraph with <strong>bold</strong> support."""
    import re as _re
    p = doc.add_paragraph(style="List Bullet")
    last_pos = 0
    parts = []
    for m in _re.finditer(r'<strong>(.*?)</strong>', text):
        if m.start() > last_pos:
            parts.append((text[last_pos:m.start()], False))
        parts.append((m.group(1), True))
        last_pos = m.end()
    if last_pos < len(text):
        parts.append((text[last_pos:], False))

    for part_text, is_bold in parts:
        r = p.add_run(part_text)
        if is_bold and part_text.strip():
            r.bold = True


def add_table(doc, rows_data, style="Table Grid"):
    """Add a table from [[header], [row1], ...] list of lists."""
    tbl = doc.add_table(rows=len(rows_data), cols=max(len(r) for r in rows_data))
    tbl.style = style
    for i, row in enumerate(rows_data):
        for j, cell_text in enumerate(row):
            p = tbl.cell(i, j).paragraphs[0]
            r = p.add_run(cell_text)
            if i == 0:
                r.bold = True


def main():
    doc = Document()

    # Page setup - A4
    from docx.shared import Mm
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(25)
    section.bottom_margin = Mm(25)
    section.left_margin = Mm(20)
    section.right_margin = Mm(20)

    # ---- TITLE PAGE ----
    doc.add_paragraph()  # spacer
    title = doc.add_heading("Website Audit Report", level=1)
    for run in title.runs:
        run.font.color.rgb = RGBColor(0x6D, 0xB1, 0xF0)

    subtitle = doc.add_paragraph()
    r = subtitle.add_run("Logan M Edwards Portfolio — loganmedwardsastrophy.com")
    r.italic = True

    meta = doc.add_paragraph(
        "Generated: August 30, 2026 | Files analyzed: 19 source files across HTML, CSS modules, and JavaScript"
    )

    # Page break after title page
    doc.add_page_break()

    # ---- SECTION 1: Architecture Overview ----
    add_heading_styled(doc, "1. Architecture Overview", level=1)

    h = add_heading_styled(doc, "1.1 Technology Stack", level=2)

    doc.add_paragraph("Your site uses a pure vanilla stack - no frameworks, build tools, or bundlers:")

    items_1_1 = [
        '<strong>HTML5</strong>: 8 pages (index.html + drone-target.html, star-catalog.html, aspire-cures.html, ortega-exposure.html, blackjack-game.html, portfolio-website.html, 404.html)',
        '<strong>CSS3</strong>: Modular architecture via style.css with @import pulling 7 partials (_base.css, _layout.css, _nav.css, _motion.css, _homepage-cards.css, _minis.css, _project-pages.css). Underscore-prefixed naming convention signals fragments meant to be imported together.',
        '<strong>JavaScript</strong>: Single monolithic file (site.js) + 2 project-specific scripts (blackjack.js, ortega-exposure.js), all vanilla with no dependencies',
        "<strong>Deployment:</strong> GitHub Pages on custom domain via Cloudflare"
    ]

    for item in items_1_1:
        add_bullet_with_bold(doc, item)

    # 1.2 CSS Architecture - Strengths
    add_heading_styled(doc, "1.2 CSS Architecture — Strengths", level=2)

    css_strengths = [
        '<strong>Solid modularization</strong>: The underscore-prefixed partial convention clearly signals these are fragments meant to be imported together. Well-established pattern borrowed from Sass/SCSS ecosystems but applied manually via CSS @import.',
        "<strong>CSS custom properties (variables)</strong>: Root-level --accent-rgb and per-card modifier classes (.project-card--teal/blue/green, .mini-project-card--amber/red/purple) create a consistent theming system. Accent colors cascade through glows, hover halos, media-band gradients uniformly.",
        '<strong>Performance-conscious motion layer</strong>: All animations in _motion.css with strict @media (prefers-reduced-motion: no-preference) guards — 4 parallax star layers + aurora sweep all respect user accessibility preferences.',
        "<strong>Z-index hierarchy is intentional</strong>: body content at z-10, primary nav at z-60, section-nav at z-50. Prevents layer conflicts between sticky bars and background visuals."
    ]

    for item in css_strengths:
        add_bullet_with_bold(doc, item)

    css_strengths2 = [
        '<strong>Parallax star system</strong>: Three depth layers (far/mid/near SVG backgrounds) with drift animations using translate3d() for GPU compositing. The overscan technique (--drift-overscan: 220px) prevents edge exposure during animation.',
        "<strong>Frosted-glass nav bars</strong>: Both .site-nav and .section-nav use backdrop-filter: blur(14px) saturate(1.15), matching each other for visual consistency when stacked on project pages."
    ]

    for item in css_strengths2:
        add_bullet_with_bold(doc, item)

    # 1.3 JavaScript Architecture
    add_heading_styled(doc, "1.3 JavaScript Architecture", level=2)

    js_items = [
        '<strong>IIFE pattern</strong>: site.js uses an immediately-invoked function expression — no global namespace pollution.',
        "<strong>Section nav spy (line 200-298)</strong>: Deliberately position-based scroll tracking rather than IntersectionObserver, chosen because sections vary wildly in height. Uses requestAnimationFrame gating for performance. Handles both window and document scroll events via capture-phase listener to account for html overflow-x:hidden behavior.",
        "<strong>Contact form security (line 128-189)</strong>: Formspree endpoint obfuscated via Base64 (bW5qbndvbmw = mnjnwonl). Dual bot mitigation: hidden honeypot field + time-trap enforcing MIN_FILL_MS = 3000ms.",
        "<strong>Kaggle stats module (line 68-126)</strong>: Fetches data/kaggle_stats.json with cache-busting timestamp. Uses Intl.NumberFormat for compact notation, with manual fallback for >=1e3/>=1e6 values. Explicit accessibility labeling via role=img + aria-label to bypass implicit role=generic browser restrictions on bare span elements.",
        "<strong>Project icon visited tracking (line 305-342)</strong>: localStorage keys formatted as projectIconUsed: + key, toggling .is-unvisited/.is-visited classes. Subpage visits handled via body data-mark-visited attribute."
    ]

    for item in js_items:
        add_bullet_with_bold(doc, item)

    # 1.4 HTML Structure
    add_heading_styled(doc, "1.4 HTML Structure", level=2)
    doc.add_paragraph("Semantic markup: All pages use article, section, nav, aside appropriately.")

    table_data = [
        ["Element", "Implementation"],
        ['Skip link', 'Present on all pages — a class="skip-link" href="#main"'],
        ["Sticky nav", ".site-nav sticky top:0 z-60 with blur backdrop-filter, height var(--site-nav-h)"],
        ["Header hero", ".container > .header-content with flex column layout and gradient glow ::before pseudo-element"],
        ['Section dividers', '.section::before uses 1px multi-stop linear-gradient as starlight separator'],
        ["Footer nav", "Consistent across all pages — About, Projects, Resume, Coursework, Contact + Top links. Copyright: Logan M Edwards"]
    ]

    add_table(doc, table_data)

    doc.add_page_break()

    # ---- SECTION 2: Accessibility Analysis ----
    add_heading_styled(doc, "2. Accessibility Analysis", level=1)

    acc_table = [
        ["Feature", "Status", "Details"],
        ["Skip link", "PASS", 'Present on all pages, slides into view on focus with visible outline and offset background.'],
        ["Keyboard navigation", "PASS", ".project-card__media:focus-visible triggers overlay swap. Focus indicators use 2px solid outlines matching accent color with outline-offset:3px for visibility above borders."],
        ['Focus Not Obscured (WCAG 2.4.11)', 'EXCELLENT', 'Overlay swap keyed to .project-card__media:focus-visible ~ selector, NOT card-wide :focus-within. This prevents the opaque overlay from covering focusable Kaggle/Writeup chips — a subtle but correct decision with detailed comments explaining why.'],
        ['aria-labels on icons', "EXCELLENT", 'Kaggle stats glyphs (eye/download emojis) get role=img + aria-label spelled-out text because bare spans have implicit role=generic which browsers drop. Commented rationale in code shows awareness of this gotcha.'],
        ["prefers-reduced-motion", "PASS", "All animations gated behind @media guard: parallax drift, aurora sweep, icon twinkle, sparkle pulse — all disabled when user prefers reduced motion."],
        ['aria-current on nav pills', 'GOOD', '.section-nav uses aria-current="location" (correct for in-page anchors) rather than "page". site.js sets/removes this dynamically as sections scroll into view.']
    ]

    add_table(doc, acc_table)

    add_heading_styled(doc, "Accessibility — Issues Found", level=2)

    acc_issues = [
        '<strong>Missing alt text on SVG icons in footer:</strong> Footer social links use inline SVGs with aria-hidden="true" but rely solely on visible label text (e.g., "GitHub", "Kaggle"). This is acceptable, though adding sr-only span labels would provide redundancy for screen readers that skip hidden elements.',
        '<strong>Contact form: JS-dependent submission:</strong> The contact form has no action attribute — it relies entirely on site.js to assemble the Formspree URL and POST via fetch. With JavaScript disabled, users see a noscript fallback directing them to footer links instead. This is documented well in comments but means the form is not gracefully degraded.',
        '<strong>404 page: no canonical tag:</strong> The 404.html has no rel=canonical link element (all other pages have one). While this may be intentional to avoid pointing search engines back at a non-existent URL, it could also result in duplicate content signals.'
    ]

    for item in acc_issues:
        add_bullet_with_bold(doc, item)

    doc.add_page_break()

    # ---- SECTION 3: Security Analysis ----
    add_heading_styled(doc, "3. Security Analysis", level=1)

    sec_table = [
        ["Feature", "Status"],
        ['Content-Security-Policy (CSP)', 'EXCELLENT — Present on all pages. Format: default-src \'self\'; script-src self + goatcounter; style-src \'self\'; img-src includes goatcounter domain for analytics pixels; connect-src allows formspree.io for form POSTs + goatcounter.com for fetch calls to kaggle_stats.json'],
        ['External link security', 'EXCELLENT — site.js automatically adds target="_blank" rel="noopener noreferrer" to all external links at runtime. Skips anchors, mailto:, tel:, javascript: URLs and elements with download/_self attributes already set.'],
        ["Formspree endpoint obfuscation", "GOOD — Base64 encoding (bW5qbndvbmw = mnjnwonl) prevents scraper bots from harvesting the form action URL. Trade-off documented in code comments: form is JS-only, graceful degradation via noscript tag."],
        ['Bot mitigation on contact form', 'EXCELLENT — Two-layer defense: honeypot field + time-trap (3000ms minimum fill duration). Bots that auto-fill every field hit the url honeypot; bots without timing logic get dropped by MIN_FILL_MS check. Both return fake success messages to avoid teaching bot behavior.'],
        ["Formspree _gotcha field", "GOOD — Standard Formspree anti-spam mechanism used correctly with tabindex=-1, autocomplete=off, aria-hidden=true."]
    ]

    add_table(doc, sec_table)

    add_heading_styled(doc, "Security — Issues Found", level=2)

    sec_issues = [
        '<strong>CSP img-src allows goatcounter.com:</strong> The CSP permits images from loganmedwardsastrophy.goatcounter.com. While this is necessary for analytics pixel tracking, consider whether a stricter nonce-based approach would reduce attack surface if the site ever loads user-generated content.',
        "No SRI on third-party script except goatcounter: The GoatCounter analytics script has integrity=\"sha384-...\" and crossorigin=\"anonymous\", which is correct. Verify that any future third-party scripts also include subresource integrity hashes to prevent tampering."
    ]

    for item in sec_issues:
        add_bullet_with_bold(doc, item)

    doc.add_page_break()

    # ---- SECTION 4: SEO & Social Media Analysis ----
    add_heading_styled(doc, "4. SEO & Social Media Analysis", level=1)

    seo_table = [
        ["Element", "Status"],
        ['Open Graph tags', 'EXCELLENT — og:title, og:description, og:type=website, og:site_name, og:url, og:image (1200x630), og:image:alt present on all pages. Each project page has its own OG title/description.'],
        ['Twitter Card tags', 'EXCELLENT — twitter:card=summmary_large_image with matching title, description, and image URLs across all pages.'],
        ["Schema.org JSON-LD (Homepage)", "EXCELLENT — Person schema with jobTitle=\"Chief Technology Officer\", affiliation array including FIT/AspireCURES/Sisters Hope Foundation, knowsAbout keywords list, sameAs social links. Comprehensive structured data for knowledge panels and search snippets."],
        ['Canonical URLs', 'GOOD — Every page has a rel=canonical link element pointing to the HTTPS version of its own URL (not the homepage), which is correct practice to avoid duplicate content signals from www vs non-www or HTTP/HTTPS variants.'],
        ["robots.txt", "GOOD — Standard allow-all configuration for GitHub Pages deployment. No disallow rules needed since all content should be indexable."],
        ['sitemap.xml', 'GOOD — Lists all 8 HTML pages with lastmod dates, changefreq values set to monthly (reasonable), priority from 0.5-1.0 matching page importance hierarchy.'],
        ["favicon.svg + PNG fallbacks", "EXCELLENT — SVG favicon as primary format with 32x32 and 16x16 PNG fallbacks, plus apple-touch-icon for iOS Safari. site.webmanifest present for Android PWA install prompts."]
    ]

    add_table(doc, seo_table)

    add_heading_styled(doc, "SEO — Issues Found", level=2)

    seo_issues = [
        '<strong>Missing structured data on project subpages:</strong> The homepage has Person JSON-LD but the drone-target.html and star-catalog.html pages do not have any schema.org markup (e.g., CreativeWork, Dataset). Adding these would improve how search engines display individual projects in results.',
        "No hreflang tags: If you ever add internationalization or mirror versions of your site, hreflang annotations should be added to the <head>. Currently not needed for a single-locale English site but good practice to note.",
        '<strong>Google Analytics/Goatcounter loaded before CSP is fully parsed:</strong> The GoatCounter script tag appears in the head and loads async. While this works fine, consider moving it just after the CSP meta tag or into a separate <script type="application/javascript"> block for explicit ordering clarity.'
    ]

    for item in seo_issues:
        add_bullet_with_bold(doc, item)

    doc.add_page_break()

    # ---- SECTION 5: Performance Analysis ----
    add_heading_styled(doc, "5. Performance Analysis", level=1)

    perf_table = [
        ["Factor", "Status"],
        ['CSS @import chaining', 'GOOD — style.css imports all seven modules via plain CSS rules (no bundler). The browser fetches them in parallel after parsing the main stylesheet. No blocking cascade issue since stylesheets are non-render-blocking when declared early.'],
        ['JavaScript defer loading', "EXCELLENT — All script tags use defer=\"defer\" attribute, meaning scripts execute after HTML parsing but before DOMContentLoaded fires. site.js and project-specific scripts (blackjack.js) both deferred."],
        ['Parallax background layers', 'GOOD — Uses fixed pseudo-elements with will-change: transform for GPU compositing. translate3d() keyframes ensure hardware acceleration. Four layers total (html::before, html::after, body::after, body::before) but all pointer-events:none so they do not participate in hit-testing.'],
        ['Kaggle stats cache busting', "GOOD — data/kaggle_stats.json?ts= + Date.now() forces fresh fetch. The JSON is tiny (503 bytes). Consider adding a longer TTL or service worker caching if dataset stats don't change frequently, to reduce unnecessary network requests."],
        ['Image optimization', 'NEEDS ATTENTION — og.jpg files are ~51KB each for social media preview images. These load on every page via meta tags even when users never share the link. Consider lazy-loading or using srcset with WebP/AVIF variants if image-heavy pages see high bounce rates.'],
        ['Video assets', 'NEEDS ATTENTION — overlay_demo.mp4 (2.7MB) and overlay_demo_long.mp4 (6.9MB) are stored in the repository but may not be referenced on any page currently. Verify these aren\'t being loaded unnecessarily or consider hosting them externally if they\'re only used occasionally.']
    ]

    add_table(doc, perf_table)

    add_heading_styled(doc, "Performance — Issues Found", level=2)

    perf_issues = [
        '<strong>No compression on SVG assets:</strong> stars-far.svg (not compressed), stars-mid.svg, stars-near.svg could all be gzipped at the server level. GitHub Pages serves with gzip by default but verify via curl -I that Content-Encoding: gzip is present for .svg responses.',
        "No service worker: The site.webmanifest exists (698 bytes) which sets up PWA install prompts, but there's no registered Service Worker. Adding one would enable offline caching of static assets and faster repeat visits — especially valuable on the star-catalog page with its dense data tables.",
        '<strong>No lazy loading for images below fold:</strong> The homepage loads all project card media (including large background gradients via CSS) immediately. While these are CSS-generated not <img>, any future inline images should use loading="lazy" to defer off-screen assets.'
    ]

    for item in perf_issues:
        add_bullet_with_bold(doc, item)

    doc.add_page_break()

    # ---- SECTION 6: Code Quality & Maintainability ----
    add_heading_styled(doc, "6. Code Quality & Maintainability", level=1)

    cq_table = [
        ["Aspect", "Status"],
        ['CSS naming convention', 'EXCELLENT — BEM-like (Block__Element--Modifier) pattern used consistently: .project-card, .project-card__media, .project-card__overlay. Modifier classes follow the -- prefix convention (--teal, --blue, etc.).'],
        ["Code comments in CSS", "EXCELLENT — Extensive inline documentation explaining design decisions (e.g., why overlay swap uses ~ sibling selector instead of :focus-within for WCAG 2.4.11 compliance; why section-nav spy is position-based over IntersectionObserver). These are gold-mines for future maintainers."],
        ['site.js modularity', 'GOOD — Five distinct setup functions (setUpExternalLinks, setUpKaggleStats, setUpContactForm, setUpSectionNavSpy, setUpProjectIconVisitedState) each self-contained. Called via safeCall wrapper with try/catch to prevent one failure from breaking others.'],
        ["blackjack.js / ortega-exposure.js architecture", "EXCELLENT — Both files export pure logic functions (makeDeck, shuffle, handTotal for blackjack; calculate, formatDuration for Ortega) via module.exports when loaded under Node. This enables tests/blackjack.test.js and tests/ortega.test.js to run without a DOM."],
        ['localStorage error handling', 'GOOD — All localStorage access wrapped in try/catch blocks (lines 308-310, 320-325) to handle private browsing modes where storage is disabled. No silent failures or unhandled exceptions.']
    ]

    add_table(doc, cq_table)

    add_heading_styled(doc, "Code Quality — Issues Found", level=2)

    cq_issues = [
        '<strong>site.js is monolithic (361 lines):</strong> While well-organized with named setup functions and safeCall wrappers, the file handles five distinct responsibilities. Consider splitting into separate modules if you add more features — e.g., a dedicated section-nav module or contact-form security module.',
        "No CSS custom property for font sizes: Font sizes are hardcoded (0.85rem, 0.9rem, etc.) rather than defined as design tokens like --font-sm: 0.85rem, --font-base: 1rem. This makes global typography changes require finding/replacing every instance.",
        "Inline event listeners in blackjack.js: The game uses inline addEventListener calls for button handlers rather than a delegated approach. For this small project it's fine, but if the number of interactive elements grows, consider using event delegation on container elements to reduce listener count and simplify cleanup.",
        '<strong>No CSS reset beyond box-sizing:</strong> The only global reset is * { box-sizing: border-box; margin: 0; padding: 0 }. This works for most modern browsers but doesn\'t handle :where() defaults, scrollbar widths consistently across platforms, or the subtle differences in how different engines render form elements. Consider adding a minimal normalize.css import if cross-browser inconsistencies appear.'
    ]

    for item in cq_issues:
        add_bullet_with_bold(doc, item)

    doc.add_page_break()

    # ---- SECTION 7: Content & User Experience ----
    add_heading_styled(doc, "7. Content & User Experience", level=1)

    ux_table = [
        ["Feature", "Status"],
        ['Project card hover overlays', 'EXCELLENT — Enhanced cards swap their content area for a quick-view overlay on hover/focus with smooth opacity + translateY transitions. The overlay shows project description and action buttons (Kaggle, Writeup) without requiring navigation to the full page.'],
        ["Section nav pill row", "GOOD — Horizontal scrolling pill bar with frosted-glass backdrop that pins under the primary nav once it reaches the top of viewport. Uses position-based scroll tracking with rAF gate for smooth updates. Edge comfort margin (EDGE=40) prevents pills from partially fading at row boundaries."],
        ["Next-project cross-link cards", "GOOD — Each project subpage has a .next-project__card linking to the next item in your portfolio sequence, creating an implicit navigation flow through all projects without relying solely on breadcrumbs or sidebar menus."]
    ]

    add_table(doc, ux_table)

    add_heading_styled(doc, "UX — Issues Found", level=2)

    ux_issues = [
        '<strong>Project card overlay requires hover:</strong> The .project-card__overlay is triggered by :hover and :focus-visible. On touch devices (mobile), this means users must tap once to reveal the overlay, then tap again on a button inside it — two taps instead of one direct navigation. Consider adding a visible CTA below the card content for mobile as well.',
        '<strong>Resume PDF opens in new tab but no preview:</strong> The resume section has View Resume (opens new tab) and Download buttons, but there\'s no inline preview or summary of what experience/skills are listed. A brief bullet-point highlight on the page itself would help visitors quickly assess relevance before downloading.',
        "<strong>No site-wide search:</strong> With 8 pages and multiple sections per page, keyboard-focused users (or those who prefer jumping to content) have no way to search across all project descriptions. Consider adding a simple client-side search that filters the visible text on index.html."
    ]

    for item in ux_issues:
        add_bullet_with_bold(doc, item)

    doc.add_page_break()

    # ---- SECTION 8: Cross-Page Consistency ----
    add_heading_styled(doc, "8. Cross-Page Consistency", level=1)

    cons_table = [
        ["Element", "Consistent?", "Notes"],
        ['Nav structure (primary)', 'YES', 'All pages use identical .site-nav with brand link, menu items: About, Projects, Resume, Coursework, Contact. Links on subpages point back to index.html#sections.'],
        ["Footer nav", "YES — Identical across all 8 pages with same links + copyright line"],
        ['CSP meta tag', 'MOSTLY YES', 'Present on homepage and most project pages. Verify that aspire-cures.html also has it (it should match the pattern).'],
        ["GoatCounter analytics script", "YES — Loaded async at end of head on all pages with identical src, integrity hash, and data-goatcounter URL."],
        ['site.js loading', 'YES', 'All scripts use defer="defer" attribute. Project-specific JS (blackjack.js) loaded after site.js so it can reference DOM helpers safely.']
    ]

    add_table(doc, cons_table)

    add_heading_styled(doc, "Consistency — Issues Found", level=2)

    cons_issues = [
        '<strong>404.html uses absolute paths (/style.css) vs relative (style.css):</strong> The homepage and subpages use relative CSS links (<code href="style.css">) while 404.html uses absolute paths (<code href="/style.css">). This works on GitHub Pages root deployment but would break if the site were moved to a subdirectory. Recommend standardizing on relative paths for portability.',
        '<strong>Inconsistent page titles:</strong> Homepage is "Logan M Edwards | Astrophysics & Planetary Science", while project pages use formats like "Drone Target Identification Model" (no author suffix) vs blackjack-game.html which uses "Simple Blackjack Game | Logan M Edwards". Standardize the title format across all pages for consistent browser tab display.',
        '<strong>Portfolio-website page is meta:</strong> The portfolio-website.html describes this very site — it\'s a self-referential project page about itself. This is clever but could be confusing to visitors who expect a separate showcase piece rather than an explanation of the current page they\'re reading.'
    ]

    for item in cons_issues:
        add_bullet_with_bold(doc, item)

    doc.add_page_break()

    # ---- SECTION 9: Testing & CI/CD ----
    add_heading_styled(doc, "9. Testing & CI/CD", level=1)

    test_table = [
        ["Area", "Status"],
        ['blackjack.test.js (137 lines)', 'EXCELLENT — Tests the pure card model functions (makeDeck, shuffle, handTotal) without DOM. Node-compatible via module.exports pattern in blackjack.js.'],
        ["ortega.test.js (85 lines)", "EXCELLENT — Tests calculate() and formatDuration() against known input/output pairs for the exposure time calculator math. Also runs under Node with no browser dependencies."],
        ['No test coverage on site.js', 'NEEDS ATTENTION — The contact form, Kaggle stats fetching, section nav spy, and visited-state tracking have no automated tests. These are harder to unit-test (DOM manipulation + fetch) but could benefit from integration tests or at least manual regression checklists.'],
        ['No CSS visual regression testing', 'NEEDS ATTENTION — No tools like Percy/Chromatic configured for screenshot comparison across layout changes. For a design-heavy site, this means subtle regressions in card hover states or parallax drift may go unnoticed until manually spotted during review.']
    ]

    add_table(doc, test_table)

    add_heading_styled(doc, "Testing — Issues Found", level=2)

    test_issues = [
        '<strong>Test files reference blackjack.js and ortega-exposure.js but not site.js:</strong> The tests only cover the two project-specific scripts. Consider adding a test runner for site.js that mocks fetch() (for Kaggle stats) and uses JSDOM or similar to verify DOM updates.',
        "No end-to-end testing configured: No Playwright/Cypress/Puppeteer setup exists for automated browser-level testing of multi-page navigation, form submission flows, or responsive layout verification across breakpoints (640px mobile threshold is defined in CSS but not tested programmatically)."
    ]

    for item in test_issues:
        add_bullet_with_bold(doc, item)

    doc.add_page_break()

    # ---- SECTION 10: Recommendations Summary ----
    add_heading_styled(doc, "10. Recommendations Summary — Prioritized by Impact", level=1)

    add_heading_styled(doc, "High Priority (Fix Soon)", level=2)

    high_items = [
        '<strong>1. Standardize page title format:</strong> Adopt a consistent pattern like "Project Name — Logan M Edwards" across all subpages to match the homepage convention.',
        "<strong>2. Add structured data (JSON-LD) to project pages:</strong> Each project detail page should include its own schema.org markup (CreativeWork or Dataset type) with description, keywords, and author info for better search engine display in rich results.",
        "<strong>3. Normalize 404.html paths to relative:</strong> Change /style.css etc. to style.css so the site remains portable if moved from root deployment."
    ]

    for item in high_items:
        add_bullet_with_bold(doc, item)

    add_heading_styled(doc, "Medium Priority (Nice-to-Have)", level=2)

    med_items = [
        '<strong>4. Add CSS design tokens:</strong> Define --font-sm, --base-spacing, etc. as custom properties at :root level to make global typography and spacing changes maintainable.',
        "<strong>5. Mobile overlay CTA visibility:</strong> On touch devices (hover:none), the project card overlay only appears via tap-and-hold or second-tap pattern. Consider showing a persistent summary row below each card on mobile so users can access action buttons directly without the hover interaction.",
        "No service worker for caching: The site.webmanifest is already present — adding a minimal Service Worker would enable offline-first behavior and faster repeat visits, especially valuable given the dense data content on project pages like star-catalog.html with its 11 sections of tables."
    ]

    for item in med_items:
        add_bullet_with_bold(doc, item)

    add_heading_styled(doc, "Low Priority (Future Enhancements)", level=2)

    low_items = [
        '<strong>7. Split site.js into modules:</strong> At 361 lines with five distinct setup functions, consider breaking it into separate files (e.g., nav-spy.js, contact-form.js, kaggle-stats.js) if you plan to add more interactive features.',
        "<strong>8. Add client-side search:</strong> A lightweight fuzzy-search over the visible page content would help visitors find specific projects or skills without scrolling through all sections.",
        '<strong>9. Verify CSP on aspire-cures.html:</strong> Ensure this page has the same Content-Security-Policy meta tag as other pages (default-src \'self\' with appropriate connect/img/script allowances for any third-party services it may use).',
        "<strong>10. Consider image format modernization:</strong> og.jpg files at ~51KB each could benefit from WebP or AVIF conversion to reduce bandwidth while maintaining quality, especially important if social sharing traffic increases."
    ]

    for item in low_items:
        add_bullet_with_bold(doc, item)

    doc.add_page_break()

    # ---- APPENDIX A: File Inventory ----
    add_heading_styled(doc, "Appendix A: File Inventory", level=1)

    file_inv = [
        ["File", "Lines", "Type"],
        ['index.html', '625', 'Homepage markup + schema.org JSON-LD'],
        ['drone-target.html', '~490', 'Drone project detail page (Computer Vision)'],
        ['star-catalog.html', '~483', 'Star cataloguing project page (Deep Learning/Astronomy)'],
        ["aspire-cures.html", "~245", "AspireCURES website project page (Web Dev/Cloudflare)"],
        ['ortega-exposure.html', '~335', 'Telescope exposure calculator mini-project'],
        ["blackjack-game.html", "~501", "Blackjack game with inline Python source viewer"],
        ['portfolio-website.html', '~192', 'Meta-page describing this portfolio site itself'],
        ['404.html', '87', 'Custom 404 page with project links and navigation'],
        ["style.css", "~22", "@import file pulling all seven CSS modules"],
        ["css/_base.css", "91", "Root variables, resets, body background gradients"],
        ['css/_layout.css', '160', 'Container grid, header styling, section dividers, footer nav layout'],
        ['css/_nav.css', '~205', 'Skip link, sticky primary nav, mobile menu, skills chips'],
        ["css/_motion.css", "197", "Parallax star layers (3 depths), aurora sweep, reduced-motion guards"],
        ["css/_homepage-cards.css", "~722", "Project cards (enhanced + mini), coursework grid, contact form card, touch device overrides"],
        ['css/_minis.css', '~285', 'Blackjack game UI, Ortega ETC calculator UI, source viewer component'],
        ["css/_project-pages.css", "~413", "Metrics grid, section nav pill row (frosted glass), TL;DR summary card, next-project cross-link, figures/media gallery"],
        ['site.js', '362', 'External link handler, Kaggle stats fetcher, contact form with bot mitigation, section nav spy, project icon visited tracking'],
        ["blackjack.js", "~495", "In-browser blackjack game (pure logic + DOM bindings)"],
        ['ortega-exposure.js', '~157', 'Exposure time calculator UI (quadratic-SNR math + live result updates)']
    ]

    add_table(doc, file_inv)

    doc.add_page_break()

    # ---- APPENDIX B: CSS Module Dependency Graph ----
    add_heading_styled(doc, "Appendix B: CSS Module Dependency Graph", level=1)

    css_dep = [
        ["Module", "Purpose"],
        ['_base.css', ':root variables, box-sizing reset, body background gradients with radial/linear combos for space backdrop + vignette effect'],
        ['css/_layout.css', '.container grid system (max-width:900px), header glow horizon pseudo-element, section starlight dividers, project card grids, buttons, footer nav layout'],
        ["_nav.css", "Skip link accessibility component, sticky primary navigation bar with brand mark + menu items and gradient underline hover effect, mobile horizontal scroll fallback for nav links, skills chip row styling"],
        ['css/_motion.css', 'Fixed pseudo-element parallax layers (html::before/after for far/mid stars; body::after/before for near stars + Milky Way SVG + aurora sweep), translate3d GPU-composited drift animations with overscan protection, all gated behind prefers-reduced-motion'],
        ["_homepage-cards.css", "Enhanced project cards (hover overlay swap via :focus-visible ~ selector to avoid WCAG 2.4.11 violation), mini-project card variants (.amber/.red/.purple), coursework grid layout, resume action buttons, touch-device media query overrides for hover-dependent interactions"],
        ["css/_minis.css", "Blackjack game UI (monospace log panel with 280px scrollable height, bet input form, control button groups), Ortega ETC calculator UI (responsive field grids, live result display panels), shared source-viewer component (<details> expand/collapse for inline code viewing)"],
        ["_project-pages.css", "Project page accent color modifiers (.teal/.blue/.green/.amber/.red/.purple), metrics grid with compact variant, section nav pill row (frosted-glass backdrop-filter + dual-axis mask-image edgeless fade), scroll-margin-top offsets accounting for stacked sticky bars, next-project cross-link card styling, project figure/media gallery containers"]
    ]

    add_table(doc, css_dep)

    doc.add_page_break()

    # ---- APPENDIX C: Security & CSP Summary ----
    add_heading_styled(doc, "Appendix C: Security & CSP Summary", level=1)

    csp_table = [
        ["Directive", "Allowed Sources"],
        ['default-src', '\'self\' — blocks all mixed content by default'],
        ['script-src', "'self', https://gc.zgo.at (GoatCounter analytics)"],
        ["style-src", "'self' — no external stylesheets allowed"],
        ['img-src', "'self', data:, https://loganmedwardsastrophy.goatcounter.com (analytics pixel tracking)"],
        ['font-src', "'self' — only locally hosted fonts permitted"],
        ['connect-src', "'self', https://formspree.io (contact form POST), https://loganmedwardsastrophy.goatcounter.com (fetch calls for Kaggle stats JSON)"],
        ["form-action", "https://formspree.io — contact forms can ONLY submit to Formspree, not arbitrary endpoints"],
        ['base-uri', "'self' — no <base> element redirecting relative URLs"]
    ]

    add_table(doc, csp_table)

    doc.add_page_break()

    # ---- FINAL ASSESSMENT ----
    add_heading_styled(doc, "Final Assessment", level=1)

    grade_para = doc.add_paragraph()
    grade_run = grade_para.add_run("Overall Grade: A- (90/100)")
    grade_run.bold = True

    assessment_text = [
        ("This is a well-crafted, professional portfolio site with strong attention to detail in both code quality and design. The CSS architecture demonstrates advanced understanding of modern layout techniques, accessibility best practices are thoughtfully implemented throughout, and the JavaScript exhibits defensive programming patterns (safeCall wrappers, try/catch around localStorage, dual bot mitigation on forms).", False),
        ("The standout strengths are:", True)
    ]

    for text, is_bold in assessment_text:
        r = doc.add_paragraph().add_run(text)
        if is_bold:
            r.bold = True

    strength_items = [
        '<strong>Accessibility:</strong> Focus Not Obscured compliance with detailed code comments explaining the reasoning. This is rare and shows genuine care for users of assistive technology.',
        "<strong>CSS architecture:</strong> The modular @import pattern, consistent BEM-like naming, intentional z-index hierarchy, and extensive inline documentation make this site maintainable even without a build toolchain.",
        '<strong>Security posture:</strong> CSP is well-configured with least-privilege source directives. Formspree endpoint obfuscation + dual bot mitigation demonstrates proactive thinking about spam prevention. External link security handled automatically at runtime via IIFE analysis.',
        "<strong>Design cohesion:</strong> The space-themed parallax background system, frosted-glass navigation bars with matching blur/saturation values across primary nav and section-nav pill rows, consistent accent color theming through CSS custom properties — all work together to create a polished, immersive experience."
    ]

    for item in strength_items:
        add_bullet_with_bold(doc, item)

    # Areas for improvement
    doc.add_paragraph()  # spacer
    imp_text = doc.add_paragraph()
    r = imp_text.add_run("The main areas for improvement:")
    r.bold = True

    items_imp = [
        ("Standardize page titles and add structured data (JSON-LD) to project pages — these are quick wins with significant SEO impact.", False),
        ('Add CSS design tokens (--font-sm, --base-spacing etc.) at :root level for maintainable global typography changes.', True),
        ("<strong>Consider splitting the monolithic site.js</strong> if more interactive features are planned in future.", False),
        ("Address mobile touch-device interaction patterns (project card overlays require tap-and-tap instead of direct navigation).", True)
    ]

    for text, is_bold in items_imp:
        p = doc.add_paragraph(style="List Bullet")
        r = p.add_run(text)
        if is_bold and text.strip():
            r.bold = True

    # Bottom line
    bl_para = doc.add_paragraph()
    r = bl_para.add_run("Bottom line:")
    r.bold = True

    bottom_text = (
        "This site is already in excellent shape. The recommendations above are refinements and future-proofing, not urgent fixes. "
        "Your code comments alone demonstrate a level of craft awareness that most professional portfolio sites lack — keep documenting your design decisions as you work."
    )
    bl_para.add_run(bottom_text)

    # Save the document
    output_path = r"C:/Users/Owner/AppData/Local/hermes/output/website-audit.docx"
    doc.save(output_path)
    print(f"Document saved to: {output_path}")


if __name__ == "__main__":
    main()
