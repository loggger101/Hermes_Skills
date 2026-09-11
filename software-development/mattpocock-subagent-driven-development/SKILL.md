---
name: mattpocock-subagent-driven-development
description: "Dispatch fresh subagents per task with task review."
version: 2.0.0
author: Adapted from obra/superpowers v6.3.0 (SDD lifecycle restructure)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [subagents, delegation, task-review, parallel-agents, planning]
    related_skills: [mattpocock-to-tickets, mattpocock-multi-agent-code-review, mattpocock-using-git-worktrees, mattpocock-finishing-a-development-branch, requesting-code-review, mattpocock-evidence-driven, test-driven-development, executing-plans, dispatching-parallel-agents]

---
<!-- source: obra/superpowers (skills/subagent-driven-development v6.3.0), adapted 2026-09-11 -->

## When to Use

Use when executing implementation plans with mostly independent tasks in the current session. Dispatch a fresh subagent per task, review after each, and do a broad whole-branch review at the end. Also useful when the user says "parallelize this", "spawn subagents for each task", or "implement this plan across multiple files".

**Routing:** if the work is small/coupled or the user wants to watch it happen in-session, use `executing-plans` instead (inline with checkpoints). If there are 2+ *independent failure domains* to investigate rather than a task list to execute, use `dispatching-parallel-agents`.

## What This Skill Does

Executes a plan by dispatching a fresh implementer subagent per task, a task review (spec compliance + code quality) after each, and a broad whole-branch review at the end. Loads `skill_view(name='mattpocock-evidence-driven')` for verification gates and `skill_view(name='mattpocock-multi-agent-code-review')` for the final broad review.

**Core principle:** Fresh subagent per task + task review (spec + quality) + broad final review = high quality, fast iteration.

## Operating Posture

- **Narrate minimally.** Between tool calls: at most one short line — the ledger and tool results carry the record.
- **Continuous execution.** Do NOT pause to check in between tasks; "should I continue?" prompts waste the user's time. The ONLY stops are the four below or completion.
- **Rulings, not stalls.** A running plan does not wait on a human: conflicts, ambiguities, plan defects — DECIDE them yourself (spec is binding authority, plan is its argument, your judgment settles the rest), record every decision in the ledger as `Ruling: <what> — <why> — <cost if wrong>`, and keep going. A wrong ruling costs rework; a session parked on a question costs the user's whole day.
- **Four-and-only-four stop conditions:** (1) irreversible/destructive operation; (2) security-sensitive action; (3) side effect outside this worktree that norms say to ask about first (merge, push to shared branch, publish); (4) plan so broken every path forward is a guess.

## Setup

- Use `skill_view(name='mattpocock-using-git-worktrees')` to ensure an isolated workspace; never start on main/master without explicit consent.
- **Plan-scoped workspace:** give each plan its own scratch dir, e.g. `.superpowers/sdd/<plan-basename>/` (gitignored). Home for the ledger, task briefs, implementer reports, and review packages. Another plan's directory is never yours to read or write — a stale foreign ledger misread as progress makes controllers skip whole task sequences; plan-scoping removes that failure structurally.
- **The ledger** (`<workspace>/progress.md`) is the durable record: conversation memory does not survive compaction, and controllers that lost their place have re-dispatched entire completed task sequences — the single most expensive observed failure. First line names the plan file; every completion/fix/ruling line carries commit ranges so `git log` can cross-check. After any compaction, trust ledger + git log over recollection: tasks marked complete are DONE (do not re-dispatch); resume at the first incomplete one.
- Read the plan once; note Global Constraints and create a todo per task. If the plan names a spec, read it — conflicts inside the plan resolve against the spec.
- **Pre-flight conflict scan** before dispatching Task 1: scan the whole plan for (a) tasks contradicting each other or Global Constraints, (b) anything the plan explicitly mandates that review would flag as a defect (assertion-free tests, verbatim duplication). Output is A TABLE — one row per pair of tasks sharing a file/interface + one self-consistency row per task. "The scan is clean" without rows = not a scan you ran. Write it to the ledger and rule on everything before execution begins.
- Run pre-flight tests as baseline (GREEN) — load `skill_view(name='test-driven-development')` for RED base if needed.

