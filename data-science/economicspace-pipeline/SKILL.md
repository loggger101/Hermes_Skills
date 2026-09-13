---
name: economicspace-pipeline
description: "Use on economicspace (asteroid-mining pipeline)."
version: v0.9.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [economicspace, asteroids, pipeline]
    related_skills: [astro-toolkit-selection, space-mission-computation-paradigms]
---

## When to Use

- When working on: Use on economicspace (asteroid-mining pipeline).

## What This Skill Does

Repo: `C:/Users/Owner/OneDrive/Documents/GitHub/economicspace` (owner loggger101). Argues from **BIT-IDENTITY**: releases are defended by exact float hashes of output CSVs, not tolerance.


# economicspace — asteroid-mining profitability pipeline

Repo: `C:/Users/Owner/OneDrive/Documents/GitHub/economicspace` (owner loggger101).
Argues from **BIT-IDENTITY**: releases are defended by exact float hashes of output CSVs, not tolerance.
The repo's own `CLAUDE.md` (~2,765 lines) is the authority for traps; this skill distills it so an agent can work here without re-learning a day-cost per mistake. **Read-only default: never edit the repo unless explicitly asked.**

## Routing (read before acting)

| Task | Read first |
|---|---|
| Any model-term change, "fixing" a result that looks wrong | `references/load-bearing-assumptions.md` |
| Before optimising anything / re-introducing a trap | `references/defect-classes-and-traps.md` |
| Strange behaviour: data sources, dirty tree, cross-host, entry points | `references/data-sources-environment-entrypoints.md` |
| Float-hash comparison discipline (generic) | skill `bit-identity-float-pipelines` |

## Repo map — name ONE authority or you have two

