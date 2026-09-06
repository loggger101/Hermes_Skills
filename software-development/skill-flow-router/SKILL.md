---
name: skill-flow-router
description: "Route any task through the right skill flow in this brain."
version: 1.0.0
author: "Matt Pocock (mattpocock/skills, MIT) + Hermes Agent — adapted to installed skills"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [router, workflow, planning, meta-skill, skill-discovery]
    related_skills: [grilling-interview, conversation-to-spec, wayfinder-map-planning, mattpocock-to-tickets, systematic-debugging, issue-triage-state-machine, test-driven-development, requesting-code-review]
---

# Skill Flow Router

## What This Skill Does

Answers "which skill or flow fits this situation?" for a brain with 160+ skills. A **flow** is a path through the skills: most work travels one **main flow**, two **on-ramps** merge onto it, and everything else is standalone or vocabulary that runs underneath. This file maps each step to the skill actually installed in this brain (names verified against SKILLS-INDEX.md).

## When to Use

- You have a task but are not sure which of the planning/spec/debugging/review skills applies — load this first, pick the flow, then follow it.
- Do NOT use for single-skill tasks where the skill is obvious from its description (e.g. "make an xlsx" → `xlsx`).

## The main flow: idea → ship

1. **Sharpen by interview** → `grilling-interview`. Start here whenever you are working in a real repo: it's stateful, retaining what it learns in CONTEXT.md and ADRs (domain terms via `mattpocock-domain-modeling`).
2. **Branch — can every question be settled in conversation?** If one needs a runnable answer (state, business logic, UI you must see), detour through throwaway code: `spike` or `mattpocock-prototype`, bridged by `mattpocock-handoff` out and back so the original thread keeps what was learned.
3. **Branch — multi-session build?**
   - **Yes** → `conversation-to-spec` (thread into a spec), then `mattpocock-to-tickets` to split into tracer-bullet tickets with declared blocking edges; work blockers-first, each ticket self-contained so its context is disposable when done.
   - **No** → build in the current session.

   Either way, building means driving TDD (`test-driven-development` / `mattpocock-tdd`, one red-green slice at a time) with evidence gates (`mattpocock-evidence-driven`), then closing out with review: `requesting-code-review` (pre-commit gate) or `mattpocock-code-review` (two-axis Standards + Spec of the diff). Ship via `mattpocock-finishing-a-development-branch` / `mattpocock-yeet`.

### Context hygiene
Keep steps 1–3 in **one unbroken context window** — don't compact until after tickets exist, so grilling/spec/tickets build on the same thinking. Each ticket's implementation then starts fresh from that ticket. The ceiling is the "smart zone" (~150k tokens where reasoning stays sharp): if a session approaches it before tickets are cut, compress at the nearest phase boundary and carry on — never push on degraded.

## On-ramps (situations that generate work)

- **Bugs/requests piling up** → `issue-triage-state-machine`: moves issues through triage roles into agent-ready briefs (+ its AGENT-BRIEF / OUT-OF-SCOPE references). Only for issues you didn't create — tickets from the main flow are already agent-ready, don't re-triage them.
- **Something's broken (the hard kind)** → `systematic-debugging` + `mattpocock-diagnosing-bugs`: refuses to theorise until there is a tight feedback loop (one command that goes red on *this* bug), fixes with a regression test; post-mortem hands off to `mattpocock-improve-codebase-architecture` when the real finding is "no good seam exists".
- **Huge, foggy effort** (greenfield or feature too big for one session) → `wayfinder-map-planning`: charts a shared map of decision tickets and resolves them one at a time — producing *decisions*, not deliverables. When the map clears it hands off to `conversation-to-spec`, which collapses linked decisions into a buildable plan; don't loop straight into implementation or you throw the detail away.

## Codebase health (not feature work)
- Spare moment → `mattpocock-improve-codebase-architecture`: surfaces deepening opportunities; picking one *generates an idea* for the main flow at step 1. Designing that chosen piece happens on the bench: `mattpocock-codebase-design`.

## Vocabulary underneath (the words, not the process)
- `mattpocock-domain-modeling` — sharpen domain language: challenge fuzzy terms, resolve overloaded words, record hard-to-reverse decisions as ADRs.
- `verification-culture` — doc-driven verification: backlog, audits, regression gates; load whenever "done" needs to mean something checkable.

## How to use this router in practice
1. Name the situation (idea / bug pile / foggy effort / broken thing / upkeep).
2. Pick the flow above; note its first skill and where it hands off.
3. Load that skill with `skill_view` and follow it — don't improvise a hybrid of three skills when one owns the step.
