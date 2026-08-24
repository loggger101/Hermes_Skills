---
name: mattpocock-subagent-driven-development
description: "Dispatch fresh subagents per task with task review."
version: 1.0.0
author: Adapted from obra/superpowers
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [subagents, delegation, task-review, parallel-agents, planning]
    related_skills: [delegate-task, mattpocock-to-tickets, mattpocock-multi-agent-code-review, mattpocock-using-git-worktrees, mattpocock-finishing-a-development-branch]
---

## When to Use

Use when executing implementation plans with mostly independent tasks. Dispatch a fresh subagent per task, review after each, and do a broad whole-branch review at the end. Also useful when the user says "parallelize this", "spawn subagents for each task", or "implement this plan across multiple files".

## What This Skill Does

Executes a plan by dispatching a fresh implementer subagent per task, a task review (spec compliance + code quality) after each, and a broad whole-branch review at the end.

**Core principle:** Fresh subagent per task + task review (spec + quality) + broad final review = high quality, fast iteration

**Why subbots:** You delegate tasks to specialized agents with isolated context. They should never inherit your session's context or history.

## The Process

### Per Task Loop

1. **Dispatch the implementer** — construct exactly what they need (no session context bleed)
2. **Task review** — spec compliance + code quality check
3. **Fix loop** (if needed) — up to 5 rounds: R≤3 resume implementer, R≥4 fresh implementer with more capable model
4. **Append completion to ledger** — record decisions, commits, review outcome

## Setup
- Use `skill_view(name='mattpocock-using-git-worktrees')` to ensure an isolated workspace
- Read the plan file once — load `skill_view(name='mattpocock-to-tickets')` if tickets need to be created from a spec
- Verify the ledger belongs to this plan (not a sibling)
- Run pre-flight tests as baseline — load `skill_view(name='test-driven-development')` for RED base if needed

### Final Review
- Dispatch `skill_view(name='mattpocock-multi-agent-code-review')` for the broad whole-branch review
- Review the full branch diff against the plan
- If clean: delete the plan's workspace (`rm -rf <workspace>`)
- Use `skill_view(name='mattpocock-finishing-a-development-branch')` to integrate

### Model Selection

| Task Type | When to Use | Model |
|-----------|-------------|-------|
| **Mechanical** | 1-2 files, complete spec, low ambiguity | Fast, cheap (e.g. o3-mini) |
| **Integration** | Multi-file changes, moderate complexity | Standard (Claude Sonnet) |
| **Architecture** | Design decisions, new abstractions | Most capable (Opus/4) |
| **Final review** | Quality gate on the whole branch | Most capable |

## Pitfalls

- **Context bleed** — subagents inheriting session history; always pass a clean, self-contained prompt
- **Oversized tasks** — one subagent handling 10 files is worse than 10 subagents handling 1 file each; keep tasks at "fits in one context window" sized
- **Skipping task review** — the whole point is independent verification; don't just merge blindly
- **Too many retry rounds** — R≥4 means the spec is wrong, not the implementation; pause and fix the spec
- **Ledger divergence** — if the ledger drifts from actual state, the final review is meaningless
- **Forgetting to clean up** — leaving workspaces around wastes disk and clutters git

## Verification

- [ ] Each subagent received a self-contained prompt with no session context bleed
- [ ] Pre-flight tests established a GREEN baseline before implementation
- [ ] Each task review checked both spec compliance AND code quality
- [ ] All retry rounds ≤3 (R≤3 resume implementer, R≥4 gets fresh agent)
- [ ] Final review covered the full branch diff against the original plan
- [ ] Workspace was cleaned up after successful merge

## AspireCURES Context

Your two-agent split maps closely to this: the preparer agent collects/gates/emits JSON (the "plan" in structured form), then the executor can use subagent-driven development to implement changes across the 9 disease pages independently. Each disease page = one subagent task, reviewed before merge.
