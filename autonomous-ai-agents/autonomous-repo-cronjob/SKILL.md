---
name: autonomous-repo-cronjob
description: Write self-contained cronjob prompts for existing repos.
version: 0.1.1
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cronjob, autonomous, repo-automation, pipeline, agent-as-gatekeeper]
    related_skills: [hermes-agent]
---

# Autonomous Repo Cronjob Skill

## Overview

When a Hermes `cronjob` needs to automate work against an existing repository that already
has its own CI pipeline (GitHub Actions, Makefile, etc.), the cronjob's prompt body must
be **self-contained** (no session context) and must embed the repository's own guardrails,
data formats, and conventions. In some cases the agent **substitutes its own model access
for an API-key-gated step** in the existing pipeline — for example, replacing a script's
direct Anthropic API call with the agent's own Claude judgments.

This skill teaches the pattern for drafting that prompt body correctly.

## When to Use

- A cronjob will run against a specific repository and needs a self-contained prompt.
- The repository has an existing CI/CD pipeline whose logic the cronjob should mirror.
- The pipeline gates a step behind an API key (e.g. `ANTHROPIC_API_KEY`) that the cronjob
  agent doesn't need — because the agent IS the model, not a script calling the model API.
- The repository has specific guardrails (append-only data, date-churn prevention, safe-fail,
  dedup logic) that must be encoded in the prompt to prevent corruption.
- The user says "document the exact specifics and guardrails within the cronjob prompt body"
  but "don't make any edits to the repo."
- The user wants a **two-agent split**: the cronjob (preparer) emits a report, and a
  separate commit agent does the actual repo writes (see references/two-agent-architecture.md).

**Don't use for:**
- Simple one-off scripts with no existing repo conventions to mirror.
- Tasks where the agent can just read and call scripts directly without replicating their
  internal logic.
- Repos with no CI pipeline or no API-key-gated steps.

## Prerequisites

- The target repository's documentation surface is readable (config files, README, workflow
  YAMLs, the main pipeline script).
- The repository's CI workflow (`.github/workflows/*.yml`) is the canonical run sequence.
- The pipeline script (e.g. `tools/research/fetch_curate.mjs`) is the source of truth for
  internal logic (dedup rules, signature computation, safe-fail behavior).

## How to Run

This is a **prompt-authoring skill** — it doesn't execute code. It produces a cronjob prompt
that is then passed to `cronjob(action='create', ...)`.

The workflow:

1. Read the repository's CI workflow file(s) end-to-end — these define the exact run
   sequence, env vars, and commit logic.
2. Read the main pipeline script(s) — these define the internal guardrails: dedup logic,
   signature/date-churn prevention, structural validation, safe-fail behavior, the
   append-only merge semantics, and which fields render vs. which are stored-only.
3. Read the config file(s) — these define per-page queries, relevance rules, thresholds,
   and spend caps.
4. Read the repo's main documentation (README, TODO, MAINTENANCE) for context on what's
   open, what's decided, and what guardrails exist.
5. Synthesize a prompt body structured as:
   - **Agent role + repo context** (self-contained, no assumptions about prior knowledge)
   - **Two run modes** (key-gated vs keyless — explain both)
   - **Your substitution role** (which steps the agent replaces vs. which the script still does)
   - **Autonomous mode guidance** (no user interaction, but full reasoning capability)
   - **The run sequence** (one step per CI step, in order, with the exact command + rationale)
   - **Guardrails** (the hard rules: append-only, date-churn signature logic, safe-fail,
     dedup keys, country normalization, spend caps)
   - **The agent-vs-commit-agent split** (if the user wants a two-agent architecture)
   - **Data file shape** (field-by-field reference, including field stripping rules)
   - **Lint-feed.pl validation matrix** (self-check rules the agent should apply before emitting)
   - **Failure modes & responses**
   - **Output format**
6. Create the cronjob with `cronjob(action='create', prompt=<body>, schedule=<cron>,
   skills=[...], workdir=<repo_root>)`.

## Quick Reference

```bash
# 1. Survey the repo's pipeline
read_file .github/workflows/research.yml
read_file tools/research/fetch_curate.mjs
read_file tools/research/config.json
read_file tools/research/README.md
read_file TODO.md
read_file MAINTENANCE.md

# 2. Draft the prompt body (see references/drafting-guide.md + prompt-template.md)
# 3. Create the cronjob
cronjob(action='create',
  prompt=<body>,
  schedule='17 13 * * 1',   # weekly Monday 13:17 UTC (match the repo's CI cron)
  workdir='~/path/to/repo',
  skills=[...],
  deliver='origin')
```

## Procedure

### Step 1: Identify the existing CI run sequence

Read the workflow YAML(s). Document each step in order — every `step:` block is a cronjob step. Note:
- `fetch-depth` requirements (pagedate.pl and similar tools walk git history)
- Node version pins
- Env var sources (`secrets.X` vs optional)
- The exact commit message format
- Conditional logic (commit-if-changed)

### Step 2: Identify the internal guardrail logic

Read the main pipeline script. For every comment that says "this is why X matters" or
"do not Y," embed the rationale in the prompt body. Key patterns:

