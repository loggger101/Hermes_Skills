---
description: "bumpalo 3.20 bump-arena notes: trade-offs, the no-Drop rule, reset, features, Send but not Sync, API names; source-read"
source_repo: fitzgen/bumpalo (MIT OR Apache-2.0)
tested_version: README and src/lib.rs read via GitHub API @ main; crates.io API for version/MSRV; NOT compiled (no Rust toolchain on this machine)
verified_date: "2026-10-05"
---

# bumpalo: bump-allocation arenas

crates.io: `bumpalo` 3.20.3 (2026-05-22), MIT OR Apache-2.0, MSRV 1.71.1, ~618M downloads (crates.io counter at check time). `no_std` by default (depends only on `alloc` and `core`).

## What it is and when it pays

A bump allocator keeps a chunk of memory and a pointer; allocating is a capacity check plus a pointer increment. You cannot free single
objects, only the whole arena at once. That fits **phase-oriented** work: allocate many objects during one phase (parse a file, handle a request,
render a frame, build an AST or graph), use them, then drop everything together. Typical wins are fewer `malloc` calls, better cache locality,
and mass deallocation by resetting one pointer.

Do not use it for long-lived objects with independent lifetimes, or where memory must be returned to the OS object by object.

When the chunk fills, it allocates a new chunk from the global allocator and continues. `Bump::with_capacity(n)` preallocates; `allocated_bytes()` reports use;
`set_allocation_limit(Some(bytes))` caps growth (returns allocation failure via the `try_*` methods).

## The rule that causes bugs: no `Drop`

Anything bump-allocated **never has its `Drop` run**, unless you do it yourself (from the `Bump` struct docs). A type that owns a heap
allocation (`Vec<T>`, `String`), a file descriptor (`File`), an `mmap` or any resource cleaned up in `Drop` will **leak** that resource when placed in the arena.

Options, in order of preference:

1. Allocate only plain data in the arena (`Copy` types, references to arena data, `bumpalo::collections::{Vec, String}` which keep their storage in the arena).
2. Use `bumpalo::boxed::Box<T>` (feature `boxed`): it runs `T`'s `Drop` when the `Box` goes out of scope, without freeing the backing memory.
3. Manage cleanup manually and document it.

`reset(&mut self)` takes an exclusive borrow, so the compiler guarantees no outstanding references into the arena; it frees extra chunks back to the global
allocator, keeps one, and **does not run any `Drop`**.

## API names (from `lib.rs`)

| Purpose | Methods |
|---|---|
| Create | `Bump::new()`, `Bump::with_capacity(bytes)` |
| Single value | `alloc(val) -> &mut T`, `alloc_with(|| val)` (constructs in place, avoids a stack copy of large values), `alloc_try_with` (fallible init) |
| Slices and strings | `alloc_str`, `alloc_slice_copy`, `alloc_slice_clone`, `alloc_slice_fill_copy / _clone / _with / _iter / _default` |
| Fallible variants | `try_alloc`, `try_alloc_str`, ... return `Result<_, AllocErr>` instead of panicking |
| Inspect and control | `allocated_bytes`, `allocated_bytes_including_metadata`, `iter_allocated_chunks`, `set_allocation_limit`, `reset` |

All allocation methods take `&self` and return `&mut T` with the arena's lifetime, so many live mutable references to distinct objects can coexist.

## Features

| Feature | Gives | Note |
|---|---|---|
| `collections` | arena-backed `Vec`, `String` (`Vec::new_in(&bump)`) | forks of std types until std collections are allocator-generic |
| `boxed` | `bumpalo::boxed::Box` that runs `Drop` | |
| `serde` | transparent serialisation of those `Vec`, `String`, `Box` | |
| `std` | e.g. `std::io::Write` for `Vec<'bump, u8>` | |
| `allocator_api` | `Bump` implements the nightly `Allocator` trait so std collections can use it | **nightly only and not covered by semver** |

```toml
[dependencies]
bumpalo = { version = "3.20", features = ["collections", "boxed"] }
```

## Threading

`Bump` implements `Send` (an `unsafe impl` in the source) and has a doc-test asserting it is **not `Sync`**. One arena per thread, or move an arena between threads,
but do not share `&Bump` across threads; use a per-thread arena (for example a `thread_local!` or one per worker) instead of a lock around a shared one.

## Python-side analogue

There is no direct analogue; in Python the closest tools are preallocated NumPy buffers and object pools (`algorithms-python-catalog` notes the general
"mass deallocation" idea). Reach for bumpalo when profiling a Rust program shows allocator time or when building large short-lived trees and graphs.
