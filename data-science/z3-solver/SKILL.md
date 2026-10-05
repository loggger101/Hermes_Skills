---
name: z3-solver
description: "Z3 SMT from Python: sat/unsat handling, sorts, traps."
version: 1.0.0
author: Hermes Agent (promoted from optimization-modeling-pyomo references, run live 2026-10-05)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [z3, smt, sat, constraint-solving, bitvector, verification, scheduling, unsat-core]
    related_skills: [optimization-modeling-pyomo, python-numerics-gotchas, property-based-testing, bit-identity-float-pipelines]
---

# Z3 SMT solving from Python

## What This Skill Does

Z3 answers "is there an assignment that satisfies these constraints?" exactly, or proves there is none. This skill holds the behaviour of `z3-solver` 5.1.0 on Python 3.14 (about 35 one-call checks): how results and models behave, how `Int`, `BitVec`, `Real` and `FP` differ, which Python operators fail, how to use timeouts and unsat cores, and where cost blows up.

## When to Use

- Scheduling, configuration or puzzle constraints with a yes/no or find-one answer
- Bit-level reasoning (overflow, signedness) and checking invariants or equivalences by asserting the negation
- Explaining why a configuration is infeasible (unsat core)
- Not for large linear or mixed-integer optimization with objectives (`optimization-modeling-pyomo`), or randomized property checks (`property-based-testing`)

## Procedure

1. `pip install z3-solver`, `from z3 import *`. Create a `Solver()`, `add` constraints, call `check()`.
2. Branch on all three outcomes: `sat`, `unsat`, `unknown` (read `s.reason_unknown()`); only call `s.model()` after `sat`. Set a timeout first: `s.set("timeout", 300)`.
3. Pick the sort deliberately: `Int` for unbounded maths, `BitVec(n)` for machine words, `Real` for exact rationals, `FP`/`Float64()` for IEEE.
4. To prove a property, assert its negation and expect `unsat`; a `sat` model is the counterexample.
5. To explain infeasibility, use assumptions: `s.check(p1, p2)` then `s.unsat_core()`, or `s.set(unsat_core=True)` with `assert_and_track(c, "name")`.
6. To enumerate solutions, loop `while s.check() == sat:` and add `x != value` each time.
7. Break symmetry and time-limit combinatorial problems before scaling them.

## Traps (all observed)

- `s.model()` after `unsat` or before `check()` raises `Z3Exception: model is not available`.
- An unconstrained variable evaluates to itself unless `m.eval(y, model_completion=True)`.
- `Optimize.maximize` on an unbounded objective still returns `sat` with `upper = oo`; test the bound.
- `BitVec` `>` is **signed**: `b > 127` on 8 bits is `unsat`; use `UGT`, `ULT`, `UDiv`, `URem`, `LShR` for unsigned.
- `Int` division stays `Int`; `Real('r') == 0.1` becomes exactly 1/10 (decimal text), not the IEEE value.
- Python `and`, `or`, `bool(x > 0)` raise `Symbolic expressions cannot be cast to concrete Boolean values`: use `And`, `Or`, `Not`, `Implies`, `Distinct`. `==` builds an expression; use `eq(a, b)` for structural identity.
- Pigeonhole 10 into 9 took 1.25 s (8 into 7: 0.02 s); symmetric combinatorial problems explode.
- Nonlinear Fermat-style constraints return `unknown` with reason `timeout`.

## Pitfalls

- Treating `unknown` as `unsat`.
- Mixing `Int` and `BitVec` reasoning for overflow questions: the arithmetic differs.
- Not run in these notes: `Fixedpoint`/Horn clauses, tactics, the `z3 -smt2` command line, parallel solving, memory limits; FP conversions are covered in `astro-toolkit-selection/references/optimization-toolkit.md`.

## Verification

- [ ] Every `check()` result is branched on, including `unknown`
- [ ] A timeout is set for anything non-trivial
- [ ] Properties are proven by an `unsat` negation, with the counterexample model kept
- [ ] The sort matches the semantics you need (signedness, wrap-around, exactness)

## References

- `references/z3-solver-notes.md` - z3-solver 5.1.0 on Python 3.14: result and model handling, sorts and their arithmetic, Python-operator traps, timeouts, scopes, unsat cores, quantifiers, arrays and strings, SMT-LIB interchange, pigeonhole scaling
