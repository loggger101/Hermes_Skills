---
description: "What Norvig's Advent of Code 2025 LLM notebook measured (LLMs: all correct, ~5x more code, ~3x slower; missed input-specific shortcuts) and how to prompt for better; a verified puzzle-utilities block"
source_repo: norvig/pytudes ipynb/Advent-2025-AI.ipynb (MIT)
tested_version: notebook markdown read (54 markdown cells, 112 cells); the utilities block below was executed on Python 3.14 as one script of asserts
verified_date: "2026-10-05"
---

# LLM-written vs expert puzzle solutions (Peter Norvig, Dec 2025)

pytudes is Norvig's collection of short Python "etudes" (notebooks on Advent of Code, Project Euler, spelling, Wordle, ...). The most useful recent item for an agent is
**Advent-2025-AI**: Gemini 3 Pro, Claude Opus 4.5 and ChatGPT 5.1/5.2 each solved the 12 AoC 2025 days, with Norvig's own earlier solutions as the baseline.
Prompt style: `Write code to solve the following problem:` plus the full Part 1 text, then `There is a change to the specification:` plus Part 2.

## Measured results (from the notebook)

| Metric | LLM code | Norvig's code |
|---|---|---|
| Correct answers | **all 22 puzzle parts** (after one correction prompt on Day 1 part 2) | all |
| Lines of code (22 parts) | 1,732 total, mean 75 | 356 total, mean 14.5 (about 5x fewer) |
| Run time, summed (12.1 excluded as incomparable) | 1,215 ms (median 2.8 ms) | 366 ms (median 0.9 ms), about 3x faster |
| Production speed | "maybe 20 times faster" than the human (not timed) | |

His verdict: LLMs did very well, got every answer, and knew what an experienced engineer should (seeing through the story to the real problem, standard library use, `re`/`split` parsing,
modular arithmetic, memoisation/DP, complexity reasoning); the three models were roughly equal.

## Where the LLM solutions lost (concrete cases)

- **Missed instance-specific shortcuts.** Day 12: given the real input, the human noticed most regions trivially fit presents into 3x3 boxes; ChatGPT wrote a general rotate-and-pack search (248 lines vs 20) that took about **two minutes** where a constant-time check takes under a millisecond. It did include the cheap `total_area > W*H` rejection. Giving the model the actual input did not make it look for structure in the data.
- **Brute force first, better method on prompt.** Day 4 part 2: scan-the-whole-grid; fixed after being prompted. Day 10: Gemini gave a DFS "making it solvable in milliseconds" which in fact took seconds and would take hours on the full input; the working approach was an integer-programming solver (`milp`), which both Norvig and Gemini ended up using. **Check claimed complexity by running it.**
- **Verbosity and structure.** One 100-line function (Day 10 part 1), "if x: True else: False" idioms, unused imports, vestigial code (a conversion step feeding a cache that no longer used it), inconsistent type annotations that appeared "when prompted" or "on some days". A refactor prompt such as `Refactor to have a function that takes the points as input and returns the area` fixed `main`-reads-stdin habits.
- **Off-by-one in the model's reasoning, fixed by a nudge.** Day 1 part 2 was wrong (distance from 0 to 0 when moving right); the bare prompt `That's not quite right.` made the "Thinking" variant find the exact error the human had made too.
- Unfair LOC comparison caught by an audience member: the human used a personal utilities module. Norvig then asked each model what utilities it would define in advance; all three produced nearly the same four areas.

## Prompts and workflow that follow from it

1. **Ask for the utility layer first**: "If you were going to do this contest, what set of utility functions would you define ahead of time?" (input parsing, 2D grid and point helpers, graph search, math). Reuse it for every task.
2. **Pass the real data and say so**: "Look at my input for structure that allows a shortcut," not only the problem statement.
3. **Ask for the pure function**, not a script: `solve(data) -> answer`, testable and timeable.
4. **Run and time it** before accepting; compare against a small brute force on tiny cases.
5. After a first correct answer, ask **"Can this be faster or simpler?"**, and name the constraint ("it must handle the full input in under a second").
6. Treat model claims about performance ("milliseconds") as hypotheses.

## Puzzle utilities block (executed; all asserts pass)

Grids are `{(x, y): char}` dicts (all three LLMs chose dicts over nested lists because AoC grids can be unbounded or sparse).

```python
"""Puzzle utilities block (the four areas all three LLMs chose in Norvig's AoC 2025 notebook). Run = asserts pass."""
import re
import heapq
from collections import deque
from math import gcd, prod

def ints(text):
    """All integers in a string, including negatives."""
    return [int(x) for x in re.findall(r"-?\d+", text)]

def paragraphs(text):
    return [p for p in text.strip().split("\n\n")]

def grid(text):
    """{(x, y): char} so the grid may be unbounded and sparse."""
    return {(x, y): ch for y, row in enumerate(text.splitlines()) for x, ch in enumerate(row)}

DIRS4 = ((1, 0), (0, 1), (-1, 0), (0, -1))
DIRS8 = DIRS4 + ((1, 1), (-1, 1), (1, -1), (-1, -1))

def neighbors(p, dirs=DIRS4):
    return [(p[0] + dx, p[1] + dy) for dx, dy in dirs]

def bfs(start, succ, goal):
    """Shortest path length from start to any node with goal(node) true, or None."""
    seen = {start}; q = deque([(start, 0)])
    while q:
        u, d = q.popleft()
        if goal(u):
            return d
        for v in succ(u):
            if v not in seen:
                seen.add(v); q.append((v, d + 1))

def dijkstra(start, succ, goal):
    """succ(u) yields (v, cost). Returns the cheapest cost to a goal node or None."""
    best = {start: 0}; pq = [(0, 0, start)]; n = 1
    while pq:
        c, _, u = heapq.heappop(pq)
        if goal(u):
            return c
        if c > best.get(u, float("inf")):
            continue
        for v, w in succ(u):
            nc = c + w
            if nc < best.get(v, float("inf")):
                best[v] = nc; heapq.heappush(pq, (nc, n, v)); n += 1

def lcm(*xs):
    out = 1
    for x in xs:
        out = out * x // gcd(out, x)
    return out

assert ints("move 3 to -12 and +5, 7x9") == [3, -12, 5, 7, 9]
g = grid("#.#\n..#")
assert g[(2, 1)] == "#" and len(g) == 6
assert sorted(neighbors((0, 0))) == [(-1, 0), (0, -1), (0, 1), (1, 0)]
maze = grid("S..#\n.#..\n...G")
start = next(p for p, c in maze.items() if c == "S")
goal = lambda p: maze.get(p) == "G"
succ = lambda p: [q for q in neighbors(p) if maze.get(q) in (".", "G", "S")]
assert bfs(start, succ, goal) == 5
wsucc = lambda p: [(q, 1 if maze[q] != "." else 2) for q in succ(p)]
assert dijkstra(start, wsucc, goal) == 9   # 4 interior "." steps at cost 2, final G step at cost 1
assert lcm(4, 6, 10) == 60 and prod([2, 3, 4]) == 24
assert len(paragraphs("a\nb\n\nc")) == 2
print("puzzle utilities: all asserts pass")
```

See `references/graph-algorithms-library-map.md` for library equivalents (`scipy.sparse.csgraph`, `networkx`) when graphs are explicit, and `mattpocock-tdd` for the red-green loop around `solve`.