## Model Selection

Least powerful model that can handle the role; **always specify the model explicitly** when dispatching — an omitted model silently inherits the session's most expensive one, which defeats this section. Turn count beats token price: cheap models take 2-3x turns on multi-step work. Plan text containing complete code = transcription + testing -> cheapest tier.

| Task Type | When to Use | Model |
|-----------|-------------|-------|
| **Mechanical** | 1-2 files, complete spec, low ambiguity (most tasks when the plan is well-specified) | Fast, cheap |
| **Integration** | Multi-file coordination, pattern matching, debugging | Standard |
| **Architecture** | Design decisions, new abstractions; fix-loop rounds 4-5 (at least one tier above the stuck implementer) | Most capable |
| **Final review** | Whole-branch quality gate — MUST be most capable available, not session default | Most capable |

## Per Task Loop

1. **Record BASE** (`git rev-parse HEAD`) before dispatching — review packages and fix-round diffs need it (never `HEAD~1`, which silently drops all but the last commit of a multi-commit task).
2. **Dispatch the implementer.** The brief is the single source of requirements: extract this one task's full text to `<workspace>/task-N-brief.md` ("read this first — exact values verbatim"). Dispatch = (a) one line on where the task fits, (b) brief path, (c) interfaces/decisions from earlier tasks the brief can't know, (d) your ruling if any ambiguity was noticed, (e) report-file path + contract. **Never make a subagent read the whole plan file; never paste accumulated prior-task summaries** — everything pasted into a prompt stays resident in YOUR context on every later turn ("a real session's dispatch hit 42k chars of which 99% was pasted history"). Contract: implementer does all work itself, NEVER spawns subagents (especially reviewers), writes its FULL report to the named file and returns only status + commits + one-line test summary + concerns. Statuses: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED — for BLOCKED assess: context problem -> more context same model; needs reasoning -> bigger model; too large -> split; plan wrong -> rule on correction, ledger it, re-dispatch with the ruling carried in dispatch.
3. **Task review (task-scoped gate).** Hand artifacts over as FILES: write commit list + `git diff --stat` + full `git diff -U10 BASE..HEAD` to `<workspace>/review-<base7>..<head7>.diff`; reviewer reads brief file + report file + that one diff file, plus Global Constraints copied verbatim. Two mandatory verdicts — spec compliance (Missing / Extra / Misunderstood) AND code quality; a report missing either is rejected. Reviewer rules: read-only, no crawling beyond concrete NAMED risks, do not re-run the suite to confirm the report's evidence, and **no pre-judging directives** in your prompt ("do not flag", "at most Minor" = you are coaching the review). ⚠️ items (requirement lives in unchanged code) must be resolved by YOU before marking complete — controller holds cross-task context.
4. **Fix loop (max 5 rounds per task).** Trigger: spec ❌, any Critical/Important finding, or a confirmed ⚠️ gap. Two routes leave the loop immediately: *Minor* findings -> ledger as `Task N: minor (deferred)` for final-review triage ("a roll-up nobody reads is a silent discard"); plan-mandated/conflicting-with-plan findings -> rule on them and LEDGER THE RULING before acting. Rounds 1-3: RESUME the original implementer with open findings verbatim — its context is intact (fallback if you can't message it: fresh dispatch carrying brief + report file paths; "the report file is the persistent memory either way"). Rounds 4-5: FRESH implementer on a more capable model, framed as "a prior implementer attempted this N times; read the report for what was tried." Every round ends with fix + covering tests re-run (evidence in the SAME report file) + ONE SCOPED re-review over just the findings list and the fix diff — out-of-scope observations go to the ledger, never extend the loop.
5. **The breaker.** If round 5 still leaves findings open: stop dispatching; adjudicate each one yourself — reviewer wrong -> park with ruling "why the code stands"; real but nothing builds on it -> park "real and deferred"; real AND load-bearing (later task depends, or plan defect) -> rule on the smallest unblocking change, ledger it, carry into next dispatch. Adjudicate ONLY at the cap; every adjudication is a ledger entry — silent discards are forbidden.
6. **Complete.** Clean review OR all open findings parked-with-ruling at cap: append `Task N: complete (commits <base7>..<head7>, [K] parked)`, mark todo, move on. Never proceed while Critical/Important issues are neither fixed nor parked-with-ruling.

**Batching:** several small same-shape tasks of the SAME kind -> ONE dispatch listing every file+change, one review unit — reserve one-dispatch-per-task for work needing its own judgment/tests/review surface. **Never dispatch multiple implementation subagents in parallel (conflicts).** While children run: keep doing local work; when genuinely idle wait in bounded 5-10 min stretches with a status line between them and reconcile live children (chase any that finished without reporting).

## Final Review

Package the whole branch (`git diff` from merge-base) to one file. Dispatch on the MOST CAPABLE model using `skill_view(name='mattpocock-multi-agent-code-review')`; point it at the ledger's deferred-minor and parked lines so it triages pre-merge fixes. If findings: dispatch ONE fix subagent with the complete list (not one per finding — "a real session's final-review fix wave cost more than all its tasks combined"), then exactly ONE scoped re-review; adjudicate residuals as in the breaker. No second fix wave — residual load-bearing findings surface when finishing presents the options.

**Finish report:** before deleting anything, collect EVERY ledger line containing `Ruling:` (preflight rulings, parked findings, breaker adjudications) into a "Rulings I made" list, each with what it costs if wrong. That list is the only place on-behalf decisions reach the user — "a ruling that dies with the workspace was a decision made in secret." When final review is clean: delete this plan's workspace (git history is the record now; leave sibling plans' dirs alone), then `skill_view(name='mattpocock-finishing-a-development-branch')`.

