---
name: mattpocock-writing-for-agents
description: "Write docs agents can consume: skills, AGENTS.md, specs."
version: 1.1.0
author: Adapted from mattpocock/skills
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [writing, documentation, agent-docs, skills, AGENTS-md, CLAUDE-md]
    related_skills: [hermes-agent-skill-authoring, mattpocock-handoff, mattpocock-domain-modeling]
---

## When to Use

When writing prompts, agent instructions, skills, or documentation that will be consumed by an AI agent rather than a human. Use this skill whenever you're creating or editing:
- A `SKILL.md` file
- An `AGENTS.md` or `CLAUDE.md` file
- A system prompt or task instruction
- Any doc an agent reaches via a `skill_view()` or file reference

## What This Skill Does

Provides principles and templates for writing documentation that agents can parse, follow, and act on reliably. Covers structure, failure handling, examples, and discoverability.

## Core Principles

| # | Principle | Why It Matters |
|---|-----------|----------------|
| 1 | **Be Specific, Not Abstract** | \"Do X\" not \"Be mindful of X\" — agents can't infer intent from vague language |
| 2 | **Use Lists, Not Paragraphs** | Agents parse structured information (numbered/bulleted) far better than prose |
| 3 | **Include Failure Modes** | \"If X fails, try Y. If Y fails, escalate to Z\" — agents hit errors and need recovery paths |
| 4 | **Provide Concrete Examples** | Both correct and incorrect output, so agents learn the boundary |
| 5 | **Make Sections Findable** | Clear headers (`## Step 1`, `## Common Errors`) so agents can jump to relevant sections |
| 6 | **Link, Don't Duplicate** | Link to elsewhere; don't copy text — links stay in sync, duplicates diverge |
| 7 | **Version and Date Everything** | Agents need to know if docs are stale |
| 8 | **Respect Context Window** | Put critical info first — agents truncate long docs |

## For Skills (SKILL.md)

### Frontmatter
```yaml
---
name: skill-name
description: Use when <trigger>. <one-line behavior>.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [tag1, tag2]
    related_skills: [other-skill, another-skill]
---
```

**Field rules:**
- `name`: lowercase, hyphens only
- `description`: max 59 chars, trigger-first, ends with period
- `version`: use semver; bump for substantive changes
- `related_skills`: every skill this one references via `skill_view()`

### Body Structure
```
## When to Use          (triggers + non-triggers)
## What This Skill Does  (scope + boundaries)
## Prerequisites         (auth, tools, setup)
## Process               (numbered steps with code)
## Common Patterns       (tables, templates, decision matrices)
## Pitfalls              (things that go wrong, and how to avoid)
## Verification          (checklist: how to know you're done)
## AspireCURES Context   (project-specific notes)
```

### Anti-patterns
| What Agents See | Problem | Fix |
|----------------|---------|-----|
| \"Take appropriate action\" | Vague, no definition of \"appropriate\" | \"If the diff is <100 lines, approve. If >100, request changes.\" |
| A 5-paragraph explanation | Agents skim; may miss critical steps | Use a numbered list with code in each step |
| No failure handling | Agent hangs or produces garbage on error | Add a \"If X goes wrong\" section |
| Internal references | \"See below\" — agent can't see \"below\" | Use absolute section headers: \"See ## Common Errors\" |

## For AGENTS.md / CLAUDE.md

### Essential Sections
1. **Project purpose** — one sentence: what is this project?
2. **Conventions** — formatting, naming, testing patterns
3. **Available tools** — what tools exist, how to use them
4. **Development workflow** — how to make, test, and submit changes
5. **Directory structure** — where things live
6. **Failure handling** — what to do when tests fail, when build breaks

### Example Template
```markdown
# Project Name — For AI Agents

## Purpose
This project [does X]. It is used by [audience] to [achieve Y].

## Conventions
- Tests: run `npm test` (Jest + React Testing Library)
- Types: strict mode on, no `any` allowed
- Commits: conventional commits (`feat:`, `fix:`, `chore:`)
- PRs: must pass CI and have one approval

## Workflow
1. Create a feature branch: `git checkout -b feat/description`
2. Write tests first (see `mattpocock-tdd`)
3. Implement until green
4. Run linter: `npm run lint`
5. Push and open PR: `gh pr create --fill`

## Directory Structure
- `src/` — application code
- `tests/` — test files
- `docs/` — documentation
- `scripts/` — dev tooling scripts

## When Tests Fail
1. Run `npm test -- --verbose` to see which test failed
2. If new test: check if expected behavior was wrong
3. If existing test: check if your change broke it
4. If unsure: load `mattpocock-diagnosing-bugs` for debugging workflow
```

## For Cronjob Prompts

### Self-Containment Rules
1. **Embed exact guardrails** — copy thresholds, validation rules, rejection criteria directly into the prompt
2. **No context bleed** — the prompt must work in a fresh session with zero prior context
3. **Explicit failure modes** — what does \"nothing to do\" look like? What does \"error\" look like?
4. **Output shape** — specify the exact JSON/CSV/text format expected as output

### Template
```
You are a [role] running a [frequency] task. Your job: [one-sentence purpose].

Context: [all prerequisites embedded here]

Procedure:
1. [Step with exact conditions]
2. [Step with exact conditions]
...

Constraints:
- Never [thing to never do]
- Always [thing to always do]
- If [condition], then [action]

Output: JSON report at /path/to/report.json with fields: [exact fields].
If no work: write {status: "no_change"} and exit.
If error: write {status: "error", message: "..."} and exit non-zero.
```

## AspireCURES Context

When writing prompts for your cronjob (preparer) and commit (executor) agents, apply these principles. Each agent's prompt must be self-contained with exact guardrails. Document failure modes for each external API (Europe PMC, PubMed, ClinicalTrials.gov, ISRCTN). Use `skill_view(name='hermes-agent-skill-authoring')` when creating new skill files.