| file | holds | is the authority for |
|---|---|---|
| `README.md` | what it does, how to run, **current** numbers (20-cell matrix) | the current answer |
| `versions.md` | per-release notes + module changelogs; every table names its release & catalog | measurement history — ONLY copy of superseded figures |
| `CITATIONS.md` | references and attribution obligations | where sources came from — **never values** (a number's source is cited on the row that carries it, in `modules/*.py`) |
| `CLAUDE.md` | traps, invariants, reasoning behind decisions that look wrong | how to edit safely |

Subdirs: `campaign/` = 20-cell campaign rig + frozen Stage-2 prices per destination (`campaign/stage2/`); findings promoted into the three main docs. `research/starred-repos/` = read-only audit of the user's star list (17 repos) against this pipeline; **nothing wired in**, scripts can't invalidate baselines. Its two Δv findings point opposite ways and partially cancel: F1 plane change overcharged, F4 transfer geometry undercharged by more — fixing either alone makes the model worse. `patch_neowise_async.py` there is a PATCH CANDIDATE, not live code.

## Build discipline (before any edit)

- `master.py` is GENERATED from `modules/*.py` by `build_master.py`. Edit the module → `py build_master.py` → commit both. A direct edit to `master.py` dies on next build.
- **`git status` immediately after a build IS the sync check**: clean = master matches modules.
- The build locates things BY PATTERN, not parsing. Every module must keep: (1) leading `# -*- coding: utf-8 -*-` followed immediately by the docstring; (2) an `# INSTALLATION` block ending with literal `print("OK  All packages present")`; (3) a `# RUN & PREVIEW` block at bottom under `if __name__ == "__main__":`; (4) config global named exactly `CONFIG`. The build asserts all four and exits `BUILD FAILED: …` rather than emit a wrong master.
- **Name collisions are handled by hand** via `word_replace()`: catalog `CONFIG→CATALOG_CONFIG`, `build_catalog→build_asteroid_catalog`, `lookup_asteroid→lookup_asteroid_catalog`; mineral_value `CONFIG→MINERAL_CONFIG`, `merge_sources→merge_mineral_sources`, `validate→validate_minerals`; transportation `CONFIG→TRANSPORT_CONFIG`, `validate→validate_transport`; calc `CONFIG→CALC_CONFIG`. The post-build AST scan catches new collisions — either add a rename or, if the duplication is deliberate and identical in every copy, add to `_EXPECTED_DUPES`.
- Consumers sit at repo root (a consumer inside `modules/` would be concatenated into what it consumes).

## Version stamps (verified from module code 2026-09-07)

Current: **catalog `1.2.0`, mineral_value `1.9.0`, transportation `1.14.0`, calc `1.20.0`, master `1.24.0`** (master literal lives in two places in `build_master.py`: the module docstring line and the startup banner print).
⚠️ **Tree-state flag found 2026-09-07:** HEAD is at calc 1.20.0 / master 1.24.0, but a local uncommitted edit in `build_master.py` reverts both literals to 1.23.0 (master.py on disk still says 1.24.0) — the tree was mid-sync when inspected; treat as OneDrive churn and verify with `git status` before trusting either copy.
- **calc 1.20.0 (2026-09-04): both insurance premiums are OFF by default** behind new `charge_insurance=False`. Module 3 prices third-party liability ($1.5M flat/mission) + launch insurance (10% of launch+spacecraft book value); the cascade charged both on every mission. Rationale: a premium is priced off an underwriter's book, not a mass/dv/kW — out of scope for a marginal-physics model; it also double-prices risk that `model_reliability` already carries (premiums don't touch p_launch/p_cruise/p_mining). Measured effect on cislunar stride cells: premium = 2.4–4.3% of total cost but **improvement is 5.5–9.6%** — an upfront line compounds through contingency + WACC, effective multiplier 2.12–2.38×; quote the improvement, not the share. The programme search makes insurance matter MORE (per-launch charges don't amortise across N). **EVERY committed measurement in the project is a `charge_insurance=True` run** — including the whole 20-cell campaign and every versions.md table: set it True to reproduce any of them; never read a table as covering an uncharged run unless it says so. With ON, calc 1.20.0 is bit-identical to 1.19.1 (all four verify cells MATCH). Winners do not change (premium ≈ proportional to launch stack: rescales the ranking far more than it reorders); evaluable set unchanged; columns stay at 141 with the two cost fields zeroed, so no consumer schema moves.
- **catalog 1.2.0 (2026-09-03) is still the newest catalog release**: NEOWISE's `ORDER BY asteroid_number` was not total, so dedup of its duplicate rows resolved **27,802 bodies by arrival order alone** (median diameter spread 11.6% → ~39% mass spread; diameter cubes into estimated_mass_kg which the ranking runs on) — now ordered to be total, both transports byte-identical. It also fetches orbit-quality fields (`condition_code` = MPC U parameter + arc/obs/rms/MOID/class/soln_date, all 100% populated): **data only, no filter applied** — the top of the ranking is enriched in barely-determined orbits (43.3% at U≥5 vs 13.9% population; winner's-curse signature) and a U cutoff / arc floor / confidence weighting is an open modelling decision. `ma` now comes with its `epoch` (per row — one body was 5,638 days off the shared epoch), and NEOWISE fetches via async TAP (UWS submit/poll/fetch; sync fallback on failure).

- Each module's `pipeline_version` is stamped into every output CSV — the only way to tell which code produced a catalog. **Changing any number a run produces means bumping it.**
- The rule is ONE-DIRECTIONAL: changing a number ⇒ bump; **bumping does not mean a number changed**. Most stamps are performance-only (bit-identical, verified). A release writes in two places, neither the module: `versions.md > Releases` (what + measurement) and `> Module changelogs` (stamp, pairing, config fields & output columns it adds — the schema half has no other home; tells you whether an archived CSV can answer your question).
- **Read the MODULE, not just the number**: mineral_value `1.7.1` ≠ calc `1.17.1`; transportation `1.14.0` shipped together with calc `1.19.0`.
- Destination trios: `mars_orbit` = calc 1.18.0 / mineral_value 1.8.0 / transportation 1.3.0; `geo` = calc 1.19.0 / mineral_value 1.9.0 / transportation 1.14.0 — each bit-identical on all existing cells.
- **Parallel-repo divergence**: the project was once developed in two places at once and `1.0.6`/`1.1.4`/`1.3.6` each shipped as TWO different things; CSVs stamped with those versions cannot be trusted, regenerate them.

