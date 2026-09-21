# Source access notes (verified from this machine)

Fetch patterns for the source classes used in General_Research rounds. These are observations, not guarantees — re-verify when a route starts failing.

## NTRS (ntrs.nasa.gov) — primary workhorse
- Full-text PDFs: `https://ntrs.nasa.gov/api/citations/<DOC_ID>/downloads/<DOC_ID>.pdf` — direct urllib with a Mozilla User-Agent works. US-government work, public domain → legally hostable in `full_texts/`.
- Citation/metadata pages (`/citations/<ID>`): web_extract returns 403; fetch the HTML directly with urllib + `Mozilla/5.0 (Windows NT 10.0; Win64; x64)` UA and parse title/authors/date by regex.

## ADS (ui.adsabs.harvard.edu)
- Blocks plain urllib GET (HTTP 405). web_extract on the `/abs/<bibcode>/abstract` page works and returns the full abstract + publication metadata — use it for AGU/AAS-family records where the publisher site is bot-blocked.

## AIAA (arc.aiaa.org)
- Article pages are paywalled/bot-blocked from this machine. Register as `open_not_pulled` with abstract-level findings; third-party excerpts may confirm an abstract's claims but never justify hosting.

## Vendor datasheets (e.g., ulalaunch.com)
- Official vendor PDFs are usually direct-downloadable via urllib + browser UA. They anchor "official spec" numbers at T2 tier — cite them as the operator's own published capability range and note which end of a range our CSV cell uses.

## Discovery fallback
- web_search can fail mid-session (backend 403). When it does, pivot to direct fetches of known/stable URLs from prior rounds or site-scoped queries on whatever backend is up — don't stall the round on discovery. NTRS document IDs are stable and reusable across rounds.
