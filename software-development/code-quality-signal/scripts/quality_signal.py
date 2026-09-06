#!/usr/bin/env python3
"""Code quality signal: 5 ungameable root-cause metrics on a Python codebase.

Derived from sentrux/sentrux docs/quality-signal-design.md (starred repo, read-only).
Stdlib only. Metrics: modularity (Newman Q over import graph), acyclicity
(Tarjan SCC cycle count), depth (longest dependency chain), equality (Gini of
per-function cyclomatic complexity), redundancy (dead + duplicate functions).
Aggregated via geometric mean -> 0-10000 signal. Lowest sub-score = bottleneck.

Usage: python quality_signal.py <project-dir> [--json]
"""
import ast
import hashlib
import json
import sys
from collections import defaultdict, deque
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".tox",
             ".mypy_cache", ".ruff_cache", "build", "dist", ".eggs"}


def find_py_files(root: Path):
    out = []
    for p in sorted(root.rglob("*.py")):
        if any(part in SKIP_DIRS or part.startswith(".") and part != ".github"
               for part in p.relative_to(root).parts[:-1]):
            continue
        try:
            src = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        out.append((p, src))
    return out


def module_name(p: Path, root: Path):
    rel = p.relative_to(root)
    parts = list(rel.parts[:-1]) + [rel.stem]
    if rel.stem == "__init__":
        parts = list(rel.parts[:-1])
    return ".".join(parts) if parts else ""


def build_graph(files, root: Path):
    """files: [(path, src)] -> (nodes {modname}, edges set[(src,dst)], parse cache)."""
    mods = {}  # dotted name -> path
    for p, _ in files:
        m = module_name(p, root)
        if m and m not in mods:
            mods[m] = str(p)

    def resolve(dotted):
        cands = []
        parts = dotted.split(".")
        for i in range(len(parts), 0, -1):
            prefix = ".".join(parts[:i])
            if prefix in mods:
                return prefix
        return None

    nodes, edges, cache = set(mods), set(), {}
    for p, src in files:
        m = module_name(p, root)
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        cache[m] = (tree, str(p), src)  # keep source text to avoid re-reading
        pkg_parts = list(Path(m).parts[:-1]) if "." in m else []
        for node in ast.walk(tree):
            targets = []
            if isinstance(node, ast.Import):
                targets += [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                lvl = node.level or 0
                base = pkg_parts[:len(pkg_parts) - (lvl - 1)] if lvl else []
                dotted = ".".join(base + node.module.split("."))
                targets.append(dotted)
            for t in targets:
                r = resolve(t)
                if r and r != m:
                    edges.add((m, r))
    return nodes, edges, cache


def newman_q(nodes, edges):
    """Directed Newman modularity with community = top-level path segment."""
    adj = defaultdict(set)
    kout = defaultdict(int)
    kin = defaultdict(int)
    for s, d in edges:
        if (s, d) not in adj[s]:
            adj[s].add(d)
            kout[s] += 1
            kin[d] += 1
    m = len(edges)
    if m == 0 or len(nodes) < 2:
        return 0.0
    comm = {n: (n.split(".")[0] if "." in n else "_root") for n in nodes}

    def kout_of(n):
        return kout.get(n, 0)

    q = 0.0
    # sum over edges present + expected term correction per community pair
    # Efficient form: Q = (1/m)*sum_c [ E_in(c) - (k_out(c)*k_in(c))/m ]
    ein = defaultdict(int)
    koutc = defaultdict(int)
    kinc = defaultdict(int)
    for n in nodes:
        c = comm[n]
        koutc[c] += kout.get(n, 0)
        kinc[c] += kin.get(n, 0)
    for s, d in edges:
        if comm[s] == comm[d]:
            ein[comm[s]] += 1
    for c in set(comm.values()):
        q += ein[c] - (koutc[c] * kinc[c]) / m
    return q / m


def tarjan_cycles(nodes, adj):
    """Iterative Tarjan SCC; returns count of SCCs with >1 member."""
    index = {}
    low = {}
    on_stack = set()
    stack = []
    counter = [0]
    cycles = 0

    for start in sorted(nodes):
        if start in index:
            continue
        work = [(start, iter(sorted(adj.get(start, ()))))]
        while work:
            v, it = work[-1]
            if v not in index:
                index[v] = low[v] = counter[0]
                counter[0] += 1
                stack.append(v)
                on_stack.add(v)
            advanced = False
            for w in it:
                if w not in index:
                    work[-1] = (v, it)
                    work.append((w, iter(sorted(adj.get(w, ())))))
                    advanced = True
                    break
                elif w in on_stack:
                    low[v] = min(low[v], index[w])
            if advanced:
                continue
            # v done
            work.pop()
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                if len(comp) > 1:
                    cycles += 1
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[v])
    return cycles


def longest_depth(nodes, adj):
    """Longest dependency chain via iterative DFS DP (cycle-safe)."""
    memo = {}
    for s in nodes:
        if s in memo:
            continue
        frame_stack = [(s, iter(sorted(adj.get(s, ()))))]
        on_path = {s}
        while frame_stack:
            v, it = frame_stack[-1]
            advanced = False
            for w in it:
                if w in memo or w in on_path:  # resolved or cycle edge: skip
                    continue
                frame_stack.append((w, iter(sorted(adj.get(w, ())))))
                on_path.add(w)
                advanced = True
                break
            if not advanced:
                best = max((memo[w] for w in adj.get(v, ()) if w in memo), default=0) + 1
                memo[v] = best
                frame_stack.pop()
                on_path.discard(v)
    return max(memo.values(), default=0)


