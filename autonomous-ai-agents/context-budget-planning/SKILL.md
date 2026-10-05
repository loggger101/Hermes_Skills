---
name: context-budget-planning
description: "Prompt-cache placement and route-bound context budgets."
version: 1.0.0
author: Hermes Agent (promoted from hermes-agent references; rlaope/oh-my-hermes run 2026-10-05)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [context, prompt-cache, token-budget, compaction, omh, long-sessions]
    related_skills: [hermes-agent, hermes-integrations, dispatching-parallel-agents, cron-job-authoring]
---

# Context budget planning

## What This Skill Does

Two ideas for long agent sessions. First, keep the prompt prefix byte-stable so provider prefix caches keep hitting. Second, compute a context budget bound to the current model route, so a window change produces a checkpoint obligation instead of a surprise. The budget mechanics were run through oh-my-hermes 3.0.0's `omh context budget-plan`; the cache-placement rules are source-read, and cache hit counters were not observed.

## When to Use

- A long session gets slow or expensive and prompt caching may be defeated
- Switching model route mid-session and needing to know what still fits
- Designing a fan-out of subagents that should share a cached preamble
- Not for diagnosing capped `delegate_task` batches (`hermes-agent`) or splitting work across agents (`dispatching-parallel-agents`)

## Quick Reference

```
usable_budget = context_window - max_output - compaction_reserve - retained_history
```

Cache placement: assemble instruction surfaces in a fixed order with the most stable first; keep volatile values (dates, token counts, git state) in the first user turn or at the tail; append mid-run changes as messages rather than editing the system prompt; keep the tool set fixed mid-session; give fan-outs a byte-identical preamble.

Run results (window 200 000, output 8 000, reserve 4 000, history 20 000): usable 168 000; after a rebind to a 100 000 window, 68 000 with `checkpoint_required`; to 36 000, 4 000 with `overflow_recovery_required`; missing or merely assumed capacity gives a null value and `capacity_unknown_hold`; ten changed rebinds in a row trigger `rebind_loop_hold`.

## Procedure

1. Order the prompt: stable instructions first, volatile values last; confirm regenerating it gives identical bytes.
2. Fix the tool set at session start; avoid connecting or dropping tool servers mid-run.
3. For a fan-out, start every sibling prompt with the same bytes and stagger the first dispatch so it writes the cache.
4. Prepare a budget plan with observed capacity values (each needs an `observed_at` clock); rebind when the route changes.
5. Treat a stale plan as an obligation: checkpoint, shrink the must-keep pack, or review capacity.

## Pitfalls

- Claiming a cache hit rate or saving without the host's usage counters.
- Editing a session-start file mid-run, which rebuilds the whole cache.
- `oh-my-hermes` is not on PyPI; install from git. State goes to `~/.omh` by default, so remove it after experiments or pass `--omh-home`.
- `capacity.json` needs `"schema_version": "route_capacity_input/v1"`; errors print only a class name with exit 2.
- Passing assumed values and expecting a number: assumed fields never produce one.

## Verification

- [ ] The prompt prefix is identical across regenerations
- [ ] Capacity fields are observed, with timestamps, before a plan is trusted
- [ ] A stale plan led to a checkpoint, not silent continuation

## References

- `references/context-budget-and-cache-placement.md` - cache placement rules, budget formula with the eight run results, traps hit running it, already-ported OMH skills
