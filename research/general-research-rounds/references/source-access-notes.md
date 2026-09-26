# Source access notes (verified from this machine)

Fetch patterns for the source classes used in General_Research rounds. These are observations, not guarantees — re-verify when a route starts failing.

## NTRS (ntrs.nasa.gov) — primary workhorse
- `api.ntrs.nasa.gov` is DNS-dead, but the web host serves the same API (R43): `https://ntrs.nasa.gov/api/citations/<DOC_ID>` returns the JSON record and `.../downloads/<file>` streams the PDF (and a text export).
- Full-text PDFs: `https://ntrs.nasa.gov/api/citations/<DOC_ID>/downloads/<DOC_ID>.pdf` — direct urllib with a Mozilla User-Agent works. The file name is not always `<DOC_ID>.pdf` (e.g. 20210024709 ships `SciTech_2022_Edquist_M2020_FINAL_112321_opt.pdf`); take it from the JSON record's downloads list.
- Hostability: NASA-authored work is public domain → legally hostable in `full_texts/`. For contractor or journal-derived records, check the JSON record's copyright `determinationType` first (R54 saw `PUBLIC_USE_PERMITTED`).
- The single-citation JSON is sparse for older records; authors and dates may only be on the HTML page. Citation/metadata pages (`/citations/<ID>`): web_extract returns 403; fetch the HTML directly with urllib + `Mozilla/5.0 (Windows NT 10.0; Win64; x64)` UA and parse title/authors/date by regex.

## NASA OIG (oig.nasa.gov)
- Audit reports download directly as PDFs (`https://oig.nasa.gov/docs/IG-22-003.pdf`, or `.../wp-content/uploads/<yyyy>/<mm>/ig-24-001.pdf` for newer ones) — public NASA documents, hostable. Register the report number in the id (e.g. `nasa_oig_2021_ig-22-003_...`).

## JPL DSN rates
- The DSN aperture-fee calculator at `dse.jpl.nasa.gov/ext/` computes server-side and exposes no API; the rate base comes from the DSN Services Catalog 820-100 PDF on nasa.gov, carried to current dollars with BLS CPI-U actuals.

## ADS (ui.adsabs.harvard.edu)
- Blocks plain urllib GET (HTTP 405). web_extract on the `/abs/<bibcode>/abstract` page works and returns the full abstract + publication metadata — use it for AGU/AAS-family records where the publisher site is bot-blocked.

## AIAA (arc.aiaa.org)
- Article pages are paywalled/bot-blocked from this machine. Register as `open_not_pulled` with abstract-level findings; third-party excerpts may confirm an abstract's claims but never justify hosting.

## Vendor datasheets (e.g., ulalaunch.com)
- Official vendor PDFs are usually direct-downloadable via urllib + browser UA. They anchor "official spec" numbers at T2 tier — cite them as the operator's own published capability range and note which end of a range our CSV cell uses.

## Discovery fallback
- web_search can fail mid-session (backend 403). When it does, pivot to direct fetches of known/stable URLs from prior rounds or site-scoped queries on whatever backend is up — don't stall the round on discovery. NTRS document IDs are stable and reusable across rounds.
