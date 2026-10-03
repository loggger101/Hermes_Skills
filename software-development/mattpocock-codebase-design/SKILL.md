---
name: mattpocock-codebase-design
description: "Deep modules: design seams, survey code for shallow ones."
version: 1.2.0
author: Adapted from mattpocock/skills
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [codebase-design, deep-modules, seams, interfaces, leverage, locality, architecture, refactoring, codebase-health, survey]
    related_skills: [mattpocock-tdd, mattpocock-domain-modeling, architecture-metrics]
---

<!-- round-57: mattpocock-improve-codebase-architecture (same source) merged in as survey mode -->

## When to Use

- **Design**: designing or restructuring code modules, asking "where should the seam go", "how deep should this module be", or "what should the interface expose"; refactoring shallow modules into deeper ones.
- **Survey**: run periodically (every few days) when asking "is this module too shallow?", "where should I refactor next?", or "is the codebase accumulating mud?" — and after `skill_view(name='mattpocock-domain-modeling')` when domain terms have shifted.

For a measured answer instead of a reading survey (dependency levels, blast radius, a quality score), load `skill_view(name='architecture-metrics')`; this skill turns what it finds into a better module.

## What This Skill Does

Designs **deep modules**: a lot of behavior behind a small interface. Uses a shared glossary (module, interface, implementation, adapter, seam, leverage, locality) so discussions about architecture are precise and unambiguous. In survey mode it scans an existing codebase for modules that are too shallow, scores the candidates, and refactors the one the user picks.

## Glossary

Use these terms **exactly**:

| Term | Meaning | Example |
|---|---|---|
| **Module** | Interface + implementation | `class ArxivParser` |
| **Interface** | Everything a caller must know | Public method signatures, return types |
| **Implementation** | What's inside | Private helper methods, internal data structures |
| **Adapter** | Concrete thing satisfying an interface | `ArxivXmlParser implements Parser` |
| **Seam** | Place where you can alter behavior without editing there | `Parser` interface (test with mock, prod with real) |
| **Leverage** | What callers get from depth | Fewer dependencies, simpler call sites |
| **Locality** | What maintainers get from depth | Changes in one place, no ripple effects |

## Deep vs Shallow

```text
Shallow Module (BAD):
  Interface: parse_a(), parse_b(), parse_c(), validate_a(), validate_b(), clean_x(), clean_y()
  Implementation: 50 lines of duplicated parsing logic
  Problem: caller knows 8 methods, can't refactor internals safely

Deep Module (GOOD):
  Interface: parse(xml_string) → dict
  Implementation: 200 lines of sophisticated XML parsing, validation, and cleaning
  Benefit: caller knows 1 method, internals can change freely
```

### The Deletion Test

Delete the module entirely. If complexity vanishes, it was a pass-through (shallow). If complexity migrates to callers, it was doing real work (deep).

### The Leverage Checklist

- Does the interface expose **one concept** or many? (one = deep)
- Does deleting the module force callers to duplicate its logic? (yes = deep)
- Can you rename an internal variable without callers noticing? (yes = deep seam)
- Is the interface name longer than the implementation? (maybe = shallow)

## Design Mode

### 1. Start with the interface

Design the smallest possible interface that lets the caller achieve their goal. Write it before the implementation:

```python
class DiseasePageRenderer:
    def render(self, disease_data: dict) -> str:
        """Render a single disease page to HTML. Returns complete HTML string."""
        ...
```

### 2. Place the seam at the boundary

The public method signature IS your seam. Everything else is implementation detail:

```python
# Public seam (tested)
def render(self, disease_data: dict) -> str:
    validated = self._validate(disease_data)
    html = self._render_template(validated)
    return self._optimize(html)

# Private implementation (not directly tested)
def _validate(self, data): ...
def _render_template(self, data): ...
def _optimize(self, html): ...
```

### 3. Push complexity inside

Move as much logic as possible behind the seam. If a caller needs to know about caching, pagination, or retry logic — that's a sign the module is too shallow.

```python
# BAD: caller must know about retry logic
result = retry(3, lambda: api.call(page=1))

# GOOD: retry is internal to the module
result = api.fetch_all()  # handles retries, pagination internally
```

