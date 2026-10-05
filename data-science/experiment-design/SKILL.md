---
name: experiment-design
description: "A/B test design: metrics, sample size, duration."
version: 1.0.0
author: Hermes Agent (from coreyhaines31/marketingskills ab-testing, tables recomputed 2026-10-05)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ab-testing, experiments, sample-size, statistics, power, mde, guardrails, peeking]
    related_skills: [python-data-science, python-numerics-gotchas, website-audit, cron-job-authoring, evolutionary-ml]
---

# Experiment design and sample size

## What This Skill Does

Gives a design order for controlled experiments (A/B tests, GA tournaments, cron-loop self-checks) and the sample-size and duration arithmetic that decides whether a test is worth running at all. The framing is marketing but the discipline applies to any comparison of two variants on a rate. The sample-size tables in the reference were **recomputed** because the source skill's two tables disagreed with each other and with the standard formula (one about 2.3x too large, one 8-23% too small).

## When to Use

- Planning an A/B or multi-variant test, or deciding whether a page, cohort or evolutionary run has enough volume to test anything
- Attaching a feasibility verdict to a "test X" recommendation in an audit
- Reviewing a result: peeking, wrong baseline, underpowered, segment fishing
- Not for the modelling workflow (`python-data-science`), or regression and inference calls (`python-numerics-gotchas`, statsmodels notes there)

## Design order

1. **Hypothesis** with a mechanism: "if we change X, metric Y improves by at least MDE, because Z."
2. **One change per test**; otherwise a win cannot be attributed.
3. **Three metric tiers, fixed before launch**: one primary, secondary (never decisive), guardrails that must not regress.
4. **Sample size** from baseline rate and minimum detectable effect, then traffic allocation, then client-side vs server-side splitting.
5. **Duration**: at least one full week (two business cycles for B2B, through paydays for e-commerce), and avoid beyond 4 to 8 weeks (novelty wears off, opportunity cost compounds).
6. **Decision rule written at launch**, then analysis against it.

## Sample-size anchors (alpha 0.05 two-sided, 80% power, per variant)

| Baseline | 10% relative lift | 20% | 50% |
|---|---|---|---|
| 1% | 163,095 | 42,693 | 7,750 |
| 3% | 53,211 | 13,914 | 2,518 |
| 5% | 31,234 | 8,158 | 1,471 |
| 10% | 14,751 | 3,841 | 686 |

Always recompute with the real baseline and MDE (formula and checks in the reference); 90% power at a 20% baseline and 10% lift needs 8,714, and alpha 0.01 needs 9,687. With a shared control and Bonferroni, three variants need 1.21x per variant (1.82x total traffic), four need 1.33x (2.67x total): budget total traffic.

## Procedure

1. Get the baseline from the specific page or metric, not a site-wide average.
2. Set the MDE from business impact and what past tests showed; compute the sample; if it is absurd, the change is too small to test.
3. Compute duration as `(sample per variant x variants) / (daily traffic x share exposed)`, then apply the floor and ceiling rules.
4. For segments you will slice, size for the smallest planned segment.
5. Choose fixed-horizon (do not peek) or a sequential method with alpha spending or Bayesian thresholds; never eyeball a fixed-horizon p-value daily.
6. After the test, report per-arm sample sizes, primary delta with interval, secondary metrics, every guardrail and every segment, including negative ones.

## Pitfalls

- Underpowered tests mostly conclude "no difference" and ship nothing; non-significant is not "no effect" when power is low.
- Stopping early because p fell below 0.05 on day 3 of a 14-day plan reintroduces peeking bias.
- A win on the primary with a guardrail breach is not shippable.
- Copying a published table without checking it: recompute.
- Concurrent tests and extra variants divide a fixed traffic budget; run fewer, larger tests.
- For GA or tournament experiments translate "weeks" into whole tournament cycles and add diversity guardrails against strategy collapse.

## Verification

- [ ] Hypothesis names a mechanism and exactly one change
- [ ] Primary, secondary and guardrail metrics and the decision rule are written down before launch
- [ ] Sample size was computed from the real baseline and MDE, and duration respects the floor and ceiling
- [ ] The analysis reports power honestly and every guardrail and segment

## References

- `references/experiment-design-sample-size.md` - full design order, corrected sample-size tables with the formula and cross-checks (statsmodels `NormalIndPower`), multiple-variant multipliers, duration floors and ceilings, the five silent design mistakes, sequential testing, analysis discipline, mapping to GA, cron-loop and audit workflows
