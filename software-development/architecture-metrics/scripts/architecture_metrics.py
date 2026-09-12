#!/usr/bin/env python3
"""Architecture metrics: levels, violations, blast radius, A/I/D distance,
stable-foundation coupling, god/hotspot files, test gaps.

Derived from sentrux/sentrux (MIT) architecture layer — Lakos 1996 levelization,
Robert C. Martin 2003 main sequence + Stable Dependencies Principle, Baldwin &
Clark 2000 DSM. Stdlib only (ast). Python codebases.

Usage: python architecture_metrics.py <project-dir> [--json] [--dsm N]
"""
import ast
import json
import sys
from collections import defaultdict, deque
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".tox",
             ".mypy_cache", ".ruff_cache", "build", "dist", ".eggs"}
GOD_FAN_OUT = 15          # per-file fan-out threshold (sentrux: per-language profile)
HOTSPOT_FAN_IN = 8        # per-file fan-in threshold
FOUNDATION_I = 0.30       # I <= this => foundation, excluded from D average (Martin stable zone)
STABLE_FOUNDATION_I = 0.15  # SDP: mostly depended-on + little outgoing
MIN_STABLE_FAN_IN = 3     # fan-in floor so leaves aren't "foundations"


def find_py_files(root):
    out = []
    for p in sorted(root.rglob("*.py")):
        rel_parts = p.relative_to(root).parts[:-1]
        if any(part in SKIP_DIRS or (part.startswith(".") and part != ".github")
               for part in rel_parts):
            continue
        try:
            src = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        out.append((p, src))
    return out


def module_name(p, root):
    rel = p.relative_to(root)
    parts = list(rel.parts[:-1]) + [rel.stem]
    if rel.stem == "__init__":
        parts = list(rel.parts[:-1])
    return ".".join(parts) if parts else ""


def build_graph(files, root):
    mods = {}
    for p, _ in files:
        m = module_name(p, root)
        if m and m not in mods:
            mods[m] = str(p)

    def resolve(dotted):
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
        cache[m] = (tree, str(p))
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
        # `from pkg import submodule` — names may be submodules of a package.
        # (sentrux parity: package index / extension probing; here we try each
        # imported name as <module>.<name>.)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                lvl = node.level or 0
                base = pkg_parts[:len(pkg_parts) - (lvl - 1)] if lvl else []
                dotted = ".".join(base + node.module.split("."))
                for a in node.names:
                    sub = resolve(dotted + "." + a.name)
                    if sub and sub != m:
                        edges.add((m, sub))
    return nodes, edges, cache


def compute_levels(edges):
    """Kahn on SCC DAG; returns ({node: level}, max_level)."""
    if not edges:
        return {}, 0
    nodes = {x for e in edges for x in e}
    adj = defaultdict(set)
    for s, d in edges:
        adj[s].add(d)

    # Kosaraju (iterative)
    visited, finish = set(), []
    for start in sorted(nodes):
        if start in visited:
            continue
        stack = [(start, iter(sorted(adj.get(start, ()))))]
        visited.add(start)
        while stack:
            v, it = stack[-1]
            advanced = False
            for w in it:
                if w not in visited:
                    visited.add(w)
                    stack.append((w, iter(sorted(adj.get(w, ())))))
                    advanced = True
                    break
            if not advanced:
                finish.append(v)
                stack.pop()

    rev = defaultdict(set)
    for s, d in edges:
        rev[d].add(s)
    seen2, scc_id, sccs_list = set(), {}, []
    for start in reversed(finish):
        if start in seen2:
            continue
        sid = len(sccs_list)
        comp_set, stack = {start}, [start]
        while stack:
            v = stack.pop()
            scc_id[v] = sid
            for w in rev.get(v, ()):
                if w not in seen2 and w not in comp_set:
                    comp_set.add(w)
                    scc_id[w] = sid
                    stack.append(w)
        seen2 |= comp_set
        sccs_list.append(comp_set)

    # SCC DAG edges (deduped)
    n_scc = len(sccs_list)
    out_adj = [set() for _ in range(n_scc)]
    for s, d in edges:
        a, b = scc_id[s], scc_id[d]
        if a != b and b not in out_adj[a]:
            out_adj[a].add(b)

    # Levels via fixpoint iteration on the SCC DAG: level(a) = max(level(child)+1).
    # O(V*E) worst case — fine for scanned project sizes; identical result to
    # sentrux's Kahn queue (which processes leaves first and propagates upward).
    levels_scc = [0] * n_scc
    changed = True
    while changed:
        changed = False
        for a in range(n_scc):
            best = max((levels_scc[b] + 1 for b in out_adj[a]), default=0)
            if best > levels_scc[a]:
                levels_scc[a] = best
                changed = True
    node_levels = {n: levels_scc[scc_id[n]] for n in nodes}
    return node_levels, max(levels_scc)


