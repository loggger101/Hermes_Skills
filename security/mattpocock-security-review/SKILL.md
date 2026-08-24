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
    related_skills: [requesting-code-review, mattpocock-code-review, mattpocock-multi-agent-code-review]

---

## When to Use

Use when auditing a codebase for security vulnerabilities, reviewing code for production deploy, or writing new code with secure-by-default patterns. Also covers static analysis tooling (CodeQL/Semgrep). Loads `skill_view(name='requesting-code-review')` for the full pre-commit security pipeline, and `skill_view(name='mattpocock-multi-agent-code-review')` for specialized security auditor sub-agent review.

## What This Skill Does

Reviews Python, JavaScript/TypeScript, and Go codebases for security vulnerabilities using language-specific guidance. Three modes:

1. **Secure-by-default** — Writing new code with secure patterns
2. **Passive flagging** — Catching critical issues during development
3. **Vulnerability report** — Generating a prioritized report

## Prerequisites

- Static analysis tools installed:
  - CodeQL (from GitHub CLI: `gh extension install github/codeql`)
  - Semgrep (`pip install semgrep`)
- Understanding of the target language's security model
- The codebase to review

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

### Go
- **SQL injection**: use parameterized queries (not `fmt.Sprintf`)
- **Command injection**: avoid `exec.Command` with user input
- **Path traversal**: use `filepath.Clean` + base directory checks
- **Insecure TLS**: enforce TLS 1.2+, pin certificates when needed

## Prerequisites Checklist

| Item | Status |
|------|--------|
| CodeQL installed and authenticated | ☐ |
| Semgrep installed | ☐ |
| Target codebase cloned/accessed | ☐ |
| Language-specific linting configured | ☐ |

## Process

### 1. Run automated scanners
Execute CodeQL and Semgrep against the codebase. Collect all findings.

### 2. Manual review pass
Go through the code line-by-line for:
- Hardcoded secrets in config files
- User input flowing to dangerous sinks
- Authentication/authorization bypasses
- Race conditions in concurrent code

### 3. Prioritise findings

| Priority | Criteria |
|----------|----------|
| **Critical** | RCE, SQL injection, auth bypass, hardcoded secrets |
| **High** | XSS, SSRF, path traversal, insecure deserialization |
| **Medium** | Weak crypto, verbose error messages, missing CORS |
| **Low** | Missing security headers, predictable IDs |

### 4. Document and report
For each finding: describe the vulnerability, show the vulnerable code, explain the impact, and provide a fix.

## Pitfalls

- **False positives**: Static scanners flag many non-issues — verify each finding manually
- **Missing context**: Scanners can't see business logic — manual review is essential
- **Outdated rules**: Keep CodeQL and Semgrep rulesets updated
- **Secret scanning fatigue**: Too many alerts from committed test keys — train developers to rotate and use `.env` files
- **Over-scanning**: Running too many ruleset combinations creates noise — focus on OWASP Top 10 first

## Verification

- [ ] CodeQL scan completed with no new Critical findings
- [ ] Semgrep scan completed with no new High+ findings
- [ ] Manual review of OWASP checklist items specific to the language
- [ ] All existing Critical/High findings are either fixed or documented as accepted risk
- [ ] Report includes proof-of-concept for each vulnerability (not just "could be vulnerable")

## AspireCURES Context

The pipeline downloads untrusted data from medical databases. Flag: hardcoded API keys in cronjob scripts, path traversal in disease-page file writes, SSRF in web-scraping code, injection in the SQLite storage layer. Run CodeQL + Semgrep before each commit.

This skill integrates with `skill_view(name='requesting-code-review')` — load both for a complete pre-merge gate that catches both security vulnerabilities and code quality issues.
