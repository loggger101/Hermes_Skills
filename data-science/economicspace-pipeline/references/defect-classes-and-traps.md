# Defect classes, code traps & performance (economicspace)

From CLAUDE.md "Durable lessons from the release history". Read before optimising anything or re-introducing a trap. The recurring defect classes are in the order they keep recurring; each has cost someone a day.

## The five defect classes

**1. A mass in one cascade with no price in the other.** The mass cascade and cost cascade live in different places; nothing checks that every kg in one has a price in the other, or that every kg the cost model pays for is actually flown. Look here FIRST (v1.11.0 introduced three fresh instances while fixing three older ones). One-line assertion catching the whole family:
```python
hardware_total_kg == mining_hardware_kg + power_system_kg + ep_system_kg
```
⚠️ `mining_hardware_kg` is NOT an output column — the rig is a config constant (2,000 kg). Written verbatim against the CSV it raises KeyError; has done so to two harnesses.

**2. A reference row that is internally contradictory**, holding two mutually exclusive physical states and collecting both benefits. Argon carried a cryogenic liquid's density AND an ambient gas's zero boil-off — its own comments contradicting each other three lines apart. Neither number was crazy alone. Check that a row's fields describe a single physical article.

**3. A quantity asked at finer granularity than it has answers.** Now the most common shape by a wide margin: a column with few distinct values and one Python call per row — found on both sides of the CSV boundary AND in between (composition derived per row when it's a function of 76 spectral types; ~25 distinct composition tuples across 1,555,667 rows). Recurs at every level: per-candidate constants varying only per body, per-option work varying only per fleet.
⚠️ **The redundancy factor is not the saving; the per-call cost is.** Largest surviving instance by row count is `_infer_from_albedo` (1,300,139 rows, 54 distinct values) and closing it is worth **0.15 s** because the function is two float comparisons — a 62,000-way redundancy over a 20 ns function is worth nothing. Do not re-find one on row count alone.

**4. A prescriptive comment nobody applied, or a gap documented and mistaken for closed.** v1.14.0's two largest findings sat in `STORAGE_REFERENCE` with citations behind a "not modelled in Module 4" note — and Module 4 doesn't load that table; the gap was quoted as a known limitation for two releases and nothing moved. **A reference table nobody reads is not a model.** If you record a gap, record which consumer would have to change, and check it can even see the table.
⚠️ Subtler version: a note documenting an INTENTION as an accomplishment — `tank_frac` spent three releases derived in two places ten lines apart beneath a note claiming one derivation with two readers; survived a release whose whole argument was bit-identity because nothing a hash can see was wrong. Check that a de-duplication claim names ONE surviving definition before believing it.

**5. The wrong behaviour is the quiet one.** A float-typed identifier stringifies to "3.0" (not null, not right, joins nothing); `.astype(bool)` reads NaN and "False" as True; `str.contains` without `regex=False` matches metacharacters. Each cost releases. Shared tell: **the dtype is inferred from the data**, so code works on a small test slice and breaks at scale.

## Bit-identity: tempting changes measured and REFUSED

Releases are argued from bit-identity, so an operation-reordering "cleanup" is a change to the PROOF rather than the number:

| tempting change | worth | why refused |
|---|---|---|
| sort the phase table at source | ~325,000 sorts removed | saturation block accumulates over its natural order — table is **load-bearing on the last ULP**: 2.8e-16 on 3 of 60 rows |
| rearrange `bracket > 0` into a launch-capacity comparison | one fewer term | re-associates arithmetic, moves boundary in last bit → changes whether a marginal row survives the prune |
| `pd.read_csv(engine="pyarrow")` | **4.8×** on the 862 MB read, identical dtypes | float parser rounds differently in last ULP: 13 of 46 columns differ; `estimated_mass_kg` moves 1e-13 relative — mass is what the ranking runs on |
| a faster CSV writer | ~84 s a full cell | every one changes formatting, which IS the contract |

✅ The ONE shape that's free: a change that only **EVICTS** (bounding a memo of a deterministic pure function forces recomputation of identical floats; nothing re-associated or approximated). That's why 1.17.7's cache bound was safe where all four rows above weren't.
⚠️ Corollary for comparisons: `float_precision="round_trip"` belongs in the COMPARATOR and must never be added to Stage 4's loader (it would move every number; the model's inputs go through the same slightly-inexact reader deterministically on every run — part of why bit-identity holds at all).

