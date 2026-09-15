# Agent-Ready Sites & the AI-Search Layer (AEO/GEO)

Source: coreyhaines31/marketingskills `skills/ai-seo/` v2.5.0 + its references (`agent-readiness.md`, `format-volatility.md`, `citations-vs-recommendations.md`, MIT; mined 2026-09-15). The classic SEO fundamentals (titles, canonicals, JSON-LD, sitemaps) already live in this skill — this reference is the **layer on top**: being *cited by AI answer engines* and *usable by autonomous agents*. Directly applicable to loganmedwardsastrophy.com and aspirecures audits: both are static sites where "can an agent read/act on this page?" is now a real discoverability axis.

## The core distinction

Traditional SEO gets you **ranked**; AI search gets you **cited**. In traditional search you need page 1; in AI search a well-structured page can get cited even from rank 2–3, because engines select on content quality/structure/relevance, not position alone. Key scale (source-cited): AI Overviews appear in ~45% of Google searches and cut clicks to sites by up to 58%; brands are **6.5x more likely to be cited via third-party sources than their own domain**; optimized content gets cited ~3x more often; statistics + citations boost visibility 40%+ across queries.

## Google's official stance vs the multi-platform reality (read once, changes everything)

Google's [AI features optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) is explicit:
- **No special markup or files required** for AI Overviews / AI Mode — they run on core Search ranking.
- **Don't chunk content for AI**, don't write separate "for AI" variants (risks the *scaled content abuse* spam policy).
- Helpful, people-first E-E-A-T content wins; **no AI-specific Search Console reporting exists** — standard Performance/Coverage/Core Web Vitals are what you measure.

Non-Google engines (ChatGPT search, Perplexity, Claude/Brave, Copilot/Bing) behave differently: they actively reward extractable structure (self-contained answer blocks, FAQs, comparison tables), parse `llms.txt` and machine-readable files when present, and cite third-party sources more heavily than top-ranked pages.

**Practical split:** for Google AIO/AI Mode → optimize for people + core Search, full stop. For ChatGPT/Claude/Perplexity → layer on extractable structure + machine-readable files (it doesn't hurt Google — it's normal good organization). When in doubt: "write for people, organize for clarity."

## Query fan-out

Google AI features generate **concurrent related queries** under the hood and synthesize across them ("how to fix lawns" → herbicides, chemical-free removal, weed prevention…). Implications: single-page-per-keyword targeting weakens; cover the full topical cluster so you're retrievable for the fan-out variants. Long-tail intent matters less than topical authority. Action when planning content: brainstorm the 5–10 related queries an AI will fan out to and make sure the site covers them. ChatGPT fans out too — its *literal* background queries are extractable via DevTools → network payload (use as a diagnostic of your niche; explicitly warned against by upstream as a mass-content-generation input).

## The three pillars

**1. Structure — make content extractable.** AI systems extract passages, not pages; every key claim should work standalone. Block patterns: definition blocks ("What is X"), step-by-step ("How to X"), comparison tables ("X vs Y"), pros/cons, FAQ, statistic-with-source. Rules: lead each section with the direct answer; keep key answer passages 40–60 words (snippet-extraction optimum); H2/H3s phrased like real queries; tables beat prose for comparisons; numbered lists beat paragraphs for processes; one idea per paragraph.

**2. Authority — make content citable.** Princeton GEO study (KDD 2024, measured on Perplexity) ranked the levers: cite sources **+40%**, add statistics **+37%**, expert quotations with name/title **+30%**, authoritative tone +25%, clarity +20%, technical terms +18%, unique vocabulary +15%; **keyword stuffing −10%** — unlike classic SEO where it's merely ineffective, it *actively reduces* AI visibility. Best combo: fluency + statistics; low-ranking sites benefit most (up to ~115% with citations). Freshness signals ("Last updated" prominent, dated stats) and E-E-A-T alignment matter as much as in core Search.

