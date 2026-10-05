---
name: rust-crate-picks
description: "Pick Rust crates by need: arena, units, time, graphs."
version: 1.0.0
author: Hermes Agent (from starred Rust repos; crates.io metadata checked 2026-10-05)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [rust, crates, arena-allocator, performance, cargo, bumpalo, pathfinding]
    related_skills: [python-craft, algorithms-python-catalog, astro-toolkit-selection, ponytail]
---

<!-- source: fitzgen/bumpalo and evenfurther/pathfinding READMEs + crates.io API; no Rust toolchain on the authoring machine, so crate behaviour below is documentation-sourced, not compiled -->

# Rust crate picks

## What This Skill Does

A short, growing guide to which Rust crate to reach for in specific situations, with the traps that the crate's own docs
call out. Entries are added as each starred Rust repo is reviewed; each has a reference page with details.

## When to Use

- Writing or reviewing Rust where allocation patterns, units, time scales or graph search matter
- Deciding between a Rust crate and a Python library for a hot loop (see the Python counterparts named per entry)
- Not a Rust tutorial; for the language itself use the official book and `cargo` docs

## Picks

| Situation | Crate | License | Version (crates.io) | Reference |
|---|---|---|---|---|
| Many short-lived allocations freed together (parsers, per-request or per-frame work, AST/graph building) | `bumpalo` | MIT OR Apache-2.0 | 3.20.3 (2026-05-22), MSRV 1.71.1, `no_std` by default | `references/bumpalo-arena-notes.md` |
| Shortest path, flow and matching over implicit or explicit graphs (A*, Dijkstra, BFS/DFS, Yen, Edmonds-Karp, Kuhn-Munkres, SCC, Kruskal) | `pathfinding` | Apache-2.0 / MIT | 4.16.0 per its README | Python equivalents in `algorithms-python-catalog/references/graph-algorithms-library-map.md` |
| Compile-time unit and dimension checking (no more mixed km/s or lbf/N) | `uom` | Apache-2.0 OR MIT | 0.38.0 (2026-02-14), MSRV 1.68.0, `no_std` via feature | `references/uom-units-notes.md` (includes the Python analogue `pint`) |
| Native desktop GUI in Rust with ready components, headless UI tests, WASM | `gpui-kit` (over `gpui`) | Apache-2.0 | 0.7.1 (2026-10-05); gpui 0.2.2 | `references/gpui-kit-notes.md` |
| Leap-second-aware time scales (UTC/TAI/TT/TDB/GPST), nanosecond Epoch and Duration; also `pip install hifitime` | `hifitime` | MPL-2.0 | 4.3.1 (2026-08-07) | `astro-toolkit-selection/references/hifitime-time-scales.md` (live-tested, leap-second caveats) |

Further entries (Bayesian optimisation) are added as those repos are reviewed.

## Procedure for choosing a crate

1. State the need and take the table row if there is one; otherwise search crates.io and read the crate's README before adding it.
2. Check `crates.io/api/v1/crates/<name>`: latest version, `updated_at`, license, `rust_version` (MSRV) against your toolchain, and downloads as a rough adoption signal.
3. Prefer the std solution first (`ponytail` ladder), then a small focused crate, then a framework.
4. Pin features explicitly in `Cargo.toml` (`default-features = false` where `no_std` or build size matters) and commit `Cargo.lock` for binaries.

## Windows note

The default Windows Rust target (`x86_64-pc-windows-msvc`) needs the Microsoft C++ Build Tools for linking, installed separately from
`rustup` (per the rustup/Rust installation docs). Not installed on this machine, so no Rust code was compiled while writing this skill.

## Pitfalls

- Documentation-sourced facts go stale; confirm versions and feature flags against docs.rs before relying on a snippet.
- Nightly-only crate features (such as bumpalo's `allocator_api`) are outside semver promises.
- Crates that run no destructors for arena contents (see `bumpalo`) change resource-management assumptions silently.

## Verification

- For any pick: `cargo add <crate>` succeeds, `cargo build` is clean, and a minimal test exercising the documented trap passes.
- This skill's facts: re-run the crates.io query and compare version, license and MSRV to the table.

## References

- `references/bumpalo-arena-notes.md` - bump allocation trade-offs, the no-`Drop` rule, features, thread-safety, when not to use an arena
- `references/uom-units-notes.md` - uom 0.38 type-safe units (features, design) and the Python analogue pint 0.26.1 run live
- `references/gpui-kit-notes.md` - gpui-kit 0.7 layering, headless UI tests, and the tested-recipe documentation pattern
