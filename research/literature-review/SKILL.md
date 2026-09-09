---
name: literature-review
description: "Plan, screen, synthesize and cite technical literature."
version: v0.1.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [literature-review, systematic-research, citation-verification, evidence-synthesis]
    related_skills: [arxiv, mattpocock-research, grounded-citations]
---

<!-- source: affaan-m/ECC (skills/scientific-thinking-literature-review), ported 2026-09-09 -->
## When to Use

- Building a systematic, scoping, or narrative literature review.
- Synthesizing the state of the art for a research question.
- Finding gaps, contradictions, or future-work directions.
- Preparing citation-backed background sections for papers or reports (see `grounded-citations`).
- Comparing evidence across peer-reviewed papers, preprints, patents, and technical reports (`arxiv` skill covers the CS/physics/preprint side).

## What This Skill Does

A systematic literature-review workflow: define a searchable question, write the search protocol BEFORE collecting sources, log every query for reproducibility, deduplicate in a fixed ID order, screen in stages with recorded exclusion reasons, extract into structured tables, synthesize by theme (not paper-by-paper), and verify every citation before finalizing.

## Review Types

- **Narrative review** — broad synthesis; useful for orientation.
- **Scoping review** — maps concepts, methods, and evidence gaps.
- **Systematic review** — predefined protocol, reproducible search, explicit screening and exclusion.
- **Meta-analysis** — systematic review plus quantitative effect aggregation.

Ask the user which level of rigor is needed. If unspecified: scoping for exploratory work; systematic for publication or clinical claims.

## Workflow

### 1. Define the Question

Convert the prompt into a searchable research question. Clinical/biomedical: PICO (Population, Intervention/exposure, Comparator, Outcome). Technical: system/domain + method/intervention + comparison baseline + evaluation metric.

### 2. Plan the Search

Create the search protocol before collecting sources — databases, date range, languages, publication types, inclusion criteria, exclusion criteria, exact search strings. Minimum useful database set:
- PubMed for biomedical and life-sciences literature.
- arXiv for CS, math, physics, quantitative biology, preprints (see `arxiv`).
- Semantic Scholar or Crossref for broad academic discovery.
- Domain-specific sources when relevant: clinical-trial registries, patent databases, standards bodies, official technical docs.

### 3. Search and Log Evidence

Keep a search log that makes the review reproducible:

```markdown
| Database | Date searched | Query | Filters | Results | Export |
| --- | --- | --- | --- | ---: | --- |
| PubMed | 2026-05-11 | `("CRISPR"[tiab] OR "Cas9"[tiab]) AND "sickle cell"[tiab]` | 2020:2026, English | 86 | PMID list |
| arXiv | 2026-05-11 | `CRISPR sickle cell gene editing` | q-bio, 2020:2026 | 9 | BibTeX |
```

Save raw IDs, URLs, DOIs, abstracts, and notes separately from the final prose.

### 4. Deduplicate

In this order: DOI -> PMID or arXiv ID -> exact title -> normalized title + first author + year. Record how many duplicates were removed.

### 5. Screen Sources

Screen in stages: title -> abstract -> full text. For systematic work, record exclusion reasons (wrong population / intervention / outcome; not primary research; duplicate; unavailable full text; outside date range).

### 6. Extract Data

Structured extraction table:

```markdown
| Study | Design | Population/Data | Method | Comparator | Outcome | Key finding | Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Author Year | RCT/cohort/review/etc. | sample or corpus | method | baseline | measured outcome | result | caveat |
```

For technical papers, include dataset, benchmark, metric, baseline, and reproducibility notes.

### 7. Synthesize

Group evidence by theme rather than summarizing papers one by one. Lenses: strongest evidence; conflicting evidence; methodological weaknesses; population/dataset limits; recency and replication; practical implications; unanswered questions. Separate claims by confidence — **High** (replicated, high-quality across sources), **Medium** (plausible but limited by sample/method/recency), **Low** (early, speculative, single-source, weakly measured).

### 8. Verify Citations

Before finalizing: verify DOI/PMID/arXiv ID or official URL; check author names and year; do not cite a paper for a claim it does not make; mark preprints as preprints; distinguish reviews from primary evidence.

## Output Template

```markdown
# Literature Review: <Topic>

Generated: <date>
Review type: <narrative | scoping | systematic | meta-analysis>
Search window: <dates>
Databases: <list>

## Research Question
## Search Strategy
## Inclusion and Exclusion Criteria
## Evidence Summary
## Thematic Synthesis
## Gaps and Limitations
## References
## Search Log
```

## Pitfalls

- Do not treat search snippets as evidence.
- Do not mix preprints, reviews, and primary studies without labeling them.
- Do not omit negative or conflicting findings.
- Do not claim systematic-review rigor without a reproducible protocol.
- Do not use a single database for a broad claim unless the scope is explicitly limited to that database.
