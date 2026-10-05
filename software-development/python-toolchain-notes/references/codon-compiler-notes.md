---
description: "Codon (exaloop) Python-to-native compiler: when it pays off, what differs from CPython, @codon.jit, CLI flags, @par, and the doc inconsistencies; Linux/macOS only"
source_repo: exaloop/codon (Apache-2.0)
tested_version: "SOURCE-READ ONLY: docs on main plus release v0.20.3 (2026-09-28) read via the GitHub API. Nothing was installed or run: releases ship Linux and macOS archives only, and this machine is Windows"
verified_date: "2026-10-05"
---

# Codon: ahead-of-time compiled Python

Codon type-checks a whole Python program ahead of time and compiles it to native code through LLVM, with no interpreter
or VM at run time. The project reports 10-100x over CPython on single-threaded numeric code (its own fib(40) table:
14.26 s on Python 3.13, 0.43 s `codon run`, 0.31 s `-release`, on an M1 MacBook), plus native multithreading and
a built-in NumPy. These are the project's own figures; none were reproduced here.

## Reach for it only when

- the hot path is **pure-Python loops over numbers, strings, lists, dicts** (primes, DP tables, parsers, simulation);
- the data is **homogeneous** (a list holds one element type) and the program can live with a 64-bit `int`.

Skip it when time goes into C-implemented libraries (NumPy calls already inside C, regex, compression), I/O or the
network: the FAQ says those see no substantial gain. When in doubt profile first (`python-debugpy`, `cProfile`),
then try `numba`/`numpy` vectorisation, which need no new toolchain.

## Platform and install

| Item | Fact |
|---|---|
| OS | Linux and macOS natively; Windows only through WSL. Release assets: `codon-{linux,darwin}-{x86_64,aarch64/arm64}` and manylinux2014 builds |
| CLI | `/bin/bash -c "$(curl -fsSL https://exaloop.io/install.sh)"` (pipes a remote script into bash: read it first) |
| Python bridge | `pip install codon-jit` (needs a Codon install; set `CODON_DIR` if it is not at the default path) |
| Licence | Apache-2.0 per the FAQ; check the LICENSE file of the version you install |
| Python used by `from python import` | set `CODON_PYTHON` to the `libpython` shared library; for a venv also `PYTHON_PATH` to its `site-packages`; for uv, `PYTHON_HOME` from `uv python find --system` |

## Where it differs from CPython (docs, "Differences with Python")

| Area | Codon |
|---|---|
| `int` | **64-bit signed**; no arbitrary precision. `Int[N]` gives wider fixed-width types. `int` and `Int[64]` became one type in v0.20, and mixed fixed-width arithmetic casts to the wider type |
| `str` | Unicode since v0.20 (older docs still say ASCII, struck through) |
| `dict` | ordered by default since v0.20; `-unordered-dict` restores the faster unordered one |
| `tuple` | compiled to a struct: length must be known at compile time, so `tuple(some_list)` is not allowed |
| Typing | whole program statically typed: no run-time monkey patching, no mixed-type collections (union types planned) |
| Numerics | some operations follow C semantics (division by zero, `math` checks). `-numerics=py|c` selects |
| Modules | most common stdlib modules have native versions; the rest via `from python import x` or `-auto-python` |
| Memory | Boehm garbage collector |

**Doc conflict:** the Differences page says numeric ops use C semantics and `-numerics=py` enforces Python's, while the
options page lists `-numerics=<py|c>` with default **`py`**. State the flag explicitly in any build you rely on, and test
integer division and division by zero on the installed version.

## Using it

```bash
codon run -release prog.py            # compile + run; default is -debug (no optimisation, backtraces)
codon run -release prog.py arg1 arg2  # args after the file
echo 'print("hi")' | codon run -release -
codon build -exe -o prog -release prog.py     # also -obj, -llvm, shared library, Python extension
```

Benchmark only with `-release`; the default build is the unoptimised debug one.

| Flag | Effect |
|---|---|
| `-release` / `-debug` | optimise, no debug info / default |
| `-disable-exceptions` | raising traps the process (SIGTRAP); removes exception paths, including NumPy bounds checks |
| `-fast-math` | LLVM fast-math: changes float semantics and assumes no `inf`/`nan` |
| `-disable-native` | do not tune to the host CPU (use for binaries shipped to other machines) |
| `-auto-python` | fall back to Python for modules Codon lacks |
| `-unordered-dict`, `-numerics=`, `-D<name>=<value>`, `-plugin`, `-log` | as described above |

## Adding it to an existing Python codebase

```python
import codon

@codon.jit                      # compiles on the first call per argument-type signature, then cached
def is_prime(n): ...

@codon.convert                  # user class -> Codon named tuple; needs __slots__
class Foo:
    __slots__ = 'a', 'b'

@codon.jit(pyvars=['helper'])   # pass a Python function/module by NAME (strings, not objects)
def bar(n): helper(n)

@codon.jit(debug=True)          # prints generated Codon code and type signature
```

- Arguments are **converted**, not shared: mutations to lists, dicts or sets inside a JIT'd function are not visible to the
  caller. Return values instead. **NumPy arrays are the exception**: the data pointer is passed through, so in-place
  edits are visible.
- Collections passed in must be homogeneous. Other objects pass as Python objects and operate through the CPython C API
  (slow, but works).
- The conversion has a cost: JIT long-running work, and put as much of the loop as possible inside the decorated function.
- Their example: 39.66 s in Python versus 1.00 s JIT'd for counting primes in 100 000-200 000 (project figure).
- `@par` inside JIT code is written `_@par`.
- The reverse direction: `from python import pandas as pd` and `@python def f() -> int:` (return type is checked and converted).

## Parallelism

```python
@par(schedule='dynamic', chunk_size=100, num_threads=16)
for i in range(2, limit):
    if is_prime(i):
        total += 1          # reduction inferred automatically for int/float
```

- OpenMP loop parallelism only for `for i in range(a, b, c)` with constant `c` (and list iteration, which is rewritten).
  Other generators become tasks.
- Parameters: `num_threads`, `schedule` (static/dynamic/guided/auto/runtime), `chunk_size`, `ordered`, `collapse`;
  `private/shared/reduction` are inferred. `OMP_NUM_THREADS` sets the default.
- Static schedules suit even iteration cost; dynamic suits uneven cost (the prime-count example).
- Shared lists and dicts need a lock or `@omp.critical`; custom reductions need a zero-value constructor plus `__add__`.
- Thread-local state: `x: threading.ThreadLocal[int] = 0`.

## Built-in NumPy

`ndarray` is typed by `dtype` and `ndim`, usually inferred; supply them when reading from disk. Contiguity matters
(`np.ascontiguousarray` after slicing or transposing). Not yet supported: string operations, masked arrays, polynomials.
ILP64 BLAS (OpenBLAS or Accelerate) is the default since v0.20. On Linux, transparent hugepages help large arrays.
GPU kernels have their own flags (`-libdevice`, `-gpu-name` default `sm_30`, `-gpu-features`, `-ptx`).

## Before adopting

1. Port the smallest hot function first, run it under Linux/macOS or WSL, and compare **output** with CPython on edge
   inputs: integers above 2^63, division by zero, negative modulo, and dict order.
2. Keep a CPython fallback for the Windows machines that cannot run it.
3. Benchmark with `-release` on the real data sizes, and against a vectorised NumPy version.
