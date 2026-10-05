# NumPy 2.5.2: promotion, overflow, removed names, Windows dtypes (run live)

Source: [numpy/numpy](https://github.com/numpy/numpy) (BSD-3). **numpy 2.5.2**, Python 3.14.6, Windows (x86-64, little endian).
About 130 calls in two probe scripts (the first leaked an `np.errstate("raise")` into later lines; those were re-run cleanly,
and only the clean results are quoted). Run with `-W error` to turn the silent-wrap warnings below into failures.

## 1. Promotion follows NEP 50 (the Python scalar adopts the array dtype)

| Expression | Result |
|---|---|
| `np.array([200], uint8) + 100` | `array([44], uint8)`: wraps **silently** for arrays |
| `np.uint8(200) + 100` | `np.uint8(44)` with `RuntimeWarning: overflow encountered in scalar add` (scalars warn, arrays do not) |
| `np.array([200], uint8) + 300`, `int8 array + 200` | `OverflowError: Python integer 300 out of bounds for uint8` (the Python int must fit the array dtype) |
| `np.array([1, 2], int8) * 100` | `[100, -56]`, silent |
| `np.abs(np.array([-128], int8))` | `-128`, silent |
| `np.int32(2**31 - 1) + np.int32(1)` | `-2147483648` with the scalar overflow warning |
| `np.int32(2**31)` | `OverflowError: Python int too large to convert to C long` (on Windows a C long is 32 bit) |
| `float32 scalar + 1.0` | `float32`; `float32 + float64` -> `float64`; `int64 array * 1.5` and `array / 2` -> `float64` |
| `uint64 + int64` | **`float64`** (no integer dtype holds both; precision loss above 2**53) |
| `np.array([2**63])` / `np.array([2**64])` | `uint64` / `object` |
| `np.array([True, 2])` / `np.array([1, 'a'])` | `int64` / `<U21` (everything becomes a string) |
| `np.array([[1, 2], [3]])` | `ValueError: ... inhomogeneous shape after 1 dimensions`; `dtype=object` gives shape `(2,)` |

`sum` of an int8 array `[100, 100]` returns `np.int64(200)` (reductions widen), `mean` returns float64 100.0.
Casts: `array([-1.0, 256.0, 3.7]).astype(np.uint8)` -> `[255, 0, 3]` (platform-defined wrap, no warning);
`array([nan, 1e30]).astype(np.int64)` -> `[-9223372036854775808, -9223372036854775808]` with `RuntimeWarning: invalid value
encountered in cast`. Use `np.clip` before casting, and `np.errstate(all="raise")` to make floating faults raise.

## 2. Windows integer widths

`np.dtype(int)`, `np.int_`, `np.intp` and `np.array([1,2]).dtype` are **int64** in NumPy 2, but `np.dtype("l")`, `"long"`,
`np.long` and `np.ulong` are **4 bytes** on Windows (`np.zeros(3, "l").dtype` -> `int32`, `np.dtype("long") == np.int64` False)
and `np.dtype("i")` is int32. Code ported from Linux that says `dtype="l"`, or `np.long`, silently halves the width.
`np.array([2**31])` is int64. Prefer explicit `np.int64`/`np.int32`.

## 3. Names that no longer exist (hasattr on 2.5.2)

Removed: `float_ complex_ bool8 object0 str0 unicode_ string_ in1d trapz product cumproduct sometrue alltrue row_stack round_
asfarray find_common_type cast`. Present: `trapezoid`, `vstack`, `round`, `int_`, `long`, `ulong`. `np.trapz` raises
`AttributeError`; `np.trapezoid([0,1,4], dx=1)` = 3.0. Newer additions that work: `np.vecdot`, `np.matvec`, `np.unique_counts`
(`([1, 3], [1, 2])`), `np.cumulative_sum`, `np.strings.upper`, `np.dtypes.StringDType`. Touching `np.object` emits a
`FutureWarning` ("will be defined as the corresponding NumPy scalar").

## 4. Copies, views and the `copy=` keyword

- `np.array(a, copy=False)` is now "never copy": it works when `a` is already an array but raises
  `ValueError: Unable to avoid copy while creating an array as requested. If using np.array(obj, copy=False) replace it with
  np.asarray(obj)` for a list; **`np.asarray([1,2], copy=False)` raises too**. Use `np.asarray(obj)`, or `copy=None` for
  "copy only if needed" (it shared memory with an existing array).
- `arange(6).reshape(2,3).T.reshape(6, copy=False)` -> `ValueError: Unable to avoid creating a copy while reshaping`.
- Slices are views (`a[::2][0] = 99` changed `a`); fancy indexing copies. `x[[0,0,1]] += 1` -> `[1, 1, 0]` (buffered, repeats
  count once); `np.add.at(x, [0,0,1], 1)` -> `[2, 1, 0]`.
- `.view(np.int16)` on `int32 [0, 1]` -> `[0, 0, 1, 0]` (little endian).

## 5. Floating point

- `np.errstate(all="raise")` as a **context manager** turns `1.0/0` into `FloatingPointError: divide by zero`; entered without
  exiting (my first probe) it leaks into every later call. Defaults: `{'divide': 'warn', 'over': 'warn', 'under': 'ignore',
  'invalid': 'warn'}`.
- Integer division by zero: `np.array([1]) // 0` and `0 // 0` return `[0]` with only a `RuntimeWarning`.
- `np.max([1, nan])` is `nan`, `nanmax` is 1.0, but `argmax([1, nan, 3])` is **1** (nan wins). `np.mean([])` is `nan` with two warnings;
  `np.max([])` raises `ValueError: zero-size array to reduction operation maximum which has no identity`.
- `nan == nan` False; `np.unique([nan, nan, 1])` -> `[1.0, nan]` (merged); `array_equal([nan],[nan])` False, `equal_nan=True` True.
- **`np.cumsum` of 2**25 float32 `0.1` ends at 2,097,152 while `.sum()` gives 3,355,443.8 and the truth is 3,355,443.2**: cumulative sums
  stall once the running total dwarfs the increment; pairwise `sum` does not. Use float64 for accumulations.
- `np.round([0.5, 1.5, 2.5, -0.5])` -> `[0, 2, 2, -0]` (half to even); `np.round(2.675, 2)` -> 2.68 but Python `round(2.675, 2)` -> 2.67.
- `arange(0, 1, 0.1)` has 10 elements, `arange(0.1, 0.4, 0.1)` -> `[0.1, 0.2, 0.30000000000000004, 0.4]` (4 items, includes 0.4);
  use `linspace` for a known count. `isclose(1e-9, 0)` True (atol 1e-8) but `isclose(0, 1e-9, rtol=0)` also True: set `atol` for small scales.
- `np.linalg.cond([[1,1],[1,1+1e-12]])` is 4.0e12; `inv(zeros((2,2)))` -> `LinAlgError: Singular matrix`.
- Printing: `str(np.array([1/3, 1e-10, 1e10]))` -> `[3.33333333e-01 1.00000000e-10 1.00000000e+10]`. Scalars repr as
  `np.float64(1.5)` (was `1.5`), `str()` stays `1.5`: **doctests and string comparisons on `repr` broke in NumPy 2**.

## 6. Strings, I/O, serialisation

- `np.array(["a","bb"]).dtype` is `<U2`; assigning a longer string truncates silently (`['xx','yy'][0] = 'abcdef'` -> `'ab'`).
  `np.array(["a", None])` is `object`. `StringDType(na_object=None)` holds `['a', 'bb', None]`; `np.strings.*` and the older `np.char.*` both work.
- `np.fromstring("1 2 3", sep=" ")` works; binary mode is gone (`ValueError: The binary mode of fromstring is removed, use
  frombuffer instead`). `np.frombuffer(b"\x00\x00\x00\x01", dtype=">i4")[0]` is 1; `np.dtype(">i4") == np.dtype("<i4")` False.
- `np.load` refuses pickled object arrays by default: `ValueError: Object arrays cannot be loaded when allow_pickle=False`
  (save with `allow_pickle` only for trusted files).
- **`json.dumps` fails on numpy ints and arrays** (`TypeError: Object of type int64 is not JSON serializable`) but accepts
  `np.float64` (a float subclass): convert with `.item()` / `.tolist()`.

## 7. Random

`np.random.default_rng(42)`: `integers(0, 10, 5)` -> `[0, 7, 6, 4, 4]`, `random(2)` -> `[0.6974, 0.0942]`; the legacy
`np.random.seed(42); randint(0, 10, 5)` -> `[6, 3, 7, 4, 6]` (a different stream). `integers(0, 3)` never returns 3 (high exclusive);
`choice(3, 5, replace=False)` -> `ValueError: Cannot take a larger sample than population`. Equal seeds give equal streams;
`rng.spawn(2)` yields independent child generators.

## 8. Timing (2,000,000 float64)

`v.sum()` 2.5 ms, Python `sum(list)` 29.5 ms, list comprehension `x*2` 221 ms vs `v*2` 9.8 ms, and `np.vectorize` on only
200,000 items 54 ms (it is a Python loop, not vectorisation).

Not covered: `np.ma`, structured and datetime64 dtypes, `einsum`, `np.fft`, free-threaded builds, and GPU array-API libraries.
