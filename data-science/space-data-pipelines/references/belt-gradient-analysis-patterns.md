---
description: "Debiasing an asteroid taxonomy analysis (loggger101/asteroid-belt-gradient): published-labels-only rule, family collapse, size-complete vs inverse-completeness weighting, KS+Bonferroni, reproducibility layout; headline numbers"
source_repo: loggger101/asteroid-belt-gradient (analysis code for L. Edwards 2026, Florida Tech)
tested_version: README read via GitHub API @ main; package not re-run here (needs a ~280 MB fetch); H-to-diameter arithmetic re-computed locally
verified_date: "2026-10-05"
---

# Debiased taxonomic analysis of the main belt: patterns that transfer

The repo tests whether the belt's S-to-C compositional gradient is primordial or an artefact, on 161,659 main-belt asteroids with a published taxonomy from the
`AsteroidCatalog` release (1,568,641 bodies; merges JPL SBDB, SsODNet, NEOWISE, MP3C) plus Nesvorny HCM families. It is the user's own analysis, so this note records its
methodology as reusable rules for any catalog-derived population statistic.

## Rules, in the order they bite

1. **Count only labels that are measurements.** 83% of the catalog's taxonomy labels were derived from an albedo *assumed from semimajor axis* and then thresholded; using them returns the gradient by construction. Filter on the provenance column (`spectral_type_source == "source"`: mostly SkyMapper and SDSS colours). General rule: before computing a trend of X vs Y, check whether X was itself imputed from Y.
2. **Group classes deliberately and say how.** First-letter groups: S-like = S,Q,A,V,R,O; C-like = C,B,F; D/P = D,P,T,Z; K/L separate; X (X,M,E) excluded because the class is ambiguous in composition. Report a narrow fraction C/(S+C) and a broad one (C+D/P+K/L)/(all but X).
3. **Collapse families, do not delete them.** A collisional family is one parent, so its members are not independent draws. Each family becomes one body: class = most common among at least 3 labelled members (X-types not voting; fewer labels or a tie takes the largest member's label), diameter from the summed D^3, orbit of the largest member. A body in two families goes to the larger; duplicate member lists in the source bundle count once.
4. **Limit samples by size, not brightness.** Two complementary estimators: a **size-complete** cut (completeness limit H_c = 10.5, which is D >= 52.8 km for albedo p = 0.04 using D = 1329 km * p^-1/2 * 10^(-H/5)) and **inverse-completeness (Horvitz-Thompson) weighting** at D >= 10 km. Re-computed: H = 10.5 gives 52.78 km at p = 0.04 and 21.11 km at p = 0.25, so the same H maps to very different sizes by albedo; that is why a brightness cut biases a composition study. Catalog H for small asteroids runs about 0.4-0.5 mag too bright near H = 14 (Pravec et al. 2012): at p = 0.04 that turns a nominal 10.53 km into about 8.76 km, shifting both estimators.
5. **Make the optional correction switchable and show it does not matter.** One-step family extension (attaches 197,421 more bodies by HCM distance) is off by default; turned on, no zone fraction changed by more than 0.01 and the crossover moved by under 0.02 AU.
6. **Use a conservative test and name the exception.** Orbit tests are KS only with Bonferroni over 8 tests (p < 0.00625). One passed (outer-belt sin i, p = 0.006), traced to the Themis and Eos family halos; with extension on none passed (smallest p = 0.011), so it is reported as family halos, not class-dependent excitation.

## Headline numbers (from the README)

| C/(S+C) | inner 2.1-2.5 AU | middle | pristine | outer to 3.3 AU |
|---|---|---|---|---|
| raw count | 0.25 | 0.35 | 0.40 | 0.70 |
| families collapsed, IPW, D >= 10 km | 0.53 | 0.63 | 0.77 | 0.90 |
| families collapsed, D >= 53 km | 0.39 | 0.69 | 0.70 | 0.89 |

S/C crossover: 2.84 AU raw, 2.41-2.47 AU once corrected, with a 10-to-90% transition 1.4-1.5 AU wide, wider than the belt. Every number the paper derives lives in `results/summary.json` with bootstrap intervals.

## Reproducibility layout worth copying

- `config.py` holds every knob (belt limits, zones, completeness threshold, size cuts, seed 4045); one RNG seeded once.
- `fetch.py` downloads and sha256-verifies pinned inputs (a dated catalog release tag, a PDS bundle with DOI); `data/` is git-ignored and `BELT_GRADIENT_DATA` relocates it.
- `pipeline.py` runs the whole analysis in order and rewrites `figures/` and `results/summary.json`; with pinned inputs it reproduces the committed JSON **bit for bit** (figures too under the stated Matplotlib version). A run takes about 1.5 minutes after the 280 MB fetch.
- A table mapping each paper figure and table to the function and file that produce it; fast unit tests on synthetic inputs (`conftest.py`) plus a `-m slow` test of the real run; `examples/walkthrough.py` prints the intermediate tables without overwriting outputs.
- Citation hygiene: required citations for merged sources (SsODNet, NEOWISE V2.0) are listed with DOIs and the standard acknowledgement; `CITATION.cff` present.

## Connections to other skills

`bit-identity-float-pipelines` (the bit-for-bit claim and its host limits), `open-data-catalog-sources/references/space-data-licensing-audit.md` (citation conditions for catalog sources), `economicspace-pipeline` (consumes the same catalog; its composition priors come from taxonomy, so rule 1 applies to any prior built from `spectral_type`).
