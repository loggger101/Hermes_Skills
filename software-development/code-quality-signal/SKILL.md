---
name: code-quality-signal
description: "Score Python repos on 5 ungameable structural metrics."
version: v1.0.0
author: Hermes Agent (ported from sentrux/sentrux design doc, verified implementation)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [code-quality, architecture, refactoring, graph-metrics, stdlib-only]
    related_skills: [architecture-metrics, mattpocock-improve-codebase-architecture, requesting-code-review, repowise]
---

<!-- source: sentrux/sentrux docs/quality-signal-design.md (starred repo deep-dive 2026-09-05); implementation written and verified against hermes-agent (5,562 files) + synthetic cycle/dup fixtures -->

## What This Skill Does

Computes a single **ungameable** code-quality signal for any Python project from five
root-cause graph metrics — not proxy symptoms. The script is stdlib-only (`ast`, `hashlib`),
runs in seconds on small repos (~85s on 5,500-file monorepos; I/O-bound).

The five root causes (a directed dependency graph has exactly these independent properties):

| Metric | Theory | Computation | Normalization |
|---|---|---|---|
| Modularity | Newman's Q (2004) | Intra-module edge density vs random null model, community = top-level package | `(Q+0.5)/1.5` |
| Acyclicity | Martin ADP (2003) | Tarjan SCC count of strongly connected components >1 member | `1/(1+cycles)` |
| Depth | Lakos levelization (1996) | Longest dependency chain in the DAG (iterative DFS DP, cycle-safe) | `1/(1+depth/8)` |
| Equality | Gini coefficient (1912) | Inequality of per-function cyclomatic complexity across all functions | `1 - gini` |
| Redundancy | Kolmogorov gap proxy | Dead module-level fns + structurally-duplicate fns / total fns | `1 - ratio` |

Aggregation: **geometric mean** (Nash-optimal — gaming one metric while tanking another can't
raise the signal) → integer 0–10000. The lowest sub-score is reported as the bottleneck, i.e.
where the next refactor buys the most.

Why ungameable: Q drops when you add useless edges (graph moves toward random); cycles are a
structural impossibility to fake; Gini can't be improved by splitting one god function into two
god functions without actually distributing complexity; dead/duplicate code is counted, not scored away.

## When to Use

- "How healthy is this codebase?" / "what should I refactor next?" — run it, read the bottleneck
- Before/after a refactor: compare signal + per-metric deltas (trend matters more than absolute)
- Deciding whether an agent's iterative changes are converging or churning (signal plateau = done)
- NOT for behavior verification (tests do that), non-Python codebases, or single-file scripts

Complement: the `repowise` skill scores per-file maintainability + defect risk *with git-history inputs* and ships concrete refactoring plans; use this one for "is the architecture structurally healthy", repowise for "which files will hurt me first".

## Usage

```bash
python {baseDir}/scripts/quality_signal.py <project-dir>          # human summary
python {baseDir}/scripts/quality_signal.py <project-dir> --json   # machine-readable
```

Output: `Quality NNNN (bottleneck: X)` + per-metric raw values and normalized scores.

## Interpreting Results

- **Bottleneck = depth**: long dependency chains — extract interfaces, break the chain at a seam
- **Bottleneck = acyclicity**: find the SCCs (the script reports count; re-run with `--json` for raw) — invert one edge per cycle via extraction or event-driven decoupling
- **Bottleneck = equality**: god functions dominate CC distribution — split by responsibility, not size
- **Bottleneck = redundancy**: dead code inflates the search space an agent must scan — delete first, it's free signal gain
- **Bottleneck = modularity**: cross-package edges are dense — move shared types to a leaf package

## Verified Behavior (2026-09-05)

| Project | Signal | Bottleneck | Notes |
|---|---|---|---|
| hermes-agent (11.8k files, 44k fns) | 2387 | depth=132 chain | Q=+0.138, 5 cycles, CC gini 0.43 — plausible for a monorepo |
| synthetic fixture (cycle + dup fn) | 109 | redundancy | correctly detected the duplicate function and dead fns; acyclicity/depth clean |

Known limits: import graph only (no call edges), so implicit re-exports undercount coupling;
"dead" = module-level name never referenced anywhere in the project (conservative — public API
functions are flagged too); community detection is top-level-package, not Louvain.