def upward_violations(edges, levels):
    """Edges where from_level < to_level (rare), plus intra-cycle edges.

    Intra-SCC edges ARE violations: the cycle prevents clean layering."""
    if not edges:
        return []
    nodes = {x for e in edges for x in e}
    sccs_of_node = {}
    # reuse SCC membership via a quick recompute (graphs are small)
    adj = defaultdict(set)
    for s, d in edges:
        adj[s].add(d)
    visited, finish = set(), []
    for start in sorted(nodes):
        if start in visited:
            continue
        stack = [(start, iter(sorted(adj.get(start, ()))))]
        visited.add(start)
        while stack:
            v, it = stack[-1]
            advanced = False
            for w in it:
                if w not in visited:
                    visited.add(w)
                    stack.append((w, iter(sorted(adj.get(w, ())))))
                    advanced = True
                    break
            if not advanced:
                finish.append(v)
                stack.pop()
    rev = defaultdict(set)
    for s, d in edges:
        rev[d].add(s)
    seen2, comp_id_of = set(), {}
    comps = []
    for start in reversed(finish):
        if start in seen2:
            continue
        sid = len(comps)
        cs, stack = {start}, [start]
        while stack:
            v = stack.pop()
            comp_id_of[v] = sid
            for w in rev.get(v, ()):
                if w not in seen2 and w not in cs:
                    cs.add(w)
                    stack.append(w)
        seen2 |= cs
        comps.append(cs)

    violations = []
    for s, d in sorted(edges):
        fl = levels.get(s, 0)
        tl = levels.get(d, 0)
        if fl < tl:
            violations.append((s, d, fl, tl))
        elif comp_id_of[s] == comp_id_of[d] and len(comps[comp_id_of[s]]) > 1 \
                and s != d:
            violations.append((s, d, fl, tl))
    return sorted(violations, key=lambda v: -abs(v[3] - v[2]))


def blast_radius(edges):
    """Per-file transitive reverse reach (if this file changes, how many files
    could be affected). Full BFS per node; uniform sampling above 5000 nodes."""
    if not edges:
        return {}
    rev = defaultdict(set)
    for s, d in edges:
        rev[d].add(s)
    all_nodes = sorted({x for e in edges for x in e})
    MAX_FULL_BFS = 5000
    if len(all_nodes) <= MAX_FULL_BFS:
        starts = all_nodes
    else:
        step = len(all_nodes) / MAX_FULL_BFS
        starts = [all_nodes[int(i * step)] for i in range(MAX_FULL_BFS)]
        # guarantee max-degree node is sampled (sentrux parity)
        max_deg = max(rev.items(), key=lambda kv: len(kv[1]))[0]
        if max_deg not in starts:
            starts[-1] = max_deg

    result = {}
    for start in starts:
        seen, q = {start}, deque([start])
        while q:
            v = q.popleft()
            for w in rev.get(v, ()):
                if w not in seen:
                    seen.add(w)
                    q.append(w)
        result[start] = len(seen) - 1
    return result


def cyclomatic(tree):
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cc = 1
            for sub in ast.walk(node):
                if isinstance(sub, (ast.If, ast.For, ast.While, ast.AsyncFor,
                                    ast.ExceptHandler, ast.Assert,
                                    ast.comprehension)):
                    cc += 1
                elif isinstance(sub, ast.BoolOp):
                    cc += len(sub.values) - 1
            out.append((node.name, node.lineno, cc))
    return out


