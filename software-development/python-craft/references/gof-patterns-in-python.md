---
description: "Which GoF patterns collapse into Python features (function, callable, generator, singledispatch, Enum, dataclass.replace); 19 runnable idioms, all asserted"
source_repo: faif/python-patterns (MIT catalog of patterns + its Anti-Patterns section)
tested_version: every snippet below was executed as one script of 19 asserts on Python 3.14 (stdlib only); the repo's pattern list read via GitHub API
verified_date: "2026-10-05"
---

# GoF patterns in idiomatic Python

`faif/python-patterns` catalogues ~40 patterns (creational: abstract_factory, borg, builder, factory, lazy_evaluation, pool, prototype;
structural: 3-tier, adapter, bridge, composite, decorator, facade, flyweight, front_controller, mvc, proxy; behavioral: chain_of_responsibility,
command, iterator, mediator, memento, observer, publish_subscribe, registry, servant, specification, state, strategy, template, visitor; plus
blackboard, graph_search, hsm). Its own *Anti-Patterns* section says Singleton, God Object and inheritance overuse are not recommended.

Most of the class-heavy patterns exist to work around languages without first-class functions. In Python the default move is the
smaller idiom below; reach for the full class form only when state, polymorphism over several methods, or a public plugin API demands it.
(Complements "Functions over classes" in `python-craft/SKILL.md`.)

| Pattern | Idiom | Use the class form when |
|---|---|---|
| Strategy | pass a function | the strategy has several cooperating methods or its own state |
| Command | a callable, bound with `functools.partial` | you need undo as a pair of operations |
| Observer / pub-sub / mediator | a list (or dict of topic -> list) of callbacks | you need weak references or ordering guarantees |
| Iterator | a generator function | the iterator must be restartable or expose extra state |
| Singleton | a module-level instance (modules import once) | never; inject it instead |
| Borg | rarely; shares `__dict__` across instances | you must keep per-instance identity but share state |
| Factory / abstract factory | a dict of callables or classes | construction needs many dependent steps |
| Prototype | `copy.deepcopy`, `dataclasses.replace` | |
| Decorator (the pattern) | a function decorator with `functools.wraps` | |
| Flyweight / memoised factory | `functools.cache` | |
| Visitor | `functools.singledispatch` or `match` | the traversal itself needs to be extensible by third parties |
| State | `Enum` plus a transition table | states carry behaviour that differs a lot |
| Chain of responsibility | ordered list of handlers returning `None` to pass | |
| Template method | a function taking hook callables | subclasses must share heavy state |
| Specification | composable predicates | |
| Registry | a decorator that registers into a dict | |
| Proxy / adapter / facade | a small class, `__getattr__` for delegation | |
| Memento | frozen dataclass snapshots in a list | |
| Builder | keyword arguments with defaults | |

## The snippets (all executed; asserts pass)

```python
import copy, functools, itertools
from dataclasses import dataclass, replace
from enum import Enum

# Strategy: a function.   total([100, 50], lambda p: p * 0.9) == 135.0
def total(prices, discount): return sum(discount(p) for p in prices)

# Command: partial.
cmds = [functools.partial(log.append, "a"), functools.partial(log.append, "b")]
for c in cmds: c()

# Observer: callbacks.
class Signal:
    def __init__(self): self._subs = []
    def connect(self, f): self._subs.append(f); return f
    def emit(self, *a): [f(*a) for f in list(self._subs)]      # copy so handlers may disconnect

# Iterator: generator.  list(chunks(range(5), 2)) == [[0, 1], [2, 3], [4]]
def chunks(it, n):
    it = iter(it)
    while chunk := list(itertools.islice(it, n)): yield chunk

# Prototype / Memento / Builder: frozen dataclass + replace.
@dataclass(frozen=True)
class Cfg: host: str; port: int
base = Cfg("h", 1); other = replace(base, port=2)              # base unchanged

# Flyweight: cache.   glyph("a") is glyph("a")
@functools.cache
def glyph(ch): return object()

# Visitor: singledispatch.   area(3) == 9, area((2, 5)) == 10
@functools.singledispatch
def area(shape): raise TypeError(type(shape))
@area.register
def _(shape: int): return shape * shape
@area.register
def _(shape: tuple): return shape[0] * shape[1]

# State: Enum + table.
class S(Enum): IDLE = 1; RUN = 2; DONE = 3
T = {(S.IDLE, "start"): S.RUN, (S.RUN, "finish"): S.DONE}

# Chain of responsibility.   chain([lambda r: None, lambda r: r * 2], 21) == 42
def chain(handlers, req): return next((r for h in handlers if (r := h(req)) is not None), None)

# Specification.
def both(p, q): return lambda x: p(x) and q(x)

# Registry.
REG = {}
def register(name):
    def d(f): REG[name] = f; return f
    return d

# Proxy: delegation with __getattr__ (counts reads; Proxy([3, 1, 2]).index(1) == 1).
class Proxy:
    def __init__(self, target): self._t = target; self.reads = 0
    def __getattr__(self, n): self.reads += 1; return getattr(self._t, n)

# Borg: shared state, distinct identity.
class Borg:
    _shared = {}
    def __init__(self): self.__dict__ = self._shared
```

Observed: `Borg()` instances are different objects (`a is not b`) yet `b.x` sees `a.x = 1`; a frozen dataclass `replace` leaves the
original untouched; `functools.cache` returns the identical object for equal arguments (one allocation per key) and a different one for a new key.

## Rules of thumb

- Do not write the pattern's class diagram first. Write the plain function, and promote it to a class when the second collaborating method appears.
- `functools.cache` on an instance method keeps `self` alive and caches per instance; use it on module-level functions or `lru_cache` with care for methods.
- `__getattr__` proxies intercept only missing attributes and bypass special-method lookup (`len(proxy)` does not go through it); define the dunders you need.
- God objects and deep inheritance are the real design failures the repo's anti-pattern list targets; patterns are not a cure for them.
