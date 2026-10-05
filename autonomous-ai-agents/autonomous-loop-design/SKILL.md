---
name: autonomous-loop-design
description: "Design scheduled and goal-seeking agent loops."
version: 1.0.0
author: Hermes Agent (promoted from cron-job-authoring references; marketingskills marketing-loops, ECC loop-design-check)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [loops, autonomous, scheduling, idempotency, goal-design, judge, goodhart, cadence, self-check]
    related_skills: [cron-job-authoring, cron-config-authoring, cron-pipeline-watchdog, verification-culture, experiment-design, dynamic-workflow]
---

# Autonomous loop design

## What This Skill Does

Answers "should this be a loop, and is it specified well enough not to run away?" for two kinds of autonomous loop: **scheduled jobs** that check a signal on a cadence (nine-part anatomy, cadence rule, two-tier action model, state and idempotency, run logging) and **goal-seeking loops** that grind toward a done-criterion (a machine-decidable goal with boundaries, an independent judge, damping, a cheat-catching green-keeper gate). `cron-job-authoring` is where the prompt for such a job gets written; this skill decides what the loop should be.

## When to Use

- Designing a watchdog, monitor, periodic review or a loop that iterates until a test passes
- Reviewing a loop for missing self-check, state, bail-out, or a goal that can be gamed
- Choosing a cadence, or deciding when not to loop at all
- Not for writing the cron prompt body or guardrails (`cron-job-authoring`), JSON job configs (`cron-config-authoring`), or watching other cron jobs (`cron-pipeline-watchdog`)

## The nine parts of a scheduled loop

Check cadence, acts-when, purpose, skills/tools used, loop body, **self-check** (is the signal real or noise, is the sample big enough), **state/idempotency** (last-run marker, dedupe key, cooldown, handled set), **stop/bail-out** (when it skips, halts, escalates or disables itself, including on error), and output. A loop missing self-check, state or bail-out is a way to do the wrong thing on a schedule. Separate "check cadence" from "acts when": most runs of a good loop are "checked, nothing to do".

## Goal-seeking loops

1. **Veto gate** (any miss means do not build one): repeats about weekly or more, verification can be automated, the token budget can take it, and the agent has tools that run the thing and see the result.
2. **Machine-decidable goal**: someone who does not know the domain can run one command and say whether it is done; boundaries sit next to it ("must not delete or weaken tests"); a retry cap then escalation; layered stop conditions; prefer reconciliation against an external fact over self-written assertions.
3. **Loop type**: servo (stops at the goal), regulator (keeps a state healthy, acts past a dead band), poll with an exit, or one of these wrapped in a schedule.
4. **A human owns judgment** (is the goal right, should it stop); the machine owns execution. Hand sign-off to the machine and it sprints toward a goal nobody questioned.
5. **Independent judge and green-keeper gate** (the gate was run with a planted cheat in the reference); five failure modes and their guards are in the reference.

## Procedure

1. Run the veto gate; if it fails, do not loop.
2. Pick the loop type and, for scheduled loops, a cadence matched to how fast the signal changes (rankings weekly, churn daily, mentions daily); over-frequency is the common failure.
3. Fill in all nine parts, naming state and bail-out explicitly; use the two-tier action model for what runs autonomously versus what is staged for a human.
4. Write the goal with its boundary clause and a retry cap; anchor it to an external fact where possible.
5. Add run logging so a vanity loop (activity without outcome) is detectable.
6. Hand the finished spec to `cron-job-authoring` to write the prompt.

## Pitfalls

- Conflating check cadence with action condition: jobs either miss the window or spam.
- Writing the date stamp or state unconditionally instead of only when something changed.
- A goal like "all tests pass" with no boundary: the loop deletes or weakens tests.
- Looping a task with no automated verification, which only amplifies errors.
- Treating over-frequent output as diligence: it trains the human to ignore it.

## Verification

- [ ] All nine parts are specified, including state and bail-out
- [ ] The goal is machine-checkable, has a boundary clause and a retry cap
- [ ] A person owns the question "is the goal still right"
- [ ] Run logs distinguish real outcomes from activity

## References

- `references/loop-engineering.md` - nine-part anatomy, cadence rule, two-tier action model, state and idempotency patterns, run logging as the vanity-loop detector, when not to loop, orchestrating several loops, mapping onto Hermes cron jobs, anti-patterns, banned vocabulary
- `references/loop-goal-design-and-review.md` - decidable goal plus boundary, loop types, plan/build/judge with an independent judge, five failure modes, and a run-measured green-keeper gate that catches a planted cheat
