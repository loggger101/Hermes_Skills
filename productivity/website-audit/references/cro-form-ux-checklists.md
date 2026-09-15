# CRO / Form / UX Audit Frameworks (for website audit reports)

Source: coreyhaines31/marketingskills `skills/cro/` v2.0.0 + `references/{form,experiments}.md`, `skills/site-architecture/` v2.0.0 + navigation patterns (MIT; mined 2026-09-15). Use these as the **domain checklists for Phase 2 of website audits** — they define what "good" looks like on conversion pages, forms, and site structure so findings can be stated against a standard rather than vibes. The report mechanics (docx generation, verification pass) stay in SKILL.md; this file is what you audit *against*.

## CRO analysis framework (7 dimensions, in impact order)

Before scoring anything, establish: **page type** (homepage / landing / pricing / feature / blog), **primary conversion goal** (signup, demo request, purchase, subscribe, contact), and **traffic context** (organic/paid/email/social — message match depends on it).

1. **Value proposition clarity (highest impact).** Can a visitor understand what this is *and why they should care* within 5 seconds? Is the primary benefit specific and differentiated, in the customer's language not company jargon? Common failures: feature-focused instead of benefit-focused; too vague or too clever; trying to say everything.
2. **Headline effectiveness.** Communicates core value prop; specific enough to be meaningful (numbers, timeframes); matches traffic source messaging. Strong patterns: outcome-focused ("Get [outcome] without [pain point]"), specificity, social proof ("Join 10,000+ teams who…").
3. **CTA placement/copy/hierarchy.** One clear primary action; visible without scrolling; button copy communicates value not just action — weak: "Submit", "Sign Up", "Learn More"; strong: "Start Free Trial", "Get My Report". Logical primary vs secondary structure; CTAs repeated at decision points.
4. **Visual hierarchy & scannability.** A scanner gets the main message; important elements visually prominent; enough white space; images support rather than distract.
5. **Trust signals & social proof.** Customer logos (recognizable ones), specific attributed testimonials with photos, case-study snippets with real numbers, review scores + counts, security badges where relevant — placed near CTAs and after benefit claims.
6. **Objection handling.** Price/value concerns, "will this work for my situation?", implementation difficulty, "what if it doesn't work?" — addressed via FAQ, guarantees, comparison content, process transparency.
7. **Friction points.** Too many form fields; unclear next steps; confusing navigation; required info that shouldn't be required; mobile experience issues; long load times.

**Page-type variants:** Homepage = clear positioning for cold visitors + quick path to most common conversion + serve both "ready to buy" and "still researching". Landing page = message match with traffic source, single CTA (remove nav if possible), complete argument on one page. Pricing = clear plan comparison, recommended-plan indication, address "which plan is right for me?" anxiety. Feature page = connect feature→benefit, use cases/examples, path to try/buy. Blog post = contextual CTAs matching content topic at natural stopping points (not generic end-of-post banners).

**Output shape for audit reports:** Quick Wins (implement now) / High-Impact Changes (prioritize) / Test Ideas (hypotheses worth A/B testing rather than assuming) / Copy Alternatives (2–3 per key element with rationale). This 4-bucket split maps directly onto the impact×effort priority matrix already in SKILL.md.

## Form audit framework

**Core principles:**
- **Every field has a cost.** Rule of thumb: 3 fields = baseline; 4–6 fields → 10–25% completion reduction; 7+ → 25–50%+. For each field ask: is it absolutely necessary *before* we can help them? Can we get it another way (enrichment from email domain, post-submission)? Can we ask later (progressive profiling)?
- **Value must exceed effort** — clear value prop above the form; make what they get obvious.
- **Reduce cognitive load** — one question per field, conversational labels, logical grouping/order, smart defaults.

**Field-by-field checks:** Email = single field with no confirmation (confirmation fields hurt), inline validation, typo detection ("did you mean gmail.com?"), proper mobile keyboard type. Name = test single "Name" vs First/Last — split only if personalization requires it. Phone = optional where possible; if required explain why; auto-format as typed. Company = consider inferring from email domain + post-submit enrichment instead of asking. Free-text message = optional, character guidance, expands on focus. Dropdowns = placeholder "Select one…", searchable when many options, radio buttons when <5 options, always an "Other" with text field.

**Layout:** Field order — easiest first (name/email), build commitment before sensitive fields, group logically; single column beats multi-column for completion and mobile (multi only for short related pairs like First/Last). **Labels stay visible** — placeholder-only labels disappear on typing and leave users unsure what they're filling in; placeholders are examples, not labels. Tap targets 44px+.

