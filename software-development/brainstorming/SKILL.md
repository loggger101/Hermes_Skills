---
name: brainstorming
description: "Triage as spike/bounded/architectural; approve first."
version: v0.1.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [brainstorming, design-first, approval-gates, task-classification, spec-writing]
    related_skills: [grilling-interview, conversation-to-spec, spike, plan]
---

<!-- source: obra/superpowers (skills/brainstorming), ported 2026-09-09 -->
## When to Use

- Any creative work before implementation: new features, components, behavior changes, or anything that modifies how the system works.
- You are about to start building and have not yet agreed with the user on what "done" looks like.
- A request is ambiguous enough that guessing wrong would waste hours.

**Don't use** for pure research questions (use `spike`) or mechanical fixes where the design IS the one-line diff description — though even those get a two-sentence plan presented before acting.

## What This Skill Does

Turns an idea into a fully formed, approved design through collaborative dialogue: classify how much process the request needs (spike / bounded / architectural), understand context, refine the idea, present a design scaled to that path, and gate implementation on explicit user approval. The ceremony scales with the task; the approval gate never does.

**HARD GATE:** Do not invoke any implementation skill, write code, scaffold anything, or take an implementation action until you have told the user what you intend and they approved it. This applies to EVERY task on EVERY path below.

## Three Paths

Before your first question, classify the request and say the classification out loud — "this looks bounded, so I'll present a short design here rather than write a spec" — so the user can override it:

- **Spike** — a feasibility question ("can we…", "is it possible…", "quick and dirty is fine") whose output is an answer, not code you keep. Present the question and what you'll try in 2–3 sentences, get a nod, then find out as cheaply as correctness allows. No design doc, no spec file. Report findings as a recommendation; anything built stays labeled throwaway (see `spike`).
- **Bounded** — a well-scoped change to code that already exists: a new flag, a small endpoint, a one-file fix. Understanding the kind of app is not enough — bounded means the flow you are changing is already here to read. If there is no existing flow to change, the task is not bounded. Ask the clarifying questions that matter, present a short design IN CHAT (a few sentences to a few short paragraphs), and STOP. Implementation starts only after the user says yes — a bounded task's approval is as hard a gate as an architectural one. No spec file, no plan document.
- **Architectural** — new projects, new subsystems, changes that restructure how components fit together or alter interfaces others depend on. Follow the full process: questions, approaches, sectioned design, written spec (see `conversation-to-spec`), then an implementation plan (see `plan`).

When in doubt between two paths, take the heavier one. The ratchet is one-way: hidden complexity discovered mid-task upgrades the path — stop, say so, and step up. Nothing downgrades mid-task.

## Anti-Pattern: "Too Simple To Need Approval"

Every path ends with user approval of intent before implementation. A todo list, a single-function utility, a config change — the design may be two sentences in chat, but you MUST present it and get approval. "Simple" tasks are where unexamined assumptions cause the most wasted work. What scales with simplicity is the artifact, never the approval.

## Red Flags

| Thought | Reality |
|---------|---------|
| "This is too simple to need a design" | Simple means a short design, not no design. Two sentences in chat, then approval. |
| "I'll call it bounded and skip the spec" | Reaching for a label to skip work IS the doubt — take the heavier path. |
| "It's bounded and the design is obvious — I'll start while they read it" | The gate is the approval, not the design's length. Present, then stop until you hear yes. |
| "I understand this kind of app, so it's bounded" | Bounded measures the repo, not your familiarity. A new project has no existing flow — it is architectural. |
| "The spike works, so I'll keep the code" | A spike's output is an answer. Keeping the code is a new request — classify it. |
| "It grew, but I'm almost done — no need to re-classify" | Hidden complexity upgrades the path mid-task. Stop and say so. |
| "They approved the spike, so the follow-up change is approved too" | Each task gets its own classification and its own approval. |

## Checklists

Classify first, announce the path, then work through each item in order.

**Spike:**
1. **Explore project context** — enough to frame the probe.
2. **Present question + probe plan** — 2–3 sentences.
3. **Get approval** — a nod is enough.
4. **Investigate** — as cheaply as correctness allows.
5. **Report findings** — a recommendation; label anything built as throwaway.

**Bounded:**
1. **Explore project context** — check files, docs, recent commits.
2. **Ask clarifying questions** — one at a time, the ones that matter.
3. **Present short design in chat** — approach, files touched, testing.
4. **Get approval** — STOP and wait for an explicit yes; presenting the design and starting in the same breath is skipping the gate.
5. **Implement** — proceed with the normal development workflow (TDD applies); no plan document.

**Architectural:**
1. **Explore project context** — check files, docs, recent commits.
2. **Scope check BEFORE detailed questions** — if the request describes multiple independent subsystems ("build a platform with chat, file storage, billing, and analytics"), flag it immediately; don't spend questions refining details of something that needs decomposition first. Help decompose into sub-projects (independent pieces, how they relate, build order); each sub-project gets its own spec -> plan -> implementation cycle.
3. **Ask clarifying questions** — one at a time; understand purpose, constraints, success criteria.
4. **Propose 2–3 approaches** — with trade-offs and your recommendation (lead with the recommended option). YAGNI ruthlessly: remove unnecessary features from every approach.
5. **Present design in sections** scaled to their complexity; get approval after each section. If a question would be clearer shown than described (a layout, a diagram), offer a visual mockup then rather than upfront. Cover architecture, components, data flow, error handling, testing.
6. **Design for isolation and clarity** — break the system into smaller units that each have one clear purpose, communicate through well-defined interfaces, and can be understood/tested independently; per unit you should be able to answer: what does it do, how is it used, what does it depend on? A file growing large is usually a signal it's doing too much.
7. **Working in existing codebases** — explore the current structure first; follow established patterns. Where existing problems affect THIS work (a file grown unwieldy, tangled responsibilities), include targeted improvements as part of the design — but no unrelated refactoring.
8. **Write the spec** — save under `docs/specs/YYYY-MM-DD-<topic>-design.md` and commit.
9. **Spec self-review** — quick inline check for placeholders, contradictions, ambiguity, scope creep; fix issues inline (no re-review loop). Optionally dispatch a calibrated subagent review (`conversation-to-spec/references/spec-document-reviewer-prompt.md`) with the rule: only flag gaps that would cause real problems during planning.
10. **User reviews written spec** — ask before proceeding.
11. **Transition to implementation** — create the plan (see `plan`); do NOT invoke any other skill in between.

## Process Flow

```
classify + announce path
        |
   explore context
        |
  clarifying questions (one at a time)
        |
+-------+---------+------------------+
| spike: probe    | bounded: short design in chat
v                 v                  architectural: approaches -> sectioned design
report answer     STOP for approval  write spec -> self-review -> user review
(throwaway only)          |                        |
                         v                        v
                     implement                implementation plan, then build
```

## Notes on the Port

- Upstream's "Visual Companion" (a browser tab opened by a companion skill) and its `writing-plans` handoff are superpowers-internal; here they map to an optional mockup step and this repo's `plan` / `conversation-to-spec` skills.
- The approval gate is the point of the skill, not the design length. If you catch yourself starting implementation before hearing "yes", stop — that is exactly the failure mode this skill exists to prevent.
