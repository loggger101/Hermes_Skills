---
name: grilling-interview
description: "Stress-test a plan by interviewing in design-tree rounds."
version: v1.0.0
author: "Hermes Agent (ported from mattpocock/skills grilling) + Rafael Zendron (rafaumeu, grill-me)"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [interviewing, planning, decision-making, adversarial, decision-tree, pre-implementation, alignment]
    related_skills: [conversation-to-spec, wayfinder-map-planning, requesting-code-review, mattpocock-subagent-driven-development, test-driven-development]
---

<!-- source: mattpocock/skills (productivity/grilling), ported 2026-09-05; round-57 merged in grill-me
     (Rafael Zendron + mattpocock grilling, v2.0.0): attack mode, question coverage, synthesis, pitfalls -->

# Grilling Interview

## When to Use

- "Grill this plan / idea", "grill me", "interview my plan", "stress test this idea"
- Before committing to a large, ambiguous build, or before complex work: auth flows, schema
  changes, migrations, payments
- Any decision tree with unresolved branches, or a plan that seems vague
- Before decomposing work for `mattpocock-subagent-driven-development`

Do NOT use for existing code (use `requesting-code-review`) or simple one-off tasks.

## What This Skill Does

Interview the user relentlessly until you reach shared understanding. Map the work as a **design tree**: every decision branches into the decisions that hang off it. Work the tree in rounds until every branch is resolved and nothing is silently assumed, then end with a summary of every decision before any code is written.

Two modes, same mechanic:

- **Elicit** (the default): the user has an idea or a request and the plan does not exist yet. Draw it out branch by branch.
- **Attack** ("grill me", "poke holes in this"): the user already has a plan. Your job is to find what is wrong with it: every question pushes on a weak point, and if everything looks fine, look harder.

## Prerequisites

None. The skill works on any plan or raw idea.

## Core Mechanic: Frontier Rounds

The **frontier** is every decision whose prerequisites are already settled — the questions you can ask *now* without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer for each. Then wait for the user's answers before the next round.

Format a round like so:

```text
❓ **Q1** - **<question title>**: <question body, may include multiple choices>

➡️ <your recommended answer + one-line why>

---

❓ **Q2** - **<question title>**: <question body>

➡️ <your recommended answer>
```

In Hermes desktop, prefer the `clarify` tool for each round (one call, all frontier questions as entries) — it renders pickable rows and captures free-text. Fall back to the text format above in CLI/other platforms.

Each round's answers reshape the tree: settled decisions push the frontier outward and unblock dependent questions. Recompute the frontier; a question whose answer depends on another still-open question belongs to a *later* round, not this one.

**Finding facts is your job, never the user's.** When a frontier question needs an environmental fact (codebase, filesystem, config, git state, docs, tool output), look it up yourself with `search_files` / `read_file` / `terminal`, or dispatch a subagent via `delegate_task` if the exploration is heavy. Never ask the user for anything you could retrieve. Don't block on it: a running lookup is an unsettled prerequisite, so only questions downstream of it wait; ask the rest now. **Decisions are the user's**: put each to them and wait.

## Question Coverage (work these branches into the tree)

**Understanding** — the real goal and boundaries:

- What is the ACTUAL objective? What is explicitly IN and OUT of scope?
- What are the constraints (time, tech, team, budget)? Who are the users?

**Technical decisions** — for each architectural choice:

- "Why this approach and not X?" / "What happens if Y fails?"
- "What's the worst case?" / "How would you roll back?"
- Cross-reference the existing codebase; if the project already has a pattern for this, call it out.

**Edge cases:**

- "What happens if the user does Z?" / "What if dependency X goes down?"
- "What if volume is 100x expected?" / "What are the security implications?"

## Synthesis (when the frontier is empty)

The session is done when the frontier is empty — every branch visited, nothing silently assumed.

1. Summarize ALL settled decisions in bullet points, so the user can veto anything before work starts
2. List anything left open, and what is explicitly OUT of scope
3. Ask: "Aligned? Should I start implementing, or adjust anything?"

Do not act on the plan until the user confirms shared understanding.

## Pitfalls

1. **Asking questions out of dependency order.** A question that depends on an unanswered question is a guess wearing a question mark. Keep it for a later round.
2. **Skipping the codebase.** Find facts in code with Hermes tools instead of asking the user.
3. **Accepting "I don't know" as final.** Suggest options, explain trade-offs, make a recommendation.
4. **Writing code during the interview.** Alignment only — code after the explicit green light.
5. **Being too agreeable in attack mode.** Your job is to find problems. If everything looks fine, look harder.
6. **Not adapting to the user's language.** Interview in whatever language the user speaks.

## Verification

- [ ] Every question in a round had all its prerequisites already settled
- [ ] Provided a recommendation with each question
- [ ] Explored the codebase for facts instead of asking the user
- [ ] Frontier empty (no branch silently assumed) before synthesizing
- [ ] Produced a clear summary of all decisions and open items
- [ ] Confirmed user alignment before stopping
