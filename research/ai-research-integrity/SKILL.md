---
name: ai-research-integrity
description: "Seven-mode integrity gate for AI-assisted research."
version: 1.0.0
author: Hermes Agent (promoted from research-paper-writing references, 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [research-integrity, hallucinated-citations, pre-submission, crossref, openalex, reproducibility]
    related_skills: [research-paper-writing, grounded-citations, human-evaluation-design, autoreason-refinement, scholar-evaluation]
---

# AI research integrity gate

## What This Skill Does

A pre-submission gate for work an AI helped produce, built on seven failure modes that read like competent work: a bug that passes self-review, a hallucinated citation, an invented result, shortcut reliance, a bug narrated as insight, a fabricated method and frame-lock. It also holds the citation-API check (DOI plus title similarity) with the behaviour seen when it was run against Crossref and OpenAlex. Checklist paraphrased from Imbad0202/academic-research-skills.

## When to Use

- Before submitting or sharing a paper, report or analysis whose code or text an AI helped write
- Reviewing a draft whose headline number has no saved run behind it
- Verifying that references exist and say what the draft claims
- Not for citation formatting and bibliography management (`research-paper-writing`, `grounded-citations`) or for judging a finished paper's quality (`scholar-evaluation`)

## Quick Reference

| # | Mode | Ask |
|---|---|---|
| 1 | Implementation bug passes self-review | is there a saved log and exit code 0 for every number? suspiciously round effects or identical error bars? |
| 2 | Hallucinated citation | does each DOI resolve to the cited title, and does the source say what is claimed? |
| 3 | Hallucinated result | do the raw numbers behind each headline figure exist, and does "N seeds" match the run directories? |
| 4 | Shortcut reliance | is there an ablation of the obvious shortcut, and does it hit the claimed mechanism? |
| 5 | Bug reframed as insight | does every "surprisingly" survive a from-scratch rerun and a literature check? |
| 6 | Methodology fabrication | does each number in Methods appear in the real run config? |
| 7 | Frame-lock | would you change the question knowing what you know now? |

Outcome per mode: CLEAR (with evidence), SUSPECTED, INSUFFICIENT EVIDENCE, NOT APPLICABLE. Block on any SUSPECTED, and also on INSUFFICIENT EVIDENCE for modes 1, 3, 5 and 6, which cannot be ruled out without the author's logs and configs.

## Procedure

1. Collect the artefacts: manuscript, run configs, logs and raw result files. Modes 1, 3, 5 and 6 compare paper against artefacts; the text alone cannot catch them.
2. Score each mode with its question and record the evidence; keep an audit log across the first and final gates.
3. Check every reference: look up the DOI, compare the returned title to the cited one (similarity of at least 0.70), fall back to a title search when no DOI exists, and open the source for each load-bearing claim.
4. Treat "not found" as unresolved, not as fabricated, and retry with a key phrase or an author name.
5. Resolve everything SUSPECTED to CLEAR or an explicit written override before the final gate.

## Pitfalls

- A Crossref 404 on an arXiv DOI: those are DataCite DOIs; resolve through `doi.org` or the arXiv ID.
- Accepting a title-only match; the same title returned a record with a different DOI, so require year or author agreement.
- Typos in a title fail at retrieval, before any similarity threshold applies.
- Unkeyed Semantic Scholar returned HTTP 429 on every request in the test; degrade gracefully and rely on Crossref plus OpenAlex.
- Reading a clean result as proof for modes that need logs the author has not supplied.

## Verification

- [ ] Each of the seven modes has an outcome and evidence
- [ ] Every reference was resolved or listed as unresolved with a reason
- [ ] Every headline number traces to a saved run
- [ ] Methods numbers match the run config
- [ ] The audit log records any override and its reason

## References

- `references/ai-research-integrity-checklist.md` - the seven modes with questions and gate rules, plus live Crossref/OpenAlex results on five planted citation inputs