def is_test_file(path_str):
    p = Path(path_str)
    name = p.name.lower()
    if "tests" in path_str.split("/") or "__tests__" in name:
        return True
    return name.startswith("test_") or name.endswith("_test.py") \
        or name == "conftest.py"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    dsm_limit = None
    for i, a in enumerate(sys.argv):
        if a == "--dsm":
            dsm_limit = int(sys.argv[i + 1])
    root = Path(args[0] if args else ".").resolve()
    files = find_py_files(root)
    nodes, edges, cache = build_graph(files, root)

    levels, max_level = compute_levels(edges)
    violations = upward_violations(edges, levels)
    br = blast_radius(edges)

    # fan maps (dedup import+call — Python: imports only here)
    fan_out, fan_in = defaultdict(int), defaultdict(int)
    for s, d in edges:
        fan_out[s] += 1
        fan_in[d] += 1

    entry_files = {m for m in nodes if Path(cache.get(m, ("", ""))[1]).name in
                   {"__main__.py"} or "conftest" in cache.get(m, ("", ""))[1]}
    god_files = sorted(((p, c) for p, c in fan_out.items()
                        if c > GOD_FAN_OUT and p not in entry_files
                        and Path(cache[p][1]).name != "__init__.py"),
                       key=lambda x: -x[1])[:20]

    def instability_of(m):
        ca, ce = fan_in[m], fan_out[m]
        return 0.5 if ca + ce == 0 else ce / (ca + ce)

    hotspots = sorted(((p, c) for p, c in fan_in.items()
                       if c > HOTSPOT_FAN_IN and Path(cache[p][1]).name != "__init__.py"
                       and instability_of(p) >= STABLE_FOUNDATION_I),
                      key=lambda x: -x[1])[:20]

    # ── Martin distance from main sequence, per top-level module ──
    mod_fan_out, mod_fan_in = defaultdict(set), defaultdict(set)
    for s, d in edges:
        a, b = s.split(".")[0], d.split(".")[0]
        if a != b:
            mod_fan_out[a].add(b)
            mod_fan_in[b].add(a)

    abstract_by_mod, total_types_by_mod = defaultdict(int), defaultdict(int)
    for m in sorted(cache):
        tree, path = cache[m]
        top = m.split(".")[0] if "." in m else "(root)"
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef,)):
                total_types_by_mod[top] += 1
                bases = {b.id for b in node.bases
                         if isinstance(b, (ast.Name,))} | \
                        {b.attr for b in node.bases if isinstance(b, ast.Attribute)}
                has_abstract_method = any(
                    (getattr(d, "id", None) == "abstractmethod" or
                     getattr(getattr(d, "func", None), "id", "") == "abstractmethod")
                    for fn in node.body if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
                    for d in fn.decorator_list)
                if bases & {"ABC", "Protocol"} or has_abstract_method:
                    abstract_by_mod[top] += 1

    distances = []
    for top in sorted(set(list(total_types_by_mod) + list(mod_fan_out) + list(mod_fan_in))):
        total = total_types_by_mod.get(top, 0)
        if total < 1:
            continue
        a = abstract_by_mod.get(top, 0) / total
        ce, ca = len(mod_fan_out.get(top, ())), len(mod_fan_in.get(top, ()))
        i = 0.5 if ce + ca == 0 else ce / (ce + ca)
        d = abs(a + i - 1.0)
        distances.append({"module": top, "A": round(a, 3), "I": round(i, 3),
                          "D": round(d, 3), "types": total,
                          "foundation": i <= FOUNDATION_I})
    non_foundation = [x for x in distances if not x["foundation"]]
    avg_d = (sum(x["D"] for x in non_foundation) / len(non_foundation)) \
        if non_foundation else 0.0

    # ── SDP-aware coupling: cross-module edges to UNSTABLE targets only ──
    stable_foundations = {top for top in set(list(mod_fan_out) + list(mod_fan_in))
                          if (lambda ce, ca: (ca >= MIN_STABLE_FAN_IN and
                                              (ce / (ca + ce) <= STABLE_FOUNDATION_I
                                               if ca + ce else True)))(len(mod_fan_out.get(top, ())), len(mod_fan_in.get(top, ())))}
    cross = [(s, d) for s, d in edges if s.split(".")[0] != d.split(".")[0]]
    bad_cross = [e for e in cross if e[1].split(".")[0] not in stable_foundations]
    coupling_score = len(bad_cross) / len(edges) if edges else 0.0

    # ── Test gaps: untested source files ranked by risk = CC x (fan_in+1) ──
    test_files, src_files = set(), {}
    for m in cache:
        path = cache[m][1]
        if is_test_file(path):
            test_files.add(m)
        else:
            src_files[m] = path
    tested_by_tests = set()
    for s, d in edges:
        if s in test_files and d in src_files:
            tested_by_tests.add(d)
    max_cc = {}
    for m in cache:
        ccs = [c for _, _, c in cyclomatic(cache[m][0])]
        if ccs:
            max_cc[m] = max(ccs)
    gaps = sorted(((m, src_files[m], max_cc.get(m, 1), fan_in.get(m, 0))
                   for m in src_files if m not in tested_by_tests and Path(src_files[m]).name != "__init__.py"),
                  key=lambda g: -(g[2] * (g[3] + 1)))[:20]

    result = {
        "project": str(root),
        "files": len(files), "modules": len(nodes), "edges": len(edges),
        "max_level": max_level,
        "upward_violations": [{"from": s, "to": d, "levels": [fl, tl]}
                              for s, d, fl, tl in violations[:20]],
        "blast_radius_top": sorted(({"file": k, "reach": v} for k, v in br.items()),
                                   key=lambda x: -x["reach"])[:10],
        "god_files": [{"file": m, "fan_out": c} for m, c in god_files],
        "hotspots": [{"file": m, "fan_in": c} for m, c in hotspots],
        "distance_from_main_sequence": {"avg_D_non_foundation": round(avg_d, 3),
                                        "modules": distances},
        "stable_foundations": sorted(stable_foundations),
        "sdp_coupling_score": round(coupling_score, 4),
        "test_gaps": [{"file": m, "path": p, "max_cc": cc, "fan_in": fi,
                       "risk": cc * (fi + 1)} for m, p, cc, fi in gaps],
    }

    if dsm_limit is not None:
        # Compact DSM text table (Baldwin & Clark): rows=importers, cols=imported.
        # Sorted HIGHEST level first so correct-direction edges (high→low) fall
        # BELOW the diagonal and inversions (low→high) appear ABOVE it — same
        # convention as sentrux's DSM panel.
        ds = sorted(nodes)[:dsm_limit]
        lvl_of = {n: levels.get(n, 0) for n in ds}
        order_key = lambda n: (-lvl_of[n], n)
        ds2 = sorted(ds, key=order_key)
        idx = {n: i for i, n in enumerate(ds2)}
        marks = {(idx[s], idx[d]) for s, d in edges if s in idx and d in idx}
        labels = [n.split(".")[-1][:8].ljust(9) for n in ds2]
        lines = ["DSM sorted by level desc (row imports col; '.'=edge):",
                 "          " + "".join(labels)]
        above = below = same = 0
        for r, rn in enumerate(ds2):
            row = []
            for c, cn in enumerate(ds2):
                if (r, c) in marks:
                    row.append(".")
                    if lvl_of[rn] < lvl_of[cn]: above += 1   # inversion
                    elif lvl_of[rn] > lvl_of[cn]: below += 1  # correct direction
                    else: same += 1                           # lateral (incl. cycles)
                else:
                    row.append(" ")
            lines.append(f"L{lvl_of[rn]} {rn.split('.')[-1][:8].ljust(9)}" + "".join(row))
        result["dsm"] = {"lines": lines, "above_diagonal_inversions": above,
                         "below_diagonal_correct": below, "same_level_lateral": same}

    if as_json:
        print(json.dumps(result, indent=2))
    else:
        r = result
        print(f"Architecture report — {r['project']}")
        print(f"  files={r['files']} modules={r['modules']} edges={r['edges']} "
              f"max_level={r['max_level']}")
        uv = r["upward_violations"]
        print(f"  upward violations: {len(uv)} (top: " +
              ", ".join(f"{v['from'].split('.')[-1]}->{v['to'].split('.')[-1]}" for v in uv[:5]) + ")")
        bt = r["blast_radius_top"][:3]
        print("  blast radius top-3: " +
              (", ".join(f"{b['file'].split('.')[-1]}={b['reach']}" for b in bt) or "(none)"))
        gf = ", ".join(f"{g['file'].split('.')[-1]}(fo={g['fan_out']})" for g in r["god_files"][:5])
        print(f"  god files: {gf or '(none)'}")
        hs = ", ".join(f"{h['file'].split('.')[-1]}(fi={h['fan_in']})" for h in r["hotspots"][:5])
        print(f"  unstable hotspots: {hs or '(none)'}")
        d = r["distance_from_main_sequence"]
        print(f"  avg distance from main sequence (non-foundation): {d['avg_D_non_foundation']}")
        for m in sorted(d["modules"], key=lambda x: -x["D"])[:5]:
            flag = " [foundation]" if m["foundation"] else ""
            print(f"    {m['module']}: A={m['A']} I={m['I']} D={m['D']}{flag}")
        sf = ", ".join(r["stable_foundations"][:8]) or "(none)"
        print(f"  stable foundations (SDP): {sf} | SDP coupling score: {r['sdp_coupling_score']}")
        tg = r["test_gaps"]
        print(f"  test gaps top-5: " +
              ", ".join(f"{g['file'].split('.')[-1]}(cc={g['max_cc']},fi={g['fan_in']})" for g in tg[:5]) or "(none)")
        if r.get("dsm"):
            print("\n".join(r["dsm"]["lines"]))
            s = r["dsm"]
            print(f"  DSM marks: inversions(above)={s['above_diagonal_inversions']} "
                  f"correct(below)={s['below_diagonal_correct']} lateral(same-level)={s['same_level_lateral']}")


if __name__ == "__main__":
    main()
