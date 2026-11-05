---
description: "pstack's steering-by-principle-name technique and its 24 named principles (core/architecture/verification/delegation/meta), with an honest map of which are already held by skills in this catalog and what is genuinely new - the accountability rule that a cited principle must name the decision it changed"
source_repo: backnotprop/pstack (MIT) - docs/guide/08-principles.md + 24 skills/principle-*/SKILL.md at main, 2026-11-04
tested_version: "SOURCE-READ. The guide and principle index were read locally; no pstack skill was installed or run in a harness"
verified_date: "2026-11-04"
---

# Principle-name steering (pstack)

## The transferable technique, which is not the list itself

pstack ships 24 principles as individual skills and uses **their names as a steering vocabulary**: *"You don't invoke
principles. You use their names to steer... one phrase redirects the work more precisely than a paragraph of
instructions."* Two things make it work rather than decorative:

1. **The name points at a complete, pre-read rule** — so `subtract before you add` carries its whole definition.
2. **Accountability is explicit**: each applied principle must be named *along with the decision it changed*, and
   "a principle citation with no decision behind it means the agent named the rule without applying it."

That second half is the part worth stealing for this catalog: we have plenty of rules; what we lack is a cheap way to
make an agent show which rule altered its behaviour. If you adopt anything here, adopt *"cite the rule + name the
decision"*, and check that claims of compliance point at a changed line, not at vocabulary.

Also worth noting from `principle-build-the-lever`: *"When an agent keeps doing the same thing by hand, have it write
the tool or skill it wishes it had... save agents for the judgment calls."* That is this repo's whole existence as a
procedure — and its failure mode (scripting over reasoning) is what our owner explicitly rejects for mining work.

## The 24 principles, grouped, mapped to this catalog

Legend: **≈** already covered by an existing skill | **+** adds something we do not state that way.

Decide how much to build / when to rethink (core):
- Laziness Protocol — deletion and smallest change; consolidate decisions behind one source of truth → ≈ `ponytail`
- Subtract Before You Add — remove dead weight before building on it → ≈ `ponytail`
- Foundational Thinking — choose core data structures before logic → ≈ `mattpocock-codebase-design`
- Model the Domain — repeated rules in one structure, not scattered conditionals → ≈ `mattpocock-domain-modeling`
- Redesign from First Principles — integrate a new requirement as if it had been there from day one → **+** (we have no skill stating this)
- Attack the Premise — write down the premise two+ failed fixes shared and test *that* before the next fix → ≈ `systematic-debugging`, `grill-me` (the explicit "shared premise of N failures" framing is sharper than ours)
- Minimize Reader Load — collapse layers/hidden state a reader must hold → **+**
- Outcome-Oriented Execution — converge on the target design; do not preserve throwaway compatibility states → **+**
- Experience First — user's result over implementation convenience → **+** (adjacent to `communication` skills)
- Exhaust the Design Space — 2–3 competing prototypes when there is no precedent → ≈ `sketch`, `spike`

Decide where state, validation and compatibility live (architecture):
- Boundary Discipline — validate at the boundary, trust internal types → **+**
- Type System Discipline — make illegal states unrepresentable → **+** (`structured-llm-outputs` covers the pydantic half)
- Make Operations Idempotent — retries converge on one end state → ≈ `cron-job-authoring` guardrails (worth citing here explicitly)
- Migrate Callers Then Delete Legacy APIs — migrate and delete in one wave → **+**
- Separate Before Serializing Shared State — remove sharing before adding locks → **+**

Define what counts as proof (verification):
- Prove It Works — verify the real artifact, not a proxy → ≈ `verification-before-completion`
- Fix Root Causes — reproduce and trace before changing code → ≈ `systematic-debugging`, `mattpocock-diagnosing-bugs`
- Sequence Work into Verifiable Units — each small unit ends in a check → ≈ `executing-plans`, `plan`
- Test Behavior, Not Implementation — assert what users can observe; survive internal change → **+** (we have TDD but not this discriminator stated as a rule)
- Explain the Number — before trusting/reporting a measured number, name what limits it and rule out that it measured something else; `/benchmark-checklist` turns it into seven questions from real runs → ≈ `dataviz`, `bit-identity-float-pipelines`; **+** as an explicit pre-report gate

Keep parallel work sane (delegation):
- Guard the Context Window — route bulk reading to subagents, keep findings (not payloads) in the main thread; size phases and cap scope with turn budgets → ≈ `context-budget-planning`
- Never Block on the Human — proceed on reversible work and present the result → **+** (our bias is to ask; this states the *reversibility test* that decides when not to)

Meta:
- Encode Lessons in Structure — advice repeated twice becomes a lint/check/script (`/correct` applies it repo-wide) → ≈ `living-docs-governance`, and literally how our gate suite grew (e.g. round-43's router-coverage gate came from exactly this failure mode); **+** as an explicit rule for agents

## Honest assessment

Roughly a third of the list restates what this catalog already holds, often in stronger prose worth quoting; about
half are architecture/verification principles we express through skills rather than as named rules (the *naming* is the
gain — it makes them referenceable mid-task); and only a handful (`Redesign from First Principles`, `Minimize Reader
Load`, `Outcome-Oriented Execution`, `Boundary Discipline`, `Test Behavior Not Implementation`) are genuine content gaps.
pstack itself ships no planning skills by choice ("cursor already has a great plan mode... personally, i don't believe
in planning"), so nothing here competes with our `plan`/`brainstorming` lanes.
Reverified 2026-11-05 against upstream: the maintainer's own sync-log commits (4a3f660, ecec42a) state no content change since our read, and the only
functional commit after it (06572d2, 'statechart run on Windows #17') is tool signal-handling - not principle knowledge. The 24-principle set documented here stands.
