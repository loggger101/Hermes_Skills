---
name: ai-search-optimization
description: "Get cited by AI search; agent-ready sites (AEO/GEO)."
version: 1.0.0
author: Hermes Agent (promoted from static-site-seo references; coreyhaines31/marketingskills ai-seo v2.5.0, MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [aeo, geo, ai-search, llms-txt, agent-readiness, citations, robots-txt, seo, markdown]
    related_skills: [static-site-seo, static-site-patterns, website-audit, publish-site, grounded-citations]
---

# AI search optimization (AEO/GEO) and agent-ready sites

## What This Skill Does

Traditional SEO gets a page **ranked**; AI search gets it **cited**. This skill covers the layer on top of classic SEO: how to make content extractable and citable, how to be present where AI systems look, whether agents can reach, navigate and parse a site, machine-readable files (`llms.txt`, `/pricing.md`), and how to monitor AI visibility honestly. Classic fundamentals (titles, canonicals, JSON-LD, sitemaps) stay in `static-site-seo`.

## When to Use

- A site should be cited by ChatGPT, Perplexity, Claude, Copilot or Google AI features, or used by autonomous agents
- Auditing agent readiness, `robots.txt` crawler stance, or `llms.txt`
- Deciding whether to build listicle or comparison pages for citations
- Not for classic ranking work (`static-site-seo`), site structure and performance (`static-site-patterns`), or sourcing claims in your own writing (`grounded-citations`)

## Google versus the other engines

Google's official guidance: no special markup or files are required for AI Overviews and AI Mode (they run on core Search ranking), do not chunk content for AI, do not write separate "for AI" variants (scaled content abuse), and there is no AI-specific Search Console report. Other engines (ChatGPT search, Perplexity, Claude/Brave, Copilot) reward extractable structure and may read `llms.txt`. Practical split: for Google optimise for people and core Search; for the others layer extractable structure and machine-readable files on top, which is also ordinary good organisation. Google's AI features run related queries concurrently (query fan-out), so cover the whole topic rather than one page per keyword.

## The three pillars

1. **Structure**: AI systems extract passages, not pages. Make claims standalone: definition blocks, step lists, comparison tables, FAQs, 40 to 60 word answer blocks, query-phrased H2/H3s.
2. **Authority**: the Princeton GEO study ranked levers: cite sources +40%, add statistics +37%, expert quotations +30%, authoritative tone +25%; keyword stuffing is -10%. Name authors with credentials and date statistics.
3. **Presence**: third-party surfaces out-cite your own site (Wikipedia, review sites, YouTube where the model reads the transcript, captions and description, podcasts with transcripts). Treat it as a portfolio: citation mixes shift overnight (a 2026-08 model update cut listicle citations by about half and comparison pages by about a third), so owned-site fundamentals are the hedge and every citation statistic is a dated snapshot.

Citation is not recommendation: the ladder is retrieved, cited, mentioned, recommended, and the last step is driven by web-wide consensus. Self-promotional listicles can backfire.

## Agent readiness: access, discovery, parseability

- **Access**: core content in the initial HTML (most agents do not run JavaScript); no WAF or bot challenge on GPTBot, PerplexityBot or ClaudeBot (many sites block them by default without anyone deciding); real status codes and stable canonicals.
- **Discovery**: `robots.txt` with an explicit stance on GPTBot and ChatGPT-User, PerplexityBot, ClaudeBot and anthropic-ai, Google-Extended and Bingbot (blocking a search or cite bot means that platform cannot cite you; blocking training-only crawlers like CCBot is the middle ground), a clean sitemap, `llms.txt` at the root and optionally `llms-full.txt`.
- **Parseability**: valid JSON-LD, a Markdown representation of each page (content negotiation with `Accept: text/markdown` and `Vary`, or an HTTP `Link` header to a parallel `.md`), one H1 and headings that answer sub-questions.
- **For agent buyers**: a `/pricing.md` with structured tiers, units and limits, kept current (stale is worse than absent). Emerging and unproven as a signal: WebMCP (pages declare forms as callable tools) and UCP.
- Score before and after with the free checkers (Is Agentic via `npx is-agentic <domain>`, Frase Agent Readiness Checker); the failed checks are the worklist.

## Procedure

1. Run an agent-readiness checker and fix access problems first (HTML content, WAF, status codes).
2. Set an explicit `robots.txt` stance per AI crawler; add `llms.txt` (and `/pricing.md` if a product exists).
3. Rewrite key pages into standalone answer blocks with sourced, dated statistics and named authors; keep freshness signals real.
4. Build a third-party presence portfolio rather than concentrating on one surface.
5. Monitor monthly without tools: top 20 queries, each run 3 to 5 times per platform, record cited or not, by whom and which page, and report rates with sample sizes. AI answers are non-deterministic; one run is an anecdote.

## Pitfalls (Google's explicit list)

- Separate content "for AI", AI-bait fragments, mass-generated thin variations, fabricated or bulk citations.
- Blocking the crawlers you want citations from.
- Hiding main content behind JavaScript that does not render.
- Skipping author identity, first-hand experience and transparent sourcing.
- Betting on a citation-share statistic without checking your own monitoring.

## Verification

- [ ] Core content is in the initial HTML without JavaScript
- [ ] `robots.txt` has an explicit AI-crawler stance and the CDN or WAF does not challenge those bots
- [ ] `llms.txt` exists at the root; `/pricing.md` if applicable
- [ ] Claims are standalone, statistics carry sources and dates, authors are named
- [ ] A citation check was run 3 to 5 times per query with sample sizes recorded

## References

- `references/agent-ready-and-ai-search.md` - the full guide: core distinction, Google's stance, query fan-out, three pillars, citation-source volatility, citation vs recommendation, agent readiness, machine-readable files, WebMCP and UCP, DIY monitoring, the do-not list and an audit checklist
