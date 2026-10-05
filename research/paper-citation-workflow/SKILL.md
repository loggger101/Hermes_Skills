---
name: paper-citation-workflow
description: "Verify citations via APIs; manage BibTeX for papers."
version: 1.0.0
author: Hermes Agent (promoted from research-paper-writing references, 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [citations, bibtex, semantic-scholar, crossref, openalex, arxiv, hallucination, latex]
    related_skills: [research-paper-writing, ai-research-integrity, grounded-citations, arxiv, literature-review]
---

# Paper citation workflow

## What This Skill Does

A five-step workflow for putting only verified references into a paper's `.bib` file, with the APIs to use, Python code (including a `CitationManager` class), BibTeX management and troubleshooting. The rule: never generate a citation from memory; search, verify in two sources, retrieve the BibTeX, check the claim in the source, then add it.

## When to Use

- Writing or revising a paper's bibliography, especially with AI-drafted text
- Turning a list of titles or DOIs into clean BibTeX
- A reference may be fabricated or its venue, year or authors may be wrong
- Not for the seven-mode pre-submission gate (`ai-research-integrity`), citing sources in non-academic writing (`grounded-citations`), or running a literature review (`literature-review`)

## Quick Reference

| Need | API |
|---|---|
| ML paper search, citation graph | Semantic Scholar (free key about 1 request per second) |
| DOI to BibTeX | Crossref content negotiation (use the polite pool with a contact address) |
| Preprints and PDFs | arXiv API (about 3 seconds between requests) |
| Open bulk data | OpenAlex (about 10 requests per second) |
| Google Scholar | no official API; scraping breaks its terms |

Steps: search, verify in at least two sources, retrieve BibTeX by DOI, validate that the claim appears in the source, add to the `.bib` file. The guide quotes about 40% error in AI-generated citations and over 100 hallucinated citations at NeurIPS 2025; both are upstream figures I did not check.

## Procedure

1. Search with specific keywords; record title, year, DOI or arXiv ID.
2. Confirm the paper in a second source; a DOI plus matching title is the strongest check.
3. Fetch BibTeX by DOI; for arXiv papers use the arXiv ID, since arXiv DOIs are DataCite DOIs that Crossref does not hold.
4. Open the source and confirm it says what you cite it for.
5. Check entry type (`@inproceedings` or `@article`), complete author names, year, venue and a consistent citation key.
6. Cache API results and back off between requests.

## Pitfalls

- A Crossref miss is not proof of fabrication; fall through to arXiv or OpenAlex.
- Unkeyed Semantic Scholar can return 429 on every request; set a key or degrade to Crossref and OpenAlex.
- Encoding errors in BibTeX: escape LaTeX characters and keep the file UTF-8, or use BibLaTeX with Biber.
- Adding BibTeX produced from metadata by hand without recording that it was.

## Verification

- [ ] Each entry was found in at least two sources
- [ ] DOI or arXiv ID verified and BibTeX retrieved, not typed from memory
- [ ] Each load-bearing claim was checked against the source text
- [ ] Entry types, authors, year, venue and keys are consistent

## References

- `references/citation-workflow.md` - why verification matters, API overview and selection, the five-step process, Python implementation, BibTeX management, citation formats, troubleshooting
