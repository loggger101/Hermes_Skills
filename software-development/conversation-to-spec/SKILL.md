---
name: conversation-to-spec
description: "Turn a conversation into a publishable spec"
version: v0.9.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [specs, planning, documentation]
    related_skills: [grilling-interview, mattpocock-spec-driven-development]
---


<!-- source: mattpocock/skills (engineering/to-spec), ported 2026-09-05 -->
## When to Use

- "Spec this out" after a design discussion
- Handing work to another agent/session

## What This Skill Does

1. Explore the repo to understand current state (if not done). Use the project's domain glossary vocabulary throughout; respect ADRs in the area being touched. 2. Sketch the **seams** at which you'll test the feature. Prefer existing seams over new ones, and use the highest seam possible — fewer sea


# Conversation → Spec

Take the current conversation context and codebase understanding and produce a spec. **Do NOT interview the user** — synthesize what you already know. If something essential is genuinely missing, note it as an open question in Further Notes rather than stalling.

## Process
1. Explore the repo to understand current state (if not done). Use the project's domain glossary vocabulary throughout; respect ADRs in the area being touched.
2. Sketch the **seams** at which you'll test the feature. Prefer existing seams over new ones, and use the highest seam possible — fewer seams is better; ideal is one. If new seams are needed, propose them at the highest point available. Check with the user that these seams match their expectations (this is the only confirmation step).
3. Write the spec from the template below and publish it: GitHub issue (`gh issue create`) when a tracker exists, else `.specs/<slug>.md` in the repo root or project docs dir.

## Spec template

```markdown
# <Feature name> — Spec

## Problem Statement
The problem the user is facing, from the user's perspective.

## Solution
The solution to the problem, from the user's perspective.

## User Stories
A LONG numbered list covering all aspects of the feature:
1. As an <actor>, I want a <feature>, so that <benefit>

## Implementation Decisions
Modules built/modified; their interfaces; technical clarifications; architectural decisions; schema changes; API contracts; specific interactions.
Do NOT include file paths or code snippets — they go stale fast.
Exception: if a prototype produced a snippet encoding a decision more precisely than prose (state machine, reducer, schema, type shape), inline it in the relevant decision and note it came from a prototype. Trim to decision-rich parts only.

## Testing Decisions
What makes a good test here (only external behavior, not implementation details); which modules get tested; prior art — similar existing tests to model on.

## Out of Scope
Things explicitly out for this spec.

## Further Notes
Open questions, risks, follow-ups.
```
