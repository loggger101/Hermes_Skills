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
    related_skills: [github-code-review, requesting-code-review, mattpocock-tdd, hermes-agent-skill-authoring]
---

## When to Use

Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X". Also use when you need to verify code quality and spec compliance in parallel before merging.

## What This Skill Does

Reviews the diff between a base point and HEAD along two axes, each executed by an independent sub-agent:

1. **Standards** — does the code conform to repo coding standards?
2. **Spec** — does the code faithfully implement the originating issue?

Loads `skill_view(name='github-code-review')` for the full PR review workflow with inline GitHub comments, and `skill_view(name='requesting-code-review')` for the automated verification pipeline. For TDD discipline, load `skill_view(name='mattpocock-tdd')`.

## Prerequisites

- A git repository with a non-empty diff to review
- Coding standards documents (`CODING_STANDARDS.md`, `CONTRIBUTING.md`, `AGENTS.md`, etc.)
- The originating spec/issue to compare against

## Smell Baseline

Use these code smells as a checklist during review:

| Smell | Action |
|-------|--------|
| **Mysterious Name** | Rename to express intent |
| **Duplicated Code** | Extract into a shared function/module |
| **Long Function** | Split into smaller, focused functions |
| **Data Clumps** | Bundle related parameters into a class/object |
| **Feature Envy** | Move method to the class it's most interested in |

## Process

### 1. Pin the fixed point
Capture the diff: `git diff...HEAD`. Confirm the fixed point resolves and the diff is non-empty.

### 2. Identify the spec source
1. Issue references in commit messages
2. A path the user passed as an argument
3. A spec file under `docs/` or `specs/`
4. If nothing found, ask the user

### 3. Identify the standards sources
`CODING_STANDARDS.md`, `CONTRIBUTING.md`, `AGENTS.md`, `.cursorrules`, `CLAUDE.md`, etc.

### 4. Run parallel sub-agents
Spawn two `delegate_task` calls — Standards sub-agent and Spec sub-agent. Each gets:
- The diff
- The relevant standards/spec source
- The smell baseline as a checklist

### 5. Consolidate findings

| Priority | Criteria |
|----------|----------|
| **Critical** | Security vulnerability, crash, data corruption |
| **High** | Logic bug, missing test, spec deviation |
| **Medium** | Code smell, naming issue, complexity |
| **Low** | Style, formatting, minor consistency |

### 6. Present options
- All clear → approve
- Minor findings → fix and re-review
- Major findings → discuss with user before proceeding

## Format for Sub-agent Prompts

```
You are a code standards reviewer. Review the diff for adherence to coding
standards. Focus on the smell baseline: Mysterious Name, Duplicated Code,
Long Function, Data Clumps, Feature Envy. Return findings with file:line
references and a suggested fix.

<diff>
[INSERT DIFF]
</diff>

<standards>
[INSERT CODING STANDARDS]
</standards>

Return findings as a structured list.
```

## Pitfalls

- **Scope creep**: Don't expand the review beyond the diff being reviewed
- **Paralysis by analysis**: Set a time box; if the diff is too large, split the review
- **Forgetting spec compliance**: Standards-only reviews miss functional bugs — always pair with spec review
- **Reviewer bias**: The sub-agents should not know who wrote the code or have prior context
- **Merge conflicts**: If the diff includes a merge, review the conflict resolution specifically

## Verification

- [ ] Both sub-agents completed and returned findings
- [ ] Findings were deduplicated across the two axes
- [ ] All Critical and High priority issues were addressed
- [ ] All Medium/Low issues were either fixed or explicitly acknowledged
- [ ] The receiving party (user or PR system) was presented with clear options

## AspireCURES Context

Insert this review between merge and commit in your preparer→executor pipeline: validate against both repo coding standards AND the originating research findings before the commit is finalized.
