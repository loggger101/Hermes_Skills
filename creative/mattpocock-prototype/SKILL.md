---
name: mattpocock-prototype
description: "Build a throwaway prototype to answer a design question."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [prototype, design, validation, spike, experimentation]
    related_skills: [sketch, spike]
---

## When to Use

Use when the user wants to explore a design question, validate an approach, test an API integration, or de-risk a technical decision before committing to a full implementation. Also useful when the "right" solution is ambiguous and multiple approaches need empirical comparison.

## What This Skill Does

Creates a minimal, throwaway implementation (a "spike" or "prototype") that answers one specific question: "Does approach X work for use case Y?" The prototype is deliberately minimal — it implements just enough to validate the core assumption, then is discarded.

## Prerequisites

- A clear design question to answer (e.g., "Can Stripe's webhook signature validation work with serverless functions?")
- An idea of what constitutes a "yes" answer (success criteria)
- Basic familiarity with the tools/libraries being tested

## The Process

### 1. Frame the Question
State the design question in one sentence. Define what success looks like.

**Example**: "Can I render 50 disease summaries from arXiv JSON into a paginated React component with search, using only SWR for data fetching and no external state management?"

Success = renders in <500ms, search filters client-side, builds without type errors.

### 2. Choose the Minimal Tech Stack
Use the simplest possible stack that can answer the question. Don't reach for your "production" framework unless the question is framework-specific.

- **Frontend questions**: `html-sketch` or `claude-design` (one-off HTML), `p5js` (interactive), or a minimal React/Vite app
- **Backend questions**: a single Python script, a FastAPI endpoint, or a shell pipeline
- **Data questions**: a Jupyter notebook or a Python script with pandas
- **API questions**: `curl` or `rest-api-client`

### 3. Build the Skeleton
Create only the files needed to test the hypothesis:

```bash
# Minimal example: testing if a PDF extraction approach works
mkdir /tmp/prototype-pdf-extract
cd /tmp/prototype-pdf-extract
python3 -m venv .venv && source .venv/bin/activate
pip install pymupdf  # candidate library
```

Write the absolute minimum code:
```python
# test_extract.py
import fitz
doc = fitz.open("sample.pdf")
text = doc[0].get_text()
print(text[:500])  # does this give us readable text?
```

### 4. Run and Observe
The prototype's only job is to produce a yes/no answer (or a quantitative metric). Don't polish it.

```bash
python test_extract.py
# Output: "This is the first paragraph..." → YES, it works
# Output: garbled text or error → investigate or try alternative
```

### 5. Answer the Question
Write down the answer explicitly. If the answer is "yes, but with caveats," note the caveats. If "no," note why and what the alternative would be.

### 6. Decide: Build or Pivot
- **Yes, proceed**: The prototype validated the approach. Now build it properly (possibly loading `skill_view(name='sketch')` for design or `skill_view(name='spike')` for a more rigorous spike).
- **No, pivot**: The approach doesn't work. Try a different approach or reframe the question.
- **Partially**: The approach works but with significant limitations. Weigh the trade-offs.

## What NOT to Do

- **Don't build the full thing** — a prototype is not a scaled-down product. It's a question with an answer.
- **Don't reuse the prototype code** — prototypes are written for clarity, not production quality. Rewriting is cheaper than refactoring a throwaway.
- **Don't skip the question framing** — building without knowing what "success" looks like produces useless code.
- **Don't over-engineer the prototype's infrastructure** — no CI, no tests, no linting. Just the code that answers the question.

## AspireCURES Context

When evaluating whether a new data source (e.g., ISRCTN, ClinicalTrials.gov) can be integrated into the AspireCURES pipeline, build a throwaway script that fetches one record and attempts to parse it into the standard JSON schema. If the prototype produces a valid record within 30 seconds of code, proceed to full integration. If not, try a different parsing library or API approach.
