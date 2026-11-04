---
description: "Rust reality on this box measured again (cargo, rustc and rustup all absent — so every crate claim in this skill stays documentation-sourced until a toolchain is installed) plus release cadence derived from actual rust-lang/rust release dates rather than remembered ('.0' releases exactly 42 days apart across three consecutive intervals; patch releases interleaving irregularly), how to determine current stable without installing anything, and the MSRV-vs-channel check that matters more than tracking latest"
source_repo: rust-lang/rust GitHub Releases API (measured 2026-11-04); local toolchain probe same day
tested_version: "release dates read live from `gh api repos/rust-lang/rust/releases`; **no Rust compiler exists on this machine** to verify anything compile-time"
verified_date: "2026-11-04"
---

# Rust here: no toolchain (measured), and cadence derived from real dates

## The box has no Rust — re-measured, not assumed

```
$ which cargo rustc rustup
cargo -> absent    rustc -> absent    rustup -> absent
```

This confirms the note already carried in this skill's frontmatter comment ("no Rust toolchain on the authoring machine, so crate behaviour below is documentation-sourced, not compiled"). It matters as a **verification bar**, not trivia: anything in `rust-crate-picks` about runtime behaviour — allocator performance, `uom` zero-cost claims, test harness quirks — has *not* been executed here. When adding to this skill from a repo read, keep labelling crate facts as documentation-sourced; the moment someone installs a toolchain is the moment those claims become checkable, and until then "verified" would be false. Note also that installing it is not free on Windows: the default `x86_64-pc-windows-msvc` target needs Microsoft C++ Build Tools for linking (recorded in this skill's workflow section), which is a separate, sizeable install from rustup itself.

## Current stable, without installing anything

The Releases API gives version + publish date directly:

```
$ gh api "repos/rust-lang/rust/releases?per_page=8" --jq '.[] | "\(.tag_name)\t\(.published_at)"'
1.99.1   2026-10-16      1.97.1   2026-07-16
1.99.0   2026-10-01      1.96.1   2026-07-05
1.98.1   2026-09-03      1.96.0   2026-05-28
1.98.0   2026-08-20      1.97.0   2026-07-09
```

So as of this writing the current stable line is **1.99.x** (latest patch published 2026-10-16). This is the cheapest way to answer "what's latest Rust" from a machine with no toolchain — cheaper and more reliable than scraping docs pages, and it comes with dates so you can tell how fresh the release actually is.

I tried `curl -sIL https://static.rust-lang.org/channel/{stable,beta,nightly}` expecting to read versions off redirect targets; in this environment that produced nothing parseable (no usable `Location:` value came back), so treat the Releases API as the working method here rather than assuming channel URLs will resolve.

## Cadence, computed from those dates instead of remembered

Intervals between consecutive **`.0`** stable releases:

```
1.96.0 -> 1.97.0 : 42 days
1.97.0 -> 1.98.0 : 42 days
1.98.0 -> 1.99.0 : 42 days
```

Exactly six weeks, three times running — so the well-known cadence holds empirically and can be used for planning rather than guessed at. Patch releases do **not** follow a rule; measured gaps from their own `.0` were 38 days (`1.96.1`, 2026-07-05), 7 days (`1.97.1`, 2026-07-16), 14 days (`1.98.1`, 2026-09-03) and 15 days (`1.99.1`, 2026-10-16), and an older line's patch can land immediately before a newer `.0` — `1.96.1` published three days ahead of `1.97.0`. Planning consequence: pin to a **minor** version in CI (`rust-version` / toolchain file) rather than "latest", because latest moves on a fixed 42-day clock regardless of whether your dependencies' MSRVs have caught up — the useful derived fact is not the date of the next release but that it *will* arrive predictably, so an unpinned `stable` in CI is a scheduled breakage.

The check that actually prevents surprises is already this skill's step 2: read `rust_version` (MSRV) from `crates.io/api/v1/crates/<name>` and compare against the toolchain you target — not against whatever stable happens to be newest. With no local compiler, MSRV arithmetic from those two numbers is the only correctness signal available here, which is worth stating plainly when handing a Rust recommendation to someone who *does* have a toolchain: they must confirm compile, because this box cannot.
