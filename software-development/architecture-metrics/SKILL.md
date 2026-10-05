---
name: architecture-metrics
description: "Python code health: quality signal + architecture metrics."
version: v1.2.0
author: Hermes Agent (ported from sentrux/sentrux Rust source + quality-signal design doc, verified implementation)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [architecture, code-quality, dependency-graph, refactoring, graph-metrics, stdlib-only]
    related_skills: [mattpocock-codebase-design, repowise, requesting-code-review]
---

<!-- source: sentrux/sentrux (MIT) — metrics/arch/ + dsm + testgap + evo modules read at source level 2026-09-11..12; implementation written and verified against synthetic fixtures + economicspace -->
<!-- quality_signal.py: sentrux/sentrux docs/quality-signal-design.md (starred repo deep-dive 2026-09-05); implementation written and verified against hermes-agent (5,562 files) + synthetic cycle/dup fixtures. Was the standalone skill `code-quality-signal` until round-57. -->

## What This Skill Does

Computes code-health metrics for a Python project from its import graph, at two levels:
one **ungameable quality signal** that names the bottleneck (what is wrong), and the
**architecture report** that locates it in the graph (which files). Stdlib-only (`ast`,
`hashlib`, no deps) plus the git CLI for evolution; runs in seconds (3s on 27-file repos,
~5s on this 190-script repo, ~85s on 5,500-file monorepos, I/O-bound).

Four scripts:

- **`quality_signal.py`** — the five root-cause metrics below, aggregated into one 0–10000 score + bottleneck (+ `--json`, + its own baseline gate)
- **`architecture_metrics.py`** — static structural report (+ `--json`, + `--dsm N`)
- **`session_gate.py`** — sentrux's baseline-gate workflow made runnable here (save before an agent session, check after; exit 0/1 for CI)
- **`evolution_metrics.py`** — git-history metrics: churn, change coupling, temporal hotspots, code age, bus factor

### Quality signal: the five root causes (`quality_signal.py`)

A directed dependency graph has exactly these independent properties:

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

Implementation details verified against the Rust source (sentrux-core/src/metrics/root_causes.rs @ 6f8ff3c): when no function data exists, Equality's Gini falls back to per-file line counts; each factor is floored at 0.01 before the geometric mean so a single zeroed dimension can't annihilate the whole signal.

### Architecture report (`architecture_metrics.py`)

| Metric | Theory | What it answers |
|---|---|---|
| Levels + max_level | Lakos levelization (1996) — Kahn topological sort on the SCC DAG; cycles collapse to one shared level | How deep are dependency chains? Which file sits at which layer? |
| Upward violations | Lakos: edges from lower→higher level, **plus intra-cycle edges** (a cycle prevents clean layering even when levels tie) | Where does the code depend on something that depends back / upward? |
| Blast radius | Reverse-edge transitive reach per file; uniform sampling above 5000 nodes with max-degree node guaranteed in sample | If I change this file, how many files could break? |
| God files | fan-out > threshold (15), excluding entry points and `__init__.py` barrels | Which files import from everywhere? |
| Unstable hotspots | fan-in > threshold (8) **and** instability I ≥ 0.15 — stable foundations are *excluded* per Martin's SDP: high fan-in + low fan-out is good architecture, not a hotspot | Where does change propagate to many dependents that themselves churn? |
| Distance from main sequence | Martin (2003): A = abstract types / total types, I = Ce/(Ca+Ce), D = \|A+I−1\| per module; foundations (I ≤ 0.30) excluded from the average because concrete stable cores SHOULD score high-D | Which modules are in the zone of pain or uselessness? |
| Stable-foundation coupling | Cross-module edges to UNSTABLE targets only — depending on `types`/`error`-style leaves is healthy hub-and-spoke, not spaghetti (SDP) | What fraction of imports actually cross toward unstable code? |
| Test gaps | Source files no test file imports; ranked by risk = max_CC × (fan_in + 1), top 20 | Where to write tests first for maximum risk reduction? |
| DSM table (`--dsm N`) | Baldwin & Clark (2000) Design Structure Matrix, sorted highest level first so correct-direction edges fall below the diagonal and inversions appear above it | Visual map of who depends on whom + inversion count |

## When to Use

- "How healthy is this codebase?" / "what should I refactor next?" — run `quality_signal.py`
  and read the bottleneck, then `architecture_metrics.py` to see which files carry it
- "Is this codebase's dependency structure healthy?" — read violations, blast-radius leaders,
  and D values together (not one number)
