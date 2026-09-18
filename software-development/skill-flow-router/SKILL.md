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

Answers "which skill or flow fits this situation?" for this brain's whole catalog (live count: SKILLS-INDEX.md). A **flow** is a path through the skills: most work travels one **main flow**, several **on-ramps** merge onto it (each listed below), and everything else is standalone or vocabulary that runs underneath. This file maps each step to the skill actually installed in this brain (names verified against SKILLS-INDEX.md).

## When to Use

- You have a task but are not sure which of the planning/spec/debugging/review skills applies — load this first, pick the flow, then follow it.
- Do NOT use for single-skill tasks where the skill is obvious from its description (e.g. "make an xlsx" → `xlsx`).

## The main flow: idea → ship

1. **Sharpen by interview** → `grilling-interview`. Start here whenever you are working in a real repo: it's stateful, retaining what it learns in CONTEXT.md and ADRs (domain terms via `mattpocock-domain-modeling`). For a plan that already exists and needs attacking rather than eliciting, use `grill-me` — adversarial interview of *your* plan before any code. Unsure whether the idea is even a spike vs. a real build? `brainstorming` triages that first.
2. **Branch — can every question be settled in conversation?** If one needs a runnable answer (state, business logic, UI you must see), detour through throwaway code: `spike` or `mattpocock-prototype`, bridged by `mattpocock-handoff` out and back so the original thread keeps what was learned.
3. **Branch — multi-session build?**
   - **Yes** → `conversation-to-spec` (thread into a spec; `mattpocock-spec-driven-development` if the spec itself is the artifact you'll drive from), then `plan` to sequence it and `mattpocock-to-tickets` to split into tracer-bullet tickets with declared blocking edges; work blockers-first, each ticket self-contained so its context is disposable when done.
   - **No** → build in the current session.

   Either way, building means driving TDD (`test-driven-development` / `mattpocock-tdd`, one red-green slice at a time) with evidence gates (`mattpocock-evidence-driven`); reach for `property-based-testing` when the invariant matters more than the example. Working from a plan someone already wrote → `executing-plans` (inline checkpoints, no re-planning). Independent work splits across agents via `mattpocock-subagent-driven-development` or `dispatching-parallel-agents`; codify a re-runnable fan-out with `dynamic-workflow`.

   Close out with review — pick by axis, don't run all four: `requesting-code-review` (pre-commit gate), `mattpocock-code-review` (two-axis Standards + Spec of the diff), `mattpocock-multi-agent-code-review` (independent reviewers, high-stakes diffs), `mattpocock-security-review` (attack surface). On the receiving end, `receiving-code-review` verifies feedback against the codebase before you act on it. Before claiming done, `verification-before-completion`. Ship via `mattpocock-finishing-a-development-branch` / `mattpocock-yeet`.

### Context hygiene
Keep steps 1–3 in **one unbroken context window** — don't compact until after tickets exist, so grilling/spec/tickets build on the same thinking. Each ticket's implementation then starts fresh from that ticket. The ceiling is the "smart zone" (~150k tokens where reasoning stays sharp): if a session approaches it before tickets are cut, compress at the nearest phase boundary and carry on — never push on degraded.

## On-ramps (situations that generate work)

- **Bugs/requests piling up** → `issue-triage-state-machine`: moves issues through triage roles into agent-ready briefs (+ its AGENT-BRIEF / OUT-OF-SCOPE references). Only for issues you didn't create — tickets from the main flow are already agent-ready, don't re-triage them.
- **Something's broken (the hard kind)** → `systematic-debugging` + `mattpocock-diagnosing-bugs`: refuses to theorise until there is a tight feedback loop (one command that goes red on *this* bug), fixes with a regression test; post-mortem hands off to `mattpocock-improve-codebase-architecture` when the real finding is "no good seam exists".
- **Production is on fire (right now)** → `incident-response`: a *different lane* from debugging — it commands the open incident (declared severity, named roles, append-only timeline, mitigation before fix, signal-based recovery). Root-causing waits; when the incident closes, hand off to `systematic-debugging` for the real fix and `retro` for the environment changes that follow.
- **Huge, foggy effort** (greenfield or feature too big for one session) → `wayfinder-map-planning`: charts a shared map of decision tickets and resolves them one at a time — producing *decisions*, not deliverables. When the map clears it hands off to `conversation-to-spec`, which collapses linked decisions into a buildable plan; don't loop straight into implementation or you throw the detail away.

## Codebase health (not feature work)
- Spare moment → `mattpocock-improve-codebase-architecture`: surfaces deepening opportunities; picking one *generates an idea* for the main flow at step 1. Designing that chosen piece happens on the bench: `mattpocock-codebase-design`.
- New to the repo → `codebase-onboarding` (architecture map + starter AGENTS.md) before you touch anything.
- Suspect the green is lying → `failure-signal-audit`: swallowed errors, dangerous fallbacks, propagation gaps, false-green status claims. Use it when checks pass but confidence doesn't follow.
- Want the health claim to be a number → `architecture-metrics` (dependency-graph metrics); to *act* on it, `simplify-code`.
- Docs drifting from the system they describe → `living-docs-governance`.

## Vocabulary underneath (the words, not the process)
- `mattpocock-domain-modeling` — sharpen domain language: challenge fuzzy terms, resolve overloaded words, record hard-to-reverse decisions as ADRs.
- `verification-culture` — doc-driven verification: backlog, audits, regression gates; load whenever "done" needs to mean something checkable. Its point-of-use sibling is `verification-before-completion` (no completion claim without fresh evidence).

## Deliberately not routed here

These carry planning/debugging/review tags but are **stack- or tool-specific**, not flow steps —
the "When to Use" rule above applies: their own description already tells you when to reach for
them, so routing through this file would add a hop and no information. `tools/check-router-coverage.py`
reads this list, so a newly added skill in that tag set must either appear in a lane above or be
named here with a reason — it cannot silently go unrouted.

- `python-debugpy` — debugger attach for one runtime; reached from `systematic-debugging`, not routed to.
- `node-inspect-debugger` — same, for Node.
- `rest-graphql-debug` — debugging one protocol surface; the flow question is already answered by then.
- `docker-containers` — container/Compose mechanics; a build environment, not a decision point.
- `mattpocock-gh-fix-ci` — acts on a specific failing CI check; no routing choice to make.
- `bit-identity-float-pipelines` — numeric-correctness verification for float pipelines; a domain technique.
- `sdlc-review` — routes Kanban handoffs; a different process system with its own board, not this flow.

## How to use this router in practice
1. Name the situation (idea / bug pile / foggy effort / broken thing / live incident / upkeep).
2. Pick the flow above; note its first skill and where it hands off.
3. Load that skill with `skill_view` and follow it — don't improvise a hybrid of three skills when one owns the step.
