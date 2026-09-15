# Programmatic / Generated Pages: Quality Gates (for templated page families)

Source: coreyhaines31/marketingskills `skills/programmatic-seo/` v2.0.0 + quality-check sections (MIT; mined 2026-09-15). Applies to ANY site that generates many pages from a template + data — not just "SEO" sites: aspirecures' weekly research-feed section, portfolio case-study listings, generated API docs per endpoint, dataset catalog pages. The failure mode is the same everywhere: hundreds of near-identical pages that add crawl/UX debt and (for indexed content) risk duplicate-content treatment or manual actions.

## Core principles (in priority order)

1. **Unique value per page.** Every generated page must provide information specific to *that* page, not just swapped variables in a template. The test: if you deleted the variable values, would anything of substance be left? If yes → real content; if no → thin variant.
2. **Data defensibility hierarchy** (strongest first): proprietary data you created > product-derived (from your users) > user-generated/community > licensed with exclusive access > public data anyone can use (weakest — competitors can generate the identical page). For a personal research site, "proprietary" = your own analysis/annotations layered over public sources; that layer is what makes generated pages defensible.
3. **Genuine intent match.** The page must actually answer what someone searching for it wants — generating 10k combinations nobody searches is the most common pSEO failure ("over-generation"). Validate demand (or, for non-SEO sites: validate each combination has a real reader) before generating at scale.
4. **Quality over quantity.** Better to ship 100 great pages than 10,000 thin ones — and it's always legitimate to *not* generate some combinations.

## URL structure rule for generated families

**Subfolders, not subdomains**: `yoursite.com/feed/2026-38` consolidates authority under one domain; `feed.yoursite.com` splits it (and complicates DNS/CSP/deploy). For GitHub Pages-style deploys this is free: everything lives in the same repo and base path.

## Template design that stays unique

Page skeleton: header with the page-specific subject → **unique intro** (generated from data, not a fixed sentence with variables) → data-driven sections (the actual content) → related pages / internal links → CTA or next-step appropriate to intent. Uniqueness mechanisms in order of strength:
- Conditional content based on the underlying data (different section set per page type/value)
- Original analysis/annotation computed for that page (even one sentence of genuine commentary beats ten paragraphs of rephrased boilerplate)
- Per-page unique title + meta description derived from actual page content, not a fixed pattern with variables

## Internal linking: hub-and-spoke

- **Hub**: the main category/index page listing the family. **Spokes**: individual generated pages. Spokes cross-link to related spokes (e.g., adjacent weeks of a feed; related endpoints in docs).
- **No orphan pages** — every generated page reachable from the main site nav or hub, and listed in the XML sitemap with breadcrumbs carrying structured data. Orphan check is mechanical: build the link graph across all HTML files and report zero-inbound nodes (same check as website-audit's cross-page consistency section).
- **Indexation discipline**: prioritize high-value pages for crawl; `noindex` genuinely thin variants rather than publishing them indexable; separate sitemaps per page type so a family problem doesn't drag the rest of the site.

## Pre-launch quality checklist (run before shipping any generated family)

**Content:**
- [ ] Each sampled page provides value specific to it (spot-check 5–10 random pages, not just the first/last)
- [ ] Answers what a reader actually wants from that URL
- [ ] Readable without knowing the generation process exists

**Technical:**
- [ ] Unique `<title>` and meta description per page (verify programmatically — duplicates are trivial to detect: count distinct titles across the family, expect 100%)
- [ ] Proper heading structure (one H1 per page)
- [ ] Schema/structured data where relevant (and remember static-fetch tools can't see JS-injected JSON-LD — see website-audit pitfall #7)
- [ ] Page weight acceptable (generated families multiply whatever each page ships)

**Linking/indexation:**
- [ ] Connected to site architecture via hub; no orphan pages
- [ ] All pages in XML sitemap, crawlable, no conflicting `noindex`/robots rules

## Near-duplicate detection — verified snippet

The mechanical check for "variable-swapped thin content": word-shingle Jaccard similarity between page pairs. **Verified live 2026-09-15** on a 4-page fixture (shared ~70% boilerplate): legitimate siblings scored 0.40–0.43 while the pair differing only in one swapped value scored **0.796** — so `>= 0.8` cleanly separates "template + real content" from "variable swap".

```python
import re, itertools
from collections import Counter

def shingles(text, n=5):
    words = re.findall(r"\w+", text.lower())
    return set(tuple(words[i:i+n]) for i in range(len(words)-n+1)) or {tuple(words)}

def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

# pages: dict url -> visible text (strip <script>/<style> first; keep body copy only)
sh = {u: shingles(t) for u, t in pages.items()}
flagged = [(x, y, jaccard(sh[x], sh[y]))
           for x, y in itertools.combinations(sorted(pages), 2)
           if jaccard(sh[x], sh[y]) >= 0.8]   # near-duplicate pairs -> flag/merge/noindex

# Boilerplate ratio: words appearing in >=95% of the family are template text;
# a page that is >~70% boilerplate is a thin variant candidate for noindex.
cnt = Counter(w for t in pages.values() for w in re.findall(r"\w+", t.lower()))
boiler_words = {w for w, c in cnt.items() if c / len(pages) >= 0.95}
for u, t in pages.items():
    ws = re.findall(r"\w+", t.lower())
    frac = sum(1 for w in ws if w in boiler_words) / len(ws)
    if frac > 0.7:
        print(f"thin-variant candidate ({frac:.0%} boilerplate): {u}")
```

Scaling note: O(n²) pairs is fine up to a few hundred pages (10k pages = ~50M pair checks — still OK in numpy-vectorized form, or cluster by shingle signature first). For feed-style families where *adjacent* entries are the risky comparisons, comparing each page only against its k nearest neighbors cuts cost and matches how thinness actually manifests.

## Common mistakes (flag these as findings)

- **Thin content**: swapping one variable in otherwise identical copy — exactly what the Jaccard check above detects
- **Keyword/term cannibalization**: multiple generated pages targeting the same query/intent with no canonical or differentiation
- **Over-generation**: combinations with zero real demand/readership published anyway
- **Stale data**: generated from a snapshot that's never refreshed — worse than not existing, because it looks authoritative while being wrong (for time-series feeds: state the generation date on every page and expire/supersede old entries explicitly)
- **Pages built for crawlers, not users**: navigation between family members is missing or buried

## Post-launch monitoring (when analytics exists)

Track per family: indexation rate (submitted vs indexed), traffic distribution across pages (healthy = spread; broken = one page hoards everything and the rest are dead weight), engagement, conversion. Watch for thin-content signals, ranking drops on the whole family at once (pattern-level penalty/quality signal), crawl errors from URL-space bloat.
