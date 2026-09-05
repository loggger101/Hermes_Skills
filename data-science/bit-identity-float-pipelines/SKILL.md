---
name: bit-identity-float-pipelines
description: "Verify correctness via exact float hashes / bit-identity."
version: v0.9.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [floats, verification, bit-identity]
    related_skills: []
---

## When to Use

- When working on: Verify correctness via exact float hashes / bit-identity CSVs.

## What This Skill Does

For projects that defend releases by **exact float hashes** (bit-identity) rather than tolerance. Distilled from the economicspace pipeline's CLAUDE.md — a repo whose entire release process is an


# Bit-Identity Float Pipelines & Verification Discipline

For projects that defend releases by **exact float hashes** (bit-identity) rather than tolerance.
Distilled from the economicspace pipeline's CLAUDE.md — a repo whose entire release process is an
argument about whether two runs produced byte-identical CSVs. The general lessons transfer to any
pipeline where "the number didn't move" must be *proven*, not assumed.

## Core principle: bit-identity changes what counts as a change

When correctness = exact float hash, **an operation-reordering "cleanup" is a change to the proof**,
not just the number. Re-associating arithmetic moves the last ULP and can flip whether a marginal row
survives a prune — with no visible error. So:
- A numerically negligible change (1e-13 relative) that re-orders or re-parses floats is **refused**, not accepted.
- The one shape of change that IS free is a change that only **EVICTS** (e.g. bounding an `lru_cache`
  of a deterministic pure function): it forces recomputation of the identical float, re-associates nothing, approximates nothing.

## The three "identical symptom" comparator bugs (the sharpest lesson)

The same four byte-identical files reported DIFFER → MATCH across three separate harness fixes; **the
hash never moved**. Each cause had to be diagnosed separately and fixing one only changed the count:

1. **Index alignment.** A live frame carries a scrambled index (rows sorted by objective); re-read from
   CSV it has a fresh RangeIndex. Comparing two pandas Series directly aligns on the **index label, not position** → spurious diffs. Fix: compare values/positions, or reset_index both sides.
2. **The default float parser is not correctly rounded.** `pd.read_csv`'s fast reader returns a float64
   one ULP from what was written (`119898.18458829961` → `...96`). Neither the default nor
   `float_precision="high"` round-trips; **only `"round_trip"` does.** Same family as a different CSV *engine* (pyarrow) rounding differently in the last bit — a 4.8× speedup was rejected for moving one column by 1e-13 relative because that column is what the ranking runs on.
   ⚠️ **This says nothing about the pipeline and must NOT be "fixed" there.** If the model's own loader uses the default parser, its inputs go through the same slightly-inexact reader every run — *deterministically* — which is part of why bit-identity holds at all. `float_precision="round_trip"` belongs in the **comparison**, never in the production load path (it would move every number).
3. **The empty string is not NaN, except that in a CSV it is.** An all-empty object column writes as bare commas and reads back as float64-of-NaN, so a live `""` meets a `nan`. A CSV cannot represent the difference, so even the file's own hash can't see it. **A comparator stricter than the artefact it compares reports failures that do not exist.**

**General rule:** report a **hash AND a column diff**, never either alone. When they disagree, the
hash is right and the disagreement means *the comparator is broken*. A column-diff alone would condemn
a release that changed nothing; a hash alone wouldn't name which column genuinely moved. And `_comparable()`
deliberately does NOT sort columns — sorting would be tidier but silently make every printed hash incomparable with hashes already committed elsewhere.

## "A check that cannot run must never say it passed"

The most dangerous harness bug is a silent skip: the original `check` skipped any cell absent from the
baseline with a bare `continue` that never touched the ok-flag, so a missing/partial baseline made the
most important comparison compare *nothing* and still print ALL CHECKS PASSED. Same shape as an empty
cell printing `(no rows)` and passing, or a never-worse join coming back empty and being skipped. Fix:
report `*** NOT VERIFIED ***`, name the cells, exit non-zero. **A broken checker looks exactly like a
broken release** — that is why these are defended at the line that would otherwise reproduce them, in a
list you add to rather than rewrite from scratch (this harness was written ~12 times before being committed).