## Destinations (7) & the campaign (5 measured)

Destinations: `earth_surface` (default), `leo`, `cislunar`, `lunar_surface`, `mars_orbit`, `geo`, `mars_surface`.
- The 20-cell campaign (2026-08-23/24, calc 1.17.7) measured **five**: cislunar, lunar_surface, leo, mars_surface, earth_surface × {raw/beneficiated} × {search off/on}. `mars_orbit` and `geo` have NEVER been run; the full matrix is now **28 cells**.
- Two facts everything leans on: **cislunar is the best case on all four settings** (by 1.72× on default cell), and **the programme search never changes the evaluable set** at any destination (N enters nothing in the mass cascade).
- `campaign/run_queue.py`'s `DESTS` holds those five; adding mars_orbit/geo is NOT a one-line edit — there's no frozen Stage-2 catalog for either, and making one means live pricing that wouldn't match the 2026-08-23 prices the other twenty share. Methodology decision, not portability gap.
- `mars_orbit` = control on the ISRU discount (takes BASE utility profile; empty dict is deliberate). `geo` = control on saturation (smallest in-space market at 40,000 kg/yr vs earth_surface's ~10¹⁵ where saturation is numerically inert and 100% of rows run to the fleet ceiling — its searched cells are NOT optima; "raise max_fleet_ships and they keep improving").
- **calc `1.19.2` fixed a latent mars_orbit defect**: `synodic_period_yr`'s second argument was chosen by a conditional testing `== "mars_surface"`, written in two places, so the later-added destination took the else branch and phased launch windows against EARTH — wrong on 99.97% of rows (median synodic 1.2976 yr vs correct 3.3033). Now reads off `DELIVERY_ARCHITECTURES`. General shape: **a conditional that names one member of a set instead of asking the set a question**; defence = put the answer in the table where the destination already declares what it is, and assert the field is total.

## THE DESTINATION TRAP (the classic error)

`delivery_destination` must be set in TWO places and they must agree: `MINERAL_CONFIG.delivery_destination` decides what a kg SELLS for; `CALC_CONFIG.delivery_destination` decides the architecture that PUTS it there. Disagreement = pricing cargo at a depot while paying to land it in Utah.
- Stage 4's `destination_check()` catches it and **shouts on STDOUT** — where a harness is least likely to be listening, and which `grep` for result lines filters away, printing a clean-looking number. This was hit measuring v1.15.0: two figures recorded as "cislunar" were run against earth_surface prices; paired comparisons stayed valid (identical inputs) but LEVELS were not.
- In `master.py` use `MASTER_CONFIG.delivery_destination`, which writes both. **Set the destination explicitly in any harness**; if you must filter stdout, keep `MISMATCH` in the pattern.
- `run_pipeline.py` is the ONE entry point that cannot hit this: its `preflight()` reads the destination Module 2 stamped into the on-disk catalog and REFUSES (exit 2) before a stage starts when Stage 4 would fly elsewhere and Stage 2 isn't in `--stages`. A refusal, not a warning. If you add another Stage-4-only entry point that doesn't go through run_pipeline.py, call `preflight()` from it.
- `CALC_CONFIG.delivery_destination` defaults to `earth_surface`; the on-disk catalog is usually whatever was last run (cislunar). So importing calc and calling straight off gives a mismatched run by default.

## Verification workflow (the six checks)

`verify.py` runs exactly **six** numbered checks: 1 BIT-IDENTITY vs baseline, 2 PRUNE ON vs OFF, 3 SERIAL vs PARALLEL, 4 MASS LEDGER (`hardware_total_kg == rig + power_system_kg + ep_system_kg`; the rig is a CONFIG CONSTANT — writing it verbatim against the CSV raises KeyError), 5 NEVER-WORSE (both invariants at cap 400; `median(1 − r)` convention), 6 STAGE-2 TABLES. Three commands:
```bash
py verify.py baseline --tag 1.17.7   # clean tree, BEFORE editing
# ... edit modules/, py build_master.py ...
py verify.py check --tag 1.17.7      # AFTER; full ~30 min (check 2 dominates: pre-filter off)
```
- `--skip prune parallel` = the ~5-minute loop for fast iteration; `invariants` runs checks 4–6 only, no baseline needed, works on any tree. The `if __name__ == "__main__": raise SystemExit(main())` guard is load-bearing: check 3 starts a process pool and on Windows a worker rebuilds the parent by importing `__main__`.
- Baselines are read back with `float_precision="round_trip"` (the comparator-only rule) and `low_memory=False`; `_comparable()` deliberately does NOT sort columns.
- **A check that cannot run must never say it passed.** The original harness skipped cells absent from baseline with a bare `continue` that never touched ok → missing/partial baseline compared nothing and printed ALL CHECKS PASSED. Now: `*** NOT VERIFIED ***`, names the cells, exit 1. Same shape as an empty mass-ledger cell printing `(no rows)` and passing, or a never-worse join coming back empty and being skipped.
- **`stamp_check()`** (calc 1.17.8): every stage stamps its own `pipeline_version` into every CSV; the loader compares that stamp against the module that WROTE it and shouts, naming each stale file + stage. Makes the one-directional bump rule self-enforcing: a write that silently fails to land is caught next run. Three deliberate limits: diagnostic not import (silent in standalone calc.py); cannot see an edit that didn't bump; cannot tell deliberate lag from failed write — reports the fact, points at the release note. **calc 1.19.1 fixed it crying wolf**: for two releases it compared EVERY catalog against Module 3 including the two Module 3 never wrote (`asteroids`, `minerals`), firing every run with "Re-run Stage 3" — a check that cries wolf toward a DESTRUCTIVE remedy is worse than no check (that's exactly what the stage-2/3 trap section exists to prevent). Fixed via `_CATALOG_PROVENANCE`.
- **`schema_check()`** checks Module-3 COLUMNS and ROWS (`_MODULE3_REQUIRED_OPS` names each row Stage 4 needs + the model term its absence silently reverts). Re-run Stage 3 after upgrading it: a stale `propellants.csv` doesn't raise — tank mass → zero, maturity gate dropped, solids/sails un-excluded, all silent. Editing a number in a Module-3 table leaves schema identical; nothing warned during v1.12.0 and two full-catalog runs were measured against the table being replaced. Cheap habit: Stage 4's loader prints row counts per Module-3 table — read them against what Stage 3 said it wrote; a count that hasn't moved after you added a row is the whole diagnosis.
- **A best-case cell is a poor detector for anything below the top**: v1.12.0's headline cislunar ratios were bit-identical with stale and correct tables because the best mission wasn't affected. The propellant-share breakdown and evaluable-row count are what caught it.

