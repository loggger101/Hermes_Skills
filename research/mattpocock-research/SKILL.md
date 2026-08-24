---
name: mattpocock-research
description: "Research a question against primary sources."
version: 1.0.0
author: Adapted from mattpocock/skills
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [research, background-agent, primary-sources, citations]
    related_skills: [parallel-cli, arxiv, grounded-citations]
---
## When to Use

- When the user asks "research X", "investigate Y", "find out about Z"
- When docs or API facts need gathering
- When reading legwork should be delegated to a background agent
- When primary-source verification of a claim is needed

# Research (mattpocock)

Spin up a **background agent** to do the research, so you keep working while it reads.

## When to Use

- When the user asks "research X", "investigate Y", "find out about Z"
- When docs or API facts need gathering
- When reading legwork should be delegated to a background agent
- When primary-source verification of a claim is needed

## Core Discipline

1. **Primary sources only** — official documentation, source code, specs, first-party APIs. Follow every claim back to the source that owns it.
2. **Capture findings as a single Markdown file**, citing each claim's source.
3. **Save where the repo already keeps such notes**; match the existing convention.

## Process

### 1. Launch the background agent

Create a `delegate_task` that runs as a self-contained background agent. Pass everything it needs in `context`:
- The exact research question
- The output file path (absolute)
- The citation format expected
- Any constraints (e.g. "only peer-reviewed sources")

### 2. The agent investigates

The agent should:
- Seek primary sources (official docs, source code, specs, first-party APIs)
- Follow every claim back to its owning source
- Capture direct quotes, code snippets, or screenshots

### 3. The agent writes findings

Produce a single Markdown file that:
- Answers the research question directly
- Cites each claim's source with a link
- Matches the repo's existing convention for notes

## AspireCURES Context

Especially relevant for the weekly research pipeline that pulls from Europe PMC, PubMed, ClinicalTrials.gov, and ISRCTN. When a disease page needs deeper background research before materialization, spin up a research agent to investigate against the primary medical databases and save findings to `docs/research/` as cited Markdown.

---
Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) — Engineering/research.
