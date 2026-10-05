---
description: "Shortest path, assignment, flow, SCC, MST, topo-sort: the pathfinding crate's algorithm list mapped to scipy.sparse.csgraph / networkx calls, with live-verified traps"
source_repo: evenfurther/pathfinding (Rust, Apache-2.0/MIT)
tested_version: scipy 1.18.1, numpy 2.5.2, networkx 3.7 on Windows py3.14, every snippet run; crate module list and Kuhn-Munkres semantics read from its source @ main
verified_date: "2026-10-05"
---

# Graph algorithms: use the library, not a hand-rolled version

The Rust `pathfinding` crate is a good map of "the graph algorithms people actually need": its modules are `directed::{astar, bfs, dfs, dijkstra,
fringe, idastar, iddfs, yen, count_paths, cycle_detection, edmonds_karp, strongly_connected_components, topological_sort}`,
`undirected::{kruskal, prim, connected_components, cliques}` and `kuhn_munkres`. Its signature idea is **implicit graphs**: you pass a
`successors(node)` closure instead of building a graph. Python has the same capabilities; pick by whether the graph is explicit (arrays) or implicit (generated).

## Map

| Need (crate module) | Explicit graph in Python | Notes |
|---|---|---|
| Dijkstra / shortest path (`dijkstra`, `astar`, `yen` k-shortest) | `scipy.sparse.csgraph.dijkstra(g, indices=s, return_predecessors=True)`; `networkx.dijkstra_path`, `astar_path`, `shortest_simple_paths` (Yen-style) | scipy is faster on large arrays; networkx takes any hashable nodes and heuristics |
| BFS / DFS on an implicit state space (`bfs`, `dfs`, `iddfs`, `idastar`) | write the 15-line `deque` loop with a `prev` dict (below); `networkx` only if you already built the graph | no library takes a successors closure as directly as the crate does |
| Assignment / Hungarian (`kuhn_munkres`) | `scipy.optimize.linear_sum_assignment(cost, maximize=False)` | **direction differs** (below) |
| Max flow (`edmonds_karp`) | `scipy.sparse.csgraph.maximum_flow(csr, s, t)`; `networkx.maximum_flow` | scipy needs integer capacities |
| Strongly connected components | `scipy.sparse.csgraph.connected_components(g, directed=True, connection="strong")` | labels array out |
| Connected components, MST (`kruskal`, `prim`) | `connected_components`, `minimum_spanning_tree` | |
| Topological sort | `graphlib.TopologicalSorter` (stdlib) or `networkx.topological_sort` | stdlib is enough for dependency ordering |
| Cliques | `networkx.find_cliques` | |

## Verified results and traps

```python
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra, maximum_flow, connected_components
from scipy.optimize import linear_sum_assignment
```

1. **Dijkstra**, 6-node weighted graph, 0 to 4: scipy `20.0` via predecessor chain `0, 2, 5, 4`; networkx `dijkstra_path` and `astar_path` (heuristic 0) gave the same path. The predecessor entries are `np.int32` values, so convert (`int(...)`) before printing or JSON-encoding the path.
2. **A dense matrix cannot express a zero-weight edge.** `csr_matrix(dense)` drops zeros (a 3-node graph kept 2 stored entries, losing the 0-weight edge 0-1). Build the CSR from explicit `(data, (rows, cols))` arrays: with an explicit stored zero, scipy treated the edge as present and returned distance `0.0` for it.
3. **Assignment direction.** `linear_sum_assignment` **minimises** total cost by default. The crate's `kuhn_munkres` computes a **maximum weight** maximum matching. For `C = [[4,1,3],[2,0,5],[3,2,2]]`: minimise gives total 5 (pairs 0-1, 1-0, 2-2), `maximize=True` gives 11 (0-0, 1-2, 2-1). A rectangular 2x3 matrix is accepted and returns 2 pairs. Porting code between the two must flip the sign or the flag.
4. **Max flow capacities must be integers**: `maximum_flow` on a float matrix raised `ValueError: graph capacities must be integers` (scale and round if you have fractional capacities). A 4-node example returned flow value 5.
5. **SCC**: a directed graph with cycle 0->1->2->0 plus a tail 2->3 gave 2 components, labels `[1, 1, 1, 0]`.
6. `networkx.topological_sort` on a DAG gave `[1, 2, 3]`; for plain dependency ordering the stdlib `graphlib.TopologicalSorter` needs no install.

## Implicit-graph search in pure Python

```python
from collections import deque
def bfs(start, successors, is_goal):
    prev = {start: None}; q = deque([start])
    while q:
        u = q.popleft()
        if is_goal(u):
            path = []
            while u is not None: path.append(u); u = prev[u]
            return path[::-1]
        for v in successors(u):
            if v not in prev: prev[v] = u; q.append(v)
```

Run on the crate README's knight-move example (from (1,1) to (4,6)) it returned a 5-node path, matching the crate's `assert_eq!(len, 5)`.
For weighted implicit graphs use `heapq` with a `(cost, counter, node)` tuple (the counter breaks ties so nodes need not be orderable).

## When to still go native

Millions of nodes with a hot inner loop: the crate (or `rustworkx`, a Rust-backed Python graph library; not tested here) is the next step after scipy.
Everything above is pure Python/scipy and fine below that scale.