## Docs discipline (after changing any number)

`verify_docs.py` (~1 s, no baseline; 11 checks): documented defaults vs dataclass fields, pipeline_version stamps, reference-table row counts, anchors/links, document structure, em-dash ratchet + the ASCII-prose check (a mechanical rewrite needs a check on what it LEAVES), cross-file manifests (`requirements.txt` against `_MASTER_REQUIRED`; README's option list against `run.bat`'s dispatcher), docstring coverage (every non-path config field carries help — a field added without comment goes red before anyone opens the dashboard), and pinning README's cislunar wall-clock row to calc.py's `MEASURED_CELL_SECONDS`. Run after touching any config field or reference table. **It cannot see a stale measurement, and it cannot see copies that live in code** (`--help` text, run banners, comments all quote runtime ratios).

- The printed cost RATIOS are now DERIVED, not typed: `modules/calc.py` holds `MEASURED_CELL_SECONDS` (four measured cislunar wall clocks) + `beneficiation_cost_ratio()` / `programme_search_cost_ratio()`; every consumer computes from it. Re-measure in one place and every printed ratio moves with it.
- **Grep the prose too**: search for the superseded CLAIM, not just digits — "best case", counts spelled out in prose, the name of whichever destination used to win. `grep -rn "<old number>" --include='*.md' .` (NOT bare `*.md`, which expands to root docs only and misses `campaign/` and `research/`). CLAUDE.md restates README headlines before adding depth — **move both, or neither**.
- **Console text is not output**: comments, banners and `--help` strings don't move a `pipeline_version` (they're not in any CSV) — but they DO live in master.py's templates, so changing them still requires rebuild + commit. The inverse trap: the destination MISMATCH shout goes to STDOUT, which is where it must NOT be filtered away.
- Counts: the general rule is *name the list; do not state its length* — a count nothing checks is a number waiting to rot (three corrections did not stop one). The fix is a checker or a deletion, never a correction.

