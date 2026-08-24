---
name: mattpocock-to-tickets
description: "Break a plan or spec into tracer-bullet tickets with edges."
version: 1.1.0
author: Adapted from mattpocock/skills
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [tickets, planning, vertical-slices, blocking-edges, spec-breakdown]
    related_skills: [mattpocock-spec-driven-development, mattpocock-handoff, mattpocock-code-review, github-issues, doc-coauthoring, mattpocock-domain-modeling, mattpocock-subagent-driven-development, hermes-agent]

---

## When to Use

Use when the user wants to turn a spec, plan, or conversation into actionable, implementable tickets. Also use when the user says "break this down into tasks", "create tickets from this spec", or "I have a big feature — help me split it up."

This skill is the planning phase of `skill_view(name='mattpocock-spec-driven-development')`.

## What This Skill Does

Breaks a plan, spec, or conversation into **tickets**: tracer-bullet vertical slices, each declaring what **blocks** it. Each ticket represents a complete path through every layer (schema → API → UI → tests) and is demoable or verifiable on its own.

## Process

### 1. Gather context
Work from conversation context. If a reference is passed (spec path, issue URL), fetch and read it. Load `skill_view(name='doc-coauthoring')` if the spec needs to be written first.

### 2. Explore the codebase
Ticket titles should use domain glossary vocabulary and respect ADRs. Check `CONTEXT.md` or `docs/adr/` for existing terminology. Load `skill_view(name='mattpocock-domain-modeling')` if domain terms are unclear.

### 3. Draft vertical slices
Each slice must be:
- **Complete**: COMPLETE path through every layer (schema, API, UI, tests)
- **Demoable** or verifiable on its own
- **Sized** to fit in a single fresh context window
- **Prefactoring done first** — structural cleanup that enables the slice

**Wide refactors**: use **expand–contract**: add the new form beside the old so nothing breaks.

### Ticket Template

```markdown
# <NN>: <title>
**What to build:** end-to-end behaviour
**Blocked by:** tickets that gate this one
**Status:** ready-for-agent
```

### 4. Publish
- **Local**: one file per ticket under `.scratch/<slug>/issues/<NN>-<slug>.md`
- **GitHub/Linear**: one issue per ticket, blockers first — load `skill_view(name='github-issues')`

## Types of Tickets

| Type | Purpose | Sizing |
|------|---------|--------|
| **Feature** | New behavior | Should be demoable end-to-end |
| **Refactor** | Structural improvement | Should preserve all existing behavior |
| **Bug fix** | Fix broken behavior | Must include a failing test first |
| **Spike** | Research/exploration | Timeboxed; produces a decision, not code |
| **Debt** | Pay down technical debt | Small, isolated, low-risk |
| **Spike → Feature** | Research then implement | Two tickets: investigation, then execution |

## Blocking Edges

Each ticket must declare what **blocks** it (other tickets that must finish first). This is the critical part — without explicit edges, a parallel executor (`skill_view(name='mattpocock-subagent-driven-development')`) will pick up tickets it can't complete.

**Example**:
```
# 3: Implement disease-page renderer
**Blocked by:** #1 (parser seam), #2 (domain model)
**What to build:** Given a disease_data dict, produce complete HTML
```

## Sizing Rules

| Ticket Size | Description | Risk |
|---|---|---|
| **XS** (<1h) | One function, one file | Low — parallelize freely |
| **S** (1-2h) | 2-3 functions or one small module | Low — safe for any agent |
| **M** (2-4h) | Cross-module change with clear spec | Medium — needs capable agent |
| **L** (1d) | Cross-cutting change, needs design | High — split further |
| **XL** (>1d) | Multi-day work | Split. Always split. |

## Pitfalls

- **Horizontal slicing** — "write all the models" then "write all the tests"; instead, cut vertical: each ticket goes through every layer
- **Missing blocking edges** — tickets that depend on unstated work cause deadlocks when run in parallel
- **Oversized tickets** — one ticket touching 10 files is worse than 10 tickets touching 1 file each
- **Vague titles** — "Improve parser" doesn't tell the executor what to build; "Parser returns None abstract instead of crashing on missing field" does
- **Circular dependencies** — ticket A blocked by B, B blocked by A; restructure to break the cycle
- **Forgetting prefactoring** — structural cleanup should happen in its own ticket before feature work

## Verification

- [ ] Every ticket has a clear, testable outcome ("What to build" is complete sentences)
- [ ] Every ticket declares what blocks it (empty is valid only for the root ticket)
- [ ] No ticket is sized XL (>1 day) — all are XS/M/S/L or smaller
- [ ] Tickets are ordered by dependency (blockers first when publishing)
- [ ] Each ticket uses domain vocabulary consistently with CONTEXT.md
- [ ] All tickets together cover the full scope without gaps or overlaps

## AspireCURES Context

When adding a new disease page or refactoring a pipeline stage, use this skill to break work into tracer-bullet tickets. Each ticket = complete slice (data fetch → gate → render → validate) with explicit blocking edges, matching your preparer→executor pattern. For the 9 disease pages, each page = one ticket, blocked by the shared parser and renderer tickets.
