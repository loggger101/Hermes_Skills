---
name: executing-plans
description: "Execute a written plan inline with checkpoints."
version: 1.0.0
author: Hermes Agent (adapted from obra/superpowers v6.3.0)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, execution, checkpoints, inline-workflow]
    related_skills: [plan, mattpocock-subagent-driven-development, mattpocock-using-git-worktrees, mattpocock-finishing-a-development-branch, test-driven-development]

---

<!-- source: obra/superpowers (skills/executing-plans), adapted 2026-09-11 -->

## When to Use

You have a written implementation plan and will execute it **in this session** — batch execution with human checkpoints instead of dispatching subagents. This is the inline counterpart to `mattpocock-subagent-driven-development`: use SDD when tasks are independent enough for fresh-subagent-per-task + per-task review; use THIS skill for small plans, tightly coupled tasks, or whenever the user wants to watch work happen in-session.

**If a subagent path fits better, say so and offer it** — "this plan has N independent tasks; I can dispatch a fresh subagent per task with two-stage review (faster) or execute inline here with checkpoints (more visible). Which do you prefer?" Default to the user's choice; never silently pick.

## What This Skill Does

Load plan -> review critically -> execute all tasks in order -> report when complete, stopping at named checkpoints instead of guessing through blockers.

**Announce at start:** "I'm executing this plan inline with checkpoints."

## The Process

### Step 1: Load and Review Plan
1. Ensure an isolated workspace if the work needs one — `skill_view(name='mattpocock-using-git-worktrees')` (create or verify existing). Never start implementation on main/master without explicit user consent.
2. Read the plan file in full. If it names a spec, read that too — the spec is the authority the plan argues from; resolve any plan-vs-plan conflict against it.
3. **Review critically** before starting: internal contradictions? missing context? steps that assume state no earlier step creates? Anything you'd get stuck on mid-run?
4. If concerns exist: raise them with the user BEFORE executing anything. A plan defect found in 10 seconds now is cheaper than one discovered at task 7 of 9.
5. If clean: create a todo per task and proceed.

### Step 2: Execute Tasks (in order)
For each task:
1. Mark it `in_progress` in the todo list.
2. Follow each step exactly — plans carry bite-sized steps with exact paths, code, and verification commands; do not paraphrase them into something vaguer.
3. Run every verification as specified (tests, builds, expected output). A skipped verification is an unverified task.
4. Mark it completed only after its verifications pass.

**Checkpoint rule:** pause for the user at natural boundaries — end of each task group, before any destructive or hard-to-reverse step (drop, force-push, schema migration), and whenever a step's outcome differs from what the plan predicted. Between checkpoints you may proceed autonomously; "should I continue?" prompts between every single step are noise.

### Step 3: Complete Development
After all tasks complete and verify: hand off to `skill_view(name='mattpocock-finishing-a-development-branch')` — it verifies the full suite, detects environment (worktree vs normal), presents merge/PR/keep options, and cleans up only what is safe.

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker (missing dependency, test fails after two attempts, instruction unclear)
- The plan has critical gaps preventing starting or continuing
- You don't understand an instruction — **ask rather than guess**; a guessed interpretation that's wrong costs more than the question
- A verification fails repeatedly

## When to Revisit Step 1 (Review Again)

Return to review when: the user updates the plan based on your feedback, or the fundamental approach needs rethinking. Don't force through blockers — stopping and asking is always cheaper than continuing on a wrong assumption.

## Remember

- Review the plan critically FIRST; raise concerns before executing
- Follow steps exactly (exact paths, exact commands)
- Never skip verifications
- Stop when blocked, don't guess
- Checkpoints at task-group boundaries and before irreversible actions — not after every step
- Hand off to finishing-a-development-branch for integration
