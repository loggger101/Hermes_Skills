---
name: open-data-catalog-sources
description: "Keyless data mirrors, data.gov API, licence checks."
version: 1.0.0
author: Hermes Agent (promoted from space-data-pipelines references, 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [open-data, huggingface, data-gov, catalog, licensing, cc-by, redistribution, space-data]
    related_skills: [space-data-pipelines, economicspace-pipeline, orbital-mechanics-data, pinned-data-contracts, huggingface-hub, duckdb-querying]
---

# Open-data catalogs, mirrors and licences

## What This Skill Does

Finds public datasets without API keys and decides whether they may be redistributed. It holds three live-checked references: the ~230 keyless Hugging Face mirrors of space and astronomy feeds (`juliensimon/*`), the catalog.data.gov search API after its CKAN endpoints were removed, and the licence audit that shows many "public" sources are not CC-BY. Pipeline construction (one script per dataset, parsers, scheduling) stays in `space-data-pipelines`.

## When to Use

- Needing a dataset from a feed that requires keys, per-object calls or a dead endpoint, and a mirror would do
- Searching data.gov for a government dataset, or a script that used `/api/3/action/*` now returns 404
- About to publish or redistribute data fetched from ESA, VizieR, WDC Kyoto, SILSO, AAVSO, CelesTrak or the Minor Planet Center
- Not for building the ingestion pipeline (`space-data-pipelines`), orbit and ephemeris libraries (`orbital-mechanics-data`), or pinning a frozen release with checks (`pinned-data-contracts`)

## Procedure

1. Look for a keyless mirror first (`references/hf-mirror-catalog.md`); load it with `datasets.load_dataset("juliensimon/<name>")` or read the parquet files directly.
2. For government catalog search, use `/search` with cursor pagination and look up `org_slug` values in `/api/organizations` (below and in `references/data-gov-catalog-api.md`).
3. Before redistributing, look the provider up in `references/space-data-licensing-audit.md` and read the provider's own policy page, not the dataset card.
4. When unsure between `cc-by-4.0` and `other`, label `license: other` with the licence name and upstream link.
5. Record in provenance: request URL, harvest date or snapshot date, dataset identifier, and the licence text relied on.

## Keyless HF mirrors of the same feeds (see `references/hf-mirror-catalog.md`)

~230 datasets under `juliensimon/*` on Hugging Face — no API keys, one-line load. Useful as frozen snapshots for cross-checks/backfills when the live feed needs auth (Space-Track), per-body calls (Asterank dv), or has dead endpoints (UCS). Cadence: ~50 daily / ~20 weekly / rest static; upstream `status.json` tracks dates + row counts.

## data.gov catalog API (see `references/data-gov-catalog-api.md`)

catalog.data.gov (515k+ datasets, incl. NASA planetary science) **dropped the CKAN `/api/3/action/*` endpoints** (404 on 2026-10-05). Use `GET /search?q=...&per_page=...&after=<cursor>`
(cursor pagination, no total count) and `/api/organizations` for valid `org_slug` values (NASA is `nasa`; a wrong slug returns an empty 200). Many records have no machine-readable distribution.

## Licensing redistributed space data (see `references/space-data-licensing-audit.md`)

Default "NASA/ESA public API ⇒ CC-BY-4.0" is **wrong** for a large fraction of providers: ESA Space Science Archives = **CC BY-NC 3.0 IGO** (no commercial use), WDC Kyoto geomagnetic indices no-commercial, SILSO sunspot numbers CC BY-NC 4.0, AAVSO NC-only, and VizieR's own terms are "scientific context" — not CC-BY at all. The source license travels with the data: fetching ESA catalogs via VizieR/HEASARC mirrors does NOT strip the restriction. When unsure, label `license: other` + upstream policy link rather than over-permissive cc-by-4.0.


## Pitfalls

- A mirror lags its live feed by its update schedule; treat row counts as "as of last refresh".
- A wrong `org_slug` returns an empty result with HTTP 200, not an error.
- A data.gov distribution entry is often an HTML project page, not a file; check `format` and `mediaType`.
- Believing a dataset card's licence: 30 of 222 cards in the upstream audit were wrong.
- Assuming a mirror changes provenance: the source licence travels with the data.

## Verification

- [ ] The data source and its snapshot date are recorded
- [ ] Each provider was checked against its own policy page before redistribution
- [ ] Any restrictive dataset is labelled `license: other` with a link
- [ ] No script depends on `/api/3/action/*` for catalog.data.gov

## References

- `references/hf-mirror-catalog.md` - all keyless Hugging Face space, astronomy and physics mirrors, grouped by domain, with update cadence and the economicspace picks
- `references/data-gov-catalog-api.md` - catalog.data.gov search API: endpoints, response shape, verified traps, minimal client
- `references/space-data-licensing-audit.md` - provider-by-provider licence risk table and the process rules from the upstream audit
