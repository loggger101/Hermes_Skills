---
description: "hifitime 4.3.1 (Rust + pip) for time scales, run live and cross-checked against astropy 8.0.1: correct scale offsets, but a 1-second TAI->UTC error at leap-second boundaries and UTC subtraction that ignores the leap second"
source_repo: nyx-space/hifitime (MPL-2.0)
tested_version: hifitime 4.3.1 (PyPI, installed on Windows py3.14) vs astropy 8.0.1; crates.io metadata for the Rust crate; Rust API from README only
verified_date: "2026-10-05"
---

# hifitime: time scales for astrodynamics (with a leap-second caveat)

hifitime is an overflow-safe, nanosecond-precision date/time library with leap-second-aware conversions between UTC, TAI, TT, TDB/ET, GPST and others.
crates.io: `hifitime` 4.3.1 (2026-08-07), MPL-2.0, ~1.26M downloads; the same release is on PyPI as `hifitime` 4.3.1 (`pip install hifitime`, Python `>=3.9`, installed fine on 3.14 here).
It is used by `nyx` (see `astro-toolkit-selection/references/optimization-toolkit.md`). Core types: `Epoch` (datetime equivalent) and `Duration`; `Epoch("2000-02-29T14:57:29.000000037 UTC")`, `Epoch.init_from_gregorian_tai(...)`, `epoch.to_time_scale(TimeScale.TAI)`.

## What worked (Python, run live)

| Check | Result |
|---|---|
| `Epoch("2026-10-05T12:00:00 UTC")` to TAI / TT / TDB / GPST | `12:00:37 TAI`, `12:01:09.184 TT`, `12:01:09.182342053 TDB`, `12:00:18 GPST` (TAI-UTC = 37 s, TT = TAI + 32.184 s, GPST = TAI - 19 s) |
| J2000: `2000-01-01T12:00:00 TT` | in UTC `2000-01-01T11:58:55.816 UTC`; `to_jde_tt_days()` = 2451545.0; `to_et_seconds()` = -7.27e-05 s (not exactly zero at J2000 TT) |
| TAI epoch minus UTC epoch at the same clock reading | `-37 s` |
| Nanosecond arithmetic | `epoch + Duration.from_parts(0, 1)` gives `...12:00:00.000000001 UTC`; `epoch + Unit.Day * 1` gives `2026-10-06T12:00:00 UTC` |
| UTC-TAI far future / before 1972 | `37 s` held for 2100 (no future leap seconds are predicted, correct), `0 ns` for 1960 (hifitime applies no offset before 1972) |
| Invalid input | `HifitimeError: ValueError, invalid day` for `2026-13-45`; a string with no scale suffix is read as UTC |

## Leap-second boundary: observed discrepancies vs astropy 8.0.1 (the 2016-12-31 leap second)

Truth (astropy): TAI `2017-01-01T00:00:35` is UTC `23:59:59`, TAI `:36` is UTC `23:59:60`, TAI `:37` is `2017-01-01T00:00:00`; elapsed from `23:59:59` to `00:00:00` UTC is **2.0 s**; UTC `23:59:60` maps to TAI `00:00:36`.

hifitime 4.3.1 (Python):

| Operation | hifitime | Expected |
|---|---|---|
| UTC `2016-12-31T23:59:59` to TAI | `2017-01-01T00:00:35 TAI` | same, correct |
| UTC to TAI at `2017-01-01T00:00:00` | `00:00:37 TAI` | same, correct |
| **TAI to UTC** `2017-01-01T00:00:35` | `23:59:58 UTC` | `23:59:59` |
| TAI to UTC `00:00:36` | `23:59:59 UTC` | `23:59:60` |
| TAI to UTC `00:00:34` | `23:59:57 UTC` | `23:59:58` |
| Round trip UTC to TAI to UTC for `23:59:57`, `:58`, `:59` | returns one second earlier each time | identity |
| `Epoch("2016-12-31T23:59:60 UTC")` | parses without error but reads back as `23:59:59` and maps to TAI `00:00:35` (same as `23:59:59`) | TAI `00:00:36` |
| **`b.timedelta(a)`** for UTC `b = 2017-01-01T00:00:00`, `a = 2016-12-31T23:59:59` | `1 s` | 2 s elapsed (SI) |
| Same two epochs converted to TAI first, then `timedelta` | `2 s` | correct |
| Day length `2016-12-31 00:00` to `2017-01-01 00:00` UTC via `timedelta` | `1 day` | 86,401 s |

The same one-second round-trip failure appeared at the 2015-06-30/07-01 leap second (UTC `23:59:58` and `:59` came back one second early); times well away from a leap boundary round-tripped exactly (`2026-10-05T12:00:00`).
So the scale **offsets** are right and ordinary conversions are fine; the TAI-to-UTC direction applies the new leap-second count to TAI instants in the 36 seconds before it takes effect, the inserted second cannot be represented as `:60`, and subtracting two UTC epochs gives a calendar-style difference, not SI elapsed time.
These are observations of the PyPI 4.3.1 wheel; the Rust crate was not compiled and a later version may behave differently, so re-run the probe after upgrading.

## Rules

- For elapsed time and propagation, convert to **TAI or TT first**, then subtract; never subtract UTC epochs across a leap-second date.
- Do not rely on UTC round trips within a minute of a leap second; use TAI as the working scale and convert to UTC only for display.
- When a result at a leap boundary matters, cross-check against `astropy.time` (or `spiceypy` `str2et` with an LSK; see `spiceypy-notes.md`).
- Keep a test of known conversions (J2000 TT in UTC, TAI-UTC = 37 s now, the 2016 leap second) so a library upgrade is caught.

## Rust

```toml
hifitime = "4"      # cargo add hifitime
```

```rust
use hifitime::prelude::*;
let epoch = Epoch::from_gregorian_utc(2000, 2, 29, 14, 57, 29, 37);
let epoch_tai = Epoch::from_gregorian_tai(2000, 2, 29, 14, 57, 29, 37);
assert_eq!(format!("{}", epoch - epoch_tai), "32 s");     // from the README: 32 leap seconds in 2000
```

Rust API above is from the README (not compiled here); the Python package is built from the same crate behind the `python` feature.
