---
name: mattpocock-security-review
description: "Review code for security vulnerabilities by language."
version: 1.0.0
author: Adapted from openai/skills
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [security, vulnerability, owasp, code-review, python, typescript]
    related_skills: [requesting-code-review, mattpocock-code-review]
---

## When to Use

Use when auditing a codebase for security vulnerabilities, reviewing code for production deploy, or writing new code with secure-by-default patterns. Also covers static analysis tooling (CodeQL/Semgrep).

## What This Skill Does

Reviews Python, JavaScript/TypeScript, and Go codebases for security vulnerabilities using language-specific guidance. Three modes:

1. **Secure-by-default** — Writing new code with secure patterns
2. **Passive flagging** — Catching critical issues during development
3. **Vulnerability report** — Generating a prioritized report

## Static Analysis (CodeQL + Semgrep)

For automated scanning, run both tools together:

```bash
# CodeQL taint analysis
codeql database create /tmp/db --language=python --command="python -m pytest"
codeql database analyze /tmp/db security-and-quality -d /tmp/results/

# Semgrep OWASP + Trail of Bits rulesets
semgrep --config=auto --output=semgrep-results.sarif

# Aggregate and deduplicate findings
# Prioritise: Critical → High → Medium → Low
```

## OWASP Checklist

### Python
- **Injection**: parameterized queries, no string interpolation in SQL
- **Hardcoded secrets**: API keys, passwords, tokens — flag immediately
- **Insecure deserialization**: avoid `pickle`, use JSON/pydantic
- **Path traversal**: validate with `os.path.realpath` + prefix checks
- **SSRF**: validate URLs before fetching

### JavaScript/TypeScript
- **XSS**: input sanitization, output encoding, CSP headers
- **Prototype pollution**: validate object keys, freeze objects
- **Dependency confusion**: pin dependencies, audit regularly
- **Insecure JWT**: verify signatures, short expiry

## AspireCURES Context

The pipeline downloads untrusted data from medical databases. Flag: hardcoded API keys in cronjob scripts, path traversal in disease-page file writes, SSRF in web-scraping code, injection in the SQLite storage layer. Run CodeQL + Semgrep before each commit.

This skill integrates with `skill_view(name='requesting-code-review')` — load both for a complete pre-merge gate that catches both security vulnerabilities and code quality issues.