| Guardrail | What to document in the prompt |
|---|---|
| **Append-only merge** | Existing items KEPT; new ones added, never removed. Retracted = flagged. Closed trials = archived. |
| **Date churn prevention** | Signature comparison: canonical JSON (sorted keys), EXCLUDING `generated` itself + unrendered fields |
| **Safe-fail** | Each entity wrapped in try/catch. Failed entity skipped, existing data untouched. |
| **Dedup keys** | PMID AND DOI (and normalized title for cross-registry). Same paper from two DBs = one entry. |
| **Spend caps** | Token budget + call budget. Agent self-regulates but knows the ceiling. |
| **Unrendered fields** | Stored but NOT rendered → EXCLUDED from date-churn signature. See references/agent-vs-script-checklist.md. |
| **Structural validation** | Real PMID/DOI, English, abstract ≥ 80, in-window date, pickDate (not print date). |
| **Country normalization** | COUNTRY_FIX map applied. Document canonical forms (Turkey/Türkiye/Turkey (Türkiye) → Türkiye). |

### Step 3: Identify the key-gated step

Find `const KEY = process.env.ANTHROPIC_API_KEY;` and `const CURATE = !!KEY;`.

The maintenance-only branch runs without the key. Document every function in it — these
are steps the script STILL does when the agent substitutes for the key.

Everything else (fetch + Claude-curate + merge) is what the AGENT must do.

**Critical:** The maintenance branch must NOT be skipped. It refreshes trial statuses
(prevents advertising closed trials as "Recruiting") and re-checks retractions.

### Step 4: Determine which fields render vs. which are stored-only

Read the renderer for each field. IS it rendered? → counts as a data change. Is it
stored but NOT rendered? → EXCLUDE from the date-churn signature.

### Step 5: Write the prompt body

Structure as a self-contained system prompt. Every fact must be IN the prompt — cronjob
sessions have no prior context. Include all guardrails with enough detail to execute.

### Step 6: Create the cronjob

```
cronjob(action='create', prompt=<body>, schedule=<cron>, workdir=<repo_root>,
  skills=[...], deliver='origin')
```

## Pitfalls

1. **Omitting the git history fetch.** If `pagedate.pl` walks commit history, a shallow
   checkout makes every page look "changed today." Include `git fetch --unshallow`. (TODO.md C6.)

2. **Skipping maintenance-only passes.** When the API key is absent, the script runs a
   maintenance-only mode that refreshes trial statuses and re-checks retractions. This
   prevents pages from advertising stopped trials as "Recruiting." Document WHY this matters.

3. **Treating "no changes" as a failure.** With signature-based date-churn prevention, a run
   that adds nothing commits nothing. Silent run IS success. The prompt must make this explicit
   or the agent will fabricate changes.

4. **Not replicating the dedup logic.** Dedup by PMID AND DOI (and normalized title for
   cross-registry). If the agent doesn't replicate this, it re-adds papers the pipeline has.

5. **Including unrendered fields in the date-churn signature.** Fields stored but NOT rendered
   must be EXCLUDED. See references/agent-vs-script-checklist.md for the UNRENDERED map pattern.

6. **Writing the date stamp unconditionally.** Must compute signature → compare → bump ONLY
   if changed.

7. **Omitting the relevance rules.** Read each page's config.json `relevance` rule and embed it.

8. **Not embedding the commit-if-changed logic.** `git status --porcelain` must be non-empty
   before committing. Do NOT fabricate changes.

9. **Omitting house-style constraints.** If the repo forbids em/en dashes, the agent must
   enforce this directly (no deDash() when the agent writes summaries).

10. **Not documenting the two-mode split clearly.** Explain which steps the SCRIPT does
    (maintenance-only) vs. which the AGENT does (candidate collection + curation + merge).

11. **Autoconfirming when the agent doesn't write files.** If the user wants a two-agent split
    (preparer + commit agent), document the exact report structure, field-stripping rules, and
    the commit_instructions block. See references/two-agent-architecture.md.

12. **Not self-validating before emitting.** The preparer should check its approved items
    against lint-feed.pl's rules BEFORE emitting the report, to prevent the commit agent from
    hitting failures. See references/agent-vs-script-checklist.md §Self-Validation.

## Verification

- The prompt body references every file in the run sequence by exact relative path.
- The guardrail list includes: append-only, date-churn signature (with field exclusions),
  safe-fail per page, dedup keys (PMID + DOI + title), spend caps, country normalization,
  silent-run-is-success.
- The data file shape section lists every field, with rendered vs. stored-only distinctions.
- The failure-modes section covers: API rate limits, corrupt JSON, render.pl skips, git push
  conflicts, sync client issues.
- The output format produces a single summary line.

## References

- `references/prompt-template.md` — Fill-in-the-blank template for the prompt body.
- `references/drafting-guide.md` — How to turn repo research into a prompt (7-phase process).
- `references/agent-vs-script-checklist.md` — Decision checklist + lint-feed.pl validation
  matrix + autonomous mode guidance + self-validation layer.
- `references/two-agent-architecture.md` — When and how to split the cronjob into a preparer
  agent (emits report) + commit agent (does repo writes + render + commit).