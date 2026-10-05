# Monolith Decomposition Analysis Pipeline (verified from tech-leads-club/agent-skills @ 0ab82f6)

Source: `packages/skills-catalog/skills/(architecture)/modular-decomposition` v1 + its five pattern references. License CC-BY-4.0; attribution: Tech Leads Club / Felipe Rodrigues (coupling model per Vlad Khononov, *Balancing Coupling in Software Design*). Mined 2026-09-17 as the exhaustion sweep of this repo.

## The pipeline shape (the part worth stealing)

Five ordered analysis patterns run BEFORE any extraction planning; each pattern's output feeds the next:

| # | Pattern | Question it answers |
|---|---------|---------------------|
| 1 | Identify & size components | What are the building blocks, and which are oversized? |
| 2 | Common domain detection | Where is business logic duplicated across components? |
| 3 | Flattening / hierarchy cleanup | Which classes live in namespaces that aren't real components? |
| 4 | Coupling analysis (S×D×V) | How bad is each cross-component dependency, really? |
| 5 | Domain grouping | Into which candidate domain-aligned units do the cleaned components group? |

Orchestration rules: run 1→5 in order; **carry context forward** (Pattern-1's inventory feeds 4 and 5); if a step is skipped at user request, state WHICH patterns were skipped and how that limits later conclusions. Pattern 6 (extraction/roadmap) deliberately lives in a separate skill (`decomposition-planning-roadmap`) — analysis and planning are different artifacts with different readers.

## Pattern 1: sizing heuristics [VERIFIED]

- **Components = leaf nodes** of the directory/namespace tree — the deepest directories containing source files. If `services/billing` is extended by `services/billing/payment`, then `billing` becomes a SUBDOMAIN and only leaves are components. This rule makes "what should be split" mechanically enumerable instead of opinion-based.
- **Size = executable statements, not LOC** (formatting-invariant). Metrics per component: percent of codebase, file count, z-score vs mean.
- Oversized flags: >30% of total (small apps <10 components) or >10% (large apps >20), OR >2 std devs above mean, OR contains multiple distinct functional areas. Undersized (<1%, or <1σ below): consolidation candidates — too-granular modules cost coordination without isolation benefit.

## Pattern 2: the domain-vs-infrastructure split [VERIFIED]

Duplicated functionality splits by WHO it serves: **domain** logic (notification, validation, auditing) is common to SOME processes → consolidate into a shared service/library; **infrastructure** concerns (logging, metrics, auth plumbing) are common to ALL processes → they belong in the platform layer, not in per-domain consolidation. Detection signals: same leaf-node name across namespaces (`*.notification`, `*.audit`), shared classes imported by N components, similar-but-divergent implementations of one job. Three consolidation shapes with different change-coupling: shared service (frequently-changing logic) / shared library (stable utilities) / component merge (highly related, low coupling impact).

## Pattern 3: orphaned classes [VERIFIED]

A class sitting in a non-leaf namespace (a subdomain root that was extended by children) has no definable owning component — it's an ORPHAN. Three fix strategies: consolidate DOWN (merge the leaf up into the parent), split UP (move root-level code into new leaves, e.g. `survey` → `survey.create` + `survey.process`), or move shared code to a dedicated `.shared` leaf.

## Pattern 4: coupling as strength × distance × volatility [VERIFIED]

Each coupled pair A→B scored on three axes (0..1): **strength** — contract coupling (weakest, ideal) < model coupling (rich object/enum leaks across the boundary; fix with integration DTO / public contract enum) < functional coupling (duplicated business logic = symmetric; mandatory execution order = sequential; distributed transactions/Saga) < intrusive coupling (strongest: reflection into private members, reading another service's DB — refactor urgently). **Distance** — same object/namespace → different services. **Volatility** — generic/supporting subdomain vs core (competitive-advantage) subdomain.

`MAINTENANCE_EFFORT = STRENGTH × DISTANCE × VOLATILITY` — the 8-cell diagnosis table: High/HIGH/high ⇒ CRITICAL; strong+stable ⇒ ACCEPTABLE (legacy integration); strong+local+volatile ⇒ GOOD ("change together, live together" is cohesion, not a defect); loose+independent ⇒ GOOD. The main problem to hunt: **strong coupling with volatile AND distant components**. Honest known limitations they state: volatility needs real git data; symmetric functional coupling needs semantic reading (static tools miss it); organizational distance needs user input; dynamic connascence (timing/value/identity) needs runtime observation.

## Pattern 5 + DDD grounding [VERIFIED]

Grouping aligns structural components with linguistic boundaries where evidence supports it — subdomain/bounded-context analysis is an OPTIONAL lens loaded before or alongside grouping, not a prerequisite ceremony. Cross-link: `strangler-fig-migration-patterns.md` (same skill) covers what happens AFTER the groups are decided; `modular-monolith-boundary-validation.md` covers keeping the boundaries honest in-repo.

## Co-change graph refinement for ownership analysis [VERIFIED]

From their security-ownership-map skill: a people↔files bipartite git-history graph plus file co-changes (Jaccard on shared commits) clustered with community detection — but the clustering is only meaningful after filtering NOISE: lockfiles, `.github/*`, editor config and other "glue" files excluded by default (`--cochange-exclude`), dependabot/bot authors excluded by default, mega-commits capped via `--cochange-max-files`. Without those exclusions every file cluster around the same CI/lockfile churn. (Extends our architecture-metrics evolution skip-rules: they filter COMMITS for metrics; this filters FILES+AUTHORS for clustering.)
