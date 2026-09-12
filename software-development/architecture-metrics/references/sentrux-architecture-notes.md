# Sentrux Architecture Notes (source-level findings)

Deep-dive of `sentrux/sentrux` (MIT, 318 commits at clone time 2026-09-11, ~34k lines of Rust).
Sentrux = "real-time architectural sensor for AI agents": scan → score → agent improves → rescan.
The `code-quality-signal` skill already ports its 5-metric quality signal; this file holds the
rest — patterns and formulas worth reusing even without the binary (which is Rust + tree-sitter,
not pip-installable on arbitrary machines).

## 1. Import resolution: suffix-index architecture (`analysis/resolver/suffix.rs`, ~1100 lines)

The hardest part of any dependency-graph tool is resolving import specifiers to files across 52
languages with zero per-language code in the binary. Sentrux's design, worth copying for any
multi-language graph builder:

- **Suffix index**: for every file `a/b/c.py`, insert suffixes `"c"`, `"b/c"`, `"a/b/c"` → file path.
  A multi-segment import specifier is resolved by progressive prefix stripping against this map —
  one shared resolver for ALL languages, no per-language resolution code.
- **Key design rule: single-segment absolute imports NEVER use the suffix index** (too many false
  positives). They resolve via dir-relative → root-relative → manifest-name aliases only.
- **Project boundaries**: a file's project = nearest ancestor directory containing a *manifest*
  file (`package.json`, `Cargo.toml`, … aggregated from plugins). Imports resolve within the same
  project. **Pitfall they hit: Makefile/CMakeLists.txt must NOT be boundary markers** — CMake and
  recursive make put them at multiple levels inside one project, silently dropping valid edges.
- **Path aliases**: two sources merged (a) config files declared in plugin.toml (`tsconfig.json`
  `paths`, with `baseUrl`) and (b) manifest names auto-discovered (`package.json "name"`,
  `Cargo.toml [package] name`). Aliases are *hints, not absolute*: try alias-substituted specifier
  first, fall back to the original if it doesn't resolve.
