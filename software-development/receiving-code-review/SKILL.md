---
name: receiving-code-review
description: "Verify review feedback against the codebase before acting."
version: v0.1.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [code-review, feedback-handling, pushback, yagni, verification]
    related_skills: [requesting-code-review, github-code-review, mattpocock-code-review]
---

<!-- source: obra/superpowers (skills/receiving-code-review), ported 2026-09-09 -->
## When to Use

- You receive code review feedback — from the user, a teammate, or an external reviewer/agent — and are about to implement it.
- Feedback seems unclear, technically questionable, or conflicts with prior decisions.
- A multi-item review needs triage before any changes land.

**Don't use** for self-review of your own uncommitted work (see `requesting-code-review`) or for conducting reviews of others' PRs (`github-code-review`, `mattpocock-code-review`).

## What This Skill Does

Code review reception with technical rigor: read feedback without reacting, restate the requirement, verify it against codebase reality, evaluate whether each item is sound *for this stack*, then respond — implement or push back with reasoning. No performative agreement, no blind implementation. Technical correctness over social comfort.

## The Response Pattern

```
WHEN receiving code review feedback:

1. READ: Complete feedback without reacting
2. UNDERSTAND: Restate requirement in own words (or ask)
3. VERIFY: Check against codebase reality
4. EVALUATE: Technically sound for THIS codebase?
5. RESPOND: Technical acknowledgment or reasoned pushback
6. IMPLEMENT: One item at a time, test each
```

## Forbidden Responses

**NEVER:**
- "You're absolutely right!" (performative)
- "Great point!" / "Excellent feedback!" (performative)
- "Let me implement that now" (before verification)

**INSTEAD:**
- Restate the technical requirement.
- Ask clarifying questions.
- Push back with technical reasoning if wrong.
- Just start working (actions > words).

## Handling Unclear Feedback

```
IF any item is unclear:
  STOP - do not implement anything yet
  ASK for clarification on unclear items

WHY: Items may be related. Partial understanding = wrong implementation.
```

**Example:**
```
user: "Fix 1-6"
You understand 1,2,3,6. Unclear on 4,5.

WRONG: Implement 1,2,3,6 now, ask about 4,5 later
RIGHT: "I understand items 1,2,3,6. Need clarification on 4 and 5 before proceeding."
```

## Source-Specific Handling

### From the user (you)
- **Trusted** — implement after understanding.
- **Still ask** if scope unclear. No performative agreement; skip to action or a technical acknowledgment.

### From External Reviewers
```
BEFORE implementing:
  1. Check: Technically correct for THIS codebase?
  2. Check: Breaks existing functionality?
  3. Check: Reason for current implementation?
  4. Check: Works on all platforms/versions?
  5. Check: Does reviewer understand full context?

IF suggestion seems wrong: push back with technical reasoning.
IF can't easily verify: say so — "I can't verify this without [X]. Should I investigate, ask, or proceed?"
IF conflicts with the user's prior decisions: stop and discuss with the user first.
```

Standing rule: external feedback — be skeptical, but check carefully.

## YAGNI Check for "Professional" Features

```
IF reviewer suggests "implementing properly":
  grep codebase for actual usage
  IF unused: "This endpoint isn't called. Remove it (YAGNI)?"
  IF used: then implement properly
```

Standing rule: if the user and the reviewer both report to the same owner, and we don't need this feature, don't add it.

## Implementation Order

```
FOR multi-item feedback:
  1. Clarify anything unclear FIRST
  2. Then implement in this order:
     - Blocking issues (breaks, security)
     - Simple fixes (typos, imports)
     - Complex fixes (refactoring, logic)
  3. Test each fix individually
  4. Verify no regressions
```

## When To Push Back

Push back when:
- Suggestion breaks existing functionality.
- Reviewer lacks full context.
- Violates YAGNI (unused feature).
- Technically incorrect for this stack.
- Legacy/compatibility reasons exist.
- Conflicts with the user's architectural decisions.

**How to push back:** technical reasoning, not defensiveness; specific questions; reference working tests/code; involve the user if it is architectural. If you're uncomfortable pushing back out loud: name that tension, then tell the user about the issue you've seen — they'll appreciate the honesty.

## Acknowledging Correct Feedback

When feedback IS correct:
```
OK:   "Fixed. [Brief description of what changed]"
OK:   "Good catch - [specific issue]. Fixed in [location]."
OK:   Just fix it and show in the code.

NO:   "You're absolutely right!" / "Great point!" / "Thanks for catching that!" / ANY gratitude expression
```

**Why no thanks:** actions speak; just fix it — the code itself shows you heard the feedback. If you catch yourself about to write "thanks": delete it, state the fix instead.

## Gracefully Correcting Your Pushback

If you pushed back and were wrong:
```
OK:  "You were right - I checked [X] and it does [Y]. Implementing now."
OK:  "Verified this and you're correct; my initial understanding was wrong because [reason]. Fixing."

NO:  Long apology, defending why you pushed back, over-explaining.
```
State the correction factually and move on.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Performative agreement | State requirement or just act |
| Blind implementation | Verify against codebase first |
| Batch without testing | One at a time, test each |
| Assuming reviewer is right | Check if it breaks things |
| Avoiding pushback | Technical correctness > comfort |
| Partial implementation | Clarify all items first |
| Can't verify, proceed anyway | State limitation, ask for direction |

## Real Examples

**Performative agreement (bad):**
```
Reviewer: "Remove legacy code"
WRONG: "You're absolutely right! Let me remove that..."
```

**Technical verification (good):**
```
Reviewer: "Remove legacy code"
RIGHT: "Checking... build target is 10.15+, this API needs 13+. Need the legacy path for backward compat. Current impl has the wrong bundle ID — fix it or drop pre-13 support?"
```

**YAGNI (good):**
```
Reviewer: "Implement proper metrics tracking with database, date filters, CSV export"
RIGHT: "Grepped codebase - nothing calls this endpoint. Remove it (YAGNI)? Or is there usage I'm missing?"
```

## GitHub Thread Replies

When replying to inline review comments on GitHub, reply in the comment thread (`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`), not as a top-level PR comment.
