---
name: retro
description: "Retrospective on a session proposing environment fixes."
version: 1.0.0
author: "Matt Pocock (mattpocock/skills, MIT) + Hermes Agent"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [retrospective, environment-improvement, agent-ops, steering-files, tool-economy]
    related_skills: [verification-culture, mattpocock-writing-for-agents]
---

# Retro (Session Retrospective)

## What This Skill Does

Conducts a retrospective on a coding session and proposes **improvements to the agent's environment** — not code fixes. Reads the primary sources of the session (session logs/history; default: current session), hunts for candidates in seven categories, and presents them ordered by severity so the user can pick what becomes an actual change (steering file edit, new check, skill update).

## When to Use

- After a long or painful session ("retro on that", "what should we improve from today?").
- NOT for debugging the work itself — that's `systematic-debugging`. This is about making *the next run* cheaper: navigation, checks, standards, tooling.

## Steps

1. Load `mattpocock-writing-for-agents` for the writing style (proposals must be agent-consumable).
2. Read primary sources of the session in question — search session logs/history on this machine if needed; default to the current one when unspecified.
3. Hunt candidates in these categories:
   - **Navigation** — was finding the right file hard? Hidden dependencies between files? A navigation pointer would help. *Use when* a lookup took long.
   - **Automated checks** — could linting/typing/tests/filesystem-linters have caught an error that actually happened? *Use when* the agent made a mistake a check would catch.
   - **Coding standards** — should the reviewer get a new rule (or lose/clarify one)? *Use when* review failed to catch something.
   - **Global steering file bloat** — are instructions in AGENTS.md better placed as coding standards or automated checks? *Use when* the steering file is large, repo- or user-global.
   - **Tool economy** — expensive tool calls that could be streamlined; token-inefficient custom CLIs/MCPs? *Use when* a call cost more than it should have.
   - **No-ops** — instructions in steering files that don't change behavior at all. *Use when* steering files are unwieldy.
   - **Information access** — missing information the agent needed (dev-server logs teed, read-only third-party access)? *Use when* a crucial fact was unavailable.
4. Present candidates to the user in order of severity. Each proposal: what changed behaviorally, where it lands (file/check/skill), and why it beats doing nothing.

## Reference: implementation vs review

All work passes two stages. The **implementation** agent carries the most context pressure — exploration + writing code + debugging failures. The **review** agent has the least — it receives a diff, no exploration needed. Therefore coding standards belong to the reviewer, not the implementer; put new rules where they get enforced with minimal context cost.

## Where things live
- `AGENTS.md`/steering files: pushed into every agent's context window in this repo — use **incredibly sparingly**, usually only navigation pointers elsewhere.
- Coding standards docs: read during review, not implementation; add navigation pointers to docs folders if a standards file passes ~1000 lines.
- Docs: reference material pointed to by other files — look for existing docs before writing new ones.
- Skills: the right home for procedural knowledge (the description lands in context anyway) and user-invoked commands — follow `mattpocock-writing-for-agents`.
