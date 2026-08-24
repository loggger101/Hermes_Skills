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
    related_skills: [mattpocock-tdd, mattpocock-multi-agent-code-review, requesting-code-review]
---

## When to Use

Use when the user wants to ensure code changes are backed by verifiable evidence before merging — especially for data-processing pipelines, security-sensitive code, or high-stakes releases.

## What This Skill Does

Implements evidence-driven method pack for AI coding agents. Every change must be backed by evidence that it works, doesn't break existing functionality, and is secure. No assumptions — everything is verified.

## The Evidence Pyramid

1. **Test evidence** — unit, integration, and e2e tests pass
   - New test written AND watched fail before implementation — load `skill_view(name='mattpocock-tdd')`
   - Full test suite green after changes

2. **Static analysis evidence** — no new issues from linters/type-checkers
   - `skill_view(name='mattpocock-security-review')` — no new security vulnerabilities (CodeQL/Semgrep + OWASP check)
   - `skill_view(name='requesting-code-review')` — no new code smells

3. **Runtime evidence** — code actually runs correctly
   - CLI invocation with fixture input produces expected output
   - End-to-end pipeline run produces correct disease page output

4. **Diff evidence** — the diff itself is clean
   - `skill_view(name='mattpocock-code-review')` — Standards axis + Spec axis both pass
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
skill_view(name='mattpocock-security-review')
```
No new critical or high-severity findings.

### 3. Run code review
Invoke `skill_view(name='mattpocock-code-review')` with the fixed point (e.g. `main` branch).

### 4. Run the actual pipeline (if applicable)
For your AspireCURES pipeline: run the preparer → executor flow end-to-end and verify the 9 disease pages still render correctly.

## AspireCURES Context

Your pipeline already has a validation step in the executor agent. This skill formalizes it: every data-source parser change is backed by a failing test (red), the full pipeline runs without errors, no new security findings from scanning, and the two-axis code review passes. If any gate fails, the commit does not happen.
