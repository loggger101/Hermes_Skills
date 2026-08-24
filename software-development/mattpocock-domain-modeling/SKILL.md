---
name: mattpocock-domain-modeling
description: "Sharpen domain terms and update CONTEXT.md and ADRs inline."
version: 1.1.0
author: Adapted from mattpocock/skills
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [domain-modeling, context-md, adrs, glossary, terminology]
    related_skills: [mattpocock-improve-codebase-architecture, mattpocock-writing-for-agents]
---

## When to Use

Use when actively changing a project's domain model, not just consuming it — i.e. when introducing new terms, deciding between competing concepts, or documenting hard-to-explain decisions.

## What This Skill Does

Actively builds and sharpens the project's domain model: maintains a `CONTEXT.md` glossary, writes ADRs (Architecture Decision Records) for key decisions, and stress-tests terms against edge cases throughout the session.

## File Structure

```
/
├── CONTEXT.md          # Glossary — every term → definition
├── docs/
│   └── adr/
│       ├── 0001-some-decision.md
│       └── 0002-another-decision.md
└── src/
```

## The Process

### 1. Read the existing glossary first
Before introducing any term, check `CONTEXT.md`. Terms should be:
- **Precise** — one clear definition, no overlap with other terms
- **Domain-first** — defined in the project's language, not technical jargon
- **Actionable** — usable in conversation and code names

### 2. Add/Sharpen terms as you work
`CONTEXT.md` is a **glossary** and nothing else. Each entry: `term` → `definition in domain language`.

**Good entry:**
```
| Term | Definition |
|------|-----------|
| disease profile | A compiled summary of research findings for one rare brain disease, rendered into a single webpage |
```

**Bad entry (too vague):**
```
| Thing | Something we work with |
```

**Bad entry (technical, not domain):**
```
| Parser | Class that parses XML |
```

### 3. Stress-test with edge cases
For each term, ask:
- **Simplest valid example** — what's the minimal case where this term applies?
- **Edge case** — what scenario breaks the assumption?
- **Conflict** — does this term overlap with another? If so, which wins?

Write these down. They become test cases.

### 4. Write ADRs for decisions
When a design decision crystallizes, capture it as an ADR in `docs/adr/`.

**ADR format:**
```markdown
# 0003-{decision-topic}

## Status
Accepted (date)

## Context
What decision point are we at? What options exist?

## Decision
What we chose and why.

## Consequences
What becomes easier/harder. Include AspireCURES-specific impacts.
```

### 5. Challenge every new term against the glossary
**Every new term** → check `CONTEXT.md`. Add if missing, sharpen if vague, reconcile overlaps. If you can't define it in one sentence, you don't understand it well enough yet.

## ADR Lifecycle

| Stage | What to do |
|-------|-----------|
| **Proposed** | Decision made but not yet implemented |
| **Accepted** | Implemented and agreed |
| **Superseded** | Replaced by a later ADR |
| **Deprecated** | No longer relevant |

Only write an ADR when the decision is real (affects code, tests, or data flow) and non-obvious. Don't write ADRs for trivial choices.

## Common Pitfalls

- **Premature glossary** — defining terms before they're used in at least 2 places
- **Tautological definitions** — \"A parser is something that parses\" tells you nothing
- **Overlapping terms** — \"disease profile\" vs \"disease page\" vs \"disease entry\" — pick one and alias the rest
- **Forgotten ADRs** — if you change a decision, update the ADR's status or write a superseding one
- **Glossary drift** — terms used in code diverge from `CONTEXT.md` definitions

## AspireCURES Context

Your domain has rich terminology: \"materialization cascade\", \"disease profile\", \"gating\", \"preparer → executor\", \"Claude gatekeeper\", \"patient matching\". This skill helps you sharpen these terms and capture decisions as ADRs. Essential when adding new disease pages or refactoring the pipeline.

For the cronjob preparer agent: every new data source integration should add terms to `CONTEXT.md` — e.g., \"materialization depth\", \"confidence score\", \"source priority\". For the executor agent: each disease-page rendering change that alters behavior should get an ADR documenting the before/after and why.
