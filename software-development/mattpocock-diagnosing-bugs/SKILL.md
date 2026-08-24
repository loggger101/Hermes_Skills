---
name: mattpocock-diagnosing-bugs
description: "Diagnose hard bugs via tight feedback loops and bisection."
version: 1.1.0
author: Adapted from mattpocock/skills
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, diagnosis, bisection, feedback-loops, root-cause, analysis]
    related_skills: [systematic-debugging, mattpocock-tdd, mattpocock-evidence-driven, mattpocock-code-review]

---

## When to Use

Use when the user says "diagnose", "debug this", or reports something broken, throwing, failing, or slow. Also use when auditing artifact quality — e.g. skill libraries, documentation, or configuration — for consistency and completeness. Loads `skill_view(name='systematic-debugging')` for structured debugging, `skill_view(name='mattpocock-evidence-driven')` for verification gates, and `skill_view(name='mattpocock-tdd')` for regression tests.

## What This Skill Does

A discipline for hard bugs. The core technique is building a tight, fast feedback loop that goes red on *this specific bug*, then using bisection/minimization to narrow the cause, form a hypothesis, and verify it. Each phase is a step; skip only when explicitly justified.

## Prerequisites

- Access to the code and the ability to run it (or a test that reproduces the bug)
- The bug is reproducible with some input or scenario
- Ability to use debugging tools: debugger, logs, print statements, `git bisect`

## Redact

Show commands, outputs and captured artifacts. **Redact every secret first**: write `[REDACTED]` in its place.

## Process

### Phase 1: Build a Feedback Loop

**This is the skill.** If you have a **tight** pass/fail signal for the bug (one that goes red on *this* bug), you will find the cause. Be aggressive. Be creative. Refuse to give up.

#### Ways to construct one, in roughly this order:

1. **Failing test** at whatever seam reaches the bug — load `skill_view(name='mattpocock-tdd')` for the test-first workflow
2. **Curl / HTTP script** against a running dev server
3. **CLI invocation** with a fixture input, diffing stdout
4. **Headless browser script** that drives the UI
5. **Replay a captured trace**
6. **Throwaway harness** — minimal subset exercising the bug path
7. **Property / fuzz loop** — run 1000 random inputs
8. **Bisection harness** — automate for `git bisect run`
9. **Differential loop** — old-version vs new-version diff
10. **HITL bash script** — structured human-in-the-loop loop
11. **Library audit** — when the "bug" is sparsity, inconsistency, or missing content in a collection of artifacts

### Phase 2: Tighten the Loop

- **Faster?** Cache setup, skip unrelated init, narrow scope.
- **Sharper signal?** Assert on the specific symptom.
- **More deterministic?** Pin time, seed RNG, isolate filesystem.

### Phase 3: Localise

- **Bisect** (`git bisect run`) if the bug appeared between two states
- **Minimise** the failing input to smallest reproduction
- **Binary search** the code by commenting out sections
- **Add instrumentation** at the seam to observe values

### Phase 4: Hypothesise and Verify

Form a hypothesis: "I believe the bug is X because of Y." Test by changing one thing. If wrong, revise.

### Phase 5: Fix and Regression-Test

Apply the fix. Add a regression test at the seam that goes red on the bug and green with the fix. Run the full test suite. Then load `skill_view(name='mattpocock-evidence-driven')` for the full verification pipeline.

## Feedback Loop Selection Guide

| Bug Type | Best Signal |
|----------|------------|
| Deterministic logic error | Failing test at the unit |
| Intermittent/timing | Property loop with pinned RNG |
| Cross-version regression | `git bisect run` |
| Integration/external | Curl script against service |
| UI visual issue | Headless browser with screenshot diff |
| Performance | Timing loop with instrumentation |
| Data quality | Library audit mode |

## Library Audit Mode

When the "bug" is poor quality across a collection of artifacts (e.g., a skill library), use the same feedback-loop discipline:

1. **Build a signal**: score each artifact on a consistent rubric (see `references/library-audit-methodology.md`)
2. **Tighten**: focus on the lowest-scoring artifacts
3. **Localise**: identify the specific failure (missing section, broken link, sparse content)
4. **Fix**: patch the specific issue
5. **Verify**: re-run the rubric to confirm the fix

## Pitfalls

- **No signal**: Without a tight feedback loop, you're guessing — invest heavily in Phase 1
- **Slow loops**: If each iteration takes minutes, you'll give up — optimise speed in Phase 2
- **Wrong fix**: If you can't reproduce the bug, you can't verify the fix — go back to Phase 1
- **Hidden state**: Non-deterministic bugs often have hidden state (time, network, filesystem) — pin everything
- **Confirmation bias**: The hypothesis should be *tested*, not *confirmed* — design experiments that could disprove it

## Verification

- [ ] A feedback loop was built that goes red on the bug before any fix attempt
- [ ] The loop was tightened for speed and determinism
- [ ] The root cause was localised via bisection or minimization
- [ ] A hypothesis was formed and tested (could be disproven)
- [ ] A regression test was added that goes red without the fix and green with it
- [ ] Full test suite passes after the fix
- [ ] `skill_view(name='mattpocock-evidence-driven')` gates passed

## AspireCURES Context

The weekly pipeline has multiple failure modes: data source API changes, gating logic regressions, rendering bugs on disease pages, commit-agent validation failures. This skill's bisection approach is ideal for tracking down which data source caused a regression. For auditing the skill library itself (e.g., checking all skills for formatting consistency), use the library audit mode and consult the methodology reference.
