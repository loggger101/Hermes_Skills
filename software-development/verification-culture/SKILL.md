---
name: verification-culture
description: "Doc-driven verification: backlog, audits, regression."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [documentation, verification, backlog-discipline, audit-passes, regression-capture, todo-management, reconciliation, health-checks, CI-gating]
    category: software-development
    related_skills: [python-craft, test-infra-ml, cli-tool-craft]
---

# Documentation-Driven Verification Culture

Guide for building and maintaining a project's verification culture — the backlog discipline, audit passes, regression capture, health checks, and standing rules that keep a complex project honest over time. Drawn from aspirecures's TODO.md (556-line single-source backlog with per-item status, owner, and verified flags) and CR-pipeline's SESSION_SUMMARY.md (chronological defect history with defect→effect→fix tables).

## When to Use

- You have a complex project with many moving parts and want a single source of truth for what's done, what's open, and what's verified.
- You want audit passes that actually catch things (not just re-read the same doc and call it verified).
- You want to capture defects in a form that prevents reintroduction (defect→effect→fix tables, regression tests that name the defect).
- You want standing rules that constrain future work (rules that, if broken, silently undo something that already works).
- You want health checks that run in CI and gate deploys (not just nice-to-have linters).

**Don't use** a heavy documentation process for a small project that can be fully understood in one sitting. The overhead is for projects where the cost of losing track of something is high (patient data, revenue, a training run that took days, a site that's live and serving real users).

## The Single-Source Backlog

One file that is the only list of open work. Not three files. Not "TODO.md plus the issues plus my memory plus the chat history."

**What it contains:**
- Every open item, in one place.
- For each item: what it is, who does it (owner), what status it's in, and (when relevant) what blocks it.
- Status levels that mean something: todo, in-progress, done, verified-done, blocked (and what blocks it).
- The last reconciliation date — when someone last scanned the whole repo and confirmed the backlog matches reality.

