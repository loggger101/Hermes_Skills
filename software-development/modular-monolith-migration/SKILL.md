---
name: modular-monolith-migration
description: "Module boundaries, decomposition, strangler-fig plans."
version: 1.0.0
author: Hermes Agent (promoted from architecture-metrics references; tech-leads-club/agent-skills, CC-BY-4.0, attribution Tech Leads Club / Felipe Rodrigues)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [architecture, modular-monolith, decomposition, strangler-fig, boundaries, ddd, migration, coupling]
    related_skills: [architecture-metrics, codebase-onboarding, mattpocock-codebase-design, system-design-scaling, verification-culture]
---

# Modular monolith, decomposition and migration

## What This Skill Does

Turns architecture measurements (`architecture-metrics`) into decisions and a plan: ten modular-design principles with eight named violations to use in reviews, an executable boundary check pattern, a five-step decomposition analysis pipeline, and strangler-fig migration patterns with rollback stories. The reference content is mined from tech-leads-club/agent-skills (CC-BY-4.0; keep the attribution to Tech Leads Club / Felipe Rodrigues when reusing it).

## When to Use

- Reviewing or designing module boundaries in a monolith, or deciding whether to extract a service
- Planning a legacy migration (framework swap, monolith to services or back) with safe cut-over
- Turning an architecture rule you keep repeating in reviews into a CI check
- Not for computing coupling, modularity or cycle numbers (`architecture-metrics`), onboarding to an unfamiliar repo (`codebase-onboarding`), or capacity and scaling design (`system-design-scaling`)

## Which reference

| Need | Reference | Key idea |
|---|---|---|
| Vocabulary for module design problems | `references/modular-design-principles-violations-and-split-criteria.md` | ten principles (state isolation is the hardest); eight named violations such as reach-through persistence, leaky exports, unscoped transactions; split and merge criteria |
| Enforce boundaries in CI | `references/modular-monolith-boundary-validation.md` | flat-by-aggregate modules, ports and adapters, transactional outbox, monolith-first rule; a stdlib script that flags cross-module deep imports and duplicate entity names |
| Analyse an existing monolith before extracting | `references/monolith-decomposition-pipeline.md` | five ordered patterns: size components, find common domain logic, flatten hierarchy, analyse coupling (strength x distance x volatility), group by domain |
| Replace legacy gradually | `references/strangler-fig-migration-patterns.md` | API-gateway strangler, adapter-based service extraction, dual-write database strangler; characterization tests, shadow reads, kill switches, a rollback plan per pattern |

## Procedure

1. Measure first with `architecture-metrics`; use the eight named violations to describe what the numbers point at.
2. Run the decomposition pipeline in order and carry context forward; if a step is skipped, say which and how that limits conclusions. Components are the leaf directories; size by executable statements, not lines.
3. Apply the monolith-first rule: extract a service only when an independent scaling, deployment or ownership need is measured.
4. Encode any recurring review rule as a small script that exits non-zero (barrel-only imports, unique entity names); note that alias imports are not resolved by the reference script.
5. For migration pick a strangler pattern per seam, write characterization tests of current behaviour first, add shadow reads and a per-route kill switch, and write the rollback plan (for gateway routing, set the percentage to 0).
6. Retire transitional code deliberately; it is justified overhead, not the destination.

## Pitfalls

- Shared kernels that become a grab-bag of everything everyone needs.
- Ambiguous ownership of data or names, the usual cause of "works until it doesn't" integration bugs.
- Dual-write that fails the operation when the legacy sync fails; log and continue, reconcile with counts and sampled rows.
- Trusting a sync job instead of a queryable reconciliation.
- Extracting to services on anticipated rather than measured needs.

## Verification

- [ ] Violations are named and tied to measured coupling, not opinion
- [ ] Each extraction has a measured driver and a seam with a contract test
- [ ] Characterization tests, shadow reads and a rollback plan exist before cut-over
- [ ] Boundary rules run in CI and fail the build

## References

- `references/modular-design-principles-violations-and-split-criteria.md` - ten modular-design principles, eight named violations, split and merge criteria
- `references/modular-monolith-boundary-validation.md` - evolutionary modular monolith pillars, executable boundary validation, NestJS notes
- `references/monolith-decomposition-pipeline.md` - the five-pattern analysis pipeline with sizing heuristics, domain-vs-infrastructure split, orphaned classes, coupling and grouping
- `references/strangler-fig-migration-patterns.md` - the three strangler patterns, rollback stories and the testing safety nets required before cut-over