- Before a refactor: identify the file with max blast radius = highest-risk edit target
- Deciding where tests are missing most dangerously (`test_gaps` risk ranking)
- Comparing architecture before/after an agent session or big change (levels + violations delta)
- Deciding whether an agent's iterative changes are converging or churning (signal plateau = done)
- NOT for behavior verification (tests do that), non-Python codebases, or single-file scripts

Run order: the quality signal says *what's wrong*, the architecture report says *which files*.
Complement: the `repowise` skill scores per-file maintainability + defect risk *with git-history inputs* and ships concrete refactoring plans; use this one for "is the architecture structurally healthy", repowise for "which files will hurt me first".

## Usage

```bash
# One-number quality signal + bottleneck
python {baseDir}/scripts/quality_signal.py <project-dir>                # `Quality NNNN (bottleneck: X)` + per-metric scores
python {baseDir}/scripts/quality_signal.py <project-dir> --json         # machine-readable
python {baseDir}/scripts/quality_signal.py <project-dir> --save-baseline .qs-baseline.json
python {baseDir}/scripts/quality_signal.py <project-dir> --baseline .qs-baseline.json   # exit 0 clean / 1 degraded

# Static structural report
python {baseDir}/scripts/architecture_metrics.py <project-dir>          # human report
python {baseDir}/scripts/architecture_metrics.py <project-dir> --json   # machine-readable
python {baseDir}/scripts/architecture_metrics.py <project-dir> --dsm 20 # + DSM table (top N modules)

# Session gate (sentrux `gate` workflow — wrap every agent session / big change)
python {baseDir}/scripts/session_gate.py save  <project-dir>            # baseline before writes
python {baseDir}/scripts/session_gate.py check <project-dir>           # after; exit 0 pass / 1 degraded

# Git evolution (needs git history in the repo dir)
python {baseDir}/scripts/evolution_metrics.py <repo-dir> --days 90     # human report
python {baseDir}/scripts/evolution_metrics.py <repo-dir> --json        # machine-readable
```

## Interpreting Results

Quality-signal bottleneck:

- **Bottleneck = depth**: long dependency chains — extract interfaces, break the chain at a seam
- **Bottleneck = acyclicity**: find the SCCs (the script reports count; re-run with `--json` for raw) — invert one edge per cycle via extraction or event-driven decoupling
- **Bottleneck = equality**: god functions dominate CC distribution — split by responsibility, not size
- **Bottleneck = redundancy**: dead code inflates the search space an agent must scan — delete first, it's free signal gain
- **Bottleneck = modularity**: cross-package edges are dense — move shared types to a leaf package

Architecture report:

- **Upward violations > 0**: each is a concrete refactor target — invert the edge by extracting the shared part to the lower level, or make it event-driven. Intra-cycle pairs (A→B and B→A both listed) break one direction per pair.
- **High blast radius on a low-level file** = change amplifier. If it's also high-complexity, that file is your #1 risk; wrap it behind an interface before touching internals.
- **D ≈ 0** module: healthy (on the main sequence). **Zone of pain**: D≈1 with low A + low I — concrete and stable, hard to change (add abstractions or accept as foundation). **Zone of uselessness**: D≈1 with high A + high I — abstract but nobody depends on it; delete candidates.
- **SDP coupling score** near 0 = most cross-module imports go to stable foundations (healthy). Rising over time = new modules are unstable and getting depended-on: freeze their interfaces early.
- **Test gaps**: rank is already risk-weighted; work top-down. `risk = CC × (fan_in+1)` mirrors sentrux's formula — untested + complex + widely-imported first.
- **Session gate DEGRADED**: the violations list names exactly what regressed — fix those specific edges/files before shipping, not "improve quality" in general. A rising SDP coupling score means new modules are being depended on while still unstable: freeze their interfaces early.
- **Evolution metrics read together**: high `churn_concentration` + a few strong co-change pairs = one subsystem absorbing all change (refactor target); low bus-factor score (many single-author files) is normal for solo repos but flags real key-person risk in teams; temporal hotspots with high CC are where regressions will cluster.

## Verified Behavior

Quality signal (2026-09-05):

| Project | Signal | Bottleneck | Notes |
|---|---|---|---|
| hermes-agent (11.8k files, 44k fns) | 2387 | depth=132 chain | Q=+0.138, 5 cycles, CC gini 0.43 — plausible for a monorepo |
| synthetic fixture (cycle + dup fn) | 109 | redundancy | correctly detected the duplicate function and dead fns; acyclicity/depth clean |

Architecture report, session gate and evolution (2026-09-11..12):

