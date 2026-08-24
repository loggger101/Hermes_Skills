---
name: mattpocock-spec-driven-development
description: "Spec-driven development with planning and quality gates."
version: 1.1.0
author: Adapted from NeoLabHQ/context-engineering-kit
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sdd, spec-driven, planning, architecture, quality-gates]
    related_skills: [mattpocock-to-tickets, mattpocock-codebase-design, mattpocock-code-review, mattpocock-domain-modeling, mattpocock-gh-fix-ci, mattpocock-security-review, mattpocock-tdd, requesting-code-review]

---

## When to Use

Use when the user wants a structured approach to turning a plan into production-ready code — with planning, architecture, implementation, and quality gates. Also use when the user says "follow a spec", "plan before building", or "I want evidence the code matches the requirements."

This skill chains from `skill_view(name='mattpocock-spec-driven-development')` when the spec is clear, and from `skill_view(name='requesting-code-review')` for the final quality gate.

## What This Skill Does

Implements **spec-driven development (SDD)**: a disciplined workflow that moves from high-level plan → concrete tickets → architectural design → TDD implementation → multi-axis quality gates. Each phase has explicit deliverables and exit criteria.

## The Workflow

```
Plan → Tickets → Architecture → Implement (TDD) → Quality Gates → Review
```

### Phase 1: Plan

Break the task into concrete, verifiable sub-tasks. Each should be testable, independent, and actionable. Load `skill_view(name='mattpocock-to-tickets')` to create tracer-bullet tickets.

**Exit criteria:**
- Every sub-task has a clear, testable outcome
- All sub-tasks together cover the full scope of the spec
- Dependencies between sub-tasks are identified (blocked by / blocks)

### Phase 2: Architecture

For each sub-task, design the interface and seam before implementing:
- What module/interface changes are needed?
- Where does the seam go? Load `skill_view(name='mattpocock-codebase-design')`
- What's the expected behavior at each seam?

Use the domain modeling vocabulary from `skill_view(name='mattpocock-domain-modeling')` to sharpen terms before drawing the architecture.

**Exit criteria:**
- Every module has a deep interface (small surface, lots of implementation)
- The deletion test passes for each major abstraction
- Edge cases are documented for each seam

### Phase 3: Implement

- Load `skill_view(name='mattpocock-tdd')` — write the failing test first, then implement
- Each sub-task is a vertical slice through every layer
- Run `skill_view(name='mattpocock-gh-fix-ci')` if CI fails

**Exit criteria:**
- New tests go RED before implementation
- Implementation goes GREEN after writing minimum code
- Refactored code still passes all tests (no regression)

### Phase 4: Quality Gates

Before marking complete, verify:
- Tests pass (new test + full suite)
- `skill_view(name='mattpocock-code-review')` — Standards axis + Spec axis both pass
- `skill_view(name='mattpocock-security-review')` — no new security concerns
- `skill_view(name='requesting-code-review')` — final human-style review

**Exit criteria:**
- All tests green (including new tests)
- Two-axis code review passes (standards + spec)
- No new security findings
- No code smells flagged

## Pitfalls

- **Skipping the ticket step** — jumping to architecture without breaking down the spec leads to oversized, untestable implementations
- **Architecture without seams** — designing modules that expose internals; load `skill_view(name='mattpocock-codebase-design')` first
- **TDD theater** — writing tests that pass immediately; the test must fail first (RED)
- **Skipping the final review** — quality gates only work if you run them
- **Scope creep in implementation** — fixing unrelated things while implementing one ticket

## Verification Checklist

- [ ] Plan → tickets: every requirement maps to a ticket
- [ ] Architecture → seams: every module has a clean public interface
- [ ] Implementation: every new behavior has a RED-then-GREEN test
- [ ] Quality gates: code review + security review + full test suite pass
- [ ] PR is small enough for a human to review in 15 minutes

## AspireCURES Context

Apply this workflow when adding a new disease page: plan the data-source parser, gating logic, and renderer as separate tickets; design module interfaces; implement with TDD at the parser seam; then run the two-axis code review against the originating research findings. This maps directly to your preparer→executor pattern.
