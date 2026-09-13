# TheAlgorithms/Python — Catalog Map & Decision Guide

Mined 2026-09-13 from commit `23c4208` (MIT). 1,466 Python files in ~50 top-level categories.
The repo's own README: *"Implementations are for learning purposes only. They may be less
efficient than the implementations in the Python standard library."* — that warning is accurate;
treat every file here as **teaching material**, not production code.

## How to read this map

- **stdlib-only** = category has no files importing numpy/pandas/tensorflow/torch (verified by grep, 2026-09-13).
- **"Use instead"** = the stdlib/library that beats these implementations in real work.
- Files are listed only where they carry a decision-relevant fact; for full listings see `DIRECTORY.md` in any clone.

## Category map (50 categories)

| Category | #files | deps | Worth reading? / Use instead |
|---|---:|---|---|
| strings | 60 | stdlib-only | **YES** — KMP/Z-function/Aho-Corasick/Rabin-Karp are the canonical plain-Python versions; see `algorithms-from-scratch.md`. Production: `re` (C-speed), or Aho-Corasick for dynamic multi-pattern sets. Edit distance → `difflib`, `python-Levenshtein` |
| hashes | 13 | stdlib-only (+1 numpy) | **YES** — Adler-32/Fletcher-16/djb2/sdbm/Luhn with the *why* behind each magic constant (5381, 65599). Production: `zlib`, `hashlib`. Their from-scratch md5/sha1/sha256 are teaching only |
| sorts | 60 | stdlib-only | Teaching. The interesting ones: **patience sort** (the algorithm CPython's timsort is derived from), intro-sort, Dutch national flag (3-way partition — the actual quicksort fix for many-duplicates). Production: `sorted()`/`list.sort()`, always |
| searches | 18 | stdlib-only | Teaching. **Median-of-medians** and **quickselect** are the only ones worth stealing ideas from (O(n) selection; production → `heapq.nsmallest`). Binary-search variants all lose to `bisect` |
| data_structures/ (13 subdirs, 138 files) | 138 | mostly stdlib | Teaching. Notable: **suffix_tree/** and **kd_tree/** are the only non-trivial spatial structures here; linked_list/binary_tree variants exist in ~20 flavors each — read ONE of each flavor max. Production: `collections.deque`, `heapq`, `dict` (hashing/), `bisect` |
| dynamic_programming | 53 | stdlib-only (+1) | **YES for patterns** — classic DP with clean tabulation code: LIS O(n log n) patience tails, matrix chain order, egg dropping, Viterbi, Needleman-Wunsch (bio alignment). Production: same algorithms exist in `numpy`/`scipy`; the value here is reading them without a framework |
| backtracking | 22 | stdlib-only | **YES for N-queens** — two implementations worth knowing: brute DFS vs the *math* version using diagonal invariants (row−col and row+col as collision keys; see `algorithms-from-scratch.md`). Sudoku/knight-tour/word-search are standard exercises |
| bit_manipulation | 31 | stdlib-only | Teaching. Steal: **Brian Kernighan's set-bit count** (`n & (n-1)`), Gray code sequence, two's complement by hand. Production: `int.bit_count()` (3.10+), `bit_length()`, format specs — all C-speed and clearer |
| maths/ (incl. numerical_analysis 20 files) | 195 | stdlib-only (+19 numpy) | **YES for numerical analysis**: Brent's method, Newton-Raphson, RK4/RK45, bisection, secant — the plainest implementations of what `scipy.optimize`/`solve_ivp` wrap. Primality: their `primelib.py` (841 lines) is a complete educational prime library; production → `sympy`, or Miller-Rabin from `cryptography.hazmat.primitives.asymmetric.utils` |
| matrix | 24 | stdlib-only (+2 numpy) | Teaching. **Sherman–Morrison** (rank-1 update of an inverse in O(n²)) and Strassen are the interesting entries; everything else → `numpy`/`scipy.linalg` |
| graphs | 68 | stdlib-only (+4) | Teaching, but the best plain-Python graph code anywhere. Dijkstra ×5 variants (read ONE: adjacency-list + heap), Bellman-Ford, Floyd-Warshall, Johnson's, Tarjan SCC, Hopcroft-Karp bipartite matching, **Karger's randomized min-cut**, PageRank, Markov chains. Production → `networkx` for anything real |
| ciphers | 48 | stdlib-only (+3) | Teaching + history: full classical cipher zoo (Playfair, Vigenère, Enigma ×2, RSA from scratch with factorization). **Never use any of it in production** — the point is understanding why. `diffie_hellman.py`/`rsa_key_generator.py` show key sizes; production → `cryptography` package |
| machine_learning | 40 | 27 files need numpy/tf | From-scratch ML: k-means, logistic regression, gradient boosting (from scratch), SVM, PCA, t-SNE. Teaching only — every one of these is in scikit-learn with better convergence guarantees and C extensions |
| neural_network/ | 25 | mostly numpy | Perceptron → MLP → CNN from scratch + optimizers (Adam, Muon). The **Muon optimizer** file is a genuinely recent addition worth reading; production → PyTorch |
| physics | 42 | stdlib-only (+2) | Formula implementations: orbital mechanics (basic capture, transfer work), N-body sim, Maxwell's equations. For the economicspace pipeline: `orbital_transfer_work.py` and `basic_orbital_capture.py` are closed-form sanity checks against brahe/skyfield numbers — but they're toy models, not oracles |
| financial | 10 | stdlib-only | Small but clean: Sharpe ratio, Kelly criterion, EMAs/SMA, EMI (equated monthly installments), present value. Production → `pandas`/`numpy_financial`; the formulas here are correct and readable |
| geodesy | 2 | stdlib-only | **Haversine** + Lambert's ellipsoidal distance — see `algorithms-from-scratch.md`. For real routing: OSRM (maps skill) or `geopy` |
| data_compression | 10 | stdlib-only (+1 numpy) | Huffman, LZ77/LZ, Lempel-Ziv with decompressor, RLE, move-to-front. Teaching; production → `zlib`, `bz2`, `lzma`. The **PSNR** file is image-quality metric, not compression — misfiled in the repo |
| conversions | 32 | stdlib-only | Base conversion, unit conversions (length/energy/pressure/speed/volume), RGB↔HSV↔CMYK, roman numerals. Production → `int(x, base)`, `math` module; HSV→RGB formulas are the only thing worth memorizing from here |
| project_euler | 309 | stdlib-only (+3 numpy) | ~145 problems × multiple solutions each — a **pattern library** more than content: sliding window over digit strings, sieve reuse across problems, memoized recursion for chain lengths. Read sol files only when you hit the same problem shape in your own work |
| boolean_algebra | 13 | stdlib-only | Karnaugh-map minimization + truth tables — teaching logic design; no production use here |
| knapsack | 7 | stdlib-only | 0/1, fractional, bounded variants side by side — good for seeing the three problem shapes at once. Production → `pulp`/Pyomo (see optimization-modeling-pyomo skill) |
| scheduling | 10 | stdlib-only | CPU scheduling: FCFS/SJF/HRRN/round-robin/multi-level feedback queue with average-wait-time math — OS-course material, clean implementations. Production → `asyncio` priority queues or a real scheduler |
| linear_algebra | 17 | mostly numpy | QR decomposition (from scratch), SVD, eigenvalues via power iteration/Lanczos. Teaching; production → `numpy.linalg`, `scipy.sparse.linalg` |
| computer_vision / digital_image_processing | 34/22 | all numpy+cv2 | Edge detection, morphological ops, template matching from scratch. Production → OpenCV directly; the repo files are just OpenCV calls with comments |
| audio_filters | 5 | numpy | FIR/IIR filter design — teaching DSP; production → `scipy.signal` |
| electronics / fuzzy_logic / fractals / graphics / quantum / blockchain / file_transfer / networking_flow | ~40 total | mixed | Niche/teaching. **networking_flow** (Ford-Fulkerson, Dinic, push-relabel) is the one worth a look if you ever need max-flow from scratch; production → `networkx` or `scipy.sparse.csgraph.maximum_flow` |
| other | 28 | stdlib-only (+1 numpy) | Mixed bag: **LRU/LFU cache** (the LFU version with frequency-bucketed doubly-linked lists is the complete interview-grade implementation), Tower of Hanoi, Fisher-Yates shuffle, DPLL SAT solver. Production → `functools.lru_cache`; their LRU is for interviews only |

## Cross-cutting facts worth knowing about this repo

1. **Doctest-driven**: nearly every file carries doctests and runs them in its `__main__` block —
   so any file can be sanity-checked with `python -m doctest <file>` before trusting it (this is how
   all ported snippets were verified).
2. **Duplicate implementations are the norm** (dijkstra ×5, BFS ×4, merge sort in 6 files) — that's
   pedagogical noise; pick the variant with the clearest docstring and ignore siblings.
3. **Docstrings can be wrong**: e.g. `rabin_karp.py` claims "O(nm)" complexity but implements a
   rolling hash (expected O(n+m)); its own test suite passes because correctness ≠ complexity claim.
   Verify any performance claim against the code, not the docstring.
4. **numpy is optional per-file**: the repo runs CI with numpy installed, so stdlib-only categories
   above are genuinely dependency-free; files in mixed categories import at module top and will fail
   without numpy — check before copying a file out of a "mixed" category.
5. **AGENTS.md exists** (repo-level agent instructions) — it restates the educational-purpose warning,
   which is why this skill treats everything as teaching material first.
