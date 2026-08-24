---
name: mattpocock-handoff
description: "Compact a conversation into a handoff doc for another agent."
version: 1.0.0
author: Adapted from mattpocock/skills
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [handoff, handoff-doc, continuation, multi-agent, context-transfer]
    related_skills: [mattpocock-to-tickets, mattpocock-writing-for-agents, mattpocock-domain-modeling]
---

## When to Use

Use when the current work needs to be picked up by another agent or session — especially at the boundary between the preparer and executor agents in a two-agent pipeline split. Also use when handing off from a human to an agent, or when a long-running task needs to checkpoint state for later continuation.

## What This Skill Does

Compacts the current conversation context into a structured handoff document that enables a new agent to pick up work without re-aligning. Captures decisions made, context accumulated, and concrete next steps so the receiving agent starts at full velocity.

Loads `skill_view(name='mattpocock-writing-for-agents')` for guidance on writing doc an agent can consume, and `skill_view(name='mattpocock-domain-modeling')` if domain terms have shifted.

## Prerequisites

- A clear receiving agent or session that can read the handoff doc
- A path to write the handoff document (default: `.scratch/handoff.md`)
- The conversation context to hand off is still in memory

## Handoff Document Structure

### 1. Summarise the state
- What problem are we solving?
- What's been built so far?
- What's in progress or blocked?

### 2. Capture decisions
- Every design decision made
- Every alternative considered and why it was rejected
- Every assumption made

### 3. Document the context
- Key files and their roles
- Project conventions and patterns followed
- Gotchas, edge cases discovered
- Dependencies or setup steps

### 4. List next steps
Concrete, actionable tasks in priority order.

### 5. Write and save
Write to the path the user specifies, or `.scratch/handoff.md` by default.

## Handoff Document Template

```markdown
# Handoff: <Brief Description>

## Problem & Context
<What problem we're solving and the background>

## State
- Status: <completed | in-progress | blocked>
- Key files:
  - `<path>`: <role>
  - `<path>`: <role>
- Decisions made:
  | Decision | Chosen | Rejected alternatives |
  |----------|--------|----------------------|
  | <...> | <...> | <...> |

## Assumptions
- <assumption 1>
- <assumption 2>

## Next Steps (in priority order)
1. <concrete task> — estimated effort: <S/M/L>
2. <concrete task> — estimated effort: <S/M/L>

## Gotcha Checklist
- [ ] <known issue or edge case>
```

## Pitfalls

- **Over-documenting**: Don't capture everything — focus on non-obvious decisions and context the receiving agent cannot infer from code
- **Stale state**: The handoff doc captures a point-in-time snapshot — if work continues after writing it, the doc becomes stale
- **Assuming context**: The receiving agent has NOT seen the prior conversation — everything it needs must be in the doc
- **Missing blockers**: Clearly flag any blockers or open questions — the receiving agent should not have to rediscover them
- **Too much code**: Include file paths and key code snippets, not entire files

## Verification

- [ ] Handoff document written to the specified path
- [ ] Next steps are concrete and actionable (not vague "continue work")
- [ ] All key decisions and assumptions are documented
- [ ] Any blockers are flagged and explained
- [ ] The receiving agent can start work without asking clarifying questions

## AspireCURES Context

This maps directly to the two-agent split: when the preparer agent finishes (collections, gating, JSON report), generate a handoff document so the executor agent (merges, renders, validates, commits) picks up with full context — no re-alignment needed. Capture: which disease pages were updated, what research was gated, edge cases the gatekeeper flagged, and the exact render+validate+commit sequence.
