---
description: "z3-solver 5.1.0 run on Python 3.14: result handling, Int vs BitVec vs Real semantics, Python-operator traps, timeouts, unsat cores, Optimize unbounded, enumeration, pigeonhole scaling"
source_repo: Z3Prover/z3 (MIT)
tested_version: "z3-solver 5.1.0 (release 2026-08-16) installed from PyPI into a uv Python 3.14 venv on Windows (21 MB); about 35 one-call checks in one script. Complements the API-name corrections in astro-toolkit-selection/references/optimization-toolkit.md"
verified_date: "2026-10-05"
---

# Z3 (z3-solver 5.1.0) from Python

Z3 answers "is there an assignment satisfying these constraints?" exactly, or proves there is none. Use it for scheduling and
configuration puzzles, bit-level reasoning, and checking invariants; use Pyomo/HiGHS-style solvers for large linear or
mixed-integer optimisation with objectives. Install: `pip install z3-solver`, `import z3`.

## Results and models

| Call | Result |
|---|---|
| `s.check()` | a `CheckSatResult` printing `sat` / `unsat` / `unknown`; `s.check() == sat` is a real boolean |
| `s.model()` after `unsat`, or before any `check()` | **`Z3Exception: model is not available`**; always test the result first |
| Variable the model never constrained | `m.eval(y)` returns the symbolic `y`; `m.eval(y, model_completion=True)` gives a concrete `0` |
| Enumerating all solutions | `while s.check() == sat: v = s.model()[x].as_long(); out.append(v); s.add(x != v)` gave `[1, 2, 3]` for `0 < x < 4` |
| `Optimize.maximize` on an unbounded objective | `check()` still returns **`sat`** and `upper(h)` is **`oo`**; test the bound, not just the status |
| `Optimize` with `y == 2*x, 1 <= x <= 10`, maximise `y` | model `x = 10`, `upper = 20` |

## Sorts change the arithmetic

| Case | Result |
|---|---|
| `BitVec('a', 8)`: `a + 1 == 0` | `a = 255` (wraps); `Int`: `x + 1 == 0` gives `x = -1` |
| `b > 127` on an 8-bit vector | **`unsat`**: `>` is **signed**, so max is 127; use `UGT(b, 127)` (found 128). Likewise `ULT`, `UDiv`, `URem`, `LShR` for unsigned |
| `simplify(IntVal(-7) / 2)` and `IntVal(-7) % 2` | `-4` and `1` (floor-style, same as Python for a positive divisor) |
| `x / 2` where `x` is `Int` | stays **`Int`** (integer division), not a Real |
| `Real` `1/3 + 1/3 + 1/3 == 1` | proved (negation is `unsat`): reals are exact rationals |
| `Real('r') == 0.1` | model `r = 1/10`: a Python float is converted through its decimal text, **not** its binary IEEE value; use `FP`/`Float64()` for IEEE reasoning |

## Python operators that fail or mislead

- `(x > 0) and (x < 3)` and `bool(x > 0)` raise **`Z3Exception: Symbolic expressions cannot be cast to concrete Boolean values`**.
  Use `And(...)`, `Or(...)`, `Not(...)`, `Implies(...)`; `And` / `Or` accept varargs or a list; `Distinct(a, b, c)` exists.
- `x == y` builds an expression (printed `x == y`), it does not compare Python objects. Use `eq(a, b)` for structural identity and
  `is_true(simplify(e))` to test a closed expression.

## Control: timeouts, scopes, cores

| Feature | Observed |
|---|---|
| `s.set("timeout", 300)` on a nonlinear Fermat-style constraint (`p^3 + q^3 == r^3`, all > 1) | `unknown`, `s.reason_unknown() == 'timeout'` after 0.31 s. Always set a timeout and branch on `unknown` |
| `push()` / `pop()` | inner `x>0, x<0` was `unsat`; after `pop()` the solver was `sat` again |
| `s.check(p1, p2)` with `Implies(p1, x>5)`, `Implies(p2, x<3)` | `unsat`, `unsat_core()` = `[p2, p1]` (an unordered subset) |
| `s.set(unsat_core=True)` + `assert_and_track(c, "name")` | core `[gt5, lt3]` by name |
| Quantifier `ForAll([x], f(x) > x)` with `f(0) <= 0` | `unsat`; proving `ForAll x: x*x >= 0` by asserting its negation also gave `unsat` (a proof) |
| Arrays, strings | `Store(A,1,5)[1] != 5` is `unsat`; `Length(S)==3, PrefixOf("ab", S)` gave `"abA"` |
| Interchange | `solver.to_smt2()` emits SMT-LIB 2 text; `parse_smt2_string("(declare-const z Int)(assert (> z 2))")` returns `[z > 2]`; `expr.sexpr()` prints `(+ x 1)` |

## Scaling sanity check

Propositional pigeonhole (n+1 pigeons into n holes, `unsat`): 8 into 7 took 0.02 s; **10 into 9 took 1.25 s**, and the cost
grows steeply with n. Symmetric combinatorial problems can blow up even when tiny, so add symmetry-breaking constraints and a
timeout.

## Habits

1. Check `check()` before `model()`; treat `unknown` as a third outcome with a reason.
2. Choose the sort deliberately (`Int` for unbounded maths, `BitVec(n)` for machine words, `Real` for exact rationals, `FP` for IEEE).
3. Prove a property by asserting its negation and expecting `unsat`; keep the model of `sat` as a counterexample.
4. Use assumptions/`unsat_core` to explain infeasible configurations rather than bisecting by hand.

Not run: `FP` conversions (covered live in `optimization-toolkit.md`), `Fixedpoint`/Horn clauses, tactics and `SimpleSolver`, `z3 -smt2`
command line, parallel solving, memory limits.
