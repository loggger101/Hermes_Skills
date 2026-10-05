---
description: "num_enum 0.7.6 (Rust): derive macros for enum <-> integer conversion (IntoPrimitive, TryFromPrimitive, FromPrimitive, UnsafeFromPrimitive), attributes, features; plus the Python IntEnum analogue run live on 3.14"
source_repo: illicitonion/num_enum (BSD-3-Clause OR MIT OR Apache-2.0)
tested_version: README read via GitHub API + crates.io API (0.7.6, 2026-03-15); NOT compiled (no Rust toolchain here). The Python IntEnum analogue was run on Python 3.14.6 / Windows
verified_date: "2026-10-05"
---

# num_enum: safe conversion between `#[repr(int)]` enums and integers

crates.io: `num_enum` **0.7.6** (2026-03-15; previous 0.7.5 2025-10-19, 0.7.4 2025-06-22, 0.7.3 2024-07-29), license
**BSD-3-Clause OR MIT OR Apache-2.0**, MSRV **1.70.0**, about 286M downloads (58M recent, crates.io counter at check time). `no_std` compatible;
features: `default = ["std"]`, `complex-expressions` (adds `num_enum_derive/complex-expressions`), `std`. Repo workspace: `num_enum`,
`num_enum_derive` (the proc macros), `renamed_num_enum`, `serde_example`, `stress_tests`, `metadata_checks`. Facts below are from the README and
crates.io metadata; **nothing was compiled** (no Rust toolchain on this machine), so treat snippets as documented behaviour and
confirm with `cargo test`.

## When to pick it

You have a `#[repr(u8)]` (or other integer repr) enum and need to convert to and from the integer, typically for wire protocols, file
formats, register values or FFI. It replaces hand-written `match` tables and `as` casts. For a plain "name to value" mapping with
string conversion, iteration or `Display`, the usual companion is `strum`, not this crate. Prefer plain `as` only for the
enum-to-integer direction when you do not care about truncation.

## The four derives

| Derive | Generates | Use when |
|---|---|---|
| `IntoPrimitive` | `From<Enum> for repr` (exactly the enum's discriminant type) | going enum to integer; **more type-safe than `as`, which silently truncates**: only the exact repr type is implemented |
| `TryFromPrimitive` | `TryFrom<repr> for Enum` with `TryFromPrimitiveError` | untrusted input; the error text is ``No discriminant in enum `Number` matches the value `3` `` |
| `FromPrimitive` | `From<repr> for Enum` (infallible) | every value is covered: needs a `default`/`catch_all` variant, or `alternatives`, or a variant for every value |
| `UnsafeFromPrimitive` | `unsafe fn unchecked_transmute_from(repr) -> Enum` | only with measured evidence that the `try_from` match is a bottleneck; passing an invalid value is **undefined behaviour** |

## Attributes (and which derive honours them)

- `#[num_enum(alternatives = [2, 3..8])]` on a variant: extra input values that map to that variant. Honoured by
  `TryFromPrimitive` and `FromPrimitive`; `IntoPrimitive` always returns the canonical discriminant. Range expressions
  (`2..16`, `18..=255`) need the **`complex-expressions` feature**.
- `#[num_enum(default)]` (or the stdlib `#[default]`) on one variant: wildcard for unmatched values. **Only `FromPrimitive` reads it;
  `TryFromPrimitive` ignores it** and still errors.
- `#[num_enum(catch_all)]` on a tuple variant with one field of the repr type (`Other(u8)`): keeps the unmatched value. At most one,
  **`FromPrimitive` only** (naturally exhaustive, so not offered for `TryFromPrimitive`).
- `#[num_enum(error_type(name = CustomError, constructor = CustomError::new))]` with `TryFromPrimitive` swaps the error type; the
  constructor takes the repr value.
- **`UnsafeFromPrimitive` ignores `default`, `catch_all` and `alternatives`**: with `#[num_enum(default)] One = 1`,
  `unchecked_transmute_from(2)` is still undefined behaviour. Do not combine them.
- Discriminants written as complex expressions (`Zero = (0, 1).0`) compile only with `complex-expressions`; it is off to save compile time.

## Pitfalls to check in review

1. Every README example carries a `#[repr(u8)]`-style attribute: the derives take the integer type from it, so add one.
2. `TryFromPrimitive` on a protocol parser: handle the `Err` (unknown opcode) instead of `.unwrap()`; or switch to `FromPrimitive` with a
   `catch_all(u8)` variant when unknown values must be kept (the README does not say how `IntoPrimitive` treats the stored value
   of a `catch_all` variant: test the round trip before relying on it).
3. Mixing derives on one enum is fine (`IntoPrimitive` + `TryFromPrimitive` is the common pair), but the attribute semantics differ per
   derive as listed above; review each attribute against the derive that reads it.

## Python analogue (run live on 3.14.6)

`enum.IntEnum` already gives the `try_from` behaviour and, through `_missing_`, the other attributes:

| Rust | Python (`IntEnum` subclass) | Observed |
|---|---|---|
| `TryFromPrimitive` on 3 | `Number(3)` | `ValueError: 3 is not a valid Number`; `Number(256)` also `ValueError` |
| `IntoPrimitive` | `int(Number.ONE)` | `1`; `Number.ONE == 1` is `True` |
| `#[num_enum(default)]` | `_missing_` returns the default member | `WithDefault(2)` and `(99)` both gave `NONZERO` |
| `alternatives = [2]` | `_missing_` maps 2 to `ONE_OR_TWO` | `Alt(2)` is `ONE_OR_TWO` with canonical value `1`; `Alt(3)` still `ValueError` |
| `catch_all(u8)` | `_missing_` builds a pseudo-member with `int.__new__` + `_value_`/`_name_` | `Open(7)` works (`int` 7, `.name == 'UNKNOWN_7'`) but `Open(7) is Open(7)` is **`False`** and it is not in `list(Open)`: unlike Rust, pseudo-members are not cached or enumerated |

For fixed-size wire formats in Python also consider `struct`/`construct`, which convert and validate in one step.
