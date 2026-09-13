#!/usr/bin/env python3
"""Live-verify the Pyomo patterns documented in this skill.

Requires an isolated env with pyomo + highspy (NOT installed on default interpreters here):
    uv venv pyvenv --python 3.12 && uv pip install --python ./pyvenv/Scripts/python.exe pyomo highspy

Verified end-to-end 2026-09-12 against pyomo 6.10.2.dev0 (built from a fresh Pyomo/pyomo clone)
+ highspy 1.15.1 on Windows / Python 3.12: every check below printed the expected value.

Exit code 0 = all checks passed; nonzero with the failing name printed otherwise.
"""
import math
import sys
import warnings

warnings.filterwarnings("ignore")


def main() -> int:
    failures = []

    def check(name, cond, detail=""):
        status = "ok" if cond else "FAIL"
        print(f"[{status}] {name} {detail}")
        if not cond:
            failures.append(name)

    # ---------- 1) V2 persistent HiGHS solve (MIP), solution written back into model vars ----------
    from pyomo.environ import ConcreteModel, Var, Objective, Constraint, RangeSet, Binary, value, maximize, NonNegativeReals
    m = ConcreteModel()
    m.I = RangeSet(3)
    m.x = Var(m.I, within=Binary)
    m.o = Objective(expr=5*m.x[1] + 4*m.x[2] + 3*m.x[3], sense=maximize)
    m.c = Constraint(expr=sum(m.x[i] for i in m.I) <= 2)

    import pyomo.contrib.solver.plugins as P  # noqa: F401 - REQUIRED side-effect import (registers solvers)
    from pyomo.contrib.solver.plugins import Highs, SolverFactory
    check("factory_registered_names", "highs" in iter(SolverFactory))
    solver = Highs()
    avail = solver.available()
    check("highs_availability_enum", str(avail) == "FullLicense", f"(got {avail})")
    res = solver.solve(m)
    check("mip_termination", res.termination_condition.name == "convergenceCriteriaSatisfied",
          f"(got {res.termination_condition.name})")
    check("mip_optimal_obj_9", abs(res.incumbent_objective - 9.0) < 1e-9,
          f"(got {res.incumbent_objective})")
    check("solution_loaded_back_into_model_vars",
          [round(value(v), 3) for v in m.x.values()] == [1.0, 1.0, 0.0],
          f"({[value(v) for v in m.x.values()]})")

    # ---------- 2) Piecewise formulations: measured binary/var/constraint counts (4 breakpoints) ----------
    from pyomo.contrib.piecewise import PiecewiseLinearFunction
    from pyomo.core.base import TransformationFactory as TF

    def build():
        mm = ConcreteModel()
        mm.xv = Var(within=NonNegativeReals, bounds=(0, 9))
        mm.pw = PiecewiseLinearFunction(points=[0, 1, 3, 6, 9], function=lambda t: math.log(t + 1))
        mm.o = Objective(expr=mm.xv - 0.2*mm.pw(mm.xv), sense=maximize)
        return mm

    expected = {
        "contrib.piecewise.incremental": (3, None, None),       # binaries exact; vars/cons > measured min
        "contrib.piecewise.convex_combination": (4, None, None),
        "contrib.piecewise.multiple_choice": (4, None, None),
    }
    for name in expected:
        mm = build()
        TF(name).apply_to(mm)
        nb = sum(1 for v in mm.component_data_objects(Var, active=True) if v.is_binary())
        nv = len(list(mm.component_data_objects(Var, active=True)))
        nc = len(list(mm.component_data_objects(Constraint, active=True)))
        check(f"pw_{name.split('.')[-1]}_binaries", nb == expected[name][0], f"(got {nb} binaries; vars={nv}, cons={nc})")

    # ---------- 3) FBBT bound tightening: x*y + z == 1, x in [-1,1], y in [-2,2] -> z in [-1,3] ----------
    from pyomo.contrib.fbbt.fbbt import fbbt as _fbbt
    m4 = ConcreteModel()
    m4.x = Var(bounds=(-1, 1))
    m4.y = Var(bounds=(-2, 2))
    m4.z = Var(bounds=(None, None))
    m4.c = Constraint(expr=m4.x * m4.y + m4.z == 1)
    _fbbt(m4)
    check("fbbt_tightens_z_to_-1_3", (m4.z.lb or -math.inf) == -1 and m4.z.ub == 3,
          f"(got lb={m4.z.lb}, ub={m4.z.ub})")

    # ---------- 4) MarkImmutable config semantics: blocks writes until released ----------
    from pyomo.common.config import ConfigDict, ConfigValue, MarkImmutable
    cfg = ConfigDict()
    cfg.declare("a", ConfigValue(default=1, domain=int))
    locker = MarkImmutable(cfg.get("a"))
    blocked = False
    try:
        cfg.a = 5
    except RuntimeError:
        blocked = True
    check("markimmutable_blocks_assignment", blocked)
    locker.release_lock()
    cfg.a = 8
    check("markimmutable_writable_after_release", cfg.a == 8, f"(got {cfg.a})")

    # ---------- 5) KKT transformation adds multipliers + stationarity constraint ----------
    m5 = ConcreteModel()
    m5.x = Var(bounds=(0, None))
    m5.o = Objective(expr=m5.x**2 - 4*m5.x)
    m5.c1 = Constraint(expr=m5.x >= 1)
    blk = m5.clone()
    TF("core.kkt").apply_to(blk)
    kkt_vars = [v.local_name for v in blk.component_data_objects(Var, active=True)]
    check("kkt_adds_alpha_multipliers", "alpha[1]" in kkt_vars and "alpha[2]" in kkt_vars, f"({kkt_vars})")

    # ---------- 6) Availability enum values (graded availability, not bool) ----------
    from pyomo.contrib.solver.common.base import Availability
    check("availability_enum_values",
          {a.name: a.value for a in Availability} ==
          {"FullLicense": 2, "LimitedLicense": 1, "NotFound": 0,
           "BadVersion": -1, "BadLicense": -2, "NeedsCompiledExtension": -3})

    # ---------- summary ----------
    if failures:
        print(f"\nFAILED: {failures}")
        return 1
    print("\nAll Pyomo pattern checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
