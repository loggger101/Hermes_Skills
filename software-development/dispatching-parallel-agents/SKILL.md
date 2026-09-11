---
name: dispatching-parallel-agents
description: "Parallel subagents for independent problem domains."
version: 1.0.0
author: Hermes Agent (adapted from obra/superpowers v6.3.0)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [subagents, parallelism, delegation, debugging, concurrency]
    related_skills: [mattpocock-subagent-driven-development, systematic-debugging, test-driven-development]

---

<!-- source: obra/superpowers (skills/dispatching-parallel-agents), adapted 2026-09-11 -->

## When to Use

Facing 2+ independent problems that can be worked on without shared state or sequential dependencies — e.g., multiple test files failing with different root causes, several subsystems broken independently, each problem understandable without context from the others.

**Don't use when:** failures are related (fixing one might fix others), understanding requires full system state, agents would interfere (same files/resources), or you don't yet know what is broken (exploratory debugging).

## What This Skill Does

Dispatches one subagent per independent problem domain and lets them work concurrently. Core principle: **dispatch one agent per independent problem domain; let them work in parallel.** Implementation work is never dispatched in parallel — this skill is for read-mostly investigation/fix domains with disjoint file scopes (see `mattpocock-subagent-driven-development` for sequential task execution with review gates).

## The Pattern

### 1. Identify Independent Domains
Group failures by what's broken: File A tests = tool approval flow; File B tests = batch completion; File C tests = abort logic. Each domain is independent — fixing one doesn't affect the others. If domains share files or state, they are NOT parallelizable.

### 2. Create Focused Agent Tasks
Each agent gets: **specific scope** (one test file/subsystem), **clear goal** ("make these tests pass"), **constraints** ("do not change other code" / "fix tests only"), **expected output** (summary of what you found and fixed).

### 3. Dispatch in Parallel
Issue ALL dispatches in the same response — multiple tool calls per turn = parallel execution; one per turn = sequential:

```python
# All three delegate_task calls in ONE assistant turn run concurrently:
delegate_task(goal="Fix the failing tests in src/agents/test_abort.py ...", context=...)
delegate_task(goal="Fix the failing tests in src/batch/test_completion.py ...", context=...)
delegate_task(goal="Fix the race conditions in src/approval/test_approval.py ...", context=...)
```

### 4. Review and Integrate
When agents return: read each summary; verify fixes don't conflict (did two agents edit the same code?); run the full test suite; integrate all changes. **Spot check** — parallel agents can make systematic errors in the same direction.

## Agent Prompt Structure

Good prompts are: 1) **Focused** — one clear problem domain; 2) **Self-contained** — all context needed (paste error messages and test names, don't assume); 3) **Specific about output** — what should come back?

```
Fix the 3 failing tests in src/agents/test_abort.py:
1. "should abort tool with partial output capture" - expects 'interrupted at' in message
2. "should handle mixed completed and aborted tools" - fast tool aborted instead of completed
3. "should properly track pending_tool_count" - expects 3 results but gets 0

These are timing/race condition issues. Your task:
1. Read the test file and understand what each test verifies
2. Identify root cause — timing issues or actual bugs? (use systematic-debugging)
3. Fix by replacing arbitrary timeouts with event-based waiting, fixing abort bugs if found,
   adjusting expectations only where behavior genuinely changed

Do NOT just increase timeouts - find the real issue. Do NOT change production code outside the abort path.
Return: summary of root cause and changes made.
```

## Common Mistakes

| Bad | Good |
|-----|------|
| Too broad: "fix all the tests" — agent gets lost | Specific: "fix test_abort.py" — focused scope |
| No context: "fix the race condition" — agent doesn't know where | Paste error messages and test names |
| No constraints — agent might refactor everything | "Do NOT change production code" / "fix tests only" |
| Vague output: "fix it" — you don't know what changed | "Return summary of root cause and changes" |

## Verification (after agents return)

- [ ] Read each summary; understand what actually changed
- [ ] Checked for conflicts — no two agents edited the same code path
- [ ] Full test suite run: all fixes work together
- [ ] Spot-checked at least one fix per agent (agents can make systematic errors)
