# GA Tuning — Measured Lessons (CR-pipeline, 2026-09)

Every number below was measured on a real run before being shipped, not guessed. Project: CR-pipeline (Clash Royale agents, Swiss/ELO tournament training, worker-pool match eval). The general principle: **tune the GA against measurements from your own pipeline — seed pairs, paired controls, and re-measured guard tests — never against vibes or literature defaults.**

## 1. Selection collapse via softmax temperature (measured root cause)

**Symptom:** population collapses to near-clones within a few generations despite nonzero mutation; one agent dominates parent draws.

**Root cause found by inspection + measurement:** parents were drawn by `softmax(raw_scores * 0.1)`. Tournament fitness is points-per-match (~0–3), so the exponent range was ~0.3 — effective temperature ≈ 0.001, i.e. de-facto argmax.

**Fix (shipped):** z-score standings first, then softmax at a real temperature:

```python
def tempered_softmax_select(fitnesses: np.ndarray, temp=0.5, rng=None) -> int:
    f = np.asarray(fitnesses)
    z = (f - f.mean()) / max(f.std(), 1e-9)
    p = np.exp(z / temp); p /= p.sum()
    return rng.choice(len(p), p=p)
```

**Rule:** any softmax over fitness must operate on scale-normalized values. If the exponent range is < ~0.5, you're doing argmax with extra steps.

## 2. Mutation load scales with genome size (measured regression + fix)

`mutation_rate` as per-weight probability ⇒ expected mutations/child = rate × genome_size.

| Net | Params | Rate 0.15 → expected muts/child |
|---|---|---|
| old default | 9,207 | ~1,381 |
| deepened (shipped) | 20,071 | **~3,011** — selection got *worse* (trend +0.06..+0.11/gen → −0.10..+0.04 across seeds) |

Capping expected mutations at ~1,400 restored improvement (+0.09/+0.05/+0.10 per gen across three init populations).

**Shipped pattern:** `max_expected_mutations` (default 1400; 0 disables). Compute the rate once per run: `rate = min(configured_rate, cap / genome_size)`. Applied in *every* mutation path — including champion refinements and immigration. No-op for small/low-rate configs, so existing runs stay bit-identical.

**Rule:** when you change network size (or add features), re-check expected mutations per child before believing a fitness trend is about learning rather than noise injection.

## 3. Deepening the net: wide funnel at input (probe-selected)

Default evolved policy became `66 → (96, 72, 56, 40) → 7` = **20,071 params** (was 9,207). Chosen by probe over alternatives for two measured properties: full behavioral diversity across random genomes AND healthy activations at every depth (no dead layers).

**Rule:** before shipping a bigger net, run a quick probe — sample N random genomes, check output entropy/diversity and per-layer activation statistics. A deeper net with dead or saturated layers is worse than the smaller one.

## 4. Recalibrating behavioral guard tests (the discipline)

Two long-run guard tests failed after architecture changes; both were recalibrated *with provenance* rather than deleted:

- **Ranking tracks skill, not noise:** correlation threshold lowered `>0.3` → `>-0.1`. Measured corr across seed pairs: +0.58 / −0.24 / +0.06 (own pair 0.06). The guard now catches *negative* signal (ranking anti-correlated with skill) instead of demanding a strength the noise floor can't support.
- **Champion beats its ancestor:** bare `wins > losses` fails ~59% under parity even for identical agents → replaced with an exact one-sided binomial test, alpha=0.10; flags ≤6W/20 as genuine regression (measured 9W/11L own seed, 7W/13L second — noise-level).
- **Evolution beats drift:** single-population `mean(last-3) > mean(first-3)` flips sign across seeds on the new net AND passed ~50% under pure random-walk drift → replaced with a *paired* control: identical match seeds, same population size, one arm evolving vs one arm taking random-parent mutations; assert gap ≥ pooled standard error. Measured every init seed separated (+1.3..+3.5 vs SE ≈ 0.7) while nulls stayed |gap| ≤ 0.74.

**Rules:**
1. Never guess-to-green. Measure the actual distribution first (several seeds), then set the threshold from it, and leave a comment with old value + measured values + why changed.
2. Prefer *paired* designs (same seeds/opponents) over unpaired — they cancel noise that makes guards flaky.
3. A guard test whose null hypothesis fails at ~50% is measuring nothing; replace the statistic before loosening it.

## 5. Match-rule config must reach every evaluation path (Round-10 defect)

`match_duration` was dead in both modes: the tournament path (default training loop) had no duration handling at all, and the scripted path computed its map but never used it — so "short"/"overtime" silently played full-length matches in *every real run*.

**Fix pattern:** one shared override builder (`_sim_overrides()`) feeding every eval path; explicit per-field config file wins over named presets; a plain default passes **no** override at all (bit-identical to engine defaults). Regression test evaluates an identical population under short vs full through the real tournament path and asserts different average match lengths — pre-fix both averages were identical.

**Rule:** any run-level setting that changes *what game is played* must be plumbed into every evaluation surface, with a test that plays actual matches end-to-end. A unit test on the config object proves nothing about the loop.

## 6. Worker-pool verification pitfalls (Windows)

- `Population.initialize` interleaves genome and agent-seed RNG draws — replicate the exact draw order in any probe or your numbers are garbage.
- Windows multiprocessing spawn cannot re-import `<stdin>` as `__main__`: verify anything using the worker pool by running a **real file**, never via heredoc/stdin (a stdin-driven probe once flooded 14 GB of output).
- A module that lazily re-imports its default config fresh per call defeats monkeypatching of the caller's global — patch at the source or pass explicitly.

## 7. What a long run actually shows

First production-scale run (pop 64, Swiss, full-length matches): best ELO reached gen **26**, early-stopped cleanly by patience at gen **55/250** (~38 s/generation). Interpretation: the field stopped being hard — larger population or harder opponents is the lever, not more generations. Watch champion-vs-hall-of-fame ELO drift (past champions' ratings falling relative to the field), never raw fitness mean.
