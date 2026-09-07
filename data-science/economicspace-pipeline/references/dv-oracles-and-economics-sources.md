---
description: "External delta-v oracles + soft-assumption data sources — Asterank schema change (2026-09-07), NHATS, per-element sigmas"
source_repos: juliensimon/space-datasets (~259 scripts read selectively; 14 verified this pass), live asterank.com API re-check
tested_version: space-datasets clone @ 2026-09-05 + LIVE Asterank API probe 2026-09-07 (this machine, py3.11)
verified_date: "2026-09-07"
---

# Delta-v Oracles & Economics Data Sources for the economicspace Pipeline

Companion to `catalog-data-sources.md` (now lives with its owning skill at `data-science/astro-toolkit-selection/references/catalog-data-sources.md`). This file covers the
**external Δv oracles** (independent checks on the closed-form estimator) and the **soft-assumption
data sources** — cited, keyless feeds that back the pipeline's softest numbers. All facts below were
source-read from the clone at `%LOCALAPPDATA%\Temp\starred-dive\space-datasets` or probed live today;
nothing is carried over unverified.

## ⚠️ Asterank API schema changed since the 2026-09-06 audit (LIVE re-check, this machine)

The economicspace repo's own `research/starred-repos/SECOND-PASS.md` (F6) measured two external Δv
oracles: JPL NHATS and Asterank's Shoemaker-Helin `dv` column. **Re-probing the live API on
2026-09-07 shows the second one is gone:**

| fact | verified today |
|---|---|
| Endpoint still up, keyless, paginated | `http://www.asterank.com/api/asterank?query={}&limit=N&offset=M` → JSON array; ~600K rows reachable (probed offsets 0 / 250k / 450k / 500k) |
| **`dv` column no longer exists** | key set has NO `dv`; new keys `two_body`, `DT` — both empty strings on every sampled row, including APO-class NEOs (1566 Icarus, 1620 Geographos, 1685 Toro). The Shoemaker-Helin oracle is **not reproducible from the live API** |
| Economics partially broken | `price`/`profit` return real values for some bodies (Ceres $8.1T) and garbage for others (Juno 2.7e-44, Eros 6.7e-42). Same failure mode SECOND-PASS flagged (`1e-42`), now more widespread |
| **NEW: per-element orbit sigmas** | `sigma_a`, `sigma_e`, `sigma_i`, `sigma_om`, `sigma_w`, `sigma_ma`, `sigma_q`, `sigma_ad`, `sigma_per`, `sigma_n`, `sigma_tp` — a free covariance DIAGONAL for ~600K bodies (Eros: σa 4.4e-10 au, σi 2.8e-06). Complements NEODyS's full 6×6 matrix on the top-N |
| **NEW: observation provenance** | `n_del_obs_used`, `n_dop_obs_used` (deltastation / doppler obs counts) alongside existing `data_arc`, `rms`, `condition_code`, `orbit_id` |

Consequences for F6-style cross-checks:
- The **NHATS leg survives and is the only external Δv oracle currently available** (below).
- Asterank's HF mirror (`juliensimon/asterank-asteroid-mining`) is a frozen snapshot with 50 columns —
  `estimated_value_usd`, `estimated_profit_usd`, `closeness_score`, `asterank_score` present, but it has
  **no dv column either** (checked via datasets-server info API today). It remains usable as an
  independent *economic ranking* prior art, not a Δv oracle.
- The per-element sigmas are the new prize: orbit-quality uncertainty at population scale with no
  per-body HTTP calls — a cheap input to any confidence-weighted ranking or pymc layer (see skill
  `economicspace-pipeline`, open candidates).

## NHATS — JPL's own Δv oracle (the surviving one) [SRC + HF live]

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
| `update-asterank.py` | Asterank API ~600K rows (schema above) | independent economic ranking prior art; per-element orbit sigmas (NEW); ⚠️ dv column dead since 2026-09-07 |
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

1. **Ranking cross-check** (research/ level, never feeds ranking math): NHATS Spearman by orbit-quality
   band — reproduces F6; re-run when the catalog or estimator changes.
2. **Orbit-quality uncertainty**: NEODyS full 6×6 covariance on top-N (per-body HTTP) + Asterank sigma
   diagonal at population scale → confidence weight feeding `comp_*` instead of a hard U cutoff.
3. **Soft-number audits** (no model change): launch-cost table diff, lunar geochemistry vs utility
   overrides, meteorite fractions vs composition table — each is an afternoon and produces either a
   citation or a correction.

## License position

space-datasets pipeline code: MIT; each dataset licensed at its own source. NHATS/SBDB/Horizons: NASA JPL
public APIs (citation requested). NEODyS: University of Pisa. Bus-DeMeo/Nesvorny/SDSS-taxonomy: NASA PDS.
CSIS launch-cost table: cited per row in the dataset card. Asterank: MIT code, data terms on their site —
the economics fields are explicitly "highly speculative order-of-magnitude estimates" even when they work.
