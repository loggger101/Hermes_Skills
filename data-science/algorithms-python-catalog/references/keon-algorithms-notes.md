# keon/algorithms (PyPI `algorithms` 1.0.1): oracle-checked, with the bugs it ships

Source: [keon/algorithms](https://github.com/keon/algorithms) (MIT, 25.6k stars, "minimal examples of data structures
and algorithms in Python"), PyPI package **`algorithms` 1.0.1** (Python >= 3.10), installed with
`pip install --target <scratch> algorithms` on Windows / Python 3.14.6. Every number below was run: each function was
compared to an oracle (`sorted`, `bisect`, `math`, textbook DP, brute force) on random inputs, and the package's own
docstring examples were run with `pytest --doctest-modules`. Use this repo for reading, not for importing: for production
use the stdlib (`sorted`, `bisect`, `heapq`, `math.gcd/lcm/comb`, `functools`) as the catalog's other references say.

## Layout and import traps

22 subpackages (`array backtracking bit_manipulation compression data_structures dynamic_programming graph greedy heap
linked_list map math matrix queue searching set sorting stack streaming string tree`), 400 modules and subpackages. Importing every one:
**396 import, 4 fail** with `ModuleNotFoundError: No module named 'bst'`:
`tree.bst_count_left_node`, `bst_depth_sum`, `bst_height`, `bst_num_empty` (`from bst import bst`, a leftover from the old
flat layout). `pytest --doctest-modules` therefore errors at collection unless you `--ignore` them.

- **Package-level names can be modules, not functions.** `algorithms.math.hailstone`, `.modular_inverse`, `.fft`,
  `.chinese_remainder_theorem`, `.rabin_miller` are the submodules (the package `__init__` imports them "for backward
  compatibility"), so `M.hailstone(7)` -> `TypeError: 'module' object is not callable`. Import from the submodule:
  `from algorithms.math.hailstone import hailstone`. Likewise `dynamic_programming.coin_change` is a module and the function
  is `count`.
- **Never run a script from inside the package directory** (`cd algorithms && python x.py` with `sys.path` containing it):
  `algorithms/string` and `algorithms/math` shadow the stdlib `string` and `math` (`ImportError: cannot import name
  'ascii_letters' from 'string'`).
- `can_attend_meetings` wants objects with `.start`/`.end`, not tuples (`AttributeError: 'tuple' object has no attribute
  'start'`).

## Sorting: contract table (random + edge inputs vs `sorted`)

Docstrings state each contract; the table shows what actually happens.

| Function(s) | Mutates input? | Notes measured |
|---|---|---|
| `bead_sort bitonic_sort bucket_sort counting_sort` | no, returns a new list | |
| `bubble cocktail_shaker comb cycle exchange gnome insertion merge pancake pigeonhole quick radix selection shell stooge max_heap min_heap` | **yes, in place, and also return the list** | do not rely on the original after the call |
| `bead_sort` | | non-negative ints only: negatives and floats raise `ValueError` |
| `bitonic_sort` | | **length must be a power of 2**: length 8 sorted correctly, lengths 10 and 100 raised `ValueError` (length 16 ran without error; correctness not checked) |
| `bucket_sort` | | negatives -> `IndexError`; empty list -> `ValueError`; floats -> `TypeError` |
| `counting_sort`, `pigeonhole_sort` | | handle negatives; empty list -> `ValueError`; floats/strings -> `TypeError` |
| **`radix_sort`** | | **negatives return a WRONG result with no error**; empty list -> `ValueError` |
| the comparison sorts | | correct on empty, single, dups, sorted, reversed, negatives, floats and strings |

Timing, n = 2000 random ints (`sorted` = 0.18 ms): quick 1.4, merge 2.4, counting 2.2, shell 2.6, comb 3.2, bucket 0.5,
radix 0.6, pigeonhole 0.5; selection 49, pancake 52, insertion 76, exchange 77, bubble 120, `max_heap_sort` 144,
`min_heap_sort` 174, gnome 156, cocktail 159, cycle 163, bead 246 (200 elements only), **stooge 48,077 ms**.
The "heap" sorts are O(n log n) but ~800x slower than `sorted`.

## Functions that are wrong (oracle or source confirmed)

| Function | Evidence |
|---|---|
| `tree.max_path_sum` | **0/50 correct vs brute force**: `maximum` is passed by value to the helper (a float), so the function always returns `-inf`; its own doctest `max_path_sum(TreeNode(1))` -> `1` fails |
| `stack.OrderedStack.push` | 66/100 random push sequences raised `IndexError`: `while item < self.peek() and not self.is_empty()` calls `peek()` before the emptiness check |
| `math.extended_gcd` | 10/200 correct: `quotient = old_r / r` is true division, so results are floats and wrong; its docstring even asserts `extended_gcd(13, 17) == (0, 1, 17)` (13*0 + 17*1 != gcd 1) |
| `math.lcm` | returns a float for every input (`lcm(180,163)` -> `29340.0`); values are right, type is not. `math.next_perfect_square.find_next_square(121)` -> `144.0` likewise |
| `searching.find_min_rotate_recur` | 113/300 wrong, e.g. `[29, 32, 34, 7]` -> 34 (the iterative `find_min_rotate` is 300/300 correct) |
| `searching.search_rotate_recur` | 17/300 wrong; its own doctest (`[4,5,6,7,0,1,2]`, target 0) returns -1 instead of 4 (the iterative `search_rotate` is 300/300 correct) |
| `searching.interpolation_search` | `ZeroDivisionError` on a one-element list |
| `dynamic_programming.longest_increasing_subsequence_optimized` | `IndexError` on `[0]` (the other two LIS variants and the plain one are 200/200) |
| `string.is_palindrome` | `IndexError` on `"  "` (whitespace only); the other four palindrome variants were correct over all strings up to length 4 on `aAb ,` |
| `string.knuth_morris_pratt` | `IndexError` on an empty pattern |
| `compression.elias_delta` | differs from the standard code (`delta(1)` is `1`) and from its own docstring (`'0'` expected, `'000'` returned) |

## Correct against oracles (200-300 random trials each)

`binary_search`, `jump_search`, `exponential_search`, `sentinel_search`, `linear_search`, `first_occurrence`,
`last_occurrence`, `search_insert`, `search_rotate` (iterative), `find_min_rotate` (iterative); DP: `edit_distance`,
`longest_common_subsequence` (length), two LIS variants, `max_subarray`, `climb_stairs`, `house_robber`, `num_decodings`
and `num_decodings2`, `word_break`, `cut_rod`; math: `gcd` (positives), `euler_totient`, `combination`, `factorial` and
`factorial_recur`, `modular_exponential`, `next_bigger`; string: `is_rotated`, `int_to_roman`, `group_anagrams`,
four of five palindrome variants. `gcd` matches `math.gcd` on negatives but raises `ValueError: One or more input arguments equals zero` when either
argument is 0 (6 of 300 trials in [-50, 50)), unlike `math.gcd(0, n)`.

## Doctests: 452 pass, 23 fail (4 modules uncollectable)

Of the 23 failing examples, most are the docstring that is wrong or float noise, not the code:
`minimax(2, True, [3,5,2,9])` docstring says 5, true value is `max(min(3,5), min(2,9))` = 3 and the code returns 3;
`sum_sub_squares(...,2)` docstring `[[6,6],[9,9]]` but the bottom 2x2 windows sum to 10, the code is right;
`text_justification` last line is left-justified (LeetCode 68), code right; `subsets`/`get_factors`/`find_all_cliques`
order differences; `cosine_similarity` 17th-digit float repr; `fft` prints `(4-0j)`; `invert_matrix` returns floats;
`max_common_sub_string` tie (`cd` vs `ef`). The real bugs above account for the rest
(`max_path_sum`, `OrderedStack`, `search_rotate_recur`, `lcm`, `find_next_square`, `elias_*`). Four (`solve_sat`,
`transitive_closure`, `construct_tree_postorder_preorder`, `find_all_cliques`) were not classified.

Command: `python -m pytest --doctest-modules algorithms -q -p no:cacheprovider --ignore=algorithms/tree/bst_count_left_node.py --ignore=algorithms/tree/bst_depth_sum.py --ignore=algorithms/tree/bst_height.py --ignore=algorithms/tree/bst_num_empty.py`
(run from the directory *containing* `algorithms/`).

## How to use this repo

- Read the implementation to learn a classic algorithm, then call the stdlib/`scipy`/`networkx` equivalent in code.
- If you copy a function, copy its oracle test too: the table above shows how often a clean-looking docstring example
  hides a wrong result (an in-docstring example can itself be the bug, as with `extended_gcd`).
- Prefer the iterative variants where both exist (`search_rotate`, `find_min_rotate`).
- Not run: graph, tree (except `max_path_sum`), matrix, bit_manipulation, heap, linked_list, queue, set, streaming and
  the data-structure classes (`AvlTree`, `BTree`, `SegmentTree`, `Trie`, `Fenwick_Tree`, ...).
