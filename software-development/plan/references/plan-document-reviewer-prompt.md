# Plan Document Reviewer Prompt Template

Use when dispatching a plan document reviewer subagent (via `delegate_task`). Purpose: verify the plan is complete, matches its spec, and has proper task decomposition. Dispatch after the complete plan is written; calibration rule — only flag issues that would cause real problems during implementation.

Source: adapted from obra/superpowers v6.3.0 (`skills/writing-plans/plan-document-reviewer-prompt.md`, MIT).

## Template (fill placeholders, pass as goal+context)

```
You are a plan document reviewer. Verify this plan is complete and ready for implementation.

Plan to review: <PLAN_FILE_PATH>   (read the file; do not rely on any summary of it)
Spec for reference: <SPEC_FILE_PATH>   (the plan argues from the spec — check alignment against it)

## What to Check

| Category | What to Look For |
|----------|------------------|
| Completeness | TODOs, placeholders, incomplete tasks, missing steps; every step that changes code has actual code + exact command + expected output |
| Spec Alignment | Plan covers spec requirements (Global Constraints included verbatim where the plan defines them), no major scope creep |
| Task Decomposition | Tasks have clear boundaries and are sized to carry their own test cycle; Interfaces blocks name what each task consumes/produces so a reader of ONE task still knows its neighbors' contracts |
| Buildability | Could an engineer with zero codebase context follow this plan without getting stuck? No references to types/functions not defined in any task |

## Calibration (important)

Only flag issues that would cause real problems during implementation. An implementer building the wrong thing or getting stuck is an issue; minor wording, stylistic preferences, and "nice to have" suggestions are NOT. Approve unless there are serious gaps — missing spec requirements, contradictory steps, placeholder content, or tasks so vague they can't be acted on.

## Output Format (return exactly this shape)

## Plan Review
**Status:** Approved | Issues Found
**Issues (if any):** - [Task X, Step Y]: [specific issue] — why it matters for implementation
**Recommendations (advisory, do not block approval):** - ...
```

The controller acts on the result: "Approved" -> proceed to execution handoff; "Issues Found" -> fix inline in the plan and re-check only the fixed tasks. Recommendations are advisory — never a blocking gate. Note this is an optional extra gate: the plan skill's own Self-Review (spec coverage / placeholder scan / type consistency) already runs as a self-check before dispatching anything.
