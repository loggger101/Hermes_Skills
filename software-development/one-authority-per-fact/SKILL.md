---
name: one-authority-per-fact
description: "One authority per fact; copies generated or checked."
version: 1.0.0
author: Hermes Agent (from the knowledge vault's one-authority-per-fact page, checked across 11 of the owner's repos, 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [single-source-of-truth, generated-files, drift, docs, ci, provenance, hygiene]
    related_skills: [verification-culture, living-docs-governance, repo-atlas, ci-gate-design, bit-identity-float-pipelines, failure-signal-audit]
---

# One authority per fact

## What This Skill Does

States the rule under most of the owner's tooling: **every fact has one authoritative place, and every other copy is either generated from it or held to it by a check.** The failure it prevents is always the same: one copy is updated, the other is not, and nothing goes red. The skill gives the techniques, the catalogue of copy types a repo grows, and the places the rule still leaks.

## When to Use

- Adding a number, table, version, address or list that already appears elsewhere
- Writing a "keep these in sync" comment (that is a request for a checker)
- Reorganising docs, or moving history out of a README or CLAUDE.md
- Auditing a repo for drift between code, docs, generated files and counts
- Not for choosing documentation roles (`living-docs-governance`), repo maps (`repo-atlas`), or masked failures in code (`failure-signal-audit`)

## Techniques

1. **Generate, then diff in CI.** Commit the generated file so it can be served or imported, and have CI prove it still equals its source. Render into a scratch directory, never over the committed copy: exporting into the directory under test is a check that cannot fail.
2. **Derive instead of typing.** Dates from `git log`, counts from the table, a CI pin from the consumer's own parser ("is what stops CI becoming the fourth place a repin has to land").
3. **Name generated files up front as an editing rule** ("`master.py` is built, never edited"; edit the domain CSV, never the merged one).
4. **Point, don't copy.** Name the authority instead of repeating it ("naming one authority is the alternative to having two that drift").
5. **When a copy cannot be avoided, a check holds the copies together**, and a register of known copies works as an allowlist: a known pair is fine, a pair nobody knows about is not.
6. **Move history with a no-loss check, then delete the old copy**: verify a few hundred distinctive numbers survive the move before removing the original.
7. **Do not restate what rots.** Do not spell a table's length or an interpreter version in prose; tell the reader to ask the machine. A number typed into a sentence among derived ones should fail a check.

## Catalogue of copy types a repo grows

A documented default against its dataclass; version tables; row counts in prose; a list in one file against another; a runtime table against the measured JSON; a measurement moved in a reorganisation; a pair of prose quotes; docs against the checks the harness actually runs; a typed number among derived ones; a guard mirrored into modules that cannot import a helper; a register of what a worked calculation borrows. Every check should **fail, not skip**, when a file it reads is missing: a renamed file once silently shrank a check from 486 definitions to 469 and the run still exited 0.

## Procedure

1. List the places a fact appears; choose the authority (code, data file, or generator input).
2. Make every other copy generated, derived, or pointed to; where a copy must stay, add a check and register it.
3. Put the rule in the repo's agent instructions as an editing rule ("edit X, never Y").
4. Write checks that fail on a missing input; prove each on a planted defect.
5. When moving history or docs, run a no-loss check first.

## Where it still leaks

- Two copies that disagree because neither holds a digit (a licence stated in two files).
- A README headline typed beside a JSON the tests guard, while nothing guards the sentence.
- A comment that restates code and drifts from it.
- A count copied through a memory, a repo doc and a wiki until it is wrong in three places.
- Cross-repo copies (a project page repeating figures from its source repo) with no checker of their own.
- **A reason can go stale while its fact stays true**: an argument for a duplicated constant outlived the circumstance that justified it. A reason has no digits in it, so grep for stale numbers will not find it.

## Pitfalls

- "Keep these in sync" comments: a promise a human keeps until the day they do not.
- Checks that skip silently when inputs are missing.
- Fixing the number but not the sentence that quotes it.

## Verification

- [ ] Each duplicated fact has one named authority
- [ ] Every remaining copy is generated or held by a failing check
- [ ] The editing rule is written where agents will read it
- [ ] A planted divergence turned the check red
