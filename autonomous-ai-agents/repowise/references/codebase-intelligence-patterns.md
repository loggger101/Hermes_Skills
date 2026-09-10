---
description: "Engineering patterns from repowise-dev/repowise (AGPL-3.0) — distillation contracts, decayed git signals, confidence-scored graphs, benchmark discipline; formulas + verified numbers"
source_repos: repowise-dev/repowise (docs/layers/*, docs/BENCHMARKS.md), clone @ 9f52f0a mined 2026-09-10; operational claims re-tested live with v0.49.0 on Windows/py3.13
verified_date: "2026-09-10"
---

# Codebase Intelligence Patterns (distilled from repowise)

General-purpose engineering knowledge extracted from how repowise builds a precomputed codebase index for AI agents. AGPL-3.0 — patterns only, no code ported. Everything marked **verified** was executed on this machine 2026-09-10; the rest is documented design intent (still useful as reference architecture).

## 1. Reversible distillation contract (command-output compression)

The problem: most of what an agent reads back from a shell command is noise — 300 lines of passing tests around 4 failures, full commit bodies when it asked "what changed recently". The fix is to compress **before** the model sees it.

Contract rules that make this safe (all verified live):
- **Errors first**: failure blocks move to the top; everything else demoted or omitted.
- **Exit code preserved exactly** — `distill` returns rc=0 for rc=0 and rc=1 for rc=1 of the wrapped command. An agent deciding "did it pass?" must never be able to mistake compression for success/failure. (Verified: both directions.)
- **Lossless by construction**: every omission leaves an inline `[repowise#<ref>]` marker; `expand <ref>` reverses it byte-for-byte so the agent can pull detail back without re-running the command. Verified round-trip on a 12,448-token git log → 1,362 tokens (89%); only difference was CRLF normalization under Windows text-mode capture — i.e., normalize line endings before comparing if you build this yourself.
- **Small outputs pass through untouched** — no compression overhead below a threshold; never "improve" output that's already cheap.
- **Deterministic token accounting**: savings counted with tiktoken, not estimates; `repowise saved` groups by filter kind (git_log etc.) so you can see which wrappers earn their keep.

Generalization: any wrapper between an agent and a noisy command should be *reversible + exit-code-faithful*, or it's silently changing the evidence base of every decision downstream.

## 2. Deterministic core, model as opt-in upgrade path

The entire index (graph, git signals, wiki structure, decisions from 6/7 sources, health scores) builds with **zero LLM calls** and no API key — verified: `init --no-prose` on a scratch project produced graph + 8 structural wiki pages in ~2s. Model-written prose is an *upgrade* applied per page / directory / ranked slice, with cost shown before confirm ("pay only for what you pick").

Why this matters as a pattern:
- The free tier must be **complete**, not a crippled demo — every layer works keyless; the LLM only changes presentation quality.
- Deterministic layers are bit-reproducible and testable without network or spend; that's why their benchmark numbers can be claimed at all (see §6).
- For any agent tooling: separate "compute" from "polish". Polish is the part you bill, cache per-input, and can regenerate.

## 3. Git behavioural signals — formulas worth stealing

Static analysis cannot see *behaviour*; git history encodes it for free. The concrete recipes (from docs/layers/*):

**Hotspots**: exponentially-decayed sum of per-commit churn with **halflife 180d**, each commit contributing up to a capped weight (~3.0), plus activity floors so one-line files don't dominate on ratio alone. Raw decayed churn is unbounded (observed max ~23) — expose `churn_percentile` for a normalized 0–1 rank, keep the raw value only as an intermediate input.

**Bug-fix history ("bug cache")**: count bug-fix commits per file in a trailing window; this is "the single most cost-effective defect predictor (defects cluster)" — Ostrand & Weyuker's classic result, and it holds here: prior-defect history adds +0.117 AUC vs churn alone (+0.100). Two refinements that make the number mean something:
- **Recency decay with 90-day half-life** (swept against 60/90/180; 90 and 180 tied, 60 lost): a fix from a year ago counts as a half. The result is "recent-equivalent fixes", not a raw tally — files that broke constantly then settled decay away to zero.
- **Anchor the clock to the change's own date, not today** — so re-scoring the same commit always yields the same number (idempotent). This is the subtle one: any score an agent consumes must be stable across runs or it becomes noise.

**Bug-fix classifier**: commits matching fix/revert/hotfix shape in message + non-test/non-config file paths; test-file and config-file changes are excluded from "the code broke" counts (patterns live in `core/ingestion/git_indexer/fix_shape.py` of the source).

**Percentile, not absolute**: a bare "3.4 decayed fixes" means nothing on its own — rank density against **the repository's own recent commits** (whole-commit population; fewer than 8 sampled commits → null rather than a fake number). Ranking against whole commits instead of per-file numbers matters: a change spread over several files legitimately averages below any single hot file.

**Co-change pairs**: files that habitually change together = hidden coupling the dependency graph doesn't show (they share no import, they share an intent). **Bus factor / ownership %** from authorship attribution round out the "who can safely review this" question.

## 4. Confidence-scored graphs instead of binary edges

Call resolution emits a **confidence score per edge**, not just resolved/unresolved:
- Static analysis gives high-confidence import/attribute edges; dynamic dispatch (callbacks, DI containers, string-based routing) is low-confidence but still recorded — consumers threshold by use case rather than silently trusting everything.
- Route→handler linkage across 22 frameworks is a separate resolution pass with its own confidence treatment.
- Community detection (Leiden) + PageRank over the resulting graph give "where does this module sit" structure without any LLM.

Same principle for **mined architectural decisions**: every decision record carries a verbatim source span and an `exact / fuzzy / unverified` stamp — provenance is part of the data model, so downstream agents can weight claims instead of taking them at face value. Six of seven sources are deterministic (commit messages, docs, config diffs...); only "comment archaeology" on high-centrality code needs a provider.

**Stale-aware responses**: every tool response carries `_meta{index_age_days, indexed_commit, stale_warning}`; the warning fires *only* when indexed HEAD diverges from live `.git/HEAD` (not merely time elapsed). Provenance age travels with the data — never let an agent read a number without knowing how old it is.

## 5. Task-shaped tool surfaces for agents

Ten tools, deliberately capped: "a small task-shaped surface is easier for an agent to choose from than a large one". The contrast they draw (and I'd generalize): most MCP servers expose **data entities** ("get file X", "list symbols in Y") which forces long sequential call chains; repowise exposes **tasks** (`get_context(targets[])` batches many targets, `get_answer(question)` collapses search→read→reason into one round-trip with a calibrated retrieval_quality score).

Measured effect (their benchmark, django/django): 3.8 tool calls vs 7.2 for a bare agent to reach an answer; −31.6% of the agent's *output* tokens (n=43, p<0.0001); loading one commit's context = 393 tokens via `get_context` vs 13,984 raw — deterministic tiktoken counts across 30 commits.

## 6. Benchmark discipline for claims about your own tool

From docs/BENCHMARKS.md — the methodology is as valuable as the numbers:
- **Sealed holdout**: a split of evaluation instances held out from *every* improvement round; improvements never see it. (Their file-coverage claim: 0.876 vs next-best 0.610 on 42 sealed instances, sign-test p=0.00004.)
- **Deterministic grading**: no LLM-as-judge for the headline metric — file coverage is graded by exact match against gold files. (LLM judges are reserved only where judgment genuinely exists, and even then reported with confidence intervals.)
- **Publish losses alongside wins** — "we publish the rows we lose" is a stated policy; they also self-report being *the slowest indexer in the comparison* on their own benchmark page.
- **Defect validation done leakage-free**: ROC AUC 0.737 across 21 repos / 9 languages / 2,826 files with explicit CI and DeLong tests vs baselines — including honest "marginal" verdicts where the edge over CodeScene is p=0.054 (they say so in the doc).
- **Statistical hygiene**: sign tests for paired instance comparisons; pooled ratios reported with n; null results stated as null (percentile = null when <8 samples) instead of fabricated precision.

Template for any "my tool beats X" claim: sealed split + deterministic grader + publish both directions + CI on the headline number + name your baselines and where you lose.

## 7. Failure-shield pattern for MCP servers

Tool exceptions don't leak as tracebacks to the agent (verified live): nested asyncio task-group failures are unwrapped to depth ≤2, then wrapped in a structured `{error, remedy, guidance}` JSON — e.g., un-indexed repo returns "run `repowise init --yes`... Indexing is the user's decision — suggest it once, do not run it yourself", plus explicit fallback instructions ("answer with your built-in tools for the rest of the session"). The server also seeds an in-memory placeholder vector store so non-vector tools work immediately while LanceDB loads in a background task (first-call wedge avoidance).

Generalization: agent-facing servers should return *actionable* error envelopes, not stack traces — and should tell the model what to do next instead of assuming it will guess.

## 8. Workspace mode (multi-repo)

A `.repowise-workspace.yaml` at a parent dir registers member repos with aliases; one MCP server then serves all of them, adds cross-repo consumer detection for dead code (`get_dead_code` sees which repo actually imports the "dead" module), breaking-change analysis across members, and per-repo `repo=` scoping in tool args. Single-repo mode is the default when no workspace file exists — detection walks up from cwd, so nested indexed repos inside a member's directory deliberately drop to single-repo rather than silently serving the enclosing repo (a containment-vs-identity disambiguation worth copying).

## 9. Agent hooks: push context at decision time

Optional hooks inject context *when it matters* instead of dumping everything at session start:
- **Pre-file-edit**: if the file is covered by a governing architectural decision, that decision arrives with its evidence span; if the file has a recent run of bug fixes, a warning does.
- **Session start**: compact briefing (not the whole wiki).
- **Transcript learning**: reads your own agent transcripts for repeated corrections ("use the shared HTTP client, not raw requests") and promotes durable ones into tracked decisions delivered back later — all local, deterministic, no LLM in that loop either.

The general pattern: context delivery should be *event-triggered* (about to edit file X → give me what governs X), with a size budget, rather than one big preamble the agent has to filter.

## 10. Code-health scoring architecture (49 detectors)

- **49 registered detectors / 52 marker ids, but only 26 may move the number** — the rest are informational findings reported alongside without affecting the score. This is an anti-gaming design: a detector that's weakly predictive of defects (e.g., `low_cohesion`, `brain_method` at ×0.5 floor) still surfaces as advice, but can't be gamed by mass-fixing cosmetic markers to inflate the number.
- Score 1–10 per file across three signals: defect risk / maintainability / performance; weighted combination with calibrated coefficients (defect-scoring set validated in §6).
- Every finding ships a **concrete refactoring plan** (Extract Class/Method/Helper, Move Method, Break Cycle, Split File) — the score is useless without the attached fix.
- Zero LLM, <30s for the whole layer; an accuracy self-check runs against its own labeled set and is exposed via `include`.

Complements (not duplicates) my `code-quality-signal` skill: that one scores *structural* root causes of a Python repo from 5 ungameable graph metrics in seconds, stdlib-only; repowise's layer scores per-file maintainability + defect risk with git-history inputs and ships refactoring plans. Use code-quality-signal for "is this architecture healthy", repowise health for "which files will hurt me first".