**What it doesn't contain:**
- Descriptions of how things work (that's architecture docs, not the backlog).
- History of what was done (that's git, or a changelog, not the backlog).
- Duplicate entries (if an item appears in two places, it's not a single source).

**The rule:** if something is open, it's in the backlog. If it's not in the backlog, it's not open. If the backlog says something is done, you can trust it (because the last reconciliation confirmed it).

**Owner labels (the aspirecures pattern):**
- 🧑 = only the owner can do it (a dashboard, a decision, a phone call, a number, something that requires authority or access the agent doesn't have).
- 🤖 = the agent can do it in a session, on request.
- 🧑🤖 = a decision from the owner, then the work (the owner decides, the agent executes).

This matters because it tells you whether an item is actionable now or waiting on a human. An agent working through the backlog should skip 🧑 items (or flag them) and do 🤖 items. 🧑🤖 items require a decision before work — the agent can draft the decision options, but the owner decides.

## Standing Rules That Constrain Future Work

Rules that aren't tasks — they're constraints that, if broken, silently undo something that already works. Listed at the top of the backlog or in a dedicated section, before the tasks.

**Examples from aspirecures:**
1. At least two disease pages must stay ad-free, permanently. (Break this and the ad kill criteria lose their baseline — two of three criteria go dark without any error.)
2. Never `git rebase` in this repo, and never `git stash`. (The repo lives on Google Drive, whose sync races any multi-phase working-tree rewrite. Use `git merge` and `git heal`.)
3. The rebuild chain is in MAINTENANCE.md step 4 and is the source of truth. Running the generators without `research/render.pl` AND `render-ads.pl` afterwards ships feed-less, rail-less disease pages. `perl tools/dedash.pl *.html` must be called WITH the glob.
4. `bash tools/verify.sh` must pass before any push. (It runs in CI on every push and gates the weekly research job, so a failure there stops the feed publishing.)
5. Copy is written in the owner's voice (we/our), never the visitor's. Medical copy is carried verbatim and is not paraphrased without Heidi's sign-off.

**What makes a good standing rule:**
- It constrains something that, if done wrong, is silent (no error, no warning, just broken).
- It's specific enough to follow (not "be careful with the rebuild" but "run the generators in this order, with these two after, and call dedash with the glob").
- It's referenceable (the rule points to where the details are, so you don't have to re-derive them).
- It's been caught once (standing rules are usually written after something broke — they're the lesson encoded as a rule).

**What makes a bad standing rule:**
- Vague ("be careful", "don't mess it up") — not actionable, can't be followed or verified.
- Redundant with existing tooling (if `verify.sh` already catches it, you don't need a standing rule that says "run verify.sh" — the rule should say something the tooling doesn't catch).
- Unverified (a rule that hasn't been checked against the current code — it may be stale).

## Audit Passes

An audit pass is a systematic scan of a surface, done on a schedule or on demand, that verifies the surface is in the expected state. Not a re-read of a doc — a check against the actual code/state.

**What an audit pass covers:**
- A defined surface (all 18 pages, all 404 external links, the research pipeline's gating and cost, the registration backend and ad inventory).
- A defined expected state ("all pages load clean in a real browser at 375px and 1280px", "all 84 NCT IDs are valid records", "the form backend saves to KV and creates a Zoho lead").
- A defined method (load each page in a real browser, check IDs via the APIs not status codes, submit a real test on the live URL).
- Results recorded per item: verified (✅), partially verified (◐), not verified (☐), with notes on what's still open.

**What an audit pass produces:**
- A record of what was checked, how, when, and what the result was.
- Open items filed as backlog items (with the audit date, so you know when it was last checked).
- Hard limits written down (the things the audit harness structurally cannot check, so nobody re-derives them and wastes time trying).

**Hard limits of an audit harness (the aspirecures lesson):**
- The browser pane runs with `document.visibilityState === 'hidden'` and never composites, so `requestAnimationFrame` never fires and no CSS transition or animation ever advances.
- Anything whose visible result depends on a transition or keyframe (dropdown fade-in, marquee scroll, consent banner rise) can only be checked for its underlying class/attribute state, never for what a human actually sees.
- Synthetic key events are a blind spot: Enter on a focused button delivers keydown and keyup but produces no click, so native button activation is unverifiable there.
- These limits should be written down explicitly, with the consequence (this can only be checked by a human on a real device). Otherwise someone re-derives them the hard way.

**Audit pass cadence:**
- On demand (before a launch, before a significant change, when something is suspected broken).
- On a schedule (quarterly external link check, monthly health check, weekly research feed run).
- After a significant change (a new feature, a refactor, a config change that affects a surface).

**Audit pass discipline:**
- An audit pass that finds nothing open is valuable — it confirms the surface is healthy. Record that.
- An audit pass that re-discovers an open item that was already in the backlog is a failure of the backlog (the item should have been caught by the normal workflow) — record it and ask why it wasn't caught earlier.
- An audit pass that re-discovers a fixed item as still open is a failure of the backlog (the fix wasn't recorded as done, or the reconciliation missed it) — record it and close the item.

## Defect→Effect→Fix Tables

A chronological record of defects found and fixed, in a form that's useful for understanding the project's history and for catching regressions.

**Structure (the CR-pipeline pattern):**

| Defect | Effect | Fix |
|---|---|---|
| `_run_matches` unpacked 5-tuples as `t[0]…t[4]` but caller passed 6th element (`config`) → `IndexError`. Bare `except Exception` swallowed it, returning `fitness=0.0` for every agent every generation. | Training ran to completion reporting progress while selecting on constant zeros. | Pass tasks straight through; let failures propagate instead of flattening them into zeros. |

**What each column captures:**
- **Defect:** what was wrong, in enough detail that someone reading it understands the bug. Not "a bug in the sim" — "king tower not flagged as `building` → king walked across the arena and attacked twice per tick".
- **Effect:** what the bug caused — the observable symptom. "Training ran to completion reporting progress while selecting on constant zeros" is more useful than "the training didn't work". The effect is what someone would have observed (or not observed) before the fix.
- **Fix:** what was done to fix it. Enough detail to understand the fix, but not a full code dump. "Pass tasks straight through; let failures propagate instead of flattening them into zeros" is the right level.

**Why this form is useful:**
- It's a history of the project's correctness journey — you can see how the sim went from "blind" to "correct" by reading the defects in order.
- It's a regression test catalog — each defect suggests a test that would have caught it. When you fix a defect, add the test.
- It's a warning system — reading the defect list tells you what categories of bugs have bitten this project before, so you can anticipate them in new code.

**When to record a defect:**
- When you fix a bug, record it in the defect table (name it, describe the effect, describe the fix).
- When you find a bug that you don't fix immediately, record it in the backlog (with enough detail to understand it later) and file a fix task.
- When a defect is found by an audit pass or a test, record it in the defect table (even if it was already fixed — the record is evidence that the test/audit caught it).

**When NOT to record a defect:**
- Trivial typos that don't affect behavior (those are just fixed, not recorded).
- Defects that are duplicates of an already-recorded defect (don't record the same defect twice — point to the existing entry).
- Defects in external dependencies (record them if they affect your project, but note that the fix is in the dependency, not your code).

## Health Checks and CI Gating

Automated checks that run on every push (or on a schedule) and gate deploys. Not linters that suggest — checks that pass or fail, and failures stop the deploy.

**What a health check covers:**
- Local link resolution (every href/src/data-src resolves to a file that exists; no orphaned assets; no broken internal links).
- Structural validity (HTML is parseable, JSON is valid, config is valid, markers are intact).
- Invariant checks (the ad rail matches slots.json; the research feed is present on disease pages; dedash pass has been run).
- Prohibited content (no Squarespace markup/CSS/JS remaining; no em/en dashes that survived the dedash pass; no unresolved @font-face families).

**What a health check does NOT cover:**
- Things that require a real browser (visual correctness, animation progress, native button activation) — those are audit-pass items, not CI checks.
- External link rot (400+ network calls would make CI slow and flaky, and rate-limit false failures would block the feed job) — separate on-demand check, not CI.
- Things that are subjective (does the page look right?) — CI can't check this.

**CI gating:**
- The health check runs on every push and must pass before the deploy.
- The weekly research job is gated by the health check — a failing health check stops the feed from publishing (so a broken link checker or a stray dash doesn't ship bad feed data).
- The health check should be fast (seconds, not minutes) — if it's slow, it blocks every push.

**Health check discipline:**
- A health check that always passes is suspicious (is it checking anything?).
- A health check that fails for the wrong reason (a flaky network check, a transient timeout) erodes trust — fix the flakiness or remove the check from CI.
- A health check that catches a real problem is the ideal — record the catch, add a regression test if applicable, and keep the check.

## Reconciliation

The act of scanning the whole repo and confirming that the backlog, the docs, and the code all agree with each other and with reality.

**What reconciliation checks:**
- Every open item in the backlog is actually open (not already done, not already filed elsewhere).
- Every done item in the backlog is actually done (the fix landed, the doc was updated, the item can be closed).
- Every doc claim is accurate against the current code (the README says X owns Y — does it? The TODO says a fix shipped — is it in the code?).
- Every doc claim that can't be verified is marked as such (not assumed true).

**Reconciliation cadence:**
- On a schedule (aspirecures: a full-repo scan every few weeks, with the date recorded).
- After a significant change (a batch of fixes, a refactor, a release).
- When something doesn't add up (a doc claim that seems stale, a backlog item that seems done but isn't marked, a test that passes but the doc says it shouldn't).

**What reconciliation produces:**
- A reconciled backlog (all items current, all statuses accurate, all owner labels correct).
- Corrections to stale docs (claims that were true at one point but aren't now, fixed or marked as historical).
- A reconciliation date (so you know how fresh the backlog is).

**Reconciliation discipline:**
- Reconciliation is not a skim — it's a scan of the whole surface. A 556-line backlog was reconciled by a full-repo scan, not by re-reading the backlog and assuming.
- Reconciliation catches phantom tasks (items that were already done when written, or that survived two reconciliations as open when they were actually done). Record the phantom and close it.
- Reconciliation catches stale claims (README says X, code says Y) — fix the doc or the code, and record the correction.

## Regression Capture

When a defect is found and fixed, capture it in a form that prevents reintroduction.

**In code (regression tests):**
- Add a test that would have caught the defect.
- Name the test for the defect (not "test_sim" but "test_king_does_not_attack_twice_per_tick" or "test_crowns_awarded_for_princess_tower_kills").
- The test should be fast and deterministic (a regression test that's slow or flaky won't be run reliably).

**In docs (defect table):**
- Add the defect to the defect→effect→fix table.
- The record is evidence that the defect was found, understood, and fixed — and a warning that this category of bug has bitten before.

**In the backlog (if the fix is not immediate):**
- File the fix as a backlog item with enough detail to understand the defect later.
- Link the defect to the backlog item (the item references the defect, the defect references the item).

**Regression capture discipline:**
- Every fixed defect should have at least one of: a regression test, a defect-table entry, or a backlog item. Prefer all three when the defect is significant.
- Regression tests that are never run are worse than no regression tests (they give false confidence). Run them in CI.
- Defect-table entries that are never read are still useful (they're there when needed) but don't rely on them being read proactively — the regression test is the proactive defense.

## The Verification Checklist Pattern

A checklist at the end of a doc or skill that enumerates what "done" means for that thing. Not a to-do list — a definition of done.

**What a verification checklist contains:**
- Specific, verifiable items (not "the site is good" but "every page has a unique, descriptive title").
- Items that cover the significant risks (the things that, if wrong, are silent or high-consequence).
- Items that are checkable (you can verify each one, ideally with a command or a look).

**What a verification checklist does NOT contain:**
- Vague items ("the code is clean", "the tests are good") — not verifiable.
- Items that are covered by existing tooling (if `verify.sh` checks it, the checklist can say "verify.sh passes" rather than re-listing every check).
- Items that are aspirational (a checklist is for what's done, not what should be done someday).

**How to use verification checklists:**
- At the end of a task, run through the checklist for that task's domain and confirm each item.
- When creating a skill or doc, include a verification checklist so the reader knows what "ready" looks like.
- When auditing a surface, use the relevant checklist as the audit scope (the checklist defines what to check).

**Checklist discipline:**
- A checklist that's never used is dead weight — if items are always green, the checklist may be too conservative or not covering real risks. Prune items that are always satisfied and add items for risks that have materialized.
- A checklist item that's frequently red is a signal — either the checklist is wrong (the item shouldn't be required) or the project has a recurring problem (fix the problem or accept the item as a known risk).

## Documentation Hygiene

Keeping docs accurate over time, without letting doc maintenance become a burden.

**Docs as code:**
- Docs live in the repo, versioned with the code, reviewed when changed.
- A doc claim that's wrong is a bug in the doc — fix it when you find it, not "later".
- Doc claims that can't be verified are marked as such (not assumed true).

**Doc ownership:**
- Each doc has an owner (the tool, the person, the process that maintains it).
- When a doc is stale, you know who to ask or what to check.
- When a doc claim is questioned, you know where to look to verify it.

**Doc updates on code changes:**
- When code changes, check whether any doc claims about that code are still accurate.
- When a fix lands, check whether any doc references the old behavior (and update or mark as historical).
- When a doc is updated, check whether the backlog needs updating (a doc claim that was a backlog item is now done).

**Doc types and their purpose:**
- **Architecture/runbook docs:** how things work, how to operate them. Living docs, updated with the code.
- **Historical docs:** why things were built a certain way, what was tried and rejected. Marked as historical — they're evidence, not current guidance.
- **Backlog:** what's open, who owns it, what's verified. Single source, reconciled on a schedule.
- **Defect history:** what broke and how it was fixed. Chronological, useful for regression and warning.
- **Standing rules:** constraints that must not be broken. At the top, before the tasks.

**Doc hygiene discipline:**
- A doc that's consistently stale is a burden — either fix the doc maintenance or reduce the doc's scope.
- A doc that's accurate but never read is still useful (it's there when needed) but don't rely on people reading it proactively — encode the important constraints in tooling (health checks, CI gates, regression tests) so they're enforced automatically.
- A doc that claims something the tooling can verify should be verified by the tooling (the doc says "verify.sh passes" and verify.sh actually passes) — don't rely on doc claims that tooling could check.

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Backlog is one of several open-task lists | Item is tracked in two places, or not tracked at all | Consolidate to a single source; reconcile so the backlog matches reality |
| Standing rules are vague | Rule can't be followed or verified | Make rules specific and referenceable; point to where the details are |
| Audit pass is a doc re-read | Nothing is actually verified; open items are assumed closed | Audit against the actual code/state, with a defined method and expected result |
| Defect history is missing or vague | Same defect reintroduced; no warning from past bugs | Record defect→effect→fix for every significant fix; add regression tests |
| Health check is slow or flaky | Every push is blocked, or the check is disabled | Make health checks fast and deterministic; remove flaky checks from CI |
| Reconciliation is a skim | Phantom tasks survive, stale claims persist | Reconcile by scanning the whole surface, not by assuming |
| Regression test is never run | False confidence; defect can recur | Run regression tests in CI; mark slow ones and run them anyway |
| Doc claims aren't verified | Stale docs, wrong guidance | Mark unverifiable claims as such; verify claims against code when found |
| Verification checklist is vague or unused | Checklist doesn't define "done"; items always green | Make checklist items specific and verifiable; prune always-green items, add items for materialized risks |
| Documentation burden is too high | Docs go stale because maintaining them is too much work | Reduce doc scope, encode constraints in tooling, mark historical docs as historical |

## Verification Checklist

Before declaring a project's verification culture healthy:

- [ ] Single-source backlog exists and is the only list of open work
- [ ] Backlog has owner labels (🧑/🤖/🧑🤖) so actionable vs. waiting-on-human is clear
- [ ] Standing rules are specific, referenceable, and constrain silent-breakage risks
- [ ] Audit passes are against actual state, with defined surface, method, and expected result
- [ ] Hard limits of audit harnesses are written down explicitly
- [ ] Defect→effect→fix table captures significant defects with enough detail to understand them
- [ ] Regression tests are added for significant defects and run in CI
- [ ] Health checks are fast, deterministic, and gate deploys (failures stop the deploy)
- [ ] Health checks don't include things that belong in audit passes (external link rot, visual correctness)
- [ ] Reconciliation is a full scan, not a skim, and the reconciliation date is recorded
- [ ] Doc claims are verified against code when found; unverifiable claims are marked as such
- [ ] Historical docs are marked as historical (evidence, not current guidance)
- [ ] Verification checklists define "done" with specific, verifiable items
- [ ] Important constraints are encoded in tooling (CI gates, health checks, regression tests) so they're enforced automatically, not just documented
