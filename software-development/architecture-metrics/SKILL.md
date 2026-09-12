---
name: architecture-metrics
description: "Dependency-graph architecture metrics for Python repos."
version: v1.1.0
author: Hermes Agent (ported from sentrux/sentrux Rust source, verified implementation)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [architecture, dependency-graph, refactoring, graph-metrics, stdlib-only]
    related_skills: [code-quality-signal, mattpocock-improve-codebase-architecture, repowise]
---

<!-- source: sentrux/sentrux (MIT) — metrics/arch/ + dsm + testgap + evo modules read at source level 2026-09-11..12; implementation written and verified against synthetic fixtures + economicspace -->

## What This Skill Does

Computes **architecture-level** metrics for a Python project from its import
graph — the layer above `code-quality-signal`'s root-cause scores. Stdlib-only
(`ast`, no deps) plus the git CLI for evolution; runs in seconds (3s on 27-file
repos, ~5s on this 190-script repo).

Three scripts:
- **`architecture_metrics.py`** — static structural report (+ `--json`, + `--dsm N`)
- **`session_gate.py`** — sentrux's baseline-gate workflow made runnable here (save before an agent session, check after; exit 0/1 for CI)
- **`evolution_metrics.py`** — git-history metrics: churn, change coupling, temporal hotspots, code age, bus factor

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

- "Is this codebase's dependency structure healthy?" — run it; read violations,
  blast-radius leaders, and D values together (not one number)
- Before a refactor: identify the file with max blast radius = highest-risk edit target
- Deciding where tests are missing most dangerously (`test_gaps` risk ranking)
- Comparing architecture before/after an agent session or big change (levels + violations delta)
- NOT for behavior verification, non-Python codebases, or single-file scripts

Complement: `code-quality-signal` gives the 5-metric ungameable quality score and bottleneck; this skill explains *where in the graph* the problems are. Run both — signal says "what's wrong", this says "which files".

## Usage

```bash
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

- **Upward violations > 0**: each is a concrete refactor target — invert the edge by extracting the shared part to the lower level, or make it event-driven. Intra-cycle pairs (A→B and B→A both listed) break one direction per pair.
- **High blast radius on a low-level file** = change amplifier. If it's also high-complexity, that file is your #1 risk; wrap it behind an interface before touching internals.
- **D ≈ 0** module: healthy (on the main sequence). **Zone of pain**: D≈1 with low A + low I — concrete and stable, hard to change (add abstractions or accept as foundation). **Zone of uselessness**: D≈1 with high A + high I — abstract but nobody depends on it; delete candidates.
- **SDP coupling score** near 0 = most cross-module imports go to stable foundations (healthy). Rising over time = new modules are unstable and getting depended-on: freeze their interfaces early.
- **Test gaps**: rank is already risk-weighted; work top-down. `risk = CC × (fan_in+1)` mirrors sentrux's formula — untested + complex + widely-imported first.
- **Session gate DEGRADED**: the violations list names exactly what regressed — fix those specific edges/files before shipping, not "improve quality" in general. A rising SDP coupling score means new modules are being depended on while still unstable: freeze their interfaces early.
- **Evolution metrics read together**: high `churn_concentration` + a few strong co-change pairs = one subsystem absorbing all change (refactor target); low bus-factor score (many single-author files) is normal for solo repos but flags real key-person risk in teams; temporal hotspots with high CC are where regressions will cluster.

## Verified Behavior (2026-09-11..12)

| Project | Result | Notes |
|---|---|---|
| synthetic fixture (cycle pair, 3-deep chain, god file candidate, ABC in core, `__init__.py` barrels) | max_level=3 ✓; cycle svc_a↔svc_b reported as the only violations ✓; blast radius c2=4 (bottom of chain hits most dependents) ✓; `core` flagged stable foundation + excluded from D average ✓; DSM inversions=0, correct(below)=15 lateral=2 ✓ | every property hand-verified against fixture construction; barrel edges correctly filtered out of the graph |
| economicspace (27 files, real imports) | 3.0s; master blast radius=4; test gaps led by calc cc=119 — plausible for a branch-heavy pipeline module; gate save→check on clean repo = PASS exit 0 ✓ | |
| Hermes_Skills repo itself (243 py files, standalone scripts) | 5.4s; edges=0 correctly (no cross-imports); no false violations | edge case: zero-edge graph handled cleanly |
| session gate degradation test (fixture + injected `svc_b → godfile` import) | signal 72.51→67.5 (-5.0), VIOLATIONS listed, exit 1 ✓ | matches sentrux ArchDiff semantics; clean re-check after revert = PASS |
| evolution_metrics on Hermes_Skills (30 days) | 114 commits / 334 files; top churn README.md x39; bus factor score 0.132 (solo repo, expected); co-change pairs + temporal hotspots plausible ✓ | merge/mega-commit skip rules active |

Known limits: import graph only (no call edges — implicit re-exports undercount coupling);
module = dotted path with top-level package as the D-metric unit; thresholds are constants, not
per-language profiles like sentrux's plugin.toml system (tune `GOD_FAN_OUT`/`HOTSPOT_FAN_IN`
at the top of the script for your project size); OneDrive cloud-placeholder files raise
OSError and are skipped silently — hydrate before scanning if a repo reports 0 files.

## sentrux Parity Notes (2026-09-12 pass)

Ported from source in this round, beyond round 1's metrics layer:
- **Mod-declaration edge filter** (`is_mod_declaration_edge`): edges FROM `__init__.py` TO the same dir or a direct child subdir are package structure, not functional dependencies — dropped before any metric (sentrux filters these so barrel re-exports don't inflate coupling/cycles/depth).
- **Composite quality_signal** in `--json`: 0–100 weighted sum of the five root causes (cycles 25 / god files 20 / SDP coupling 25 / layering violations 15 / depth 15) — sentrux's same idea normalized to 0–10000 with per-language inputs; fixed scale here so baseline diffs are comparable.
- **Session gate** = sentrux `ArchBaseline`/`ArchDiff` rules: signal drop >2 pts OR coupling rise >0.05 OR any increase in cycles / god files / complex functions (CC>15) ⇒ degraded, exit 1. Baseline JSON at `<project>/.sentrux-baseline.json` by default (`--baseline PATH` to override).
- **Evolution skip rules** = sentrux `git_walker.rs`: merge commits skipped (double-count changes), mega-commits >50 files skipped (noise), renames excluded via `--no-renames`; binary numstat lines count as touched with zero churn. Formulas: coupling strength J = co_changes/(c_a+c_b−co) min 3; hotspot risk = churn_commits × max_CC; bus factor score = 1 − single-author-file ratio; evolution_score = min(bus, churn-concentration).
- **Incremental rescan design** (sentrux `rescan.rs`, documented not ported): full scan on first pass, then per-changed-file re-parse with a body-hash cache — only files whose hash changed are re-analyzed; graph is rebuilt from the cached per-file import lists. That's why sentrux rescans run in milliseconds during an agent session.
- **CI grammar-bundle pattern** (sentrux `ci.yml`): language grammars compiled once into a shared bundle artifact and reused across test jobs — avoids re-downloading tree-sitter grammars per job; useful template for any multi-language CI.

## References

- `references/sentrux-architecture-notes.md` — everything else learned from the sentrux source: import-resolution patterns (suffix index, manifest boundaries, path aliases), git-evolution metrics formulas (churn×complexity risk, Jaccard change coupling, bus factor), quality-gate/baseline workflow, what-if simulation design, and the Pro licensing architecture.
