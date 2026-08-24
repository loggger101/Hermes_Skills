---
name: mattpocock-ask-if-underspecified
description: "Ask clarifying questions when a request is ambiguous."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [clarity, questioning, requirements, ambiguity, communication]
    related_skills: [mattpocock-handoff, mattpocock-writing-for-agents]
---

## When to Use

Use when the user's request is ambiguous, underspecified, or could lead to multiple valid interpretations. Also use proactively when the cost of getting it wrong (time, resources, user frustration) is high.

## What This Skill Does

Rather than guessing and producing output that doesn't match the user's needs, this skill structures the process of asking targeted clarifying questions before starting work. It helps you identify which aspects of a request are ambiguous and ask the right questions efficiently. Loads `skill_view(name='mattpocock-writing-for-agents')` when the response needs to be written as an agent-consumable document, and `skill_view(name='mattpocock-handoff')` when the clarified task will be handed off.

## Prerequisites

- A `clarify` tool available in the current session
- The user's request is identifiable as potentially ambiguous
- At least one ambiguity marker was detected

## The Process

### 1. Detect Underspecification

Before producing output, scan the request for these ambiguity markers:

| Ambiguity Type | Example | What to Ask |
|----------------|---------|-------------|
| **Scope too broad** | "Improve the pipeline" | Which specific step? What does "improve" mean here? |
| **Missing constraints** | "Summarize this paper" | Length? Audience? Focus areas? Format? |
| **Unclear success criteria** | "Make this faster" | What's the target? Measure of success? |
| **Missing context** | "Fix the bug" | Which bug? What's the expected behavior? |
| **Multiple valid interpretations** | "Create a dashboard" | For what data? What actions? Who's the audience? |

### 2. Ask the Right Questions

Use the `clarify` tool with targeted questions. Each question should resolve one ambiguity.

**Good clarifying questions are:**
- **Specific** — not "tell me more" but "which of these 3 approaches do you prefer?"
- **Actionable** — the user can answer with a choice or a brief statement
- **Bounded** — offer 2-4 options when possible, with a clear recommendation
- **Independent** — each question resolves a different axis of ambiguity

### 3. Group Related Questions

Ask 2-5 related questions in a single `clarify` call (they'll be answered on one form). Group by theme:

**Example grouping**:
1. "Which disease page needs updating?" (specificity)
2. "What changed in the data source — format, fields, or availability?" (problem definition)
3. "Do you want me to fix just the parser, or also the renderer and tests?" (scope)
4. "What does success look like — all 9 pages render, or just this one?" (success criteria)

### 4. Make Reasonable Assumptions Visible

If the user gives a brief answer but the request is still somewhat open, state your assumptions explicitly before proceeding:

> "I'll proceed with these assumptions: [assumption 1], [assumption 2], [assumption 3]. If any are wrong, tell me and I'll adjust. I'll start with [specific first step]."

This turns assumptions into checkable constraints rather than hidden failure modes.

## When NOT to Ask

- **Routine, well-understood tasks** — "summarize this 3-paragraph article into 3 bullet points" is clear enough
- **The user has already provided extensive context** — they may have over-communicated on purpose
- **The cost of asking exceeds the cost of doing** — sometimes it's faster to produce a draft and iterate
- **The user is clearly exploring** — "show me a few options" is a valid request that doesn't need upfront clarification

## Pitfalls

- **Over-clarifying**: Asking too many questions paralyzes the user — aim for 2-4 questions that resolve the most critical ambiguities
- **Vague questions**: "Tell me more about what you want" is not actionable — offer specific options
- **Ignoring user hints**: If the user says "just pick something reasonable," trust them and proceed
- **Hidden assumptions**: If you don't surface assumptions, the user may not realize you've made them until it's too late
- **Wrong timing**: Asking after 50% of the work is done defeats the purpose — ask upfront

## Verification

- [ ] Each question in the `clarify` call resolves a different axis of ambiguity
- [ ] Questions are bounded (offer 2-4 options where possible)
- [ ] Assumptions are stated explicitly before proceeding
- [ ] The user's response was incorporated into the task definition

## AspireCURES Context

When the weekly cronjob reports a data-source API change, the preparer agent should first ask the user whether this is expected (API evolution) or unexpected (breaking change) before diving into parser fixes. Similarly, if a disease page renders incomplete results, ask whether the user wants a full fix or a temporary stub before proceeding. The `clarify` tool allows up to 5 questions per call — use them to resolve scope, priority, and success criteria in one round.
