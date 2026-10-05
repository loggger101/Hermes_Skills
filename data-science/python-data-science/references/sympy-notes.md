---
description: "sympy 1.14.0 for derivations feeding numeric code: exactness traps (Float vs Rational, nsimplify), equality, solve return shapes, lambdify broadcasting; run live"
source_repo: sympy/sympy (BSD-3-Clause)
tested_version: sympy 1.14.0 + numpy 2.5.3 pip --target on Windows py3.14; one probe script, outputs quoted
verified_date: "2026-10-05"
---

# sympy: symbolic maths for derivations that end up as numeric code

Use sympy to derive, simplify and verify formulas (closed-form delta-v terms, Jacobians, series), then **generate the numeric function with `lambdify`** instead of retyping the result. Python-only, BSD-3-Clause.

## Exactness traps (all reproduced)

| Expression | Result | Lesson |
|---|---|---|
| `0.1 + 0.2` | `0.30000000000000004` | plain Python floats leak into sympy expressions |
| `sp.Rational(1,10) + sp.Rational(2,10)` | `3/10` | use `Rational`/`Integer` for exact work |
| `sp.sympify("0.1")` | a `Float` (not `1/10`) | parsing a decimal string gives a Float; use `sp.Rational("0.1")` (`== 3/10` held for the sum) |
| `1/3` vs `sp.Integer(1)/3` | `0.333...` vs `1/3` | a Python-int division happens before sympy sees it; wrap an operand |
| `nsimplify(0.333333333)` | `1/3` | rationalises approximate floats: convenient, but it also **hides** a real 1e-10 difference; pass a tolerance deliberately |
| `nsimplify(0.1 + 0.2)` | `3/10` | the float error is "repaired" silently |
| `float(sp.sqrt(2))` vs `sp.N(sp.sqrt(2), 50)` | `1.4142135623730951` vs 50 digits | `N(expr, digits)` for high precision; `float()` is double |

## Equality, simplification, assumptions

- `==` is **structural**: `(x+1)**2 == x**2 + 2*x + 1` is `False`; `sp.expand(lhs) == rhs` or `sp.simplify(lhs - rhs) == 0` are `True`. Use the latter for "is this identity right".
- `simplify(sin(x)**2 + cos(x)**2)` returns `1`; `series(sin(x), x, 0, 6)` gives `x - x**3/6 + x**5/120 + O(x**6)`; `limit(sin(x)/x, x, 0)` = `1`; `integrate(exp(-x**2), (x, 0, oo))` = `sqrt(pi)/2`.
- **Assumptions change answers**: `sqrt(n**2)` stays `sqrt(n**2)` for a plain symbol but becomes `p` for `Symbol("p", positive=True)`. Declare `positive=True`, `real=True`, `integer=True` where the physics says so, or simplification will refuse or be wrong.
- Cost: `expand((x+y+1)**14)` took 0.02 s (120 terms); `simplify(expand((x+y+1)**8))` took 0.12 s. `simplify` can be slow on big expressions; prefer targeted `expand`, `factor`, `cancel`, `trigsimp`.

## solve, nsolve

- A list of equations returns a **dict** `{x: 2, y: 1}` by default; `dict=True` returns a list of dicts `[{x: 2, y: 1}]`: always pass `dict=True` so downstream code has one shape.
- `solve(x**2 - 2, x)` gives `[-sqrt(2), sqrt(2)]`. A quintic without a closed form (`x**5 - x - 1`) returns `CRootOf(...)` objects (exact root descriptors), not numbers: use `nsolve(x**5 - x - 1, x, 1.2)` for the numeric root (`1.16730397826142`) with a good starting value.

## lambdify (the bridge to NumPy)

```python
f = sp.lambdify(x, sp.sin(x)**2 + x, "numpy")
f(np.array([0.0, 1.0, 2.0]))          # -> [0.0, 1.7081, 2.8268]
```

- `lambdify(x, Integer(5), "numpy")(np.array([1.0, 2.0]))` returned the **scalar `5`**, not an array: a constant expression does not broadcast. Wrap with `np.broadcast_to` or `np.full_like(x, f(x))` when the result must match the input shape.
- With the default module and an integer array, `lambdify(x, x**2)(np.array([1, 2, 3]))` gave `[1, 4, 9]` (integers preserved): cast inputs to float when you expect float arithmetic.
- Specify `"numpy"` (or `"scipy"`, `"math"`) explicitly; the generated code uses that module's functions.
- Matrices: `Matrix([[1,2],[3,4]]).inv()` is exact (`[[-2, 1], [3/2, -1/2]]`, `det = -2`); the same matrix with float entries returns `Float` entries printed with 15 digits: stay exact until the numeric step.

## Workflow

1. Derive with exact symbols and assumptions; 2. verify identities with `simplify(a - b) == 0` and spot-check numerically against an independent implementation (see `orbital-mechanics-data`);
3. `lambdify` to NumPy for evaluation; 4. record the sympy version, since simplification output can change between releases (relevant to `bit-identity-float-pipelines`); do not paste long auto-simplified expressions into code you must audit.
