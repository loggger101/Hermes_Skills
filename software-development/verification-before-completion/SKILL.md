---
name: verification-before-completion
description: "No completion claims without fresh verification evidence."
version: v0.1.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [verification, evidence-first, completion-gates, anti-hallucination]
    related_skills: [verification-culture, mattpocock-evidence-driven]
---

<!-- source: obra/superpowers (skills/verification-before-completion), ported 2026-09-09 -->
## When to Use

- About to claim work is complete, fixed, or passing — before committing, pushing, creating PRs, or moving to the next task.
- Any expression of satisfaction about work state ("done", "all tests pass", "build succeeds").
- Trusting a subagent's self-report that it finished successfully.

**Don't use** as a substitute for project-level verification culture (`verification-culture`) — this is the per-claim gate; that skill is the standing infrastructure around it.

## What This Skill Does

Enforces one iron law: **NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE.** If you haven't run the verification command in THIS message, you cannot claim it passes. Evidence before assertions, always — violating the letter of this rule is violating its spirit.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: state actual status with evidence
   - If YES: state claim WITH evidence
5. ONLY THEN: make the claim

Skip any step = lying, not verifying
```

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags - STOP

- Using "should", "probably", "seems to".
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!").
- About to commit/push/PR without verification.
- Trusting agent success reports.
- Relying on partial verification.
- Thinking "just this once"; tired and wanting work over.
- **ANY wording implying success without having run verification.**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently (check the diff) |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
OK:   [run test command] [see: 34/34 pass] -> "All tests pass"
NO:   "Should pass now" / "Looks correct"
```

**Regression tests (TDD red-green):**
```
OK: write -> run (pass) -> revert fix -> run (MUST FAIL) -> restore -> run (pass)
NO: "I've written a regression test" without the red step
```

**Build:**
```
OK: [run build] [see: exit 0] -> "Build passes"
NO: "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
OK: re-read plan -> checklist -> verify each item -> report gaps or completion
NO: "Tests pass, phase complete"
```

**Agent delegation:**
```
OK: agent reports success -> check VCS diff -> verify changes -> report actual state
NO: trust the agent's self-report
```

## Scope

Applies to exact phrases, paraphrases and synonyms, implications of success — ANY communication suggesting completion or correctness. Always before committing, PR creation, task completion, moving to the next task, or delegating onward.
