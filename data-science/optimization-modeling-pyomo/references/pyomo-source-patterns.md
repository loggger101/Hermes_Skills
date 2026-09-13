# Design Patterns Mined from Pyomo Source (portable to any Python project)

General code knowledge extracted while reading Pyomo/pyomo at source level (2026-09-12, main branch).
Each pattern is small enough to lift verbatim; the "why" notes are what make them worth copying.

## 1. Factory registry — `pyomo/common/factory.py` (66 lines total)

The whole file: a dict of name→class plus doc strings, with two call conventions and decorator
registration:

```python
class Factory:
    def __init__(self, description=None):
        self._description = None if description is None else str(description)
        self._cls = {}
        self._doc = {}
    def __call__(self, name, **kwds):          # returns instance; unknown -> None (or ValueError with exception=True)
        ...
    def register(self, name, doc=None):         # @factory.register('name') decorator form
        def fn(cls): self._cls[name] = cls; self._doc[name] = doc; return cls
        return fn
```

Pyomo's `ModelComponentFactory` subclasses it so components register by their own class name
(`@ModelComponentFactory.register()` with no args). **Why steal this:** one importable module gives you
plugin registration, `in` membership tests (`'highs' in SolverFactory`), iteration over registered names,
and a factory-call that returns None instead of raising (callers decide whether absence is an error) —
the exact shape needed for "solver X may or may not be installed" code. The `exception=True` kwarg on
`__call__` flips to ValueError with the description in the message: one registry, two failure modes.

## 2. Config system + class-swap immutability — `pyomo/common/config.py` (~3000 lines)

Hierarchy: `ConfigValue` (one typed value) → `ConfigList` / `ConfigDict` (containers). Key mechanics
verified from source:

- **Domain as callable**: every field has a `domain=` — any callable that converts+validates and returns.
  Built-in domains include `In(set)` (membership), `IsInstance(cls)`, `ListOf(T)/SetOf(T)`, `Path` /
  `Module` (import-or-path resolution with caching). The domain is the *only* validation point — no
  scattered asserts.
- **Visibility tiers**: each field carries a `visibility=` int; template/doc generation filters by it, so
  "advanced" and "developer" options exist in one config object without separate classes.
- **`MarkImmutable(config_value)`** (verified live: blocks assignment with RuntimeError until released):

```python
locker = MarkImmutable(cfg.get('a'), cfg.get('b'))   # also usable as `with MarkImmutable(...):`
# ... any write raises RuntimeError("'a' is currently immutable") ...
locker.release_lock()
```

