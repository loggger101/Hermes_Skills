---
name: regex-vs-llm-structured-text
description: "Regex-first parsing; LLM only for flagged edge cases."
version: v0.1.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [parsing, hybrid-pipelines, cost-optimization, confidence-scoring]
    related_skills: [python-data-science]
---

<!-- source: affaan-m/ECC (skills/regex-vs-llm-structured-text), ported 2026-09-09 -->
## When to Use

- Parsing structured text with repeating patterns (questions, forms, tables, invoices).
- Deciding between regex and LLM for text extraction.
- Building hybrid pipelines that combine both approaches.
- Optimizing cost/accuracy tradeoffs in text processing.

**Don't use** for free-form, highly variable prose — go straight to an LLM (or a dedicated parser like `pdfplumber` for PDFs).

## What This Skill Does

Decision framework plus reference implementation: regex handles 95–98% of structured-text cases cheaply and deterministically; reserve expensive LLM calls for the low-confidence remainder. Ships a stdlib-only hybrid pipeline (`scripts/hybrid_parser.py`) with confidence scoring, an injectable LLM validator, and a pytest suite in `tests/`.

## Decision Framework

```
Is the text format consistent and repeating?
+-- Yes (>90% follows a pattern) -> Start with Regex
|   +-- Regex handles 95%+ -> Done, no LLM needed
|   +-- Regex handles <95% -> Add LLM for edge cases only
+-- No (free-form, highly variable) -> Use LLM directly
```

## Architecture Pattern

```
Source Text
    |
[Regex Parser] ---- Extracts structure (95-98% accuracy)
    |
[Text Cleaner] ---- Removes noise (markers, page numbers, artifacts)
    |
[Confidence Scorer] -- Flags low-confidence extractions
    +-- High confidence (>=0.95) -> Direct output
    +-- Low confidence (<0.95)  -> [LLM Validator] -> Output
```

## Reference Implementation

`scripts/hybrid_parser.py` is stdlib-only and dependency-free; the LLM step is an injected callable so any client works:

```python
from hybrid_parser import parse_structured_text, process_document, score_confidence

items = parse_structured_text(content)                 # regex pass only
flags = [score_confidence(i) for i in items]           # confidence audit
final = process_document(                              # full pipeline; llm_validator=None skips LLM
    content,
    llm_validator=lambda item, text: corrected_item,   # your client here
    confidence_threshold=0.95,
)
```

Key design rules (from the production run this came out of):
- **Never mutate** parsed items — cleaning/validation return new instances (`ParsedItem` is frozen).
- Regex pass first even when imperfect: it gives a measurable baseline and flags what needs help.
- Use the cheapest capable model for validation; 500 max tokens is plenty for one item.
- Log pipeline metrics (regex success rate, LLM call count) to track health over time.

Run the suite any time: `python -m pytest tests/` from this skill dir (or let CI's discovery runner find it).

## Real-World Metrics

From a production quiz-parsing pipeline (410 items):

| Metric | Value |
|--------|-------|
| Regex success rate | 98.0% |
| Low-confidence items | 8 (2.0%) |
| LLM calls needed | ~5 |
| Cost savings vs all-LLM | ~95% |
| Test coverage | 93% |

## Best Practices

- **Start with regex** — even imperfect regex gives you a baseline to improve against.
- **Use confidence scoring** to programmatically identify what needs LLM help; don't guess per-item.
- **TDD works well for parsers** — tests for known patterns first, then edge cases (malformed input, missing fields, encoding issues).

## Anti-Patterns

- Sending all text to an LLM when regex handles 95%+ of cases (expensive and slow).
- Using regex for free-form, highly variable text.
- Skipping confidence scoring and hoping regex "just works".
- Mutating parsed objects during cleaning/validation steps.
- Hard-coding one vendor's client API into the pipeline — keep the validator injectable.

## When to Use (concrete)

Quiz/exam question parsing; form data extraction; invoice/receipt processing; document structure parsing (headers, sections, tables); any structured text with repeating patterns where cost matters.
