---
name: autoreason-refinement
description: "When LLM self-refinement helps; autoreason loop."
version: 1.0.0
author: Hermes Agent (promoted from research-paper-writing references, 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [autoreason, iterative-refinement, llm-judges, borda-count, self-critique, writing, code]
    related_skills: [research-paper-writing, multi-agent-deliberation, ai-research-integrity, dispatching-parallel-agents]
---

# Autoreason refinement

## What This Skill Does

Answers a question that comes before any "revise it again" loop: will iterating on this output with an LLM make it better or worse? It holds the strategy-selection tree, the autoreason loop (incumbent, critic, author, synthesizer, blind judge panel with Borda count), the scope constraints that make it work, the failure taxonomy and the compute cost. All figures come from the NousResearch/autoreason paper as written up in `references/autoreason-methodology.md`; none was reproduced here.

## When to Use

- About to run critique-and-revise on a draft, script, analysis or task definition and unsure it will converge
- Output quality gets worse with each revision pass, or the model keeps changing things that were fine
- Designing a judge panel for subjective output where no automated score exists
- Not for splitting independent work across agents (`dispatching-parallel-agents`), a multi-agent debate on a decision (`multi-agent-deliberation`), or tuning skill text against a metric (`skill-intake-and-release`)

## Quick Reference

| Situation | Strategy reported to work |
|---|---|
| Objectively checkable task the model solves first time | single pass |
| Objectively checkable, not solved first time | autoreason (structured analysis, then reason-informed revision) |
| Subjective, weak model | single pass; refinement degrades its output |
| Subjective, mid-tier model | autoreason with stronger judges |
| Subjective, frontier model, constrained scope | autoreason |
| Subjective, frontier model, unconstrained | critique-and-revise or single pass; autoreason drifts |
| Best-of-N | almost never; no ranking signal means more mediocre options |

Loop roles, each a fresh agent with no shared context: **critic** (problems only, no fixes), **author B** (revises per critique), **synthesizer** (merges A and B into AB), **judge panel** (blind, randomised labels and order, Borda points 3/2/1). Converged when the incumbent A wins twice in a row. Cost: about 6 calls per pass and 10-15 passes, roughly 60-90 times a single pass.

## Procedure

1. Pick the strategy from the table; if single pass is indicated, stop.
2. Constrain scope before looping: fixed facts, fixed deliverable, fixed structure or a fixed list of changes. An unconstrained task is where synthesis drift appears.
3. Run the loop with isolated roles, at least three valid judges and randomised labels.
4. For writing about experiments, give the critic the ground-truth data; without it the critic invented ablations and confidence intervals in the reported run.
5. Watch for the failure modes: incumbent wins under 15% with the synthesis dominating (drift), judge parse failures (no convergence), all candidates alike (model too weak).
6. Stop on convergence or a budget you set up front; keep the single-pass output as the baseline to compare against.

## Pitfalls

- Looping a weak model: self-refinement lowered its scores below single pass in the reported runs.
- Unconstrained "improve this" prompts on strong models.
- Judges that see authorship or fixed label order.
- Counting a loop with a broken judge parser as converged.
- Quoting the model names and win rates as current: they are the paper's snapshot.

## Verification

- [ ] A baseline single-pass output exists to compare with
- [ ] Scope constraints are written down before the first pass
- [ ] Every pass had at least three valid judge rankings
- [ ] For paper text, the critic had access to the real results
- [ ] Total calls stayed within the budget set at the start

## References

- `references/autoreason-methodology.md` - strategy selection, loop architecture and prompts, Borda scoring, model guide, scope constraints, failure taxonomy, code adaptation, paper-writing application, compute budget
