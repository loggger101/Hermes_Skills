# Modular Design Principles: Violations & Split/Merge Criteria (verified from tech-leads-club/agent-skills @ 0ab82f6)

Source: `(architecture)/modular-design-principles` v1. License CC-BY-4.0; attribution: Tech Leads Club / Felipe Rodrigues. Mined 2026-09-17 (final screen). Technology-agnostic companion to `monolith-decomposition-pipeline.md` (which MEASURES structure) and `modular-monolith-boundary-validation.md` (which ENFORCES boundaries in-repo): this ref is the PRINCIPLE layer — what good looks like, how to name violations when reviewing, and WHEN to split or not.

## The ten principles (one line each) [VERIFIED]

1. Well-defined boundaries — small stable public surface; consumers depend on contracts, not internals
2. Composability — usable alone or combined without knowledge of each other's internals
3. Independence — no hidden shared mutable state across boundaries; testable in isolation with fakes at the edges
4. Individual scale — resources (compute/storage/rate limits/batch) tunable per module where it matters
5. Explicit communication — cross-module interaction via documented contracts, never incidental coupling
6. Replaceability — dependencies expressed through interfaces/protocols so implementations can change
7. Deployment independence — no assumed shared process/host/release cadence unless explicitly decided
8. **State isolation** (the hardest one) — each module OWNS its persistent state and naming; "ambiguous ownership of data or names is a frequent source of 'works until it doesn't' integration bugs"
9. Observability — logs/metrics/traces/health attributable to the unit that emitted them
10. Fail independence — failures contained (timeouts, bulkheads, circuit breaking, idempotency) so one module's outage doesn't blindly cascade

Layered mental model: **composition roots** (thin orchestration wiring modules together) → **modules/bounded contexts** (cohesive behavior + data ownership) → **shared kernels** (use sparingly — "resist turning them into a grab-bag of everything everyone needs"). Physical layout (monorepo/multi-repo/packages) is a DELIVERY CHOICE, not the definition of modularity.

## The eight named violations [VERIFIED]

These are review-ready names for what `architecture-metrics`'s coupling/cycle numbers point at:
1. **Colliding concepts** — same name/schema meaning different things in different modules; duplicate "global" definitions that diverge over time
2. **Reach-through persistence** — a module reading/writing another's tables/buckets/documents without going through an agreed contract (the cross-module deep-import analog for data)
3. **Centralized data ownership** — one persistence layer registering/exposing ALL stores for ALL modules, encouraging hidden coupling
4. **Logic at the edge** — business rules in transport adapters (HTTP handlers/UI/CLI) instead of domain/application code
5. **Edge talking to storage directly** — adapters depending on low-level persistence APIs instead of use cases
6. **Unscoped transactions** — writes spanning boundaries without clear transaction ownership and failure semantics
7. **Leaky exports** — repositories, internal services, or implementation types exposed as the public API (cf. our barrel-only import rule: a barrel that re-exports internals IS leaky)
8. **Facades that aren't thin** — "public" entry points embedding querying/mapping/policy instead of delegating

## Split / merge criteria [VERIFIED]

SIX split signals, each answerable without ideology: (1) LANGUAGE — different vocabulary or conflicting definitions of the same word; (2) RATE OF CHANGE — parts change on different cadences/for unrelated reasons ("most edits touch one side"); (3) SCALE/SLO — different throughput/latency/availability targets needed; (4) CONSISTENCY — different transaction boundaries, can't share one atomic write model cleanly; (5) OWNERSHIP — clear team lines would reduce conflict and review churn; (6) PAIN SIGNAL — observable integration pain: ripple effects, fear of change, unclear bug ownership.

**Merge-or-wait rule**: if the only motivation is "files got big" or folder aesthetics → merge or wait. Also don't split when boundaries are artificial (same language/lifecycle/constant cross-calls), splitting would duplicate logic/data without a clear single-writer rule, or the team isn't ready to own contracts/versioning/ops for extra units. Decision prompts: "Would separation REDUCE accidental coupling more than it INCREASES coordination cost?" and "Is there a natural ubiquitous-language boundary, or only a technical seam?"

## Sub-units inside one bounded context [VERIFIED]

Principles apply WITHIN the context too: each sub-unit owns its slice of model/persistence where possible; cross-sub-unit access via internal application APIs/thin facades (not peers importing each other's storage types); async flows should carry **enriched payloads** so handlers don't "chat" across sub-units for data that could travel with the event. Named anti-pattern: a single "persistence"/"data" sub-module becoming the only place knowing all tables/documents, everyone reaching through it — reach-through INSIDE the boundary is just as bad as across it.
