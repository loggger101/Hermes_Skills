---
name: mattpocock-code-review
description: "Sub-agent code review: two-axis, or a 5-reviewer panel."
version: 1.1.0
author: Adapted from mattpocock/skills (two-axis) + NeoLabHQ/context-engineering-kit (panel mode)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [code-review, standards, spec, parallel-sub-agents, smells, multi-agent, bug-hunter, security-auditor, contracts]
    related_skills: [github-code-review, requesting-code-review, mattpocock-security-review, mattpocock-tdd, hermes-agent-skill-authoring]
---

<!-- round-57: mattpocock-multi-agent-code-review (NeoLabHQ/context-engineering-kit) merged in as panel mode -->

## When to Use

Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X". Also use when you need to verify code quality and spec compliance in parallel before merging. Use **panel mode** when the user asks for a "thorough review", "multiple perspectives on this code", or "check for subtle issues".

## What This Skill Does

Reviews the diff between a base point and HEAD with independent sub-agents, then consolidates their findings. Two modes:

- **Two-axis** (default, faster): two sub-agents.
  1. **Standards** — does the code conform to repo coding standards?
  2. **Spec** — does the code faithfully implement the originating issue?
- **Panel** (thorough): five specialized reviewers.
  1. **Bug hunter** — logic errors, edge cases, off-by-one, null safety, race conditions
  2. **Security auditor** — injection, auth issues, secrets, SSRF, path traversal (load `skill_view(name='mattpocock-security-review')` for the OWASP checklist)
  3. **Code quality reviewer** — naming, complexity, testability, adherence to conventions (the Standards axis, widened)
  4. **Contracts reviewer** — does the diff match the originating spec/issue (the Spec axis)
  5. **Historical context reviewer** — how the change interacts with past decisions (reads ADRs)

Loads `skill_view(name='github-code-review')` for the full PR review workflow with inline GitHub comments, and `skill_view(name='requesting-code-review')` for the single-agent pre-commit pipeline. For TDD discipline, load `skill_view(name='mattpocock-tdd')`.

### Choosing the mode

| Scenario | Recommendation |
|----------|---------------|
| Small diff (< 200 lines) | `requesting-code-review` — a single agent is sufficient |
| Familiar code, trusted team | Two-axis — faster |
| New codebase, unclear conventions | Panel — more perspectives catch convention gaps |
| Security-critical code | Panel — the security auditor adds depth |
| High-stakes release | Panel — bug hunter + contracts reviewers add safety |

## Prerequisites

- A git repository with a clean base branch and a non-empty diff to review
- Coding standards documents (`CODING_STANDARDS.md`, `CONTRIBUTING.md`, `AGENTS.md`, etc.)
- The originating spec/issue to compare against
- Ability to spawn `delegate_task` sub-agents

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

Capture the diff: `git diff <base>...HEAD -- > /tmp/diff.patch`. Confirm the fixed point resolves and the diff is non-empty.

### 2. Identify the spec source

1. Issue references in commit messages
2. A path the user passed as an argument
3. A spec file under `docs/` or `specs/`
4. If nothing found, ask the user

### 3. Identify the standards sources

`CODING_STANDARDS.md`, `CONTRIBUTING.md`, `AGENTS.md`, `.cursorrules`, `CLAUDE.md`, etc. Panel mode also needs the decision record: `docs/adr/`, `CONTEXT.md`.

### 4. Run parallel sub-agents

Spawn one `delegate_task` call per reviewer — two in two-axis mode, five in panel mode. Each gets the diff, the source it reviews against (standards, spec, or ADRs), the smell baseline as a checklist, and its prompt from the next section. Keep them independent: no reviewer sees another's findings.

### 5. Consolidate findings

Merge findings from all reviewers into a single report. Deduplicate overlapping findings. Prioritise:

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

## Sub-agent Prompts

Two-axis, Standards reviewer:

```text
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

The Spec reviewer gets the same shape with the spec in place of the standards and the Contracts prompt below as its instruction.

Panel personas:

```text
# Bug hunter
Review this diff for logic errors, edge cases, off-by-one bugs, null
safety issues, and race conditions. For each finding, note the
file:line and explain the failure mode.

# Security auditor
Review this diff for security vulnerabilities: injection, XSS, SSRF,
path traversal, hardcoded secrets, auth bypass. Use the OWASP
checklist. Flag every security concern with file:line reference.

# Code quality
Review this diff for code quality issues: unclear naming, high
cyclomatic complexity, missing tests, inconsistency with repo
conventions. Provide file:line references with suggestions.

# Contracts
Review this diff against the originating spec/issue. Verify each
change maps to a requirement. Flag any scope creep or unrequested
changes with file:line references.

# Historical context (written in round-57; the source named this reviewer without a prompt)
Review this diff against the project's recorded decisions (docs/adr/,
CONTEXT.md). Flag changes that contradict a decision, reintroduce an
approach that was reverted, or rename a domain term, with file:line
references and the decision they conflict with.
```

## Pitfalls

- **Scope creep**: Don't expand the review beyond the diff being reviewed
- **Paralysis by analysis**: Set a time box; if the diff is too large, split the review. Panel mode produces more findings: set priority thresholds
- **Forgetting spec compliance**: Standards-only reviews miss functional bugs — always pair with spec review
- **Reviewer bias and false consensus**: Sub-agents should not know who wrote the code, have prior context, or see each other's findings
- **Conflicting findings**: Different reviewers may disagree — the human (user) has final say
- **Slow turnaround**: Spawning five agents takes longer than two — use panel mode only when the diff warrants it
- **Merge conflicts**: If the diff includes a merge, review the conflict resolution specifically

## Verification

- [ ] Every reviewer sub-agent completed and returned findings
- [ ] Findings were deduplicated across reviewers
- [ ] All Critical and High priority issues were addressed
- [ ] All Medium/Low issues were either fixed or explicitly acknowledged
- [ ] The receiving party (user or PR system) was presented with clear options
- [ ] If fixes were made, a re-review was conducted

## AspireCURES Context

Two-axis: insert this review between merge and commit in your preparer→executor pipeline, validating against both repo coding standards AND the originating research findings before the commit is finalized.

Panel: use it as the final review gate before the executor agent commits the weekly pipeline output. The bug hunter catches data-source parsing edge cases, the security auditor checks the web-scraping code for SSRF/path traversal, the contracts reviewer verifies against the gating thresholds, and the historical context reviewer checks for regressions in previously rendered disease pages.
