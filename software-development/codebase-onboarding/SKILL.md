---
name: codebase-onboarding
description: "Onboard to a new repo: arch map + starter AGENTS.md."
version: v0.1.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [onboarding, codebase-analysis, architecture-map, agents-md, reconnaissance]
    related_skills: [code-wiki, mattpocock-codebase-design]
---

<!-- source: affaan-m/ECC (MIT), ported 2026-09-09; CLAUDE.md references adapted to AGENTS.md -->
# Codebase Onboarding

Systematically analyze an unfamiliar codebase and produce a structured onboarding guide. Designed for developers joining a new project or setting up agent instructions in an existing repo for the first time.

## What This Skill Does

Runs a four-phase workflow — reconnaissance (parallel signal gathering without reading every file), architecture mapping, convention detection, artifact generation — producing two outputs: a 2-minute-scannable onboarding guide and a starter `AGENTS.md` with detected conventions. Enhances rather than replaces an existing instruction file.

## When to Use

- First time opening a project in an agent harness
- Joining a new team or repository
- User asks "help me understand this codebase"
- User asks to generate an AGENTS.md (or CLAUDE.md) for a project
- User says "onboard me" or "walk me through this repo"

## How It Works

### Phase 1: Reconnaissance

Gather raw signals about the project without reading every file. Run these checks in parallel:

```text
1. Package manifest detection
   → package.json, go.mod, Cargo.toml, pyproject.toml, pom.xml, build.gradle,
     Gemfile, composer.json, mix.exs, pubspec.yaml

2. Framework fingerprinting
   → next.config.*, nuxt.config.*, angular.json, vite.config.*,
     django settings, flask app factory, fastapi main, rails config

3. Entry point identification
   → main.*, index.*, app.*, server.*, cmd/, src/main/

4. Directory structure snapshot
   → Top 2 levels of the directory tree, ignoring node_modules, vendor,
     .git, dist, build, __pycache__, .next

5. Config and tooling detection
   → .eslintrc*, .prettierrc*, tsconfig.json, Makefile, Dockerfile,
     docker-compose*, .github/workflows/, .env.example, CI configs

6. Test structure detection
   → tests/, test/, __tests__/, *_test.go, *.spec.ts, *.test.js,
     pytest.ini, jest.config.*, vitest.config.*
```

### Phase 2: Architecture Mapping

From the reconnaissance data, identify:

**Tech Stack** — language(s) and version constraints; framework(s) and major libraries; database(s) and ORMs; build tools and bundlers; CI/CD platform.

**Architecture Pattern** — monolith, monorepo, microservices, or serverless; frontend/backend split or full-stack; API style: REST, GraphQL, gRPC, tRPC.

**Key Directories** — map the top-level directories to their purpose (e.g. `src/components/` → UI components, `src/api/` → route handlers, `tests/` → test suites). Replace examples with detected directories.

**Data Flow** — trace one request from entry to response: where does it enter (router/handler/controller)? how is it validated (middleware/schemas/guards)? where is business logic? how does it reach the database (ORM/raw queries/repositories)?

### Phase 3: Convention Detection

Identify patterns the codebase already follows:

**Naming Conventions** — file naming style; component/class naming patterns; test file naming (`*.test.ts`, `*.spec.ts`, `*_test.go`).

**Code Patterns** — error handling style (try/catch, Result types, error codes); dependency injection or direct imports; state management approach; async patterns.

**Git Conventions** — branch naming from recent branches; commit message style from recent commits; PR workflow (squash/merge/rebase). If the repo has no commits yet or only a shallow history (e.g. `git clone --depth 1`), skip this section and note "Git history unavailable or too shallow to detect conventions".

### Phase 4: Generate Onboarding Artifacts

#### Output 1: Onboarding Guide

```markdown
# Onboarding Guide: [Project Name]

## Overview
[2-3 sentences: what this project does and who it serves]

## Tech Stack
| Layer | Technology | Version |
|-------|-----------|---------|
| Language | ... | ... |
| Framework | ... | ... |
| Database | ... | ... |
| Testing | ... | - |

## Architecture
[Diagram or description of how components connect]

## Key Entry Points
- **API routes**: `...` — route handlers
- **UI pages**: `...` — authenticated pages
- **Database**: `...` — data model source of truth
- **Config**: `...` — build and runtime config

## Directory Map
[Top-level directory → purpose mapping]

## Request Lifecycle
[Trace one API request from entry to response]

## Conventions
- [File naming pattern]
- [Error handling approach]
- [Testing patterns]
- [Git workflow]

## Common Tasks
- **Run dev server**: `...`
- **Run tests**: `...`
- **Database migrations**: `...`
- **Build for production**: `...`

## Where to Look
| I want to... | Look at... |
|--------------|-----------|
| Add an API endpoint | `src/api/` |
| Add a test | `tests/` matching the source path |
```

#### Output 2: Starter AGENTS.md

Generate or update a project-specific `AGENTS.md` (or `CLAUDE.md`, whichever harness file this repo already uses — check first) based on detected conventions. If one already exists, read it and enhance it — preserve existing project-specific instructions and clearly call out what was added or changed:

```markdown
# Project Instructions

## Tech Stack
[Detected stack summary]

## Code Style
- [Detected naming conventions]
- [Detected patterns to follow]

## Testing
- Run tests: `[detected test command]`
- Test pattern: [detected test file convention]
- Coverage: [if configured, the coverage command]

## Build & Run
- Dev / build / lint commands as detected

## Project Structure
[Key directory → purpose map]

## Conventions
- [Commit style if detectable]
- [PR workflow if detectable]
- [Error handling patterns]
```

## Best Practices

1. **Don't read everything** — reconnaissance should use glob and grep, not file reads on every file. Read selectively only for ambiguous signals.
2. **Verify, don't guess** — if a framework is detected from config but the actual code uses something different, trust the code.
3. **Respect existing instruction files** — if AGENTS.md/CLAUDE.md already exists, enhance it rather than replacing it; call out what's new vs existing.
4. **Stay concise** — the onboarding guide should be scannable in 2 minutes. Details belong in the code, not the guide.
5. **Flag unknowns** — if a convention can't be confidently detected, say so rather than guessing. "Could not determine test runner" is better than a wrong answer.

## Anti-Patterns to Avoid

- Generating an instruction file longer than 100 lines — keep it focused
- Listing every dependency — highlight only the ones that shape how you write code
- Describing obvious directory names — `src/` doesn't need an explanation
- Copying the README — the onboarding guide adds structural insight the README lacks

## Examples

### Example 1: First time in a new repo
**User**: "Onboard me to this codebase" → Run full 4-phase workflow; Onboarding Guide printed to conversation plus `AGENTS.md` written to project root.

### Example 2: Generate instructions for existing project
**User**: "Generate an AGENTS.md for this project" → Phases 1–3 only, produce the instruction file with detected conventions.

### Example 3: Enhance existing instructions
**User**: "Update the AGENTS.md with current project conventions" → Read existing file, run Phases 1–3, merge new findings with additions clearly marked.