| Project | Result | Notes |
|---|---|---|
| synthetic fixture (cycle pair, 3-deep chain, god file candidate, ABC in core, `__init__.py` barrels) | max_level=3 ✓; cycle svc_a↔svc_b reported as the only violations ✓; blast radius c2=4 (bottom of chain hits most dependents) ✓; `core` flagged stable foundation + excluded from D average ✓; DSM inversions=0, correct(below)=15 lateral=2 ✓ | every property hand-verified against fixture construction; barrel edges correctly filtered out of the graph |
| economicspace (27 files, real imports) | 3.0s; master blast radius=4; test gaps led by calc cc=119 — plausible for a branch-heavy pipeline module; gate save→check on clean repo = PASS exit 0 ✓ | |
| Hermes_Skills repo itself (243 py files, standalone scripts) | 5.4s; edges=0 correctly (no cross-imports); no false violations | edge case: zero-edge graph handled cleanly |
| session gate degradation test (fixture + injected `svc_b → godfile` import) | signal 72.51→67.5 (-5.0), VIOLATIONS listed, exit 1 ✓ | matches sentrux ArchDiff semantics; clean re-check after revert = PASS |
| evolution_metrics on Hermes_Skills (30 days) | 114 commits / 334 files; top churn README.md x39; bus factor score 0.132 (solo repo, expected); co-change pairs + temporal hotspots plausible ✓ | merge/mega-commit skip rules active |

Known limits: import graph only (no call edges — implicit re-exports undercount coupling);
in the quality signal, "dead" = module-level name never referenced anywhere in the project
(conservative — public API functions are flagged too) and community detection is
top-level-package, not Louvain; in the architecture report, module = dotted path with top-level package as the D-metric unit; thresholds are constants, not
per-language profiles like sentrux's plugin.toml system (tune `GOD_FAN_OUT`/`HOTSPOT_FAN_IN`
at the top of the script for your project size); OneDrive cloud-placeholder files raise
OSError and are skipped silently — hydrate before scanning if a repo reports 0 files.

## sentrux Parity Notes (2026-09-12 pass)

Ported from source in this round, beyond round 1's metrics layer:

- **Mod-declaration edge filter** (`is_mod_declaration_edge`): edges FROM `__init__.py` TO the same dir or a direct child subdir are package structure, not functional dependencies — dropped before any metric (sentrux filters these so barrel re-exports don't inflate coupling/cycles/depth).
- **Composite quality_signal** in `architecture_metrics.py --json`: 0–100 weighted sum of five architecture inputs (cycles 25 / god files 20 / SDP coupling 25 / layering violations 15 / depth 15) — sentrux's same idea normalized to 0–10000 with per-language inputs; fixed scale here so baseline diffs are comparable. **Not the same number as `quality_signal.py`**, which is the 0–10000 geometric mean of the root causes above; `session_gate.py` diffs this 0–100 one.
- **Session gate** = sentrux `ArchBaseline`/`ArchDiff` rules: signal drop >2 pts OR coupling rise >0.05 OR any increase in cycles / god files / complex functions (CC>15) ⇒ degraded, exit 1. Baseline JSON at `<project>/.sentrux-baseline.json` by default (`--baseline PATH` to override).
- **Evolution skip rules** = sentrux `git_walker.rs`: merge commits skipped (double-count changes), mega-commits >50 files skipped (noise), renames excluded via `--no-renames`; binary numstat lines count as touched with zero churn. Formulas: coupling strength J = co_changes/(c_a+c_b−co) min 3; hotspot risk = churn_commits × max_CC; bus factor score = 1 − single-author-file ratio; evolution_score = min(bus, churn-concentration).
- **Incremental rescan design** (sentrux `rescan.rs`, documented not ported): full scan on first pass, then per-changed-file re-parse with a body-hash cache — only files whose hash changed are re-analyzed; graph is rebuilt from the cached per-file import lists. That's why sentrux rescans run in milliseconds during an agent session.
- **CI grammar-bundle pattern** (sentrux `ci.yml`): language grammars compiled once into a shared bundle artifact and reused across test jobs — avoids re-downloading tree-sitter grammars per job; useful template for any multi-language CI.

## References

- `references/sentrux-architecture-notes.md` — everything else learned from the sentrux source: import-resolution patterns (suffix index, manifest boundaries, path aliases), git-evolution metrics formulas (churn×complexity risk, Jaccard change coupling, bus factor), quality-gate/baseline workflow, what-if simulation design, and the Pro licensing architecture.
- `skill_view(name='modular-monolith-migration')` — modular design principles, boundary validation, monolith decomposition pipeline and strangler-fig migration (moved there in round-251)
