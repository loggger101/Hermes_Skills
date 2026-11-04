---
description: "Registry-verified notes on four starred Rust crates - sprs (sparse matrices, with its LGPL opt-in Cholesky trap), statrs (statistics; nalgebra is optional-but-default, MSRV 1.89), num-traits (frozen since 2024 yet the de-facto numeric abstraction; Float/Real need the libm feature under no_std) and trybuild (compile-fail UI tests: wip/ directory, TRYBUILD=overwrite, 'fails to fail' semantics) - with Python equivalents for choosing between ecosystems"
source_repo: sparsemat/sprs, statrs-dev/statrs, rust-num/num-traits, dtolnay/trybuild at default branches, 2026-11-04 (READMEs + Cargo.toml read via `gh api`; versions/dates/MSRV from the crates.io API)
tested_version: "REGISTRY-VERIFIED + SOURCE-READ. No Rust toolchain on this box (`cargo`/`rustc` both absent), so nothing here was compiled or run - treat behaviour descriptions as upstream-documented, and every version/date/MSRV number as fetched from crates.io"
verified_date: "2026-11-04"
---

# Rust numerics + compile-fail UI testing (four stars, one file)

## Versions and maintenance, measured 2026-11-04 via the crates.io API

| Crate | Latest stable | Released | Edition | MSRV | Downloads | Signal |
| --- | --- | --- | --- | --- | --- | --- |
| `sprs` | **0.11.6** | 2026-10-13 | 2021 | 1.88 | 9.4 M | active; still pre-1.0 API ("a work in progress") |
| `statrs` | **0.19.1** | 2026-08-11 | **2024** | **1.89** | 45.6 M | active, but the MSRV is very recent — see below |
| `num-traits` | **0.2.19** | **2024-05-03** | 2021 | 1.60 | **1.19 B** | frozen ~2.5 yr and still ubiquitous; stability, not abandonment |
| `trybuild` | **1.0.122** | 2026-10-07 | 2024 | 1.88 | 78.8 M | very active (dtolnay) |

Two planning facts fall out of this before any code: `statrs` needs **Rust 1.89**, so pinning it forces a recent toolchain in CI
and in every container that builds you; and the crate with by far the most downloads here (`num-traits`) has not been touched since
May 2024 — for an abstraction layer, "unchanged for two years" is the expected healthy state, unlike an algorithm library.

## `sprs` — sparse matrices in pure Rust (≈ `scipy.sparse`)

Structures: **CSR/CSC**, **triplet** (`TriMat`), sparse vector; operations cover sparse×sparse, sparse×dense, add/sub and
outer/inner iteration. Pure Rust — no BLAS linkage to fight on Windows, which is exactly why it gets chosen over bindings.

**The licensing trap worth remembering:** the repo is a **workspace**, and the factorisation lives in its own member crate. Verified from
`sprs-ldl/Cargo.toml`: `name = "sprs-ldl"`, `version = "0.10.0"`, **`license = "LGPL-2.1"`**, with a companion `LICENSE-LGPL` file — while the
root carries only `LICENSE-MIT` / `LICENSE-APACHE`. The README says it plainly: *"simple sparse Cholesky decomposition (requires opting into an
LGPL license)"*. So a permissively-licensed dependency can drag in one copyleft-gated routine through a workspace member or feature: check
**feature-level and sub-crate licences**, not just the top-level `license = "MIT"`. (Same repo also holds `sprs-rand`, `sprs-benches` and
`suitesparse_bindings` — the last is for benchmarking against SuiteSparse, not a runtime dependency. Default branch is **master**, so `?ref=main`
fetches return nothing.) Triplet construction is the `TriMat` type (confirmed in `sprs/src/lib.rs`).

## `statrs` — statistics (≈ parts of `scipy.stats`)

Distributions (Normal, Exponential, Student's T, Gamma, Uniform …) plus gamma/beta/error functions. Lineage matters for trust:
*"began as a port of the statistical capabilities in the C# Math.NET library"* and *"all unit tests … borrowed from Math.NET when
possible"* — so its correctness evidence is inherited from a mature implementation rather than self-written, which is a point in its favour.

From `Cargo.toml` (verified): `default = ["std", "nalgebra", "rand"]`. So **nalgebra is optional but on by default** — you can drop it
(`default-features = false`) if you don't want the linear-algebra type surface, and `kde` (kd-tree density estimation) additionally pulls
`kdtree` + `std`. `no_std` works via `default-features = false`. Gotcha for version pinning: README literally recommends
`statrs = "*"` — never ship that; it will silently jump majors.

## `num-traits` — the abstraction layer you probably already depend on

`Num`, `Float`, `Real`, `Zero`/`One`, `NumCast` … the glue under most numeric crates (including `statrs`, which depends on
`num-traits` with `features = ["libm"]`). no_std recipe from its README, verified:

```toml
[dependencies.num-traits]
version = "0.2"
default-features = false
# features = ["libm"]    # <--- Uncomment if you wish to use `Float` and `Real` without `std`
```

The trap is in the comment: disabling `std` compiles fine, but **`Float`/`Real` are unavailable until you add `libm`** — so a build that
"works no_std" can fail later at the exact trait you needed, with an error pointing away from Cargo.toml. MSRV 1.60 makes it safe almost everywhere.

## `trybuild` — compile-fail / UI tests for macros (and misuse of any API)

Minimal harness: one test that globs source files and asserts each fails to compile **with exactly the expected diagnostics**:

```rust
#[test]
fn ui() {
    let t = trybuild::TestCases::new();
    t.compile_fail("tests/ui/*.rs");   // expects tests/ui/<name>.stderr alongside
}
```

Verified mechanics from its README, each of which bites someone:
- **A compile-fail test that fails to fail is a failure.** Fixing your macro without updating the `.stderr` set turns CI red — good.
- `[dev-dependencies]` are visible *inside* the test cases, so fixtures can use your crate's friends.
- Single case filter: `cargo test -- ui trybuild=example.rs` (`ui` = the `#[test]` fn name).
- **Missing `.stderr` ⇒ output is written to a `wip/` directory next to `Cargo.toml`.** Add `/wip` to `.gitignore`, or your first run "creates files" that look like your work.
- `TRYBUILD=overwrite` writes compiler output in place instead — and the docs themselves say *"You'll want to check `git diff` afterward"*, because blessing silently accepts whatever rustc now says (diagnostics drift across toolchain versions). Bless locally, review the diff, never bless in CI.
- `t.pass(...)` mode also exists: passes only if it compiles **and** its `main()` runs without panicking — a cheap way to run workshop-style incremental suites.
- Its own scoping advice is a testing-judgment rule worth stealing generally: *"don't write compile-fail tests simply calling all of your public APIs with arguments of the wrong type; there would be no benefit."* Test the diagnostics you *curated* (targeted macro errors, unknown-attribute messages, correct span placement — "not on a useless `call_site` span"), not every possible misuse.

## Choosing between these and the Python stack

For this owner's work: `sprs` ≈ `scipy.sparse`, `statrs` ≈ `scipy.stats`/`scipy.special`, but neither matches the Python ecosystem's
breadth — the reason to pick them is a pure-Rust, no-BLAS, deployable binary (see `data-science/python-data-science` and
`rust-crate-picks`' existing picks). If you only need distributions for simulation inside a Rust pipeline, `statrs` + `rand` is enough;
if you need sparse linear algebra with solvers, budget time to evaluate maturity first (`sprs` is honest that its API is rough).