## Pitfalls

| Excuse | Reality |
|--------|---------|
| "I'll fix it myself, dispatching is overhead" | Controller fixes pollute your context and skip review. Resume the implementer. |
| "One more round will converge" | Past the cap, rounds don't converge — the failure is structural. Adjudicate and route. |
| "This finding is obviously wrong, I'll drop it" | You adjudicate only at the cap, and every ruling is a ledger entry. Silent discards are forbidden. |
| "The fix was small, skip the re-review" | Unreviewed fixes are how regressions land. Every round ends with a scoped re-review. |
| "Ledger bookkeeping is overhead" | The ledger is what survives compaction. Controllers without one have re-dispatched entire completed task sequences. |
| "The implementer spawned its own reviewer — free extra assurance" | It's a duplicate seat reviewing the same diff; worker-spawned reviewers are a defect to flag, not rigor. |
| Context bleed | Subagents must never inherit session history; always pass clean, self-contained briefs (file handoff, not pasting). |
| Oversized tasks | One subagent handling 10 files is worse than 10 subagents handling 1 file each; keep tasks "fits in one context window". |

## Verification

- [ ] Each plan has its own workspace dir + ledger naming the plan on line 1
- [ ] Pre-flight conflict scan table written to ledger before Task 1 dispatched
- [ ] Every dispatch named a model explicitly and handed artifacts by file path (no pasted history)
- [ ] Each task review checked BOTH spec compliance AND code quality against a diff file
- [ ] Fix rounds ≤5; round 4+ used fresh implementer on higher tier; breaker adjudications ledgered with cost-if-wrong
- [ ] Final review ran on most-capable model and triaged the deferred-minor roll-up
- [ ] "Rulings I made" list delivered to user before workspace deletion

## AspireCURES Context

Your two-agent split maps closely to this: the preparer agent collects/gates/emits JSON (the "plan" in structured form), then the executor can use subagent-driven development to implement changes across the 9 disease pages independently. Each disease page = one subagent task, reviewed before merge — a natural plan-scoped workspace per weekly run keeps ledgers from contaminating each other between runs.
