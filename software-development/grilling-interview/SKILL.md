---
name: grilling-interview
description: "Stress-test a plan by interviewing in design-tree rounds."
version: v0.9.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [interviewing, planning, decision-making]
    related_skills: [conversation-to-spec, wayfinder-map-planning]
---


<!-- source: mattpocock/skills (productivity/grilling), ported 2026-09-05 -->
## When to Use

- "Grill this plan / idea"
- Before committing to a large, ambiguous build
- Any decision tree with unresolved branches

## What This Skill Does

``` ❓ **Q1** - **<question title>**: <question body, may include multiple choices>


# Grilling Interview

Interview the user relentlessly until you reach shared understanding. Map the work as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask *now* without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer for each. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, may include multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body>

➡️ <your recommended answer>
```

In Hermes desktop, prefer the `clarify` tool for each round (one call, all frontier questions as entries) — it renders pickable rows and captures free-text. Fall back to the text format above in CLI/other platforms.

Each round's answers reshape the tree: settled decisions push the frontier outward and unblock dependent questions. Recompute the frontier; a question whose answer depends on another still-open question belongs to a *later* round, not this one.

**Finding facts is your job, never the user's.** When a frontier question needs an environmental fact (filesystem, git state, tool output), look it up yourself — dispatch a subagent if heavy — and don't ask the user for anything you could retrieve. Don't block on it: a running lookup is an unsettled prerequisite, so only questions downstream of it wait; ask the rest now. **Decisions are the user's**: put each to them and wait.

The session is done when the frontier is empty — every branch visited, nothing silently assumed. Do not act until the user confirms shared understanding. End with a one-paragraph recap of all settled decisions so they can veto anything before work starts.