## Measured and declined (closed, not deferred)

| item | measured | verdict |
|---|---|---|
| inlining `builtins.max` | 1.2–2.4× per call on Python 3.13 (not the 6× recorded on an older interpreter); 18.7 M calls ≈ 0.4% of a run | closed — cProfile attributes 2.5 s to it, which is dispatch overhead on a C builtin and what will tempt the next person |
| ratio-independent prologue hoist | 2.3% default cell / 2.6% raw (~89% recoverable) | declined: ~2% for splitting a 570-line function with ~40 locals crossing the seam; the **7.6%** quoted for three releases was stale |
| `integrity_check`'s second factorize | 0.454 s ≈ 0.03% of full raw pass | declined — optimises the harness, not the pipeline; every clean fix widens a contract (cProfile says 0.85 s = instrumentation) |
| `_infer_from_albedo` by distinct value | ~0.15 s, 0.07% of Stage 1 | declined — defect class 3 |
| `viability_only` on `max_return_payload_kg` | 519 ns of a 2,105 ns call but only 31% of calls in raw cell | declined at under 1%, against a new branch in the hottest function in the model |
| rig block in `_mission_cost_tail` | 3.2% priced alone | **taken in 1.17.5** — once priced with the neighbour that shares its key: price the BLOCK, not the line |
| Parquet instead of CSV for catalog | 19.7 s → 2.1 s | real and free, NOT taken: changes Module 1's output contract; no measured cell would move detectably |
| nickel-iron missing market ceiling | 7.7e−8 relative one mission / 7.7e−5 at N=100 | declined — breaks bit-identity on a destination not re-measured since 1.14.0; take it in that pass if earth_surface is ever re-run |

