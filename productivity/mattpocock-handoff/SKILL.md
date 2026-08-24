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
    related_skills: [mattpocock-to-tickets, mattpocock-writing-for-agents]
---

## When to Use

Use when the current work needs to be picked up by another agent or session — especially at the boundary between the preparer and executor agents in a two-agent pipeline split.

# Handoff (mattpocock)

Compact the current conversation into a handoff document so another agent can continue the work.

## What a Handoff Document Captures

1. **What was already decided** (design choices, rejected alternatives)
2. **Where the work stands** (completed, in-progress, blocked)
3. **The context the next agent needs** (relevant files, conventions, gotchas)
4. **The next steps** (concrete tasks, in priority order)

## Process

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

## AspireCURES Context

This maps directly to your two-agent split: when the preparer agent finishes (collections, gating, JSON report), generate a handoff document so the executor agent (merges, renders, validates, commits) picks up with full context — no re-alignment needed. Capture: which disease pages were updated, what research was gated, edge cases the gatekeeper flagged, and the exact render+validate+commit sequence.
