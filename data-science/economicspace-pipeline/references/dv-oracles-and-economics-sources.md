---
description: "External delta-v oracles + soft-assumption data sources — Asterank two-mode API correction (2026-09-07 re-probe #2), NHATS, per-element sigmas; 2026-09-12 deep pass adds keyless HF mirrors + licensing traps"
source_repos: juliensimon/space-datasets (~259 scripts read selectively; full shared-library read @ 5f886cd on 2026-09-12), live asterank.com API re-checks
tested_version: space-datasets clone @ 2026-09-12 + LIVE Asterank/NHATS/HEASARC probes (this machine, py3.11)
verified_date: "2026-09-12"
---

# Delta-v Oracles & Economics Data Sources for the economicspace Pipeline

Companion to `catalog-data-sources.md` (now lives with its owning skill at `data-science/astro-toolkit-selection/references/catalog-data-sources.md`). This file covers the
**external Δv oracles** (independent checks on the closed-form estimator) and the **soft-assumption
data sources** — cited, keyless feeds that back the pipeline's softest numbers. All facts below were
source-read from the clone at `%LOCALAPPDATA%\Temp\starred-dive\space-datasets` or probed live today;
nothing is carried over unverified.

## ⚠️ Asterank API has TWO modes — the 2026-09-07 audit misread one as a schema change (CORRECTED, live re-probe #2, this machine)

The first round-4 pass probed only **bulk-scan projections** (`query={}` at offsets
0 / 250k / 450k / 500k) and concluded the Shoemaker-Helin `dv` column was removed.
That is wrong: bulk-scan rows simply never carried a `dv` key — **targeted queries do.**

| mode | query shape | dv present? | verified values (2026-09-07, stable across repeats) |
|---|---|---|---|
| Bulk scan | `query={}&limit=N&offset=M` (~600K rows reachable) | **NO `dv` key at all** in the 82-key projection — this is what made it look dead | n/a (key absent on every sampled row incl. offsets 1k+) |
| Targeted | `query={"name":"Eros"}` or `{"pdes":"1999 AO10"}` | **YES** | Eros 6.112354 · Icarus 15.298098 · Apophis 5.687675 · Itokawa 4.637086 · 2010 PS66 4.425463 |