**Multi-step forms:** use when >5–6 fields, logically distinct sections, or conditional paths. Progress indicator (step X of Y), one topic per step, allow back navigation, save progress across refresh, clear required-vs-optional indication. Progressive commitment pattern: low-friction start (just email) → detail (name/company) → qualifying questions → preferences.

**Error handling:** validate on field blur not while typing; error messages specific to the problem + how to fix + positioned near the field ("Please enter a valid email address (e.g., name@company.com)" not "Invalid input"); never clear entered input on submit failure; focus first error field; preserve all data.

**Submit button:** copy = action + what they get ("Get My Free Quote", not "Submit"); immediately after last field, left-aligned with fields, high contrast; loading state disables the button (prevents double-submit); success confirmation states clear next steps.

**Trust near form:** privacy statement, security badges for sensitive data, expected response time, objection lines ("No spam, unsubscribe anytime", "No credit card required"). Perceived-effort cues: "Takes 30 seconds".

**Form metrics to check when analytics is available:** start rate (page views → first field focus), completion rate (started → submitted), per-field drop-off and error rates, time-to-complete, mobile vs desktop split. Audit finding pattern for each issue: **Issue / Impact (estimated effect) / Fix / Priority**.

**Form-type specifics:** Lead capture = minimum viable fields (often just email); test email-only vs email+name; enrichment questions post-download. Contact form = Email/Name + Message essential, phone optional, set response-time expectations, offer alternatives (chat/phone). Demo request = Name/Email/Company required, phone optional with preferred-contact choice, use-case question helps personalization, calendar embed raises show rate. Quote requests = multi-step works well; technical details later; save progress. Surveys = progress bar essential, one question per screen, skip logic for relevance.

## Site structure & navigation audit framework

**Hierarchy:** 3-click rule — any important page within 3 clicks of homepage (not absolute, but critical pages buried 4+ levels deep is a defect). Go as flat as possible while keeping nav clean; a dropdown with 20+ items means add a hierarchy level. Levels: L0 homepage → L1 primary sections (/features, /blog, /pricing) → L2 section pages → L3+ detail. Represent hierarchies in reports as ASCII trees (quick drafts, text contexts) or Mermaid (visual presentations, nav zones, link patterns).

**URL structure:** readable/descriptive; keywords where natural; consistent pattern per page type; lowercase hyphen-separated; no unnecessary parameters. **Breadcrumbs must match URLs** — breadcrumb "Products > Widget" with URL `/shop/widget-pro` is a defect worth flagging.

**Navigation anti-patterns (flag each occurrence):**
| Anti-pattern | Why it fails |
|---|---|
| 8+ header items | Decision paralysis; unreadable on small screens |
| Dropdown inception (dropdowns in dropdowns) | Cognitive overload, mobile-hostile |
| Mystery icons without labels | Users can't decode them |
| Primary nav hidden in hamburger **on desktop** | Buries important pages where users expect a menu bar |
| Nav inconsistent between pages | Should be identical site-wide (except app vs marketing surfaces) |
| No mobile consideration for the header design | Desktop-only thinking; test on real devices |
| Footer as unorganized sitemap dump (50+ links, no structure) | Wastes trust-space and crawl equity |

**Internal linking:** important pages well-linked with descriptive anchors; no orphan pages (zero inbound internal links — pair this with a programmatic check: build the link graph from all HTML files and report zero-inbound nodes); reasonable link counts per page; over-optimized anchor text flagged.

## Benchmarking appendix (comparing one site against competitors)

From unmerged community PR #306 (social-benchmarking methodology — never merged upstream, but the normalization discipline is sound): when an audit compares a user's site/account against competitors, **compare efficiency not raw size** — normalize: rate per follower/reach/impression (always state which denominator), engagements per post (when volume differs), growth rate = net new / starting, cadence (posts per week/month), format mix (% by type), share of top posts (how much performance concentrates in a few winners). **Keep platform context separate** — LinkedIn comments and TikTok views mean different things; don't blend into one leaderboard unless asked for a high-level summary. Use the same date range for every account, and label data-source confidence when mixing live exports with manually collected public data ("perfect data is less important than consistent definitions across accounts").

## Provenance notes

- All frameworks above are from marketingskills' cro/site-architecture skills (MIT); page-type experiment catalogs (`references/experiments.md` upstream) exist for generating Test Ideas per page type — the 4-bucket output shape covers what an audit needs without porting the full catalog.
- The benchmarking appendix is explicitly **unmerged community content** (PR #306, closed stale by maintainer; author re-cut only the tool-integration half as PR #566) — treat its methodology as practitioner-grade, not upstream-vetted.
