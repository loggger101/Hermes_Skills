# `smallvec` — inline storage, and the v1/v2 feature-name break

Source: `crates.io` API for `smallvec` (version records + per-version features), README at
`smallvec/smallvec`, redirect probe of `servo/rust-smallvec`. Measured 2026-11-11. No Rust toolchain on this
box, so nothing here is compiled — registry and README facts only (see
`references/toolchain-absence-and-release-cadence.md`).

## What it is

`SmallVec<T, N>`: a `Vec`-shaped type that keeps up to `N` elements **inside the value itself** and only spills
to the heap past that. The win is one fewer allocation + better locality for collections that are almost always
short (function arguments, AST child lists, matrix rows). 1,442,136,320 downloads recorded — it sits under huge
swaths of the ecosystem transitively, so version churn here is not a private decision.

`no_std` by default: README states SmallVec with no features enabled does not use the standard library. The
`rayon`, `proptest` and `schemars` features implicitly require `std`; `allocator-api2` requires `allocator-api`
but not nightly.

## Version state (registry, 2026-11-11)

| Fact | Value |
|---|---|
| Newest **stable** | `1.16.5` published 2026-11-06, edition 2018, license `MIT OR Apache-2.0`, no MSRV declared on the 1.x line |
| `max_version` reported by the API | **`2.0.0-beta.4`** — prerelease outranks stable in that field |
| v2 beta targets | `rust_version = 1.86`, edition 2024 |

Trap: any probe or bot that reads `max_version` (or sorts versions naively) will report a **beta** as the current
release and may then 'fix' a pin onto it. Use `max_stable_version`, or filter prereleases explicitly.

## The real migration trap: feature names changed spelling *and* membership

| v1 features (underscore) | v2 features (hyphen) |
|---|---|
| `const_generics`, `const_new` | dropped from the list; const-generics are in the 2.x signature itself: `SmallVec<i32, 4>` instead of `SmallVec<[i32; N]>` |
| `drain_filter`, `drain_keep_rest` | absent (std's own drain-filter story took over) |
| `impl_bincode`, `may_dangle`, `specialization`, `union`, `write` | v2 set is instead: `allocator-api`, `allocator-api2`, `internals`, `malloc-size-of`, `may-dangle`, `proptest`, `rayon`, `schemars`, `serde`, `specialization`, `std` |

Consequences worth stating plainly:

- A `Cargo.toml` written against v1 feature names **fails to build** on 2.x (unknown feature), and the reverse loses
  const-constructor features. Feature flags are not a stable interface across this major bump.
- The signature change (`SmallVec<[i32; N]>` -> `SmallVec<i32, N>`) touches every type annotation in a codebase,
  so it is not a dependency-bump-sized change even when features line up.

## Upstream's own advice (README)

v2 is pre-release with breaking changes, deprecations and feature churn still moving; the README explicitly says to
downgrade to the latest v1 if that risk matters to you. Actionable rule: **pin `smallvec = "1"`** in application
and library manifests today, and treat 2.x as an opt-in experiment until it ships stable.

## Registry metadata lags org renames

`crates.io` still lists the repository as `servo/rust-smallvec`; that repo is a **301** to
`smallvec/smallvec` (crate id 33456236, created 2015-04-05). So: do not treat old-name and new-name URLs as two
different projects, and do not trust a registry `repository` field to be current. Probe with
`curl -sSI https://github.com/<old>` and read the `location:` header before concluding anything about identity.

## Picking rule for this repo

- Need short-collection inline storage in Rust: use `smallvec`, pinned to `1.x` (`= "1"`).
- Need bulk/arena allocation rather than per-value inlining: that is `bumpalo`, not this — see
  `references/bumpalo-arena-notes.md`. They solve different problems (arena lifetimes vs inline vector capacity).
