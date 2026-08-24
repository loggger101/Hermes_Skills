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

## What This Skill Does

Spins up a **background agent** (via `delegate_task`) to conduct research against primary sources, so the main agent keeps working while the research agent reads, verifies, and writes findings to a file. Loads `skill_view(name='parallel-cli')` for web search capabilities, `skill_view(name='arxiv')` for academic papers, and `skill_view(name='grounded-citations')` for citation format guidance.

## Prerequisites

- A clear, specific research question
- Output file path (absolute path) for the findings document
- Understanding of the citation format expected

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

```python
delegate_task(
    goal="Research [question]. Investigate using primary sources only. Follow every claim back to the source that owns it. Capture direct quotes, code snippets, or evidence. Write findings to [output_path] as Markdown with citations.",
    context="[Full research question, output path, citation format, constraints]",
    background=True
)
```

### 2. The agent investigates

The agent should:
- Seek primary sources (official docs, source code, specs, first-party APIs)
- Follow every claim back to its owning source
- Capture direct quotes, code snippets, or screenshots
- Avoid summarizing secondary sources — go to the original

### 3. The agent writes findings

Produce a single Markdown file that:
- Answers the research question directly
- Cites each claim's source with a link
- Matches the repo's existing convention for notes
- Flags any claims that could not be verified with primary sources

### 4. Verify findings

Read back the output file and verify:
- Each claim has a citation
- Sources are primary (not blog summaries of blog summaries)
- The research question is directly answered
- Ambiguous or unverifiable claims are flagged as such

## Research Quality Checklist

| Criterion | Check |
|-----------|-------|
| **Primary sources** | At least one source is the original documentation, spec, or codebase |
| **Verifiable** | Each claim can be traced back to a cited URL or file |
| **Non-redundant** | No claim is supported only by a secondary source when a primary exists |
| **Directly relevant** | Every finding relates to the research question |
| **Uncited claims flagged** | Claims without primary source verification are marked as such |

## Pitfalls

- **Source creep**: Don't let the research scope expand beyond the original question — set boundaries in the agent context
- **Circular citations**: A blog post citing the docs is fine; a blog post citing another blog post is not a primary source
- **False authority**: Being first-party doesn't make a source correct — cross-check surprising claims
- **Over-researching**: If 3 sources agree on a point, stop — don't keep digging for a 4th
- **Writing instead of researching**: The background agent should capture findings, not synthesize opinions

## Verification

- [ ] Output file exists at the specified path
- [ ] Every claim in the findings file has a citation to a primary source
- [ ] The research question is directly answered in the output
- [ ] Any unverifiable claims are explicitly flagged
- [ ] No secondary-source-only claims were presented as fact

## AspireCURES Context

Especially relevant for the weekly research pipeline that pulls from Europe PMC, PubMed, ClinicalTrials.gov, and ISRCTN. When a disease page needs deeper background research before materialization, spin up a research agent to investigate against the primary medical databases and save findings to `docs/research/` as cited Markdown.

---
Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) — Engineering/research.
