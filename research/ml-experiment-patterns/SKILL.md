---
name: ml-experiment-patterns
description: "ML experiment infrastructure, evaluation and recovery."
version: 1.0.0
author: Hermes Agent (promoted from research-paper-writing references, 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [experiments, evaluation, blind-judges, statistics, monitoring, failure-recovery, figures, benchmarks]
    related_skills: [research-paper-writing, experiment-design, human-evaluation-design, autoreason-refinement, python-plotting]
---

# ML experiment patterns

## What This Skill Does

Patterns from running research experiments at scale with an agent: directory layout and crash-safe scripts, evaluation protocols (blind judge panels, objective code evaluation, compute-matched comparison), required statistical tests and reporting standards, a cron monitoring pattern, failure recovery with a pre-flight checklist, benchmark and task design, and figure conventions for papers. The full text is in `references/experiment-patterns.md`.

## When to Use

- Setting up a batch of model runs that must survive crashes, rate limits and credit exhaustion
- Choosing how to evaluate subjective or code outputs and which tests to report
- Designing tasks for a benchmark, including constrained tasks that test scope effects
- Making paper figures with a consistent, colourblind-safe style
- Not for A/B tests on live traffic (`experiment-design`), human annotation studies (`human-evaluation-design`), or the paper pipeline (`research-paper-writing`)

## Quick Reference

| Topic | Pattern |
|---|---|
| Layout | `experiments/` for runners and config, `results/<experiment>/<task>/<strategy>/` with `result.json`, `final_output.md`, `history.json` |
| Scripts | save after every unit of work and skip finished work on restart |
| Subjective evaluation | blind judge panels with randomised labels and order |
| Comparison | compute-matched, so methods get the same budget |
| Tests | McNemar for two methods on the same problems, Fisher's exact for small samples, two-proportion z-test, bootstrapped CIs, Cohen's h for effect size |
| Reporting | sample size, number of runs, error bars, 95% CIs, p-values, effect sizes |
| Retries | suffix log names by round (`_r2`, `_r3`) |
| Parallelism | cut to 2-3 experiments at once if each slows to twice its time |

## Procedure

1. Create the directory layout and a shared config; make every script resumable.
2. Run the pre-flight checklist: credits, model IDs tested on one problem, writable output, resume logic, unique log path, task files reachable, config matches intent.
3. Launch, and monitor with a cron job that reports progress and errors.
4. On failure, match the symptom to the recovery table (402 credit exhaustion, 429 rate limits, crash, wrong model ID, timeout on a hard problem) and re-run under a new suffix.
5. Analyse with the required tests and report every item in the reporting standards.
6. Draw figures with the documented palette and sizes.

## Pitfalls

- Overwriting earlier logs or results on a re-run.
- Skipping the one-problem test of a model ID.
- Reporting means without sample sizes or intervals.
- Comparing methods with unequal compute.
- Treating the Haiku 3.5 and model-name examples as current.

## Verification

- [ ] Re-running a script does not overwrite finished results
- [ ] Pre-flight checklist ticked before each batch
- [ ] Every key comparison has a test, a CI and an effect size
- [ ] Figures use the stated palette and two-column sizes

## References

- `references/experiment-patterns.md` - infrastructure, evaluation protocols, statistics, monitoring, code experiments, failure recovery, task and benchmark design, visualisation