## THE SAMPLING RULE (canonical)

A sample predicts full-catalog runtime here **to no better than ~5×**, and the misses run BOTH ways (fixed costs dominate small runs; expensive tails under-represented in stride samples). It covers RATIOS between two settings too — four mispredictions, two of them ratios. Budget from a measured full run of the same cell, or don't budget at all. **Memory is the third quantity it covers**: peak RSS tracks output size (8.2→10.4 GB across cells), and a stride sample does not predict a full run's memory either (the 70 M-entry cache showed 18,000 entries on a 400-row cell). The ONE projection that has held: extrapolating a **measured full-catalog speed-up on one cell** to another setting of the same cell — never from stride sample to full catalog. Compounding per-release ratios understates (scored once: three cells within 3%, default cell 20% low) and is still forbidden.

## Known model limitations (do not "fix" one-sided)

- **The outbound Δv is OPTIMISTIC by ~0.4–1.3 km/s** — a standing limitation inherited by the whole 20-cell campaign, documented in README and versions.md rather than fixed: measured against a validated Izzo-Lambert porkchop oracle (research/starred-repos/orbital.py + probe_lambert.py), the closed-form estimator understates on **86% of bodies** (median +1.30 km/s / 11.9%). It simultaneously OVERcharges the plane change by a median 4.87%, and the two errors partially cancel — **correcting only the overcharge makes the model worse in every inclination band**. Neither term moves without the other; both measurements live in research/starred-repos/FINDINGS.md (F1, F4).
- **Nothing is viable anywhere**: best cell 13.1443× short of breakeven — zero profitable asteroids is the honest answer, and the ranking means "which target loses least". Launch is only ~2.3% of a mission; cheap launch does not rescue it. Rank by `total_cost_usd / gross_value_usd` (there is no cost_revenue_ratio column); profit_usd degenerates into a pure cost ranking.
- **Taxonomy reliability**: 90.2% of NEOs have albedo-assumed spectral type; an independent SDSS cross-survey disagrees on ~34% where it overlaps, and the top-ranked bodies join it not at all — comp_* is a distribution reported as a point estimate (the standing argument for pymc credible intervals).
- Launch windows are statistical (synodic), not ephemeris-based; composition uniform per class; beneficiation recovery 0.90 borrowed from terrestrial flotation; refinery priced but not flown; boil-off estimated, not integrated; C-type "ice" is bound water with extraction hardware uncosted; tank mass scales purely with volume (deliberately conservative direction).

## Console output: ASCII only, and the build anchors that depend on it

- **Every `print(...)` in the four modules is pure ASCII** — Windows picks cp1252 for redirected stdout, so any non-ASCII character (emoji were under a fifth of it; box-drawing `─` alone was 1,204 occurrences) crashes `py master.py > run.log` on the first banner. Regression test: Stage 4 pass under `PYTHONUTF8=0 PYTHONIOENCODING=cp1252`, stdout redirected — must exit 0 with empty stderr; re-run after touching any print. Only PRINTED strings were converted (AST-driven); comments/docstrings/data keep non-ASCII because the notes fields are written into CSVs and rewriting them changes bytes. `run.bat` still sets PYTHONUTF8=1 + chcp 65001 as belt-and-braces; that cannot move an output byte (the only bare open() is binary).
- **build_master.py's anchors match on lines the ASCII pass changed**: the install-block anchor is `print\("OK  All packages present"\)` — do NOT "improve" it to `[OK]` (inside a regex that's a character class matching O or K, and the anchor silently stops matching). Every replacement used here is free of regex metacharacters for this reason. Anchor and target change together or not at all.

## Campaign rig (campaign/) details

