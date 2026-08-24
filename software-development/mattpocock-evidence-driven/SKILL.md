---
name: mattpocock-evidence-driven
description: "Validate code changes with evidence and testing gates."
version: 1.0.0
author: Adapted from GanyuanRan/Aegis
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [evidence, testing, validation, pre-merge, gates, aegis]
    related_skills: [mattpocock-tdd, mattpocock-multi-agent-code-review, requesting-code-review, mattpocock-code-review, mattpocock-security-review, mattpocock-using-git-worktrees]

---

## When to Use

Use when the user wants to ensure code changes are backed by verifiable evidence before merging — especially for data-processing pipelines, security-sensitive code, or high-stakes releases. Also use when the user says "verify", "validate", "quality gate", or "don't merge without tests".

## What This Skill Does

Implements evidence-driven method pack for AI coding agents. Every change must be backed by evidence that it works, doesn't break existing functionality, and is secure. No assumptions — everything is verified. Loads `skill_view(name='mattpocock-tdd')` for test-first discipline, `skill_view(name='mattpocock-security-review')` for security scanning, and `skill_view(name='mattpocock-code-review')` for standards/spec review.

## Prerequisites

- A git repository with a clean working tree (or isolated worktree via `skill_view(name='mattpocock-using-git-worktrees')`)
- Test suite configured and runnable
- Security scanning tools available (CodeQL, Semgrep) or willingness to do manual review

## The Evidence Pyramid

1. **Test evidence** — unit, integration, and e2e tests pass
   - New test written AND watched fail before implementation
   - Full test suite green after changes
2. **Static analysis evidence** — no new issues from linters/type-checkers
   - No new security vulnerabilities
   - No new code smells
3. **Runtime evidence** — code actually runs correctly
   - CLI invocation with fixture input produces expected output
   - End-to-end pipeline run produces correct results
4. **Diff evidence** — the diff itself is clean
   - Standards axis + Spec axis both pass
   - No hardcoded secrets, no path traversal, no injection vectors

## Process

Before merging any change:

### 1. Run the test suite
```bash
pytest tests/ -v
```
All tests must pass, including new tests that would fail without this change.

### 2. Run security scan
```bash
# Use mattpocock-security-review for OWASP checklist
skill_view(name='mattpocock-security-review')
```
No new critical or high-severity findings.

### 3. Run code review
```bash
# Use mattpocock-code-review for two-axis parallel review
skill_view(name='mattpocock-code-review')
```
Invoke with the fixed point (e.g. `main` branch).

### 4. Run the actual pipeline (if applicable)
For your project: run the end-to-end pipeline and verify the output is correct.

## Evidence Collection Table

| Evidence Type | Tool/Method | Pass Criteria | Must Have Test? |
|---------------|------------|---------------|-----------------|
| Unit tests | pytest/jest | All green, +1 new failing → passing | ✅ |
| Integration tests | pytest -m integration | All green | ✅ |
| Security scan | CodeQL + Semgrep | No new critical/high findings | ✅ (security-sensitive) |
| Code review | mattpocock-code-review | Standards + Spec both pass | ✅ |
| Type checking | mypy/tsc | No new errors | Recommended |
| Linting | ruff/eslint | No new warnings | Recommended |
| E2E test | Pipeline run | Output matches expected | ✅ (data pipelines) |

## Pitfalls

- **False confidence**: A green test suite doesn't mean the right thing was tested — verify the test actually exercises the changed code
- **Missing baseline**: If the test suite was already failing, you can't tell if your changes made it worse — capture baseline first
- **Security theater**: Running a scanner is not security — review the findings manually for context
- **Cargo-cult testing**: Copy-pasting tests that don't actually validate behavior
- **Over-engineering**: Not every change needs e2e — use judgment based on risk

## Verification

- [ ] Test evidence: New test written before implementation, watched fail, then pass after fix
- [ ] Static analysis: No new critical/high findings from security scan
- [ ] Runtime evidence: Pipeline produces correct output (or CLI produces expected output)
- [ ] Diff evidence: Two-axis code review passes (Standards + Spec)
- [ ] All evidence is documented in the commit or PR description

## AspireCURES Context

Your pipeline already has a validation step in the executor agent. This skill formalizes it: every data-source parser change is backed by a failing test (red), the full pipeline runs without errors, no new security findings from scanning, and the two-axis code review passes. If any gate fails, the commit does not happen.
