---
name: optimization-modeling-pyomo
description: "Model LP/MIP/NLP/GDP in Pyomo with live-verified patterns."
version: v0.1.0
author: Hermes Agent (mined from Pyomo/pyomo source, verified against 6.10.x)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [optimization, pyomo, mip, nlp, gdp, solvers, modeling]
    related_skills: [economicspace-pipeline, space-mission-computation-paradigms]
---

<!-- source: Pyomo/pyomo (COIN-OR, BSD-3-Clause) cloned + read at 2026-09-12; every behavior in this skill and its references was executed live against pyomo 6.10.2.dev0 built from that clone with highspy 1.15.1 on Windows -->

## What This Skill Does

Optimization modeling in Python via Pyomo: build LP/MIP/QP/NLP/GDP models as symbolic
components, transform them (piecewise-linear MIP reformulations, KKT duality, complementarity),
and solve with the new-style persistent solver interface. Carries two layers of knowledge mined
from the source tree:

1. **Operational patterns** — the exact import/registration/solve idiom that works on 6.x (the
   legacy `SolverFactory('glpk')` docs are stale; the V2 API is what ships now).
2. **General code/design knowledge** from Pyomo's own internals: a minimal Factory registry,
   class-swap immutability for config objects, an isinstance-preserving deprecation metaclass,
   per-type deepcopy dispatchers, lazy-construction semantics — all portable to any Python project.

## When to Use

- Modeling LP/MIP/NLP in Python where the model is data-driven (indexed over sets/rules) rather than fixed-shape
- Piecewise-linear cost/revenue functions that must stay MIP-exact (not approximated by smoothing)
- Disjunctive / logical constraints ("either this plant runs OR that one") — GDP + big-M/hull reformulations or GDPopt global solvers
- Sensitivity/duality: KKT multipliers of a solved model, complementarity conditions (LCP/MPEC)
- You need the *library design patterns* themselves (factory registry, config immutability, deprecation shims) for your own Python code — see `references/pyomo-source-patterns.md`

## Setup (one-time)

Pyomo is NOT installed in this machine's default interpreters. Use an isolated venv:

```bash
uv venv pyvenv --python 3.12 && uv pip install --python ./pyvenv/Scripts/python.exe pyomo highspy
# or from a clone (what was used for verification):
git clone https://github.com/Pyomo/pyomo.git && uv pip install --python ./pyvenv/Scripts/python.exe /path/to/pyomo
```

`highspy` is the only solver needed to verify everything in this skill — HiGHS covers LP/MIP/QP,
ships a Windows wheel, and Pyomo's new-style interface wraps it persistently. (Verified: pip
install + full MIP solve on Windows 11 / Python 3.12.)

## Quick Reference (canonical V2 solve pattern)

```python
import pyomo.contrib.solver.plugins            # REQUIRED side-effect import: registers solvers in the factory
from pyomo.contrib.solver.plugins import Highs, SolverFactory   # or any registered name via SolverFactory('highs')
from pyomo.environ import ConcreteModel, Var, Constraint, Objective, RangeSet, Binary, maximize

m = ConcreteModel()
m.I = RangeSet(3)
m.x = Var(m.I, within=Binary)
m.o = Objective(expr=5*m.x[1] + 4*m.x[2] + 3*m.x[3], sense=maximize)
m.c = Constraint(expr=sum(m.x[i] for i in m.I) <= 2)

solver = Highs()                                # persistent: keeps a live solver model across solves
res = solver.solve(m)                           # solution is written straight back into m's vars (no load step)
print(res.termination_condition.name)           # 'convergenceCriteriaSatisfied'
print(res.solution_status.name)                 # 'optimal'
print(res.incumbent_objective)                  # 9.0 for the model above — verified live
```

Verified component counts after piecewise transforms (4 breakpoints, univariate): see
`references/formulations-and-algorithms.md`. FBBT bound tightening: `from pyomo.contrib.fbbt.fbbt import fbbt; fbbt(model)`
(note the double module path — `pyomo.contrib.fbbt` alone is a package).

## Key patterns (details in references)

- **Piecewise-linear MIP reformulations** (`contrib.piecewise.incremental | convex_combination | multiple_choice`, plus nested-inner-repn for log-many binaries): binary/variable/constraint counts measured live, when each formulation wins. → `references/formulations-and-algorithms.md`
- **GDPopt global solvers** (LOA/GLOA/LD-SDA/RIC/LBB) and which are exact vs heuristic; FBBT two-pass bound propagation algorithm with its worked example; KKT transformation output anatomy (`core.kkt` adds `kkt.alpha[i]` multipliers + stationarity constraints); MPEC complementarity standard-form rules. → same reference
- **Library design patterns worth stealing**: 66-line Factory registry, ConfigDict/ConfigValue + MarkImmutable (class-swap immutability with rollback), RenamedClass deprecation metaclass that preserves isinstance, moved_module importlib shims, autoslots per-type deepcopy dispatcher, MockMIP recorded-output solver testing. → `references/pyomo-source-patterns.md`

## Pitfalls

1. **Forgetting the plugins side-effect import.** `from pyomo.contrib.solver import Highs` fails;
   solvers register only when `pyomo.contrib.solver.plugins` is imported (or a plugin module directly).
2. **V1 vs V2 results API.** New-style `Results` has `.termination_condition`, `.solution_status`,
   `.incumbent_objective` — there is NO `.problem_info` attribute on it (that's the legacy wrapper);
   code copied from old tutorials raises AttributeError.
3. **Builtins on expressions are a trap.** `abs(expr)` works (returns `AbsExpression`) because Pyomo
   overloads it, but `min(a, expr)`, `max(...)`, and any boolean context (`if x >= 1:`) raise
   `PyomoException: Cannot convert non-constant expression to bool` — builtins evaluate the
   comparison. Write relational expressions inside `Constraint(expr=...)` instead; there is no
   `min_expr`/`max_expr` in `pyomo.environ` on 6.x.
4. **Unattached components are not constructed.** A standalone `Param(default=10)` raises ValueError
   if evaluated before it's attached to a model (lazy construction); attaching to a ConcreteModel
   constructs immediately. Abstract models defer everything until `model.create_model()`.
5. **Transformation objects aren't callable** — use `TransformationFactory('name').apply_to(model)`,
   not the factory result directly; and transform configs reject unknown kwargs (`keep_originals` is
   NOT a generic kwarg on contrib transforms).
6. **Complementarity standard form demands exactly two finite bounds** across both complemented
   expressions, and both sides must be relational (a bare expression side raises RuntimeError).

## Verification

```python
# the 57-second smoke test — every line below was executed live against pyomo 6.10.2.dev0 + highspy 1.15.1:
import warnings; warnings.filterwarnings("ignore")
from pyomo.environ import ConcreteModel, Var, Objective, Constraint, Binary, RangeSet, value, maximize
m = ConcreteModel(); m.I = RangeSet(3); m.x = Var(m.I, within=Binary)
m.o = Objective(expr=5*m.x[1]+4*m.x[2]+3*m.x[3], sense=maximize)
m.c = Constraint(expr=sum(m.x[i] for i in m.I) <= 2)
import pyomo.contrib.solver.plugins as P; from pyomo.contrib.solver.plugins import Highs
res = Highs().solve(m)
assert res.solution_status.name == "optimal" and abs(res.incumbent_objective - 9.0) < 1e-9
assert [round(value(v), 3) for v in m.x.values()] == [1.0, 1.0, 0.0]   # solution loaded back into model vars
```