- `run_cell.py` shells out to run_pipeline.py as a SUBPROCESS: `[sys.executable, run_pipeline.py, --stages 4, --destination <dest>, --rows 0]` — inherits preflight(), can't hit the destination trap; resumable queue in run_queue.py (DESTS = the five measured destinations).
- `results.csv` is the committed measurement record: one row per cell with wall_s, best_obj, winner/vehicle/propellant/conc_ratio/power_source, programme structure (N/fleet/trips/span), payload_kg, saturation, p_mining, aerocapture/rtg/isru shares, full prop_shares + vehicle_shares strings, calc_version and catalog_date. The per-cell gz archives (~350–500 MB each) are gitignored under campaign/cells/.
- Frozen Stage-2 prices live in `campaign/stage2/mineral_value_catalog.<dest>.csv` (one per measured destination).

## Citations that travel with any publication

CITATIONS.md is the authority for references, never values. Two sources require citation as a condition of use: **IMCCE SsODNet/ssoBFT** (Berthier et al. 2023) and **NEOWISE Diameters & Albedos V2.0** (Mainzer et al. 2019, doi:10.26033/18S3-2Z54); the committed SDSS taxonomy table (Hasselmann/Carvano/Lazzaro PDS + Carvano et al. 2010 method paper) is cited as a condition of its use too. Prices are live, so any derived figure is a figure ON A DATE — quote `catalog_date`.

## Runtime anchors (current, calc 1.17.7+)

- Default cislunar run ≈ **1.6 h** (was 6.8 h pre-1.17.x perf line). Every timing/cost ratio older than calc 1.17.7 is high by 1.78–4.32×; beneficiation costs **4.67×**, programme search **1.71×** (cislunar figures; leo/mars_surface/earth_surface cost 2.1–2.7× more per cell).
- Full twenty-cell matrix = **26.1 h**. A full-catalog 2×2 cannot be run inside one calendar date: `catalog_date` is a provenance column, and midnight falling mid-run makes beneficiated cells DIFFER from raw ones on the date alone (strip BOTH `pipeline_version` AND `catalog_date` before hashing two runs).
- Catalog = **1,554,353–1,555,667 rows** (grew 17× at catalog 1.1.0: 89,367 → ~1.55 M; JPL adds bodies daily — a rebuilt catalog is comparable with nothing already measured). Cap `eval_row_cap` for interactive work (it now SAMPLES rather than truncates since calc 1.13.0).

## Config discipline

- Configs are dataclasses instantiated once at module scope. Edit the field default INSIDE the dataclass; mutating `CONFIG.foo` after construction defeats one editable source of truth.
- **A field's comment IS its UI help text, and attachment is POSITIONAL**: `ui_meta.scrape_field_docs` walks UPWARD from a field to the comment block directly above it (stopping at first blank line or section banner) plus a trailing single-line comment on the field's own line. A block explaining two fields but sitting above only the first leaves the second with NO help in the dashboard (39 of 105 fields were once in that state). Fix per field: its own block preceded by a blank line, or a single-line trailing comment — which CANNOT be continued onto the next line (`#` below belongs to whatever comes next).
- `check_defaults_preset()` re-derives the `full` preset's four values from `dataclasses.fields` and shouts if the preset stops matching "THE PIPELINE DEFAULTS".

## Open candidates — useful, not yet implemented (surveyed 2026-09-04; re-verified against source + live APIs 2026-09-07)

Forward-looking items from the star-list audit that would benefit this repo but are NOT used or noted in its docs. None touches committed floats unless explicitly promoted; anything float-moving goes through baseline → edit → check like everything else, and any new dep lands pinned in BOTH requirements files outside modules/' import path. Full source detail: `references/dv-oracles-and-economics-sources.md` (this skill) + `data-science/astro-toolkit-selection/references/catalog-data-sources.md`.