## Inputs move underneath your comparison

- A stage that **re-fetches live data** (prices, an upstream catalog that grows daily) will silently change the population. Running such a stage "just to look at the banner" overwrote the only copy of frozen inputs and made every baseline stop reproducing — with the signature of a code regression (all differing columns downstream of price; mass/mission columns untouched). That split is why a column-by-column diff earns its keep against a bare hash.
- **Never run an input-moving stage to test something unrelated.** Use a read-only path that consumes CSVs already on disk. If you must move inputs deliberately, back them up first (nothing else will), and when they have moved, **re-isolate rather than argue**: baseline the pre-change build against the *same* refreshed inputs, restore, re-check. Comparing two builds against identical inputs is the only construction that answers it once an input moved.
- A soft-failing data source doesn't shrink your population — it often **inflates** it with backfilled/guessed values (e.g. inferring taxonomy from albedo when a spectral-type fetch fails). Check provenance columns before comparing any run to a committed number; "source reported success" ≠ "source contributed rows."

## Cross-host: bit-identity is not portable and cannot be made so

`math.exp/log/cos` are platform libm; numpy picks SIMD kernels per architecture. None is IEEE-required
to be correctly rounded (only `sqrt`, etc., are). So two byte-perfect runs on different CPUs can differ in the last ULP with every input identical.
- **Do not file cross-host deltas as regressions.** Re-baseline on that host and compare across hosts *with a tolerance*.
- A fast platform check: hash raw IEEE bit patterns of `math.exp/log/cos` over the model's own argument ranges, using an IEEE-guaranteed function (`sqrt`) as the control. If it diverges, you know before running anything expensive.
- **Line endings are part of the hash.** Pin `lineterminator="\r\n"` (or whatever) in every CSV writer AND the hasher; pandas.to_csv defaults to os.linesep, so an unpinned CRLF pin makes a byte-perfect Linux run report DIFFER on all cells with every float identical. It reads like a Windows leftover and is exactly why it must be called out.

## Versions spelled out in prose rot — ask the machine instead

A version number typed into documentation has gone stale in both directions within days (said 3.14 while
3.13 was installed, then corrected to "3.14 never existed," then that correction itself became false). The fix is to **delete the number** and point at `py -VV` / a platform-check script instead — three files already derive or pin it. Same for any count ("four consumers") stated in prose above a table: read the column, don't count the rows.

## Sampling rule (for runtime/cost budgeting)

A stride sample predicts full-catalog cost to no better than ~5×, **in both directions** — fixed costs
dominate small runs; expensive tails are under-represented in samples. Budget from a measured full run of
the same cell, or don't budget at all. Compounding per-release performance ratios understates (worst on the
default/most-expensive cell). The one projection that DOES hold: extrapolating a *measured* full-catalog speed-up
on one setting to another setting of that same cell — not from a sample to the full catalog.

## Quick checklist before trusting a "no change" claim in a bit-identity pipeline

- [ ] Compared with BOTH hash and column diff; if they disagree, treat as comparator bug, not release bug
- [ ] Float comparison uses `round_trip` precision (in the comparator only)
- [ ] Index alignment handled (compare positions/values, not label-aligned Series)
- [ ] Empty-string-vs-NaN normalised on both sides before comparing object columns
- [ ] Baseline actually present and complete for every cell being compared (else NOT VERIFIED, not PASSED)
- [ ] No input-moving stage ran since the baseline; inputs are byte-identical between the two builds
- [ ] Line terminator pinned in writers + hasher; same on both hosts if cross-host
- [ ] Cross-host: re-baselined and comparing with tolerance, deltas NOT filed as regressions
- [ ] Any "cleanup" checked for arithmetic re-association (only EVICT-only changes are free)
