---
name: feature-flag-lifecycle
description: "Flag types, rollout maths, kill switches, cleanup."
version: 1.0.0
author: Hermes Agent (promoted from system-design-scaling references; alirezarezvani/claude-skills feature-flags-architect, scripts run 2026-10-05)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [feature-flags, progressive-delivery, canary, rollout, kill-switch, flag-debt, release]
    related_skills: [system-design-scaling, incident-response, failure-signal-audit, experiment-design, github-pr-workflow]
---

# Feature-flag lifecycle

## What This Skill Does

Treats a feature flag as a controlled lifecycle (`request -> design -> ship -> ramp -> cleanup -> archive`) and the debt as the flags that never reach cleanup. It holds flag types and their lifespans, rollout schedules with measured results from three stdlib scripts (run against a planted git repo), the registry fields that make a kill switch real, and the traps in those scripts.

## When to Use

- A design says "ship behind a flag", "canary" or "ramp to 100%"
- Planning a rollout schedule, defining a kill switch, or hunting stale flags
- Reviewing flag scripts before trusting their output
- Not for A/B test statistics (`experiment-design`), live incident command (`incident-response`), or general scaling design (`system-design-scaling`)

## Flag types decide the lifespan

| Type | Purpose | Lifespan | Cleanup trigger |
|---|---|---|---|
| Release | hide unfinished work | days to weeks | 100% reached, then delete the branch |
| Experiment | A/B variants | weeks | winner picked |
| Operational | kill switches, circuit breakers | months to years | feature retired |
| Permission | entitlements per plan or account | permanent | plan removed |

Only Release and Experiment flags belong on a stale-flag watchlist. A permanent `if (FLAG_X)` repeated across the code is a Permission flag in disguise: move it to runtime config. Target: retire a Release flag within 60 days of reaching 100%.

## Procedure

1. Classify the flag and write its registry entry before the code: owner, type, kill-switch trigger, dashboard, abort threshold.
2. Deploy at 0%, prove the kill switch in staging, then ramp starting at 1% or an internal cohort.
3. Pick the rollout shape: `ring` (1, 5, 25, 50, 100%), `linear`, `log` or `cohort`. Replace the generated abort text (`error_rate > baseline + 1pp OR p99_latency > baseline * 1.2`) with metrics that fit the feature.
4. After 100%, schedule cleanup within the lifespan and delete the flag and its dead branch.
5. Scan for stale flags regularly and check every flag has a kill-switch entry.

## Measured script behaviour (population 100,000)

- `ring`, 14 days, target 100: stops on days 0, 3, 6, 9, 12, so it ends on day 12, not 14 (interval is `duration // (stops-1)`).
- `linear`, 14 days, target 50: 3.57% per day with no canary stage; the first phase exposes 3,570 users.
- `log`, 14 days: **25.6% on day 0**, so only use after a ring canary.
- `cohort`: percentages are `target / 5` steps, so "internal" is sized at 20,000 users; treat cohort names as an order, not sizes.

## Pitfalls

- Starting a ramp at a tenth of the users.
- Letting a Release flag become permanent.
- Trusting generated abort criteria without adjusting them.
- Kill switches with no owner or no tested path.
- Quoting the script traps for other versions: run the scripts again.

## Verification

- [ ] Every flag has a type, owner, kill-switch trigger and dashboard
- [ ] The kill switch was exercised in staging before the ramp
- [ ] The ramp starts at 1% or an internal cohort with real abort metrics
- [ ] A cleanup date exists for every Release and Experiment flag

## References

- `references/feature-flag-lifecycle.md` - flag types and lifespans, rollout schedules with run results, kill-switch registry fields, stale-flag detection, and the traps in the three source scripts
