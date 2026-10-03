---
name: mattpocock-multi-agent-code-review
description: "Multi-agent PR review: bug-hunter, security, contracts."
version: 1.0.0
author: Adapted from NeoLabHQ/context-engineering-kit
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [code-review, multi-agent, bug-hunter, security-auditor, contracts]
    related_skills: [mattpocock-code-review, requesting-code-review, mattpocock-security-review]
---

## When to Use

Use when the user wants a comprehensive, multi-perspective code review of a PR or diff — going beyond the single two-axis review with specialized reviewer personas. Also use when the user says "thorough review", "get multiple perspectives on this code", or "check for subtle issues".

## What This Skill Does

Dispatches multiple specialized sub-agents to review a diff from different angles, then consolidates findings:

1. **Bug hunter** — looks for logic errors, edge cases, off-by-one, null safety, race conditions
2. **Security auditor** — scans for injection, auth issues, secrets, SSRF, path traversal (load `skill_view(name='mattpocock-security-review')` for the OWASP checklist)
3. **Code quality reviewer** — checks naming, complexity, testability, adherence to conventions
4. **Contracts reviewer** — verifies the diff matches the originating spec/issue requirements
5. **Historical context reviewer** — reviews how this change interacts with past decisions (reads ADRs)

Loads `skill_view(name='requesting-code-review')` for the single-agent pre-commit pipeline and `skill_view(name='mattpocock-code-review')` for the two-axis review as alternatives.

## Prerequisites

- Git repository with a clean base branch
- Diff to review (captured via `git diff <base>...HEAD`)
- Ability to spawn `delegate_task` sub-agents

## Process

### 1. Prepare the diff
```bash
git diff <base-branch>...HEAD -- > /tmp/diff.patch
```

### 2. Dispatch parallel reviewers
Each reviewer gets the diff + a focused prompt:

- **Bug hunter prompt**: "Find logic errors, edge cases, null safety issues, race conditions. Look at each changed line for correctness."
- **Security auditor prompt**: "Review for injection, XSS, SSRF, path traversal, hardcoded secrets, auth bypass. Use OWASP checklist."
- **Code quality prompt**: "Check naming clarity, cyclomatic complexity, testability, consistency with repo conventions."
- **Contracts prompt**: "Verify each change maps to a requirement in the spec. Flag scope creep."

### 3. Consolidate findings
Merge findings from all reviewers into a single report. Deduplicate overlapping findings. Prioritise:

| Priority | Criteria |
|----------|----------|
| **Critical** | Security vulnerability, crash, data corruption |
| **High** | Logic bug, missing test, spec deviation |
| **Medium** | Code smell, naming issue, complexity |
| **Low** | Style, formatting, minor consistency |

### 4. Present options
- All clear → approve
- Minor findings → fix and re-review
- Major findings → discuss with user before proceeding

## Reviewer Persona Prompts

```python
# Bug hunter
"Review this diff for logic errors, edge cases, off-by-one bugs, null
safety issues, and race conditions. For each finding, note the
file:line and explain the failure mode."

# Security auditor
"Review this diff for security vulnerabilities: injection, XSS, SSRF,
path traversal, hardcoded secrets, auth bypass. Use the OWASP
checklist. Flag every security concern with file:line reference."

# Code quality
"Review this diff for code quality issues: unclear naming, high
cyclomatic complexity, missing tests, inconsistency with repo
conventions. Provide file:line references with suggestions."

# Contracts
"Review this diff against the originating spec/issue. Verify each
change maps to a requirement. Flag any scope creep or unrequested
changes with file:line references."
```

## When to Use

| Scenario | Recommendation |
|----------|---------------|
| Small diff (< 200 lines) | `skill_view(name='requesting-code-review')` — single agent is sufficient |
| New codebase, unclear conventions | Multi-agent — more perspectives catch convention gaps |
| Security-critical code | Multi-agent — security auditor persona adds depth |
| High-stakes release | Multi-agent — bug hunter + contracts reviewers add safety |
| Familiar code, trusted team | `skill_view(name='mattpocock-code-review')` — two-axis is faster |

## Pitfalls

- **Reviewer overlap**: Multiple reviewers may flag the same issue — deduplicate in consolidation
- **Conflicting findings**: Different personas may disagree — the human (user) has final say
- **Analysis paralysis**: Too many reviewers can produce too many findings — set priority thresholds
- **Slow turnaround**: Spawning 5 agents takes longer than 1 — only use when the diff warrants it
- **False consensus**: Reviewers should not know each other's findings — keep them independent

## Verification

- [ ] All reviewer sub-agents completed without errors
- [ ] Findings were deduplicated across personas
- [ ] All Critical and High priority issues were addressed
- [ ] Medium and Low issues were either fixed or explicitly acknowledged
- [ ] The user was presented with clear options (approve, fix then re-review, discuss)
- [ ] If fixes were made, a re-review was conducted

## AspireCURES Context

Use this as the final review gate before the executor agent commits the weekly pipeline output. The bug hunter catches data-source parsing edge cases, the security auditor checks the web-scraping code for SSRF/path traversal, the contracts reviewer verifies against the gating thresholds, and the historical context reviewer checks for regressions in previously rendered disease pages.
