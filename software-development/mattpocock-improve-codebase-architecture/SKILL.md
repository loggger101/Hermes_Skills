---
name: mattpocock-improve-codebase-architecture
description: "Survey code for module deepening opportunities and fix them."
version: 1.1.0
author: Adapted from mattpocock/skills
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [architecture, deep-modules, refactoring, codebase-health, survey]
    related_skills: [mattpocock-codebase-design, mattpocock-domain-modeling]

---

## When to Use

Run periodically (every few days) when asking "is this module too shallow?", "where should I refactor next?", or "is the codebase accumulating mud?". Also use after loading `skill_view(name='mattpocock-codebase-design')` to apply deep-module principles, or after `skill_view(name='mattpocock-domain-modeling')` when domain terms have shifted.

# Improve Codebase Architecture (mattpocock)

Scan a codebase for **deepening opportunities** and present candidates for refactoring.

## What This Skill Does

Surveys the codebase for modules that are too shallow (large interface, little implementation) and presents prioritized refactoring candidates. Uses the deep-module vocabulary from `skill_view(name='mattpocock-codebase-design')` to identify where complexity should be moved behind smaller interfaces.

## What It Looks For

| Anti-pattern | What It Means | Fix |
|---|---|---|
| **Shallow** | Large interface, little implementation | Collapse multiple methods into one deep module with a smaller interface |
| **Leaking** | Implementation concerns bleeding through the interface | Hide internals behind the seams; expose only stable abstractions |
| **Mis-seamed** | Interface exposes internals | Redesign the interface so callers don't need to know about internal structure |
| **Duplicated** | Same logic across multiple modules | Extract to a shared deep module |
| **Misnamed** | Names don't reveal what the module does | Rename to match the actual responsibility |

## Prerequisites

- Codebase with modules/classes/functions that have public interfaces
- Ability to read and understand the code (no special tools required)
- Familiarity with the glossary terms from `skill_view(name='mattpocock-codebase-design')`

## Process

### 1. Survey the codebase
Read each module at its interface. Ask:
- Does this interface expose more than it should?
- Does deleting this module remove or relocate its complexity? (the deletion test)
- Is the seam clean?
- Is behavior well-distributed or scattered?

For each module, write down:
- **Interface surface**: number of public methods, arguments each takes
- **Implementation depth**: lines of code inside the module
- **Callers**: how many places use this module, and for what purpose

### 2. Apply the scoring rubric

For each candidate module, score on three axes (1-5 scale):

| Metric | Score 1 (low) | Score 3 (medium) | Score 5 (high) |
|--------|--------------|------------------|----------------|
| **Impact** | Minor cleanup | Improves multiple callers | Fixes a core abstraction |
| **Effort** | Hours | Days | Weeks |
| **Risk** | No callers affected | Some callers need updating | Many callers or critical path |

**Prioritization**: High Impact + Low Effort + Low Risk = do first.

### 3. Score each candidate
- **Impact**: how much does fixing this improve the codebase? (5 = core abstraction used everywhere)
- **Effort**: how hard is the fix? (5 = weeks of work)
- **Risk**: how likely is the fix to break things? (5 = many callers or critical path)

### 4. Present candidates
Present candidates ranked by impact/effort/risk. Then implement whichever one the user picks.

### 5. Implement the fix
For a shallow module:
1. Identify the one concept it abstracts (collapse multiple methods into one purpose)
2. Design a new interface with 1-2 public methods (down from 5+)
3. Move all current logic behind the seam
4. Update all callers to use the new interface
5. Run tests to verify behavior is preserved

### 6. Verify
Run the deletion test: if removing this module doesn't reduce complexity elsewhere, it's still too shallow.

## Pitfalls

- **Chasing metrics** — a module with 20 methods might be legitimate; focus on whether the interface reveals too much, not on line counts
- **Premature extraction** — don't extract a shared module until 3+ modules share the same pattern
- **Breaking callers** — always score risk high when many callers depend on the current interface
- **Forgetting the seam** — after refactoring, verify that internal changes don't affect callers
- **Shallow renaming** — renaming a module without actually changing its structure doesn't help

## Verification

- [ ] Each candidate was scored on impact/effort/risk
- [ ] The highest-priority candidate was implemented and callers updated
- [ ] Tests pass after refactoring
- [ ] The deletion test passes (removing the module relocates complexity)
- [ ] No caller needs to know about internal implementation details

## AspireCURES Context

Run on your pipeline repo periodically. Candidates might include: the data-source parser layer, the gating engine, the disease-page renderer, the preparer→executor handoff protocol.

For the Arxiv parser: if each API query, XML parse, and field extraction is a separate function, the module is shallow — wrap it in a single `fetch_and_parse(query) -> results` interface. For the disease-page renderer: if HTML generation, asset loading, and HTML optimization are exposed separately, collapse them into one `render_disease_page(disease_data) -> html` call.