**3. Presence — be where AI looks.** Third-party surfaces out-cite your own site: Wikipedia (~7.8% of ChatGPT citations), review sites (G2/Capterra/TrustRadius for B2B SaaS), YouTube (**models don't watch video — they read the text layer**: transcript, captions, chapters, description, pinned comment), podcasts (transcripts + show notes get crawled and cited), Quora, industry roundups.

### Citation-source volatility (the 2026-08 case study)

Third-party citation mixes are **not stable** — they shift overnight with model/retrieval updates:
- **ChatGPT 5.6 (Aug 2026)** demoted the exploited formats in one release: listicle citations fell **−50.5%** (15.77% → 7.80%) and comparison-page citations **−32.1%** (9.08% → 6.17%), while `site:` and "official" retrieval surged — a shift toward primary sources and owned pages. Stop justifying scaled listicle/comparison production with "wins AI citations"; comparisons *still* convert humans and still earn citations on Google AIO/Gemini/Perplexity (per-platform table, not one-size-fits-all).
- ChatGPT's fan-out changes **nearly wiped Reddit as a citation source within days** (practitioner-reported; one team had 24-hour citations at 1M+ impressions/month before the change). Business-owned websites reportedly dominate Gemini citations (~60%).

Strategy consequences: never concentrate AI-visibility work in one third-party surface — it's a portfolio, not a menu. Owned-site fundamentals are the hedge (the one surface no platform can drop you from). Treat any citation-share statistic as a **dated snapshot** — verify against your own monitoring before betting on it. Freshness is fast: new content on retrieved surfaces can be cited within ~24 hours.

### Citation ≠ recommendation (visibility ladder)

`retrieved → cited → mentioned → recommended`. Getting *recommended* onto the buyer's shortlist is governed by web-wide consensus (reviews, forums, analysts, press), largely independent of your own content. Measured backfire: in one 100-query B2B study, **69% of AI-Overview citations that self-promotional listicles earned came in answers recommending competitors** instead of the publishing brand.

## Agent-readiness: can an agent reach, navigate, and parse you?

Separate from content quality — whether agents can *get to it at all*. Free scoring tools (both Aug 2026) made this measurable; run one before AND after any work — the score is a shareable artifact and the failed checks are your worklist:
- **Is Agentic** (Vercel + Ora): `npx is-agentic yourdomain.com` or is-agentic.com — 100+ checks, Essential vs Recommended tiers, includes an observed agent journey showing where friction hit.
- **Frase Agent Readiness Checker**: Access/Discovery/Parseability triad; ≥80 reliable, 60–79 solid-with-gaps, <60 real access problems.

### The three questions

**1. Access — can an agent get the page and see real content?**
- Core content in the **initial HTML response**. Most agents never execute JavaScript — if content only exists after client-side rendering, it doesn't exist (the #1 essential check). For our static sites this is a near-pass by architecture; for JS-heavy pages it's fatal.
- No bot challenge/WAF block on the request path: aggressive Cloudflare challenges that block `GPTBot`/`PerplexityBot`/`ClaudeBot` are self-inflicted invisibility — audit what your CDN actually does to those user agents (many sites block them by default without anyone deciding).
- Correct HTTP behavior: real status codes (no soft-404s), stable canonicals, recoverable errors.

**2. Discovery — do files tell agents what's here?**
- `robots.txt` with an **explicit AI-crawler stance**: GPTBot + ChatGPT-User (OpenAI), PerplexityBot, ClaudeBot + anthropic-ai, Google-Extended (Gemini/AIO), Bingbot (Copilot). Blocking a search/cite bot = that platform literally cannot cite you. Middle ground: block training-only crawlers (CCBot) while allowing the search-and-cite ones.
- Sitemap loads and parses cleanly; `llms.txt` at root (product overview + key-page links incl. pricing); **`llms-full.txt`** — entire site in one file so an agent gets everything in a single request (emerging, cheap to generate alongside llms.txt).

**3. Parseability — once there, can the agent tell what the page is?**
- Valid substantive JSON-LD (see this skill's structured-data section).
- A **Markdown representation of the page**, two implementations: content negotiation (`Accept: text/markdown` at the same canonical URL + `Vary` header) or an HTTP `Link` header pointing to a parallel Markdown file. For static hosts, serving `<page>.md` next to `<page>.html` with a Link header is trivially doable.
- Clear document structure: one H1, headings that answer sub-questions, extractable blocks (pillar 1).

### Machine-readable files for agent buyers

AI agents increasingly compare products programmatically before a human visits. If pricing sits behind JS rendering or a "contact sales" wall, agents skip you and recommend competitors whose info they can read:
- **`/pricing.md`** — structured tiers with consistent units, specific limits/thresholds (not just feature names), what's included per tier; keep current (stale is worse than absent); link from sitemap + pricing page. Same principle as robots.txt / llms.txt / AGENTS.md.

### Emerging: agent-*actionable*, not just readable

**WebMCP**: a page declares its forms/CTAs as callable tools with input schemas so an agent doesn't reverse-engineer the UI (emerging — no ranking/citation signal yet). **UCP** (Universal Commerce Protocol): Google-referenced forthcoming standardized commerce hooks. Practical today: highest-intent actions (signup, pricing, demo booking, contact) must work without JS-only flows, with labeled semantic form fields and machine-readable confirmation.

## Monitoring AI visibility (DIY, no tools)

Monthly: pick your top 20 queries → run each through ChatGPT/Perplexity/Google → record cited? who? which page? → log in a spreadsheet, track month-over-month. **AI answers are non-deterministic — one run is an anecdote:** run each query 3–5 times per platform and report the mention *rate* with sample size ("cited 3/5, n=5"), comparing rates over time rather than single runs; attribute misses to technical (not retrieved) vs comprehension vs trust causes. Commercial options exist for scale (Peec AI multi-platform, Otterly share-of-voice, ZipTie mention+sentiment, LLMrefs keyword mapping).

## What NOT to do (Google's explicit list — hurts both classic and AI search)

1. Write separate content "for AI" (scaled-content-abuse risk).
2. Chunk pages into AI-bait fragments ("don't break your content into tiny pieces").
3. Mass-generate thin variations for ranking manipulation.
4. Pursue inauthentic mentions (fabricated citations, bulk Reddit/Wikipedia spam).
5. Block the search/cite crawlers while wanting citation.
6. Hide main content behind JS that doesn't render — loses both core Search and agents.
7. Skip E-E-A-T fundamentals (author identity, first-hand experience, transparent sourcing).

## Audit checklist for a static site (adds to this skill's existing verification list)

- [ ] Core content present in initial HTML without JS execution
- [ ] robots.txt has an explicit stance on GPTBot / PerplexityBot / ClaudeBot / Google-Extended / Bingbot (and CDN/WAF doesn't challenge them)
- [ ] `llms.txt` at root; consider `/pricing.md` if a product/pricing exists
- [ ] Answer blocks: key claims work standalone, 40–60 word passages, query-phrased H2/H3s
- [ ] Statistics carry sources + dates; named authorship with credentials on substantive pages (E-E-A-T)
- [ ] Freshness signals visible ("Last updated") — and real (see this skill's lastmod rules)
- [ ] No keyword stuffing anywhere (−10% AI visibility, not just classic ineffectiveness)
- [ ] Third-party presence portfolio in place (Wikipedia accuracy, review-site profiles, YouTube text layer for video content)
- [ ] DIY citation check run 3–5x per query with sample sizes recorded; re-run monthly
