---
description: "uom 0.38 (Rust type-safe units of measure): features, design, usage; plus the Python analogue pint 0.26.1 run live (dimension errors, temperature offset trap, AU and year definitions)"
source_repo: iliekturtles/uom (Apache-2.0 OR MIT)
tested_version: uom README read via GitHub API + crates.io metadata (0.38.0, 2026-02-14); NOT compiled (no Rust toolchain here). pint 0.26.1 installed and run on Python 3.14 / Windows
verified_date: "2026-10-05"
---

# uom: dimensional analysis in the type system

crates.io: `uom` 0.38.0 (2026-02-14), Apache-2.0 OR MIT, MSRV 1.68.0, ~13.65M downloads at check time. It does **type-safe, zero-cost dimensional analysis**: adding a length to a time
is a compile error (`error[E0308]: mismatched types`), and operations compile down to the raw float arithmetic. The README's motivating example is the Mars Climate Orbiter loss.

## Design (from the README)

- Code works with **quantities** (length, mass, time ...), not units. Units appear only at the boundary: `Length::new::<kilometer>(5.0)` in, `time.get::<nanosecond>()` out. Internally everything is normalised to the base unit of the system, so `+ - * /` cost nothing over the storage type.
- Ships a pre-built SI/ISQ system with many quantities and units; you can define your own system (examples `mks.rs`, `base.rs`) or add units to existing quantities (`unit.rs`).
- Compile errors on dimension mismatch are the point: `let error = length + time;` does not build; `length / time` gives a `Velocity`, and a function taking `(Velocity, Time) -> Acceleration` is checked by the compiler.

```toml
[dependencies]
uom = "0.38"                       # defaults: f32, f64, std, si
# no_std + only f64 + serde:
# uom = { version = "0.38", default-features = false, features = ["f64", "si", "serde"] }
```

```rust
use uom::si::f64::*;                              // Length, Time, Velocity, ...
use uom::si::{length::kilometer, time::second};
let v: Velocity = Length::new::<kilometer>(5.0) / Time::new::<second>(15.0);
```

## Features

| Feature | Meaning |
|---|---|
| `f32`, `f64` (default), `u8..u128`, `i8..i128`, `usize`, `isize`, `bigint`, `biguint`, `rational*`, `bigrational`, `complex32`, `complex64` | underlying storage type; **at least one must be enabled** |
| `si` (default) | the pre-built SI system |
| `std` (default) | turn off for `no_std` |
| `autoconvert` | automatic base-unit conversion in binary operators; exists because the compiler does not generate zero-cost code for non-float storage in that case, so with it disabled only quantities with the same base units interact directly |
| `serde` (off by default) | (de)serialisation of quantities |

Floating-point storage is the common choice; integer and rational storage trade ergonomics for exactness.

## Python analogue: pint (run live)

Python has no compile-time check, so the discipline is a unit-aware type that fails fast at runtime. `pip install pint` (0.26.1):

```python
import pint
u = pint.UnitRegistry(); Q = u.Quantity
```

| Expression | Result |
|---|---|
| `Q(5,"km") + Q(3,"s")` | `DimensionalityError: Cannot convert from 'kilometer' ([length]) to 'second' ([time])` |
| `(Q(5,"km") / Q(15,"s")).to("m/s")` | `333.333... meter / second` |
| `Q(1,"km") + Q(1,"mile")` | `2.609344 kilometer` (the left unit wins) |
| `Q(20,"degC") + Q(5,"degC")` | `OffsetUnitCalculusError: Ambiguous operation with offset unit` |
| `Q(20,"degC") + Q(5,"delta_degC")` | `25 degree_Celsius` |
| `Q(20,"degC").to("K")` | `293.15 kelvin` |
| `Q(1,"lbf*s").to("N*s")` | `4.4482216... newton * second` (the orbiter's actual bug class) |
| `5 + Q(5,"km")` | `DimensionalityError` (a bare number is dimensionless) |
| `0 + Q(5,"km")` | `5 kilometer` (zero is special-cased and allowed) |
| `Q(1,"au").to("km")` | `149597870.70000002 kilometer` (IAU value; SPICE's own is 149597870.6137, see `astro-library-notes/references/spiceypy-notes.md`) |
| `Q(1,"year").to("day")` | `365.25 day` (Julian year) |
| `Q(5,"km/s").check("[length]/[time]")` | `True`; `Q(5,"km").check("[time]")` is `False` |

Rules: temperatures need `delta_degC` for differences; keep one registry per program; convert at the boundaries and store canonical SI floats internally for hot loops;
`astropy.units` is the heavier equivalent for astronomy (it ships constants and equivalencies).

## When to use which

| Situation | Pick |
|---|---|
| Rust code where unit mix-ups must be unrepresentable | `uom` (SI, f64) |
| Python scripts or notebooks, runtime safety is enough | `pint` or `astropy.units` |
| Plain NumPy hot loop | strip units at the boundary and document the unit in the variable name (`dv_m_s`) |