⚠️ Two of those figures went stale while being quoted forward, in opposite directions (the `max` figure by interpreter version; the prologue's by three releases of work around it). **Measure the remainder after taking the cheap items, not before** — the ranking changes.

## Why the GPU is not the answer (measured on RTX 2080 Ti)

```
numpy fp64 exp, 40M elements   0.222 s
cupy  fp64 exp, 40M elements   1.695 s   <- 7.6x SLOWER than CPU (TU102's 1:32 FP64 rate; property of every consumer GeForce)
cupy  fp32 exp                 0.137 s   <- unusable: every verification is a bit-identity check
host->device, 320 MB           0.055 s
```
Workload is the wrong shape anyway (branchy scalar Python with early exits, fixed-point loop, knapsack with sorted()); the one GPU-shaped piece — the pre-filter — is ~14 GFLOP for the entire catalog, under a second on either processor. RAM not a constraint (~6 GB peak vs 64 GB) except what 1.17.7 closed.

## The open structural item: branch-and-bound on the objective

Pruning candidates that CAN close but cannot beat the incumbent needs an **admissible** upper bound on `selection_key` (lexicographic over profit and cost/revenue, revenue out of the payload knapsack) — a bound provably never optimistic is real work.
🚨 **Do not approximate it**: a bound occasionally too tight silently drops winners WITHOUT changing row count — the one failure mode none of verify.py's six checks would catch. Neither 1.17.4's pre-filter (prunes on feasibility, monotone in two masses, provable in four lines) nor 1.17.7's cache bound (eviction value-neutral by construction) is a precedent — neither is monotone in anything the objective reads.

## Traps in the code a reader will otherwise re-introduce

- `_combo_can_close` and `max_return_payload_kg` are TWO statements of one algebra; pre-filter side written in three pieces, kept adjacent for that reason. Defence: `prune_infeasible_combos = False` + column diff (verify.py check 2). Change one → re-run the diff.
- The pre-filter's second stage must run at pass 1's `structure_frac`: containment grows that term and it appears in `denom`, not `bracket`, where a larger value only helps. Testing `denom <= 0` instead looks sound and is wrong in the one direction no output diff can see.
- `want_phase` must stay a short circuit inside the ONE walk, not a water-only copy: the greedy walk is cheap, bookkeeping costs; a copy buys nothing + drift hazard on a function load-bearing on the last ULP.
- `totals_only` is an early return, NOT a second code path — keep `total_cost` final before it or the ladder silently prices from a different number than reported.
- The prologue tuple's ORDER is load-bearing (unpacked in one statement): insert a field in one place and not the other shifts every value after it, changes no row count.
- Three sums stay written out term by term (`hardware_cost`, `spacecraft_book_value`, `upfront_lines`): they interleave N-dependent and N-independent terms; pre-adding re-associates.
- A cached `None` needs a SENTINEL: None is the legitimate answer for "this propellant can never be made from asteroid material"; `.get(key)` alone re-derives it every call on exactly those rows — a cache that silently stops caching = quiet-wrong-answer wearing performance clothing.
- NaN and None must normalise to the same cache key; bare NaN keys never hit (two NaNs not equal). Anything not a real number or None takes the uncached path rather than inventing a key.
- `factorize`, NOT `unique` + dict: factorize is total — NaN is a code like any other, so missing values can't fall through a lookup that `nan != nan` would break.
- Give each row its OWN list when expanding a column by distinct value (a 62,000-way alias on a mutable object costs 0.4 s and is a trap whether or not today's code springs it).
- `AsteroidContext`'s membership test = "does it vary with the candidate", NOT field count: if a quantity varies with vehicle/propellant/return mode/power source/concentration ratio it must not live there. `synodic_period_yr` carried separately from `window_wait_yr` (wait is zero when `model_launch_windows` off; period still an output column).
- Non-electric candidates skip the stage-2 solver entirely — with no electric stage, the second pass IS the first.
- Memo on the config VALUES a function reads, not `id(config)` (a config edited between runs must still be answered correctly).
- Do NOT memoise a warning path: an unknown destination must shout every call; that loudness is the point of the warning.

## Where a cache is safe and where it isn't

1.17.7 bounded the one memo keyed on a PER-CANDIDATE FLOAT (~45 entries/row → 70 M entries / 11–18 GB projected against ~6 GB run peak). Every other memo is bounded by its key space: (N, rate) pairs, ~25 composition tuples, a handful of ladder rungs, one destination string.
**Rule: `maxsize=None` is safe exactly when you can name the ceiling; if you cannot, bound it.** A replay of real keys showed hit rate flat at 83.9% from unbounded down to maxsize=64 (all reuse local to one candidate); bounded lru_cache not measurably slower than unbounded.
🚨 It survived three releases because no full-catalog run was made in them — a 400-row verification cell shows 18,000 entries rather than 70 M. **A stride sample does not predict a full run's MEMORY either.**

## Performance-stamp reading rules (the 1.17.x line)

- `1.17.2` is INERT on some cells and worth 1.45× on others: removes work that only exists when a programme LADDER exists → search-OFF 0.99–1.02×, search-ON 1.35–1.46×. Every previous perf stamp moved every cell — do not quote one number for it.
- `1.17.4` is uneven the OTHER way (lands on MASS cascade): 2.04× beneficiated-without-search vs only 1.26× raw-with-search; plus fixed ~15 s off LOAD at any row cap and 3.44× off per-row walk (~67–78 s full cislunar pass). Quoting either release's number for the other gets it backwards.
- `1.17.5` is shaped like 1.17.2, SMALLEST perf stamp: 1.06× (search-OFF cells 1.00–1.01×) — what's left in the ladder is per-option overhead in tens of ns; do not expect another 1.5× from that path.
- `1.17.6` lands on PER-ROW WALK: first worth MORE raw than default, and its ratio DEPENDS ON THE ROW CAP (at 150/400-row caps it reads 1.03–1.10× because fixed ~1.6 s is half those cells). Quote the cap with the ratio; prefer per-row figures: 1.15 / 1.05 / 1.18 / 1.12×.
- `1.17.7` fixes a DEFECT (the memory bound), not a cost — and is also faster (180 → 91 ns a hit). First stamp that does; no cell could have shown it.