- **NHATS rank cross-check** (research/-level; `scripts/nhats_rank_crosscheck.py` runs it end-to-end against live JPL): JPL NHATS (~7,033 NEAs, round-trip crewed Δv < 12 km/s) is the population-scale external oracle — one keyless call for ~7k bodies. CORRECTION (re-probe #2, same day): Asterank's Shoemaker-Helin `dv` was NOT removed — it survives via targeted queries (`{"name":"Eros"}` → 6.112; `{"pdes":"1999 AO10"}` → 5.380), while bulk-scan projections simply never carry a `dv` key (that is why the first re-probe read it as dead). Asterank stays a per-body spot-check oracle alongside NHATS, not full-catalog (~600K HTTP calls); its economics fields are partially garbage and the query param must be JSON. HF mirror `juliensimon/nhats-accessible-asteroids`. Compare Spearman rank by orbit-quality band (F6 baseline: 0.598 overall, 0.659 at U≤4 vs 0.585 at U≥5); transfer the RANK disagreement only — NHATS is round-trip + constrained, an upper bound on a differently-shaped quantity, never a second estimate of the one-way gap magnitude.
- **Orbit-quality uncertainty as error bars** (supersedes the plain "U cutoff" framing): two verified feeds now make this cheap without any modelling decision about thresholds — NEODyS full 6×6 covariance per body (`astroquery.solarsystem.neodys.NEODySClass.query_object`, one HTTP call each → scope to top-N of ranking) + Asterank's NEW per-element sigma diagonal (σa/σe/σi/... for ~600K bodies, zero extra calls; `scripts/asterank_sigma_probe.py` exercises both API modes and prints live schema notes). Push through the Δv estimator → distribution over cost/revenue ratio per body. Winner's-curse context: 79.5% of JPL's own accessible population is at U≥5 vs 13.9% catalog — a property of the accessible population, not just selection; no ranking change removes it.
- **Gated cross-check script** (brahe and/or skyfield, research/-level): closed-form dv vs numerical per body + exact phase angles → comparison CSV that never feeds ranking math. A lib that changes a committed float is not a cross-check, it's a regression — the gate IS the feature. Install reality verified 2026-09-07: brahe 1.7.0 has a cp311 win_amd64 wheel for THIS machine (no Rust/CSPICE build); native SPICE reader covers **type 21** (the segment Horizons emits for small bodies) + `HorizonsClient.get_spk()` generates targeted per-body kernels (~hundreds of KB, cached) — so F4's two-body error can be bounded on the actually-sampled bodies instead of JPL's pre-integrated set. Keep it beside verify.py, never in `_MASTER_REQUIRED` (compiled extension = a second libm in the room; bit-identity argument).
- **Soft-number audits** (afternoon each, no model change): pipeline vehicle table vs CSIS launch-cost compilation (Falcon Heavy disagrees: 50–64 t cited vs CLAUDE.md's 57 t); lunar utility overrides vs Astromat/EarthChem sample geochemistry; `TAXONOMY_COMPOSITION` metal/carbon fractions vs Wikidata meteorite classes. Each produces a citation or a correction — the cheapest way to find rows that were never checked.
- **Nesvorny families before any pymc work**: ~170K asteroids in 274 collisional families (PDS SBN, `update-nesvorny-families.py`) is the hierarchical structure a prior over spectral_type actually has — fragments of one parent body share composition; F2's flat categorical prior throws that away.
- **SDSS cross-survey at scale**: cheaper than live TAP now verified — PDS serves Carvano et al. 2010 as fixed-width tables with exact colspecs in `update-sdss-taxonomy.py` (107,466 obs rows + 63,468 asteroid rows; note the pds3 path). Converts the manual ~34%-disagreement spot check into a per-body provenance column for every body in SDSS footprint — natural input to the uncertainty layer above.
- **verify.py watchdog + untrusty re-run** (harness-only, zero model change): full run is ~30 min with no timeout — a hang in any check reads as slowness and costs a day silently. Wrap each check (at least prune/parallel) in subprocess.run with per-check time budgets; killed = named failure + non-zero exit (composes with the NOT VERIFIED rule); failed checks re-run at end before the verdict so one bad module can't mask the rest.
- **Run the two missing campaign destinations** (mars_orbit, geo) to complete the 28-cell matrix: prerequisite = frozen stage-2 catalogs for each (live prices wouldn't match the 2026-08-23 cohort); budget from anchors — cislunar default cell 5,692 s, leo/mars_surface/earth run 2.1–2.7× more per cell; mars_orbit should price in the mars_surface class (same heliocentric transfer stopped one leg early). ⚠️ All campaign cells are `charge_insurance=True` measurements — a new default-off run is not comparable to them without setting it True.
- **pymc uncertainty layer on comp_* / price elasticities**: engine selection is NOT interchangeable — NUTS MCMC for a handful of load-bearing global constants (exact-ish posteriors, high cost); ADVI variational inference for per-body comp_* at ~1.5M-row scale (fast approximate). Both PyTensor-based; heavy dep chain, gated + pinned. nutpie (Rust NUTS) auto-selected when installed — big speedup, no code change.
- **MIQP fleet-allocation study** (Pyomo + COIN-OR, BSD-3): "which subset of top-N candidates maximizes net value under N launches/yr and fleet bounds" — calc.py's per-row outputs are exactly the coefficient vector; one-off research script unless a result is promoted. Pyomo mining done 2026-09-12 (see `data-science/optimization-modeling-pyomo`): install reality verified on this box (isolated venv + highspy wheel, MIP solve live), and the exact V2 idiom that works — `import pyomo.contrib.solver.plugins` side-effect import is REQUIRED or solver registration silently doesn't happen; results use `.termination_condition/.incumbent_objective`, NOT legacy `.problem_info`. Piecewise-linear launch-cost curves stay MIP-exact via `contrib.piecewise.incremental` (fewest binaries, n−1) if the study wants non-constant per-launch cost.
- **z3 invariant proofs for harness structure** (one-time + re-run on schema changes): preflight covers every destination pair, mass-ledger identity over config space, window_phasing_au total across all seven destinations — empirical checks catch data regressions, a proof catches the structural class calc 1.19.2 just fixed (a conditional naming one member of a set instead of asking the set).
- **mesa market-dynamics sandbox** (long-term): competing-firm agents against static saturation constants; stress-tests geo's role as the smallest in-space market (40,000 kg/yr anchor) from a fixed number into a process. ⚠️ mesa v3 requires Python ≥3.12 — this box is 3.11; install a second interpreter first.
- **Headless ui.py testing**: Streamlit's `streamlit.testing.v1.AppTest` drives the dashboard without a browser window; destination-seeding logic and runtime estimates are visible-but-untested. (ui.py grew ~600 lines in PR #63 — more surface to test.)
- **Standing non-optimal detector cell in campaign/**: any single-cell regression test is blind to changes that only affect non-winning rows (v1.12.0 lesson); carry one deliberately high-inclination body where F1/F4 errors are largest, since best-case cells never exercise those rows.

## Quick pre-flight checklist before claiming anything about this repo

1. Which working copy? (`ls -d .git && cat .git 2>/dev/null` — a `gitdir:` pointer = Drive setup; confirm branch up to date with remote)
2. `py build_master.py` then `git status` clean (sync check)
3. Destination set explicitly and matching the on-disk catalog (`MISMATCH` absent from stdout)
4. Baseline taken BEFORE edit, `verify.py check` AFTER
5. Provenance columns checked before comparing to committed numbers (`spectral_type_source`, `source_*`)
6. `py verify_docs.py` after touching config fields / reference tables
7. No stage 1/2/3 re-fetch ran since the baseline (it destroys every `.verify` baseline + overwrites the only frozen-input copies)

## References (verified detail lives here, not in this file)
- `references/load-bearing-assumptions.md` — model terms that look wrong but are deliberate; read before "fixing" any result.
- `references/defect-classes-and-traps.md` — the recurring failure shapes (destination trap, sampling rule, NOT-VERIFIED discipline).
- `references/data-sources-environment-entrypoints.md` — data sources, dirty-tree behavior, cross-host notes, entry points.
- `references/dv-oracles-and-economics-sources.md` — external Δv oracles (NHATS; Asterank schema change 2026-09-07) + the nine soft-assumption data sources with exact fetch specs. Companion: `data-science/astro-toolkit-selection/references/catalog-data-sources.md`.
