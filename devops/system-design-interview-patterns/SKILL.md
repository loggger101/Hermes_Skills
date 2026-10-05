---
name: system-design-interview-patterns
description: "System-design case studies and OO exercises."
version: 1.0.0
author: Hermes Agent (promoted from system-design-scaling; donnemartin/system-design-primer, CC BY 4.0)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [system-design, interview, case-studies, capacity-estimation, object-oriented-design, patterns]
    related_skills: [system-design-scaling, sql-for-data, python-craft, feature-flag-lifecycle]
---

# System design interview patterns

## What This Skill Does

Turns the system-design-primer's worked solutions into reusable recipes: eight case studies (URL shortener, Twitter timeline, web crawler, social graph, query cache, Mint, sales rank, scaling on AWS) with their key numbers and non-obvious tricks, and six object-oriented design exercises (cards and Blackjack, call center, hash map, LRU cache, chat, parking lot) with the bugs found in the primer's own skeleton code. Core principles and estimation live in `system-design-scaling`.

## When to Use

- Practising or conducting a design interview, or sketching a similar system
- Estimating capacity: the guide's conversion is 2.5 million seconds per month, so 1 request per second is 2.5 million per month and 400 per second is 1 billion
- Modelling a domain as classes with enums, abstract bases and state machines
- Not for CAP, caching and sharding fundamentals (`system-design-scaling`)

## Quick Reference

Cross-cutting patterns from the case studies:

- Precompute offline, serve online: aggregate by MapReduce into a small SQL table plus cache.
- Split storage: object store for blobs, key-value or NoSQL for fast writes, SQL for relational truth.
- Put an async queue at the write edge for slow operations; keep cheap paths synchronous.
- Stateless app servers with central sessions and cache make horizontal scaling possible.
- Scale iteratively: each stage adds one technique triggered by a measured bottleneck.

OO lessons: open with clarifying questions; use `Enum` for closed vocabularies; an abstract base with one polymorphic hook; put responsibility on the more specific object (a parking spot decides whether a vehicle fits); keep lifecycle separate from membership.

## Procedure

1. Clarify scope and constraints, then estimate with the conversion above.
2. Draw the high-level design, then the core components, then scale one bottleneck at a time.
3. Pick the closest case study from `references/case-study-patterns.md` and reuse its pattern and numbers.
4. For an OO prompt, use `references/oo-design-interview-patterns.md`: ask questions, model entities, assign behaviour to the right object.
5. Do not copy the primer's skeleton code verbatim; the reference lists its defects.

## Pitfalls

- Jumping to the final architecture.
- Copying the primer's notebook code: it has `super(Operator, self)` in the wrong classes, `raise NotImplemented`, and bare names where `self.` attributes were meant.
- Treating the capacity numbers as targets rather than worked examples.

## Verification

- [ ] Capacity estimates show their arithmetic
- [ ] Each scaling step names the bottleneck that justifies it
- [ ] OO model uses enums and an abstract base where the domain has closed sets and variants

## References

- `references/case-study-patterns.md` - eight designs as recipes, shared conversion guide, cross-cutting patterns
- `references/oo-design-interview-patterns.md` - six OO exercises, source defects, cross-cutting OO lessons
