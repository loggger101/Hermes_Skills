---
description: "Seven failure modes of AI-assisted research (buggy code, fake citations, invented results, shortcuts, bug-as-insight, fabricated methods, frame-lock) as a pre-submission gate; plus live citation-API checks"
source_repo: Imbad0202/academic-research-skills (licence listed by GitHub as 'Other'; checklist paraphrased, not copied)
tested_version: "Checklist source-read from academic-pipeline/references/ai_research_failure_modes.md and deep-research/references/{crossref,openalex,semantic_scholar}_api_protocol.md. API behaviour run on 2026-10-05 from Windows with a ~60-line stdlib script against Crossref, OpenAlex and Semantic Scholar (no key, no contact email sent)"
verified_date: "2026-10-05"
---

# Integrity gate for AI-assisted research

`paper-citation-workflow` handles fabricated references. The harder failures are the ones that read like competent work.
Imbad0202's pipeline turns the Limitations section of Lu et al., *Towards end-to-end automation of AI research*
(Nature 651, 914-919, 2026) into a seven-item gate run before review and again before finalising. That paper's DOI,
`10.1038/s41586-026-10265-5`, was checked live: Crossref returns `journal-article` with the exact title.

## The seven modes (what to rule out, and the question to ask)

| # | Mode | What it looks like | Ask |
|---|---|---|---|
| 1 | Implementation bug passes self-review | plausible number from code with a silent error | Is there a saved log or script run for every number, exit code 0, no warnings? Suspiciously round effect sizes, or identical error bars across conditions? |
| 2 | Hallucinated citation | reference missing, wrong year/venue/authors, or does not say what is claimed | Resolve every DOI and compare title (see below); open the source for each load-bearing claim |
| 3 | Hallucinated experimental result | "12% improvement" that no run produced | Do the raw numbers behind each headline figure exist? Does the table match a saved CSV/run? Does "N seeds" match the run directories? |
| 4 | Shortcut reliance | real number, wrong reason (a spurious feature) | Is there an ablation removing the obvious shortcut? Does the ablation hit the claimed mechanism or only hyperparameters? Is the baseline strong enough? |
| 5 | Bug reframed as insight | an odd result narrated as a discovery | Every "surprisingly/unexpectedly": does literature predict the opposite? Did it appear on the first run? Reproduced from scratch in a fresh environment? |
| 6 | Methodology fabrication | Methods text describes a plausible experiment that is not the one that ran | Does each number in Methods (lr, batch, epochs, split, sizes) appear in the real run config? Any preprocessing step you cannot point to in code? |
| 7 | Frame-lock | an early framing that later stages could not back out of | Would you change the question or method knowing what you know now? "In hindsight" / "we realised later" in the Discussion is a tell |

Outcome per mode: **CLEAR** (with evidence), **SUSPECTED**, **INSUFFICIENT EVIDENCE**, or **NOT APPLICABLE** (modes 1, 3, 5, 6
only, when the author declares there were no experiments or analyses). Gate rule from the source: block if any mode is
SUSPECTED (mode 4 is flag-only at the first gate and blocks at the final one), and also block when modes 1, 3, 5 or 6
are INSUFFICIENT EVIDENCE, because they cannot be ruled out without the user's logs and configs. Modes 2, 4, 7 may proceed
with a warning and are re-checked. Anything SUSPECTED earlier must be CLEAR, NOT APPLICABLE or explicitly overridden with
written reasoning before the final gate; keep an audit log of the history.

Practical use: demand the **run config and logs as inputs** to the check, not only the manuscript text. Modes 1, 3, 5, 6 are
checks of paper against artefacts; a reader of the paper alone cannot catch them.

## Citation checks run live (title similarity >= 0.70, DOI cross-check)

The source protocol: look the DOI up, compare the returned title with the cited title (Levenshtein ratio >= 0.70); a hit
with a low ratio is `DOI_MISMATCH` (a fabricated DOI resolving to an unrelated paper); no DOI means title search; no index
match is "not found", which is **not** proof of fabrication. Results of that procedure on five planted inputs:

| Input | Crossref DOI | Crossref title search | OpenAlex title search |
|---|---|---|---|
| Real DOI + real title (Lu 2026) | MATCH, sim 1.00 | MATCH 1.00 | MATCH 1.00 |
| Real DOI `10.1038/nature14539` + wrong title | **DOI_MISMATCH**, sim 0.17 (record is "Deep learning") | (title search finds the Lu paper) | same |
| Fabricated DOI `10.1234/fake...` + plausible title | 404 | NOT_FOUND, best sim 0.54 | NOT_FOUND, 0 results |
| Real paper, arXiv DOI `10.48550/arXiv.1706.03762` | **404** | MATCH 1.00, but returned a *different* DOI (`10.65215/...`) than the canonical one | MATCH |
| Real title with typos ("Atention is all you nede") | n/a | NOT_FOUND, best sim 0.33 | NOT_FOUND, 0 results |

Lessons:

- The **DOI-plus-title cross-check works**: it is the only row that catches a real DOI attached to the wrong paper.
- **A Crossref 404 does not mean fabricated.** arXiv DOIs are DataCite DOIs; Crossref does not hold them. Resolve those
  through `doi.org`/DataCite or the arXiv ID, and treat a Crossref miss as "fall through", as the source does.
- **A title-only match is not the same work.** The exact title matched a record with a different DOI; require year or
  author agreement, and prefer the DOI you were given.
- Typos fail at **retrieval**, before any similarity threshold is applied. A mangled title returning nothing is a weak
  signal either way: retry with a key phrase or the author's surname.
- Anonymous rate limits seen in headers: Crossref `x-rate-limit-limit: 5`, interval `1s` (the source quotes 10 req/s for the
  polite pool with a contact address in the User-Agent; this run sent none, so only the anonymous figure was observed).
- **Semantic Scholar without an API key returned HTTP 429 on every request**, including after 15 s and 30 s waits. The
  source says to degrade gracefully and never block the pipeline on it; do that, and set `S2_API_KEY` when you need the
  tier. Crossref + OpenAlex were enough for all five planted cases.
- Crossref `GET /works/{doi}` carries `updated-by` metadata (retractions and corrections); the real DOI checked had none.
  Read it for any reference you rely on heavily.

Not run: the source's own client scripts, PDF/claim-alignment audits, plagiarism checks, or the rest of its 7-stage
pipeline; no model-judged review panel was exercised.