- **Module prefixes**: parse `go.mod` `module <path>` (line format) or composer.json PSR-4 /
  tsconfig paths (json_map format: prefix→directory pairs, namespace separator converted `\`→`/`,
  values may be string OR array of dirs). Sorted longest-first for greedy matching.
- **Directory-is-package languages** (Go): any `.go` file in a dir is part of that package — add the
  *parent directory* as an extra module path so `import "internal/config"` resolves to files inside.
- **Package index files** (`__init__.py`, `mod.rs`, `index.js/ts`) use their parent directory as the
  module path, detected by filename alone (no language knowledge).
- **Manifest name extraction**: 5 strategies auto-detected from extension — JSON, TOML, XML
  (nested element navigation), YAML, and line-match fallback (`name := "x"` in build.sbt, `spec.name`
  in gemspecs, Elixir atoms `app: :my_app`, Swift Package names). One generic mechanism.
- **False-positive guard they learned the hard way**: previously fell back to parent-module when a
  submodule didn't resolve — created wrong import edges. Rule now: if the exact specifier doesn't
  resolve, return None rather than silently returning the wrong file.
- Resolution runs in parallel (rayon `par_iter` over files) with atomic resolved/unresolved counters;
  unresolved count is reported so you can see how much of your graph is guesswork-free.

## 2. Language plugin architecture (`analysis/plugin/`)

The binary contains ZERO language knowledge: every language = a directory in `~/.sentrux/plugins/<name>/` with:

```
plugin.toml        # name, version, extensions, grammar source+ref+abi, capabilities, [semantics]
grammars/lib<lang>.so   # compiled tree-sitter grammar (cc -shared)
queries/tags.scm   # tree-sitter queries — the actual language knowledge
tests/             # fixture files for `sentrux plugin validate`
```

Required query captures: `@func.def` / `@class.def` / `@import.path`, optional `@call.name`.
Everything semantic (thresholds, test-file detection, entry points, resolver config) lives in
plugin.toml `[semantics]`: per-language `fan_out`/`fan_in`/`cc_high`/`func_length` thresholds,
`package_index_files`, `test_function_prefixes`, `qualified_name_separator`, implicit entry point
lists, abstract-base-class names (Python: Protocol/ABC), resolver config (alias_file/field, module
prefix file/directive/format). Adding a language = zero Rust.

Generic AST import walker replaces 13 compiled per-language text extractors with ONE tree-sitter
walker + two strategies from TOML: `field_read` (named field: Python `module_name`, Go `path`, JS
`source`) and `scoped_path` (concatenate identifier chains: Rust, Java). Max recursion depth 64.

Parse results cached in an LRU keyed by content hash (2000 entries) — rescan only re-parses changed files.

## 3. Graph algorithms (`metrics/arch/graph.rs`)

- **Kosaraju SCC** (iterative, O(V+E), no stack overflow): pass 1 DFS finish-order on forward
  graph; pass 2 DFS on reverse graph in *reverse* finish order. Computed ONCE and shared by both
  levelization and violation detection (`_with_sccs` variants) — don't recompute SCC per metric.
- **Levelization (Lakos)**: Kahn topological sort on the SCC DAG, leaves first (no outgoing deps =
  level 0), propagate `max(child)+1`. All cycle members share one level.
- **Upward violations**: cross-level edges where from_level < to_level are rare by construction;
  the real signal is **intra-SCC edges** — a same-level edge inside an SCC of size >1 IS an
  architectural violation (the cycle prevents clean layering). Sort by |level diff| desc.
- **Blast radius**: reverse-edge transitive reach per node ("if this file changes, how many files
  could be affected"). Performance notes from source: index-based BFS with one reusable `Vec<bool>`
  instead of V HashSets (O(V²)→O(V) memory); for >5000 nodes sample uniformly but **guarantee the
  max-degree node is in the sample**; sort the node list before sampling or HashSet iteration order
  makes results non-deterministic between runs.
- **Attack surface**: forward BFS from entry points — files reachable from public APIs.

## 4. Martin metrics (`metrics/arch/distance.rs`, `stability.rs`)

Per module (directory): A = abstract_types/total_types, I = Ce/(Ca+Ce), D = |A + I − 1|.
- Abstract types = interfaces/traits/ADTs; Python abstractness detected via base classes in the
  profile's list (Protocol, ABC) — per-language data, not hardcoded.
- **Foundations excluded from average**: modules with I ≤ 0.30 are architecturally CORRECT when
  concrete (they implement core types everything depends on); including them inflates avg D without
  indicating a flaw. Martin defines stable as I < 0.5; 0.30 is the conservative first-quartile cut.
- **SDP-aware coupling**: cross-module edges to *stable foundations* (I ≤ 0.15 AND fan-in ≥ 3) do NOT
  count as problematic coupling — depending on `types.rs`/`error.rs` leaves is healthy hub-and-spoke.
  The fan-in floor prevents single-leaf nodes from being misclassified as "foundations". Without this,
  any project with shared foundational types scores worst-case entropy/coupling.
- **Entropy dampening**: Shannon entropy of the cross-module edge distribution is multiplied by
  `min(coupling/0.35, 1)` — when coupling is low there are few cross edges and their concentration
  is meaningless; binary cutoff at a threshold created score cliffs.
- **Cohesion**: per module, fraction of a spanning tree's n−1 baseline edges that actually exist.
  Test files excluded from the file count (they inflate N without contributing incoming edges — same
  principle as excluding entry points from god-file detection: known one-way consumers shouldn't be
  penalized by metrics they can't contribute to).
- **Module boundary heuristic** (`core/path_utils.rs`): adaptive depth — depth-3 module when ≥3 dir
  levels, depth-2 at exactly 2; files directly under *dominant* source dirs (src/, lib/ per plugin)
  get per-file modules. Documented bug fix: root-level file `src/app.rs` used to be treated as same-module
  with ALL subdirs of src — masking real coupling. Now strict equality.

## 5. Git evolution metrics (`metrics/evo/mod.rs`, git2 log walk, no shell-out)

Constants from source: default lookback **90 days**; min co-change count for a reported pair = **3**.
- **Churn**: per file over window — commit_count, lines_added/removed, total (saturating add to avoid u32 overflow on high-churn files).
- **Change coupling** (logical coupling): pairs of files changed in the same commits; strength = Jaccard `co_changes / (changes_a + changes_b − co_changes)`. Sorted by strength desc with deterministic tiebreaker (HashMap iteration order previously made output non-deterministic under par_iter — always sort with a total order).
- **Temporal hotspots**: risk = churn_count × max_complexity_in_file. Theory: Nagappan & Ball 2005 (churn×complexity predicts defect density), Gall et al. 1998 for change coupling, Ricca et al. 2011 for bus factor.
- **Bus factor**: per-file author distribution; primary_ratio = fraction of commits by the top author; score = 1 − single_author_file_ratio (files with exactly one distinct author).
- **Churn concentration**: [0,1] where 1.0 = uniform churn, 0.0 = all churn in the top 10% of files.
- Overall evolution_score = min(bus_factor_score, churn_score) — weakest dimension dominates, same philosophy as the geometric-mean signal (no averaging that lets one good score hide a bad one).

## 6. Test-gap analysis (`metrics/testgap/mod.rs`)

Coverage via import graph, not runtime: source file is "tested" if at least one test file imports it
(transitively through BFS in their impl; direct-import set suffices for ranking). Risk = max_CC × (fan_in + 1), top-50 list. Test detection is three layers: universal dir patterns (`test/`, `tests/`, `__tests__/`, `spec/` — cross-language) → language-specific prefixes/suffixes from plugin profile → universal filename fallbacks (PascalCase Test/Spec suffix, stem match). Coverage ratio = tested_source / total_source; no source files = vacuously 1.0.

## 7. Rules engine + quality gate (`metrics/rules/`, `main_impl.rs`)

The "spec" half of the cybernetic loop — externalize architectural judgment as machine-checkable constraints:

```toml
# .sentrux/rules.toml
[constraints]                 # only SET fields are checked (all optional)
min_quality = 0.6             # root-cause gates: minimum per-dimension scores [0,1]
max_cycles = 0                # specific limits on individual metrics
max_cc = 25                   # user thresholds may be stricter than built-ins —
no_god_files = true           # engine receives RAW unfiltered metric lists for this reason

[language.python.constraints] # per-language override cascade: lang-specific > global (field-wise merge)
max_cc = 10

[[layers]]                    # dependency direction enforcement
name = "core"                 # order lower = more foundational; layers may only depend downward
paths = ["src/core/*"]
order = 0

[[boundaries]]                # explicit glob deny-rules with human-readable reason
from = "src/app/*"
to = "src/core/internal/*"
reason = "App must not depend on core internals"
```

CI contract: `sentrux check .` exits 0/1. **Quality gate**: `.sentrux/baseline.json` saved before an
agent session (`gate --save`), compared after (`gate`) — degraded if quality_signal dropped by more
than 0.02 OR any tracked metric (coupling, cycles, god files) regressed; prints per-violation lines.
This is the pattern to copy for agent governance without sentrux: snapshot N cheap metrics before a
session, diff after, fail on regression — it's exactly what `code-quality-signal --json` + jq can do.

## 8. What-if simulation (`metrics/whatif/mod.rs`)

Predict architectural impact of hypothetical changes with zero side effects (cloned graph): five atomic
actions — MoveFile(old→new rewrites all referencing edges), AddEdge, RemoveEdge, RemoveFile, and
**BreakCycle(files)** which removes the cycle's *weakest edge* = the one whose target has the fewest
other dependents (removing it reduces blast radius least). Output: before/after score, max level,
upward violations, max blast radius + per-file level changes. Use for "what if I move this file?"
before actually moving it — the refactor planner's decision input.

## 9. MCP server design (`app/mcp_server/`)

- **ToolRegistry pattern**: each tool is ONE `ToolDef` struct co-locating name + description + JSON
  schema + license tier + handler function pointer in a single place, registered at startup (duplicate
  names panic). Their stated reason: previously the same tool's metadata lived in three files
  (schema / handler logic / routing) and they desynced. Adding a tool = adding one struct; dispatch
  does license check → cache invalidation → handler uniformly. Portable principle for any multi-tool
  MCP server (see fastmcp skill).
- **Declarative cache invalidation**: tools that mutate the snapshot carry an `invalidates_evolution`
  flag — registry clears cached git-evolution results before running them, instead of manual cleanup
  in each handler.
- Free-tier tool set: scan, rescan, session_start/end (baseline diff), health, check_rules, evolution, dsm, test_gaps; Pro registers extra tools into the same registry at startup via a callback — one dispatch path for both tiers.

## 10. Dead-code detection details (`metrics/mod.rs`)

A function is dead only if: not public/exported (public = API surface), **not a method** (object
dispatch can't be traced statically — self/this methods always excluded), name doesn't match test
prefixes, isn't a qualified trait-impl name, base name isn't in the implicit entry-point list
(`main`, `new`, `init`, `setup`, `run`, `start`, `build`, `register`, `draw`, `render`, … 18 defaults + per-language additions), and no call site anywhere references it (matching both full qualified name AND base name after last `::`). Test files skipped entirely via profile detection + path heuristic. Call set built from file-level calls + per-function calls, each inserted with its base-name variant so `Foo.bar()` matches a definition named `bar`.

## 11. Pro licensing architecture (`docs/pro-architecture.md`) — trust-boundary pattern

Worth reading even if you never ship paid software:
- **Free binary = 100% public source, zero private code** (anyone can cargo build and verify what it does). No `if tier.is_pro()` gates around hidden computation in the free binary.
- Paid features live in a separately downloaded dylib loaded at runtime via an extension trait (`MetricsExtension` registered into a global OnceLock registry; MCP tools registered through callback) — the free binary contains only *call sites*, not implementation.
- License key = **Ed25519-signed JSON** (user, tier, issued/expires, id + signature over all fields). Validation is pure offline math against a hardcoded public key: parse → verify sig → check expiry. No server call, no internet.
- **Per-user watermarked dylib**: each download embeds the buyer's identity; loader verifies watermark matches license (mismatch = stolen binary). Source-available under BSL — auditable, not redistributable.

## 12. Open ideas in sentrux worth stealing (`metrics/cross_validation.rs` — skeleton only)

**Compression-ratio cross-validation of quality signal**: serialize the dependency graph's adjacency
list to bytes → DEFLATE compress → ratio = compressed/original as an INDEPENDENT second opinion on
quality (high compressibility = redundant structure). If both sensors agree, confidence high; if they
diverge, one is blind. Kolmogorov complexity K(x) is uncomputable but compression gives a computable
upper bound — the same "best computable approximation" framing as the quality signal itself. Not yet
implemented upstream (marked FREE tier); trivial to prototype in Python (`zlib` + adjacency list).

## 13. Design philosophy notes (README + design doc)

- **Continuous scores, never letter grades**: A/B boundaries get gamed at the boundary; with a continuous
  signal every point of improvement matters equally and agents converge naturally when marginal gain → 0
  ("exactly like gradient descent"). All their sub-scores are [0,1] floats for this reason.
- **Root causes over proxy symptoms**: proxies (coupling ratio, dead-code %, function length) can be gamed —
  fake imports boost cohesion, make-everything-public kills "dead code", superficial splits reduce length.
  Root-cause metrics only improve via genuine restructuring. Their refactor history shows the discipline:
  they REMOVED letter grades and several proxy sub-scores (levelization_score, distance_score, blast_score)
  once root causes covered them — a metric that duplicates another dimension gets deleted, not kept for coverage.
- **Cybernetic framing**: sensor → signal → controller(agent) → actuator(changes) → system(codebase) → sensor;
  the signal must be monotone (real improvement always raises it), smooth (small change = small delta), ungameable,
  observable from static data. Lyapunov stability cited as the convergence guarantee for the loop.
