# Modular Monolith & Boundary Validation (verified from tech-leads-club/agent-skills @ 0ab82f6)

Source: `packages/skills-catalog/skills/(architecture)/evolutionary-modular-architecture` (SKILL.md + 7 references +
`scripts/validate-boundaries.mjs`) and `(development)/nestjs-modular-monolith`. License CC-BY-4.0; attribution: Tech Leads Club / Felipe Rodrigues.
Mined 2026-09-16. The architecture skill is a complete design system for **evolutionary modular monoliths** (DDD strategic + tactical); the portable core below.

## Design pillars (from their references/)

1. **Flat-by-aggregate organization**: modules organized by AGGREGATE, not by technical layer — `src/modules/<aggregate>/` owns its entities, value objects, services, and adapters; a flat per-module tree beats deep feature/layer nesting because it keeps the unit of change small and boundaries visible in the file path.
2. **Ports & adapters (hexagonal)**: each module exposes a port interface; vendor-specific code sits only in the adapter layer — an Anti-Corruption Layer for every external dependency (ERP, storage, AI provider) so "vendor independence" is structural, not aspirational.
3. **Transactional outbox** for events: write event + business state in ONE transaction to an outbox table; a relay publishes and marks sent. Guarantees at-least-once without distributed transactions — the standard answer to "how do modules/services exchange events reliably."
4. **Smart resilience, not blanket retries**: backoff WITH JITTER (un-jittered synchronized retries cause thundering-herd amplification), circuit breakers on flaky dependencies, and IDEMPOTENCY keys so retried calls are safe — each applied per-dependency by measured failure mode, never as a uniform wrapper.
5. **Monolith-first decision rule**: start modular-monolith; extract to services only when an independent scaling/deployment/ownership need is MEASURED (team boundaries, resource profiles), not anticipated. The flat-by-aggregate + ports structure means extraction later is moving directories, not rewriting coupling.

## Executable boundary validation (`validate-boundaries.mjs` — the pattern worth stealing)

Their skill SHIPS a stdlib-only Node script that turns architecture principles into CI-enforceable invariants (exit 1 on error). Two checks:

- **Cross-module deep imports**: for every relative import, resolve it and take the first path segment under root; if it's another module AND the target is NOT its barrel/facade (`index.ts` or a depth-≤1 file), warn "import the sibling's barrel only." Barrel-only imports are what make modules replaceable — deep imports re-couple them.
- **Entity uniqueness + naming prefix**: collect every exported class from `*.entity.ts` (and Prisma `model` names); duplicate entity NAME across two different modules = ERROR ("prefix with module name"); entities lacking their module's pascal-case/compact prefix warn. Global name-space collisions are how modular monoliths silently re-couple.

Documented limitation they state honestly: alias imports (`@scope/...`) aren't resolved — project path mapping is unknown to the script; it only trusts relative climbs. The generalization for this brain: **any architecture rule you keep restating in reviews should become a small executable check** (cf. our `architecture-metrics` skill's stdlib port of sentrux's metrics layer, and the lint-rule flywheel idea from the PR-judge protocol).

## NestJS-specific notes (nestjs-modular-monolith refs)

Module communication via domain events through an event bus with per-module subscribers; state isolation enforced by a `validate-isolation.sh` script that greps for cross-module entity imports in tests/services; CQRS split only where read/write load genuinely diverges (not as default ceremony); authentication at the gateway, authorization re-checked inside each module's service layer ("the boundary is not just the outer wall").