Implementation trick (the interesting part — it's a **runtime class swap**, not a flag):
`lock()` sets each target's `__class__ = ImmutableConfigValue`, whose `_setter` saves the old value,
attempts the write, and if the value actually changed restores the old one AND raises; on any exception
during locking, `release_lock()` runs in an except clause so a half-locked state can never persist.
Copying an immutable yields a *mutable* copy (`__new__` returns plain ConfigValue). **Why steal this:**
you get context-manager-scoped immutability with rollback safety and zero boilerplate on the value
classes themselves — useful for "freeze config during solve, allow re-tuning between phases".

## 3. Deprecation toolkit that preserves isinstance — `pyomo/common/deprecation.py`

Five tools (policy documented in `doc/OnlineDocs/explanation/developer_utils/deprecation.rst`: every
deprecation must carry a required `version=` set to the current dev version, bumped at release):

- **`RenamedClass(type)` metaclass** — verified from source: old class declares
  `__renamed__new_class__ = NewClass; __renamed__version__ = '6.0'`. The metaclass injects a warning +
  redirect in `__new__`, warns on *deriving* from the old name, and keeps **isinstance/issubclass both
  directions working** (old↔new). This is what lets Pyomo rename hundreds of classes across releases
  without breaking third-party type checks.
- **`moved_module(old_name, new_name, version=...)`** — installs a `MovedModuleFinder` at the END of
  `sys.meta_path` (last-chance finder → zero cost for normal imports) that resolves old module names to
  the new file and registers the result under BOTH names in sys.modules. The old .py file can be deleted
  entirely; the shim lives only as a one-line call in any parent package's `__init__.py`. Duck-types the
  importlib ABCs deliberately "to avoid a surprisingly costly import of importlib.abc" (comment, verbatim).
- **`relocated_module_attribute(old_path, new_path)`** — same idea for attributes inside modules.
- **`deprecated(...)` decorator + `deprecation_warning(msg, version=, remove_in=, calling_frame=...)`** —
  the warning carries which *calling frame* triggered it (via `_find_calling_frame(module_offset)`) so
  users see their own file:line, not Pyomo internals.

**Why steal this:** for any library you maintain that outlives its first API, the combo of metaclass-
redirected classes + meta_path module shims + frame-aware warnings is a complete rename/move workflow —
and it's all stdlib (importlib, types, sys).

## 4. Fast deepcopy with per-type dispatch — `pyomo/common/autoslots.py` (~480 lines)

Pyomo models are deep-copied constantly (`model.clone()`), so they replaced generic `copy.deepcopy`:
- **AutoSlots**: metaclass that auto-generates `__slots__` from the class hierarchy (with mixin support —
  `AutoSlots.Mixin`) and a custom `fast_deepcopy`.
- **Dispatch table** (verified): `_DeepcopyDispatcher(collections.defaultdict)` maps *type → specialized
  function*; `__missing__` assigns `_deepcopy_dunder_deepcopy` if the type defines one, else falls back to
  stdlib deepcopy — and caches. Specialized handlers for tuple/list/dict skip memo bookkeeping where safe:
  tuples that come out unchanged are returned as-is (matching CPython's own "don't dup unchanged tuples"
  behavior, deliberately NOT cached in the memo because it's faster not to). Self-referential list/dict
  handled by writing `memo[id]` *before* recursing into items.

**Why steal this:** if deepcopy is on your hot path (model cloning, undo stacks, graph algorithms), a
type-dispatched copy with per-container fast paths and memo-order discipline for self-references is the
standard fix — measure first though; it only pays off when you're copying many small objects.

## 5. Lazy construction semantics (core modeling)

Verified live: components are **not constructed until attached to a model** that constructs them. A
standalone `Param(default=10)` raises ValueError on evaluation ("before the Param has been constructed");
attaching it to a ConcreteModel constructs immediately; Abstract models defer everything to
`create_model()`. Indexed components take *rules* (callables of `(model, index)`) instead of values —
see the verified `Param(m.I, default=lambda m_, i: 7*(i+1))` → [14, 21, 28]. **Why steal this:** for any
data-driven generator, separating "declaration with a rule" from "instantiation over an index set" gives
you lazy evaluation, testable rules (call the lambda directly), and models whose size is decided at build
time — no metaprogramming required.

## 6. Expression safety: fail loudly on boolean contexts

Pyomo's Var/Param `__bool__` raises a **long, example-laden PyomoException** ("Cannot convert non-constant
expression to bool... usually caused by using a Var in an if statement or membership check") instead of
returning some default. Verified live: `min(3, x + 1)` dies exactly this way because the builtin evaluates
the comparison. Note the asymmetry they chose deliberately: `abs(expr)` IS overloaded (returns AbsExpression)
because abs-in-optimization is common and unambiguous; min/max are not in pyomo.environ on 6.x — you write
`Constraint(expr=min_expr...)` only if a version provides it, else model with aux vars. **Lesson:** when your
library's objects can appear where Python silently coerces to bool (dict keys, `in`, ternaries), raise an
exception whose message contains the two most common user mistakes as runnable examples — that error text is
your documentation for the failure mode nobody reads docs about.

## 7. MockMIP: fixture-replay testing for subprocess tools (`pyomo/solvers/mockmip.py`)

The mock solver's `_execute_command` never runs anything: it globs recorded files named after the input
problem file, copies `<name>.sol/.soln` to where the real solution would land (preferring .sol over .soln),
copies other artifacts back into the working dir, and reads `<name>.out` as the solver log. Every legacy
solver wrapper's parse logic is thus tested against recorded fixtures with zero external binaries — and a
missing fixture raises `ValueError("Missing mock data file")`, so an untested path fails loudly rather than
passing silently. **Portable:** for any tool you shell out to, keep per-case `.out`/`.sol`-style fixtures in
the test tree; the "executable" is 30 lines of shutil + glob.

## 8. Solver availability as a graded enum (not bool)

Verified values: `FullLicense=2 > LimitedLicense=1 > NotFound=0 > BadVersion=-1 > BadLicense=-2 >
NeedsCompiledExtension=-3`, with `bool(availability)` = "usable at all" and the name stringifying for logs.
**Lesson:** binary "is it installed?" loses exactly the information users need to act — *wrong version* vs
*no license* vs *needs a compiled extension* each have different fixes; encode them as an ordered enum whose
truthiness is "usable".

## 9. Transformation framework: apply_to + reverse tokens

Every model rewrite in Pyomo (piecewise→MIP, KKT, big-M/hull GDP reformulations, scaling...) goes through
one interface: `TransformationFactory('name').apply_to(model) -> reverse_token`; the token lets you undo or
re-derive the mapping (`get_transformation_var(original_expr)` — verified used in their own tests to find
which new var replaced an original expression). **Lesson:** when your pipeline rewrites objects, return a
token that maps old→new identities; downstream code (solution loading! results reporting!) depends on being
able to translate back. Pyomo's solution loader uses exactly this: solver returns values for *transformed*
vars, the token map writes them onto the user's original vars — which is why `solver.solve(m)` appears to
load solutions into your un-transformed model automatically in the persistent path.