def cyclomatic(tree):
    """Per-function CC: decision points + 1."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cc = 1
            for sub in ast.walk(node):
                if isinstance(sub, (ast.If, ast.For, ast.AsyncFor, ast.While,
                                    ast.ExceptHandler, ast.Assert,
                                    ast.comprehension)):
                    cc += 1
                elif isinstance(sub, ast.BoolOp):
                    cc += len(sub.values) - 1
            out.append(cc)
    return out


def gini(values):
    vals = sorted(v for v in values if v > 0)
    n = len(vals)
    total = sum(vals)
    if n == 0 or total == 0:
        return 0.0
    s = sum((2 * i - n - 1) * x for i, x in enumerate(vals))
    return abs(s) / (n * total)


def structural_hash(tree):
    """Shape hash: identifiers renamed positionally; constants kept. No re-parse."""
    counters = defaultdict(int)
    out = []

    def emit(node, depth=0):
        t = type(node).__name__
        if isinstance(node, ast.Name):
            counters["Name"] += 1
            out.append(f"v{counters['Name']}")
            return
        if isinstance(node, ast.arg):
            counters["arg"] += 1
            out.append(f"a{counters['arg']}")
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            counters["fn"] += 1
            nargs = len(node.args.posonlyargs) + len(node.args.args) + len(node.args.kwonlyargs)
            out.append(f"{'  ' * depth}FN args={nargs}")
            for stmt in node.body:
                emit(stmt, depth + 1)
            return
        if isinstance(node, ast.ClassDef):
            counters["cls"] += 1
            out.append(f"{'  ' * depth}CLS")
            for stmt in node.body:
                emit(stmt, depth + 1)
            return
        if isinstance(node, (ast.Constant,)):
            # keep type only, not value — shape, not content
            out.append(f"{t}:{type(node.value).__name__}")
            return
        if isinstance(node, ast.Attribute):
            counters["attr"] += 1
            emit(node.value, depth)
            out.append("ATTR" + str(counters["attr"]))
            return
        # generic: type + children in field order (skip names/strings already handled)
        out.append(t)
        for _, v in ast.iter_fields(node):
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, ast.AST):
                        emit(item, depth + 1)
            elif isinstance(v, ast.AST):
                emit(v, depth + 1)

    emit(tree)
    return hashlib.sha256("\n".join(out).encode()).hexdigest()[:16]


def redundancy(cache):
    """cache: {modname: (tree, path, src)}. Returns (dead, dups, total_fns, ratio)."""
    names_used = set()
    for m, (tree, _, _) in cache.items():
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                names_used.add(node.id)

    dead = 0
    total_fns = 0
    hashes = defaultdict(list)
    for m, (tree, path, text) in sorted(cache.items()):
        # module-level functions only count toward "dead"
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                total_fns += 1
                if not node.name.startswith("_") and node.name not in names_used:
                    dead += 1
        # all functions count toward duplicates — hash shape directly, no re-parse
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                hashes[structural_hash(node)].append(f"{m}:{node.name}")
    dups = sum(len(v) - 1 for v in hashes.values() if len(v) > 1)
    ratio = min((dead + dups) / total_fns, 1.0) if total_fns else 0.0
    return dead, dups, total_fns, ratio


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    root = Path(args[0] if args else ".").resolve()
    files = find_py_files(root)
    nodes, edges, cache = build_graph(files, root)
    adj = defaultdict(set)
    for s, d in edges:
        adj[s].add(d)

    q = newman_q(nodes, edges)
    cycles = tarjan_cycles(nodes, adj)
    depth = longest_depth(nodes, adj)
    cc_values = []
    for m in sorted(cache):
        tree = cache[m][0]
        cc_values.extend(cyclomatic(tree))
    gini_cc = gini(cc_values)
    dead, dups, total_fns, red_ratio = redundancy(cache)

    scores = {
        "modularity": (q + 0.5) / 1.5,
        "acyclicity": 1.0 / (1.0 + cycles),
        "depth": 1.0 / (1.0 + depth / 8.0),
        "equality": 1.0 - gini_cc,
        "redundancy": 1.0 - red_ratio,
    }
    prod = 1.0
    for v in scores.values():
        prod *= max(v, 1e-9)
    signal = int(round((prod ** (1 / 5)) * 10000))
    bottleneck = min(scores, key=scores.get)

    result = {
        "project": str(root),
        "files": len(files),
        "modules": len(nodes),
        "edges": len(edges),
        "functions": total_fns,
        "raw": {"newman_q": round(q, 4), "cycles": cycles, "max_depth": depth,
                "cc_gini": round(gini_cc, 4), "dead_functions": dead,
                "duplicate_extras": dups},
        "scores": {k: round(v, 4) for k, v in scores.items()},
        "quality_signal": signal,
        "bottleneck": bottleneck,
    }
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        r = result["raw"]
        s = result["scores"]
        print(f"Quality {signal}  (bottleneck: {bottleneck})")
        print(f"  files={result['files']} modules={result['modules']} "
              f"edges={result['edges']} functions={total_fns}")
        print(f"  modularity   Q={r['newman_q']:+.3f}      score {s['modularity']:.4f}")
        print(f"  acyclicity   cycles={r['cycles']:<5d}     score {s['acyclicity']:.4f}")
        print(f"  depth        max_chain={r['max_depth']:<3d}    score {s['depth']:.4f}")
        print(f"  equality     cc_gini={r['cc_gini']:.3f}   score {s['equality']:.4f}")
        print(f"  redundancy   dead={r['dead_functions']} dup_extra={r['duplicate_extras']:>3d}"
              f"             score {s['redundancy']:.4f}")


if __name__ == "__main__":
    main()