## Survey Mode

Scan a codebase for **deepening opportunities** and present candidates for refactoring.

### What it looks for

| Anti-pattern | What It Means | Fix |
|---|---|---|
| **Shallow** | Large interface, little implementation | Collapse multiple methods into one deep module with a smaller interface |
| **Leaking** | Implementation concerns bleeding through the interface | Hide internals behind the seams; expose only stable abstractions |
| **Mis-seamed** | Interface exposes internals | Redesign the interface so callers don't need to know about internal structure |
| **Duplicated** | Same logic across multiple modules | Extract to a shared deep module |
| **Misnamed** | Names don't reveal what the module does | Rename to match the actual responsibility |

Prerequisites: a codebase with modules/classes/functions that have public interfaces, and the glossary above. No special tools required.

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

### 2. Score each candidate

Score on three axes (1-5 scale):

| Metric | Score 1 (low) | Score 3 (medium) | Score 5 (high) |
|--------|--------------|------------------|----------------|
| **Impact** — how much the fix improves the codebase | Minor cleanup | Improves multiple callers | Fixes a core abstraction used everywhere |
| **Effort** — how hard the fix is | Hours | Days | Weeks |
| **Risk** — how likely the fix breaks things | No callers affected | Some callers need updating | Many callers or critical path |

**Prioritization**: High Impact + Low Effort + Low Risk = do first.

### 3. Present candidates

Present candidates ranked by impact/effort/risk. Then implement whichever one the user picks.

### 4. Implement the fix

For a shallow module (this is Design Mode applied to existing code):

1. Identify the one concept it abstracts (collapse multiple methods into one purpose)
2. Design a new interface with 1-2 public methods (down from 5+)
3. Move all current logic behind the seam
4. Update all callers to use the new interface
5. Run tests to verify behavior is preserved

### 5. Verify

Run the deletion test: if removing this module doesn't reduce complexity elsewhere, it's still too shallow.

## Common Module Shapes

| Shape | Purpose | Example |
|-------|---------|---------|
| **Facade** | Collapse multiple sub-systems into one interface | `PipelineRunner` wrapping fetch, gate, render |
| **Gateway** | External system boundary with retry/circuit-breaker | `ArxivApi` with exponential backoff |
| **Service** | Business logic orchestration | `DiseasePageService` coordinating 9 pages |
| **Repository** | Data persistence abstraction | `SqliteStorage` abstracting SQLite |
| **Adapter** | Convert between incompatible interfaces | `XmlToJsonAdapter` |

## Pitfalls

- **Leaking concerns** — If callers must know about caching, retries, or validation, the module is too shallow
- **Naming the implementation** — Interface names should describe the concept, not the mechanism
- **Premature abstraction** — Don't extract a shared module until 3+ use sites share the same pattern
- **False depth** — Moving code into a private method doesn't make the module deeper; the interface must shrink
- **Chasing metrics** — a module with 20 methods might be legitimate; focus on whether the interface reveals too much, not on line counts
- **Breaking callers** — always score risk high when many callers depend on the current interface
- **Shallow renaming** — renaming a module without actually changing its structure doesn't help

## Verification

- [ ] The interface exposes one concept, and callers need no internal details
- [ ] The deletion test passes (removing the module relocates complexity)
- [ ] Survey mode: each candidate was scored on impact/effort/risk
- [ ] Survey mode: the chosen candidate was implemented and callers updated
- [ ] Tests pass after refactoring

## AspireCURES Context

When refactoring data-source parsers, the gating engine, or the disease-page renderer, apply this vocabulary. Ask: "Is this module deep? Does it have leverage? Does the deletion test pass?" Run a survey on the pipeline repo periodically; candidates include the data-source parser layer, the gating engine, the disease-page renderer, and the preparer→executor handoff protocol.

For the preparer agent: the Arxiv API client should be a deep module that handles pagination, retries, and XML parsing internally with a single `fetch(query) -> results` interface. If each API query, XML parse, and field extraction is a separate function, the module is shallow. For the executor agent: the disease-page renderer should abstract away template compilation, asset loading, and HTML optimization behind one `render(disease_data)` call.
