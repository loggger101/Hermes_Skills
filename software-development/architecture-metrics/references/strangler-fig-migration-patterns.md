# Strangler Fig Migration Patterns (verified from tech-leads-club/agent-skills @ 0ab82f6)

Source: `packages/skills-catalog/skills/(architecture)/legacy-migration-planner/references/strangler-fig-patterns.md`
(+ assessment-framework, testing-safety-nets, plan-phase refs). License CC-BY-4.0; attribution: Tech Leads Club / Felipe Rodrigues. Mined 2026-09-16.

The Strangler Fig (Martin Fowler) gradually replaces legacy by building around it — named for fig vines that germinate on a
host tree, draw its nutrients, and become self-sustaining. Their framing: the pattern works in ALL directions (monolith→services,
services→monolith, framework A→B), not just decomposition. Four activities per Cartwright/Horn/Lewis as cited by Fowler: establish
clear desired outcomes with organizational alignment · identify seams to decompose into manageable components · replace isolated
components at acceptable risk · evolve the org's development practices alongside the system. Key principle: **transitional architecture** —
temporary code enabling new+legacy coexistence is justified overhead vs big-bang replacement.

## The three core patterns (each with rollback story)

1. **API Gateway Strangler** — routing layer in front of legacy; new implementations register per route; traffic split by feature flag /
   percentage / user segment. Routing decision logic: `0%` all-legacy, `100%` all-new, between ⇒ consistent hashing on user/session for
   STICKY canary (same user always hits the same implementation). **Rollback = set percentage to 0; instant, no deployment.** Applies to
   monolith→microservices AND framework migrations (Flask→FastAPI: proxy unmigrated routes to old framework).
2. **Service Extraction with Adapter** — extract interface → wrap legacy behind it (adapter delegates) → build new implementation behind the
   SAME interface → route via DI/feature flags. Both implementations must satisfy the same CONTRACT TESTS; during transition the interface IS the seam.
   The adapter absorbs protocol differences (sync→async, error-type translation, data formats). Works in reverse for absorbing a service into a monolith:
   create an interface whose implementation calls the service, then inline and remove the service.
3. **Database Strangler (dual-write)** — new writes go to the NEW store (source of truth); async best-effort sync back to legacy (log failures, don't fail
   the operation); reads try-new-then-fallback-to-legacy; LAZY migration copies records from legacy on first read; stop dual-write + decommission once migrated.

## Safety nets their planner insists on before any cut-over (testing-safety-nets.md)

Characterization tests of CURRENT behavior before touching it ("golden master": record outputs, assert stability) · shadow reads comparing new vs
legacy results in production without serving them from the new path · per-route kill switches independent of deploy state · data-backfill verification
as a queryable reconciliation (counts + sampled row comparison), never "trust the sync job" · and an explicit ROLLBACK PLAN PER PATTERN written into
the migration plan document, because rollback that requires a deployment is not a rollback.

## Planning discipline (plan-phase.md)

Assessment first: inventory components by change frequency × coupling risk; pick seams where DEPENDENCIES point one way already (reversing dependency
direction mid-migration multiplies cost); order extraction so each step ships value independently — "a migration step that only reorganizes code and
changes nothing observable is a refactor wearing a trench coat" (their words, paraphrased from the assessment framework). Cross-link: see
`modular-monolith-boundary-validation.md` in this skill for the monolith-side structure these patterns extract FROM.
