---
name: mattpocock-codebase-design
description: "Design deep modules with small interfaces."
version: 1.1.0
author: Adapted from mattpocock/skills
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [codebase-design, deep-modules, seams, interfaces, leverage, locality]
    related_skills: [mattpocock-tdd, mattpocock-improve-codebase-architecture]
---

## When to Use

When designing or restructuring code modules, asking \"where should the seam go\", \"how deep should this module be\", or \"what should the interface expose\". Also use when refactoring shallow modules into deeper ones.

## What This Skill Does

Designs **deep modules**: a lot of behavior behind a small interface. Uses a shared glossary (module, interface, implementation, adapter, seam, leverage, locality) so discussions about architecture are precise and unambiguous.

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

```
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

## Process

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
- **Premature abstraction** — Don't extract a module until you have 3 use sites
- **False depth** — Moving code into a private method doesn't make the module deeper; the interface must shrink

## AspireCURES Context

When refactoring data-source parsers, gating engine, or disease-page renderer, apply this vocabulary. Ask: \"Is this module deep? Does it have leverage? Does the deletion test pass?\"

For the preparer agent: the Arxiv API client should be a deep module that handles pagination, retries, and XML parsing internally with a single `fetch(query) -> results` interface. For the executor agent: the disease-page renderer should abstract away template compilation, asset loading, and HTML optimization behind one `render(disease_data)` call.