Consequences (corrected):
- **Asterank remains an external Δv oracle** for targeted bodies, alongside JPL NHATS — but it is a per-body HTTP call at population scale (~600K), so its role stays *spot-check / top-N*, not full-catalog. The `asterank_sigma_probe.py` script (this skill's scripts/) exercises both modes and prints the schema notes automatically.
- **The query param is a JSON object, not free text** — `query=433` returns HTTP 500; working keys verified: `name` (proper names), `pdes` (MPC designation strings like "1999 AO10"; numeric for numbered bodies). Plain-number lookups must go through `pdes`.
- **Economics fields are still partially garbage** in both modes (`price`/`profit`: Ceres $8.1T real, Juno 2.7e-44 nonsense — same failure mode SECOND-PASS flagged as `1e-42`). Treat them as order-of-magnitude priors only.
- **NEW: per-element orbit sigmas** (both modes): `sigma_a`, `sigma_e`, `sigma_i`, `sigma_om`, `sigma_w`, `sigma_ma` + derived `sigma_q/ad/per/n/tp` — a free covariance DIAGONAL for ~600K bodies with zero extra calls in bulk mode (Eros: σa 4.4e-10 au, σi 2.8e-06). Complements NEODyS's full 6×6 matrix on the top-N.
- **NEW: observation provenance**: `n_del_obs_used`, `n_dop_obs_used` alongside existing `data_arc`, `rms`, `condition_code`, `orbit_id`.


## NHATS — JPL's population-scale Δv oracle (~7k bodies, keyless single call) [SRC + HF live]

- Source: NASA JPL **NHATS** study via `ssd-api.jpl.nasa.gov/nhats.api`; fetched by
  `space-datasets/scripts/update-nhats.py` through the repo's shared `jpl_api.jpl_query()` helper.
- Content: ~7,033 NEAs with at least one viable **crewed round-trip** trajectory — total Δv < 12 km/s,
  duration < 450 days, stay ≥ 8 days (the study's search limits). Per body: `min_delta_v_kms`,
  `n_viable_trajectories`, min/max diameter bounds from H + albedo range, orbit condition code.
- HF mirror **live**: `juliensimon/nhats-accessible-asteroids` (updated 2026-09-03 per the repo's own
  second-pass audit; re-confirm before relying).
- Interpretation rule from SECOND-PASS F6: NHATS is round-trip + crewed-constrained, so its number is an
  **upper bound on a differently-shaped quantity** — transfer the *rank* disagreement with the shipped
  estimator (Spearman ≈ 0.598), never quote it as a second estimate of the one-way gap magnitude.

## Soft-assumption data sources (verified scripts, all keyless) [SRC]

Each row: what `space-datasets/scripts/<script>` fetches → which economicspace soft assumption it backs.
All are live public feeds; HF mirrors exist for most under `juliensimon/*`.

| script | source / shape | backs in the pipeline |
|---|---|---|
| `update-nhats.py` | JPL NHATS API, 7,033 NEAs (above) | external Δv oracle; accessible-population orbit-quality enrichment (79.5% at U≥5 vs 13.9% catalog — a property of the population, not just selection) |
| `update-asterank.py` | Asterank bulk-scan ~600K rows (two-mode schema above) | independent economic ranking prior art; per-element orbit sigmas (NEW); dv available via targeted queries only — the HF mirror's 50-col snapshot has no dv either |
| `update-nesvorny-families.py` | PDS SBN zip: Nesvorny HCM families V2.0 — ~170K asteroids in **274 collisional families** (119 from 2015 + 153 new 2024) | family membership = composition evidence (fragments share a parent body); the hierarchical structure a pymc prior over `spectral_type` actually has, vs the flat categorical currently proposed |
| `update-bus-demeo.py` | PDS SBN fixed-width `.tab`: DeMeo et al. 2009 — **371 reference asteroids**, ~24 classes + PC1–PC5 scores; parsed with exact colspecs (`(0,7),(8,25),(26,36),(37,40),(41,51),(52,55)`) | the *reference* taxonomy that defines the classes `TAXONOMY_COMPOSITION` keys on |
| `update-sdss-taxonomy.py` | PDS **PDS3** fixed-width (note: pds3 path): Carvano et al. 2010 — 107,466 observation rows + 63,468 asteroid rows with exact colspecs in the script; per-observation u/g/r/i/z log-reflections | turns the manual ~34%-disagreement spot check into a **per-body provenance column** for every body in SDSS footprint (the open "astroquery SDSS cross-survey at scale" candidate) |
| `update-lcdb.py` | Asteroid Lightcurve Database zip: rotation periods, family codes, taxonomy | rotation constrains whether a rubble pile can be anchored/dug — an uncosted assumption in the model |
| `update-launch-cost.py` | **CSIS** compilation (aerospace.csis.org): 63 launch vehicles, cost/kg to LEO, 2024 USD, cited per row | the most load-bearing external number: in-space value is dominated by launch-cost-avoided. ⚠️ Disagrees with the pipeline's vehicle table on Falcon Heavy (CSIS 50–64 t vs CLAUDE.md 57 t); New Glenn agrees at 45,000 kg — an afternoon cross-check, no model change |
| `update-lunar-geochemistry.py` | Astromat Synthesis + EarthChem lunar sample geochemistry (tar) | ground truth for `IN_SPACE_UTILITY_BY_DESTINATION`'s lunar overrides — the softest assumption per CLAUDE.md ("engineering judgements") |
| `update-meteorites.py` | Wikidata SPARQL: all Q60186 meteorite entities, classes + masses | ground truth for metal/carbon fractions in `TAXONOMY_COMPOSITION` |
| `update-ssodnet.py` | IMCCE SsODNet ssoBFT flat table — a **second implementation** of the fetch | worth diffing against the pipeline's own `fetch_ssodnet`, which lost an entire source for four releases to a column rename (the standing argument for schema_check-style guards on every external feed) |
| `update-yarkovsky-nea.py` | VizieR TAP: Greenberg et al. 2020 AJ 159, 92 table1 — **247 NEAs** with direct da/dt drift detections (orbit-fit + bootstrap-resampled, p-values, significance σ, Yarkovsky efficiency ξ) | long-baseline orbital evolution; VizieR TAP gotcha applies: `SELECT *` + recno pagination only (see skill `space-data-pipelines`) |

## Placement in the pipeline's verification stack

1. **Ranking cross-check** (research/ level, never feeds ranking math): NHATS Spearman by orbit-quality band — reproduces F6; re-run when the catalog or estimator changes. `scripts/nhats_rank_crosscheck.py` (this skill) runs it end-to-end against a live JPL fetch + any economicspace CSV with a designation column.
2. **Orbit-quality uncertainty**: NEODyS full 6×6 covariance on top-N (per-body HTTP) + Asterank sigma
   diagonal at population scale → confidence weight feeding `comp_*` instead of a hard U cutoff.
3. **Soft-number audits** (no model change): launch-cost table diff, lunar geochemistry vs utility
   overrides, meteorite fractions vs composition table — each is an afternoon and produces either a
   citation or a correction.

## space-datasets deep pass (2026-09-12) — repo state + keyless HF mirrors

Full source read of `juliensimon/space-datasets` @ 5f886cd this pass (clone `%LOCALAPPDATA%\Temp\space-ds-dive`,
read-only; ~2,800 lines of shared library). Findings now live with the owning skill:

- **Keyless HF mirrors for every soft-assumption source above** — `juliensimon/<name>` on Hugging Face loads in one line, no API keys. Full 230-dataset catalog + top-downloaders + cadence: skill `space-data-pipelines`, ref `hf-mirror-catalog.md`. For this pipeline that means frozen snapshots of SBDB/NEO/Sentry/Nesvorny/Bus-DeMeo/SDSS-taxonomy/LCDB/launch-cost/lunar-geochemistry/meteorites are available without touching the live endpoints (useful for backfills and independent cross-checks; they lag by up to one update cycle).
- **Shared-library internals** — retry budget rationale, HEASARC HTTP-200 failure blocks, MAST keyset pagination + 504 page-halving, LFS-pointer upload recovery: skill `space-data-pipelines`, ref `shared-library-internals.md`.
- **Licensing correction that matters for any redistribution of these feeds**: the repo's own 2026-05-26 audit found its blanket cc-by-4.0 labels wrong on ~89 datasets — ESA Space Science Archives (incl. everything fetched via VizieR/HEASARC mirrors) is **CC BY-NC 3.0 IGO**, WDC Kyoto geomagnetic indices no-commercial, SILSO CC BY-NC 4.0, and VizieR's terms are "scientific context", not CC-BY at all. Full provider table + policy URLs: skill `space-data-pipelines`, ref `space-data-licensing-audit.md`.
- **Watchdog pattern** — the repo runs a daily stale-checker over its ~108 workflows (cron-derived periods, persistent retry state, idempotent issue escalation, NO_RETRY for Space-Track): generalized in skill `devops/cron-pipeline-watchdog`, directly applicable to aspirecures' scheduled feeds.
- Upstream churn since the 2026-09-05 audit: only status/stats commits (no schema changes) — all facts above still hold; NHATS HF mirror re-probed live this pass (HTTP 200, real parquet file list).

## License position

space-datasets pipeline code: MIT; each dataset licensed at its own source. NHATS/SBDB/Horizons: NASA JPL
public APIs (citation requested). NEODyS: University of Pisa. Bus-DeMeo/Nesvorny/SDSS-taxonomy: NASA PDS.
CSIS launch-cost table: cited per row in the dataset card. Asterank: MIT code, data terms on their site —
the economics fields are explicitly "highly speculative order-of-magnitude estimates" even when they work.
⚠️ For anything fetched via VizieR/HEASARC mirrors of ESA missions (Gaia subsets etc.): **CC BY-NC 3.0 IGO**, not cc-by-4.0 — see the licensing-audit ref above before redistributing.
