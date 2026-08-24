---
name: mattpocock-code-review
description: "Two-axis code review: Standards and Spec via sub-agents."
version: 1.0.0
author: Adapted from mattpocock/skills
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [code-review, standards, spec, parallel-sub-agents, smells]
    related_skills: [github-code-review, requesting-code-review, mattpocock-tdd]
---

## When to Use

Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X".

# Code Review (mattpocock)

Review the diff between `HEAD` and a fixed point along two axes:

- **Standards**: does the code conform to repo coding standards?
- **Spec**: does the code faithfully implement the originating issue?

Both axes run as **parallel sub-agents** so they don't pollute each other's context.

## When to Use

Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X".

## Process

### 1. Pin the fixed point

Capture the diff: `git diff...HEAD`. Confirm the fixed point resolves and the diff is non-empty.

### 2. Identify the spec source

1. Issue references in commit messages
2. A path the user passed as an argument
3. A spec file under `docs/` or `specs/`
4. If nothing found, ask the user.

### 3. Identify the standards sources

`CODING_STANDARDS.md`, `CONTRIBUTING.md`, `AGENTS.md`, `.cursorrules`, `CLAUDE.md`, etc.

Plus the **smell baseline**:
- **Mysterious Name** → rename
- **Duplicated Code** → extract
- **Long Function** → split
- **Data Clumps** → bundle
- **Feature Envy** → move

### 4. Run parallel sub-agents

Spawn two `delegate_task` calls: Standards sub-agent and Spec sub-agent.

## AspireCURES Context

Insert this review between merge and commit in your preparer→executor pipeline: validate against both repo coding standards AND the originating research findings before the commit is finalized.
