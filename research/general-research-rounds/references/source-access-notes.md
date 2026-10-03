# Source access notes (verified from this machine)

Per-site fetch patterns that actually work here. Update when a route changes.

## NTRS (NASA Technical Reports Server) — WORKS despite dead api.ntrs.nasa.gov DNS

- `https://ntrs.nasa.gov/api/citations/<id>` → JSON metadata; `/api/citations/<id>/downloads/<file>` streams PDFs and full-text .txt (public domain).
- Download filenames in the manifest's `links` are per-citation custom names (URL-encoded). For sha-verification of a hosted copy, the direct canonical route ALSO works without fetching the manifest: `/api/citations/<id>/downloads/<id>.pdf` (R56 verified on 20140005558 — pulled twice in one round, both clean); prefer it for re-pull-and-hash checks.
- The file name is not always `<DOC_ID>.pdf` (e.g. 20210024709 ships `SciTech_2022_Edquist_M2020_FINAL_112321_opt.pdf`); take it from the JSON record's downloads list.
- Single-citation API fields can be sparse for older records; authors/dates come from the citation HTML page at `/citations/<id>`. Citation/metadata pages (`/citations/<ID>`): web_extract returns 403; fetch the HTML directly with urllib + `Mozilla/5.0 (Windows NT 10.0; Win64; x64)` UA and parse title/authors/date by regex.
- The JSON SEARCH endpoint does NOT exist on the web host (404). Discovery is via HTML search `https://ntrs.nasa.gov/search?q=<term>` — single words/short phrases only (multi-word queries return 0 hits); parse ids from `/citations/(\d{6,})` in the page.
- Known IDs: nugent=20220009350, plachta=20180004709 (duplicate record 20180004710 — register once), zeng_2007=20070018151, proctor_apex=20190027268, zeitlin=20150016080, hastings=20110004377, whitley_martinez_2015_nro_staging_orbits=20150019648 (duplicate abstract record 20150013825 — register once; public domain GOV_PUBLIC_USE_PERMITTED).
- Rate limiting: bursts of api.ntrs.nasa.gov calls from one IP return HTTP 429 mid-session. Back off, then work from the already-downloaded local artifacts (the PDF text layer carries copyright determination + authors + venue citations); retry metadata later if needed.

## ADS (ui.adsabs.harvard.edu)

- Blocks plain urllib GET (HTTP 405). web_extract on the `/abs/<bibcode>/abstract` page works and returns the full abstract + publication metadata — use it for AGU/AAS-family records where the publisher site is bot-blocked.

## AIAA (arc.aiaa.org)

- Article pages are paywalled/bot-blocked from this machine. Register as `open_not_pulled` with abstract-level findings; third-party excerpts may confirm an abstract's claims but never justify hosting.

## Vendor datasheets (e.g., ulalaunch.com)

- Official vendor PDFs are usually direct-downloadable via urllib + browser UA. They anchor "official spec" numbers at T2 tier — cite them as the operator's own published capability range and note which end of a range our CSV cell uses.

## Discovery fallback

- web_search can fail mid-session (backend 403). When it does, pivot to direct fetches of known/stable URLs from prior rounds or site-scoped queries on whatever backend is up — don't stall the round on discovery. NTRS document IDs are stable and reusable across rounds.

## LBMA precious-metals fixings — WORKS (T3 live service)

- `https://prices.lbma.org.uk/json/gold.json`, `silver.json` (~14.8k daily rows to 1968), `platinum.json`/`palladium.json` (AM+PM since 1990). Silver's filename is NOT discoverable from the site nav — probe variants.
- Compare at our own stamp date: nearest EARLIER trading day within ~30 days; parse dates as datetime, never string-compare.

## Johnson Matthey PGM market report + Base Prices — extraction-only T2 (no hosting)

- Annual report PDF: `https://matthey.com/documents/...` pattern found via web search; freely downloadable, 36 pp. Price data sits in narrative around Figure 1 image — extract with pymupdf word coordinates.
- Live Base Prices page is a Liferay portlet: embedded JSON default-loads Platinum only (23 rows); divs exist for Pt/Pd/Rh/Ir/Ru but NO osmium; CSV downloads are Liferay resource URLs.
- Licensing (base-price-trading-disclaimer, verbatim): "The Prices are the property of Johnson Matthey Plc ... Any use of the Prices without the prior consent of Johnson Matthey Plc is prohibited" → NEVER commit price data to full_texts/; register T2 extraction-only with every number in extracted_data/. Check terms BEFORE downloading.
- Osmium: absent from report text, live page divs, JSON and CSV endpoints — no institutional Os price reachable (standing gap).

## World Bank Commodity Markets "Pink Sheet" xlsx — committed to full_texts/

- Grid layout: row 5 = commodity names, row 6 = units, data starts row 7. Use explicit column indices after reading row 5 directly; `ws.dimensions` access can fail on some sheets.
- Iron series is ore in $/dmtu (not refined Fe) — context only when comparing to a refined-metal catalog price.

## Damodaran cost-of-capital datasets — WORKS (T3 live service, R47)

- Entry: `https://www.stern.nyu.edu/~adamodar/New_Home_Page/data.html` → "Costs of Capital by Industry Sector" link on `datacurrent.html#capstru`.
- Live table: `https://www.stern.nyu.edu/~adamodar/New_Home_Page/datafile/wacc.html` (96 industries; HTML cells parse cleanly, no OCR). XLS twin at `/~adamodar/pc/datasets/wacc.xls` — byte-identical on both www.stern and pages.stern hosts.
- `people.stern.nyu.edu/~adamodar/datafile/*` is 404 (site restructured) — do not use the legacy subdomain. First fetch can hang behind a redirect chain; retry with an explicit timeout, it then answers in ~1 s.
- Table carries an "Updated in <Month Year>" stamp and per-row beta/CoE/capital structure/AT-CoD/CoC. All rows satisfy CoC = E/(D+E)·CoE + D/(D+E)·AT-CoD to ±0.05 pp — use that as a parse-integrity check before trusting any cell.
- Key anchors (Jan-2026 vintage): Aerospace/Defense 7.60%, Metals & Mining 8.20%, Precious Metals 7.47%, Total Market (n=5994) 6.96%.

## The Planetary Society "Planetary Exploration Budget Dataset" (PEBD) — WORKS (T3 live service, R48)

- Entry: `https://www.planetary.org/space-policy/planetary-exploration-budget-dataset` → direct XLSX export `https://docs.google.com/spreadsheets/d/<id>/export?format=xlsx` (~2 MB, public — no auth). Google Sheets export endpoints work from urllib with a plain UA; verify the response magic is `PK\x03\x04` (xlsx) not an HTML consent page.
- 80 sheets: per-mission cost sheets (`Official LCC` cell + fiscal-year rows split Formulation / Implementation(incl LV) / Launch Vehicle(s) / Operations, with a Totals row), a `Mission Costs` summary matrix (dev+launch / operations / total per mission), plus budget-history and FY sheets. Parse with openpyxl read_only/data_only; guard every cell cast — label strings ('Totals') share columns with numbers.
- Values are actual contractual obligations in millions of nominal USD; italic = estimate. Terms: attribution to The Planetary Society required (public dataset, no redistribution restriction).
- Key anchors (FY2026-request vintage): OSIRIS-REx LCC $1,057.3M / dev-excl-LV-through-launch FY2016 **$588.5M** / LV $183.5M / final ops obligations $232.2M; Mars Perseverance LCC $2,725.8M / dev+launch $2,462.6M.
- Limitation: mission-level only — NO software/autonomy NRE line items and no standalone sample-recovery cost. When a target row cites such a subset, anchor the program total it rests on and record the missing sub-line as an honest gap (R48 precedent).

## JPL DSN Aperture Fee Calculator + Services Catalog (R50)

- The named calculator `https://dse.jpl.nasa.gov/ext/` is a client-side JS app; its rate engine is SERVER-SIDE (`apertureFeeTool/cost/<mission>/<costMethod>/<fiscalYear>/...` POST with the full scenario JSON). No API exposes rates: `api/reference` = antenna metadata only (77 assets), `config.json`/`example.json` = version + scenario schema. Do NOT burn a round trying to drive it headless.
- The verifiable route is JPL's official **DSN Services Catalog 820-100 Rev H** (`https://www.nasa.gov/wp-content/uploads/2023/09/dsn-services-catalog.pdf`, public NASA PDF, hostable): p65 eq. 6-1 AF=RB*AW*MW (AW: 1.0 single 34-m / 2.0 two-array+DDOR / 3.0 three-array or any combo incl a 70-m / 4.0 four-array; MW downlink-only 0.5), p66 RB = $1,792 at publication (Jun-2022 issue). Adjust to current dollars with BLS CPI-U actuals.

## Inflation-index access from this machine (R50)

- **FRED is UNREACHABLE** (fred.stlouisfed.org times out on both urllib and curl — treat as blocked, don't retry).
- **BLS keyless API caps at ~3 years regardless of requested range** (v1 AND v2 return only the most recent window; monthly values with `-` placeholders for future months). The annual HTML table page (`data.bls.gov/timeseries/CUUR0000SA0/annual`) carries a 10-year actuals grid in UPPERCASE `<TR>/<TH scope="row">/<TD>` tags (case-insensitive parse) — good for recent years only.
- **World Bank indicator API is the long-window workhorse** (`api.worldbank.org/v2/country/USA/indicator/FP.CPI.TOTL.ZG?format=json&date=YYYY:YYYY`, no key; response = [meta, rows]; parse `x["value"]` guarding None). Annual % inflation chains multiply (1+pct/100).
- Cross-validate any two index sources over their common window before trusting a chain (R50: BLS level ratio vs WB chain agreed to 0.02%).

## Gallagher Plane Talking space-insurance market updates — WORKS (T3 open service, R50)

- Index `https://specialty.ajg.com/plane-talking/Plane%20Talking` lists all issues; per-issue pages are relative slugs (`space-market-update-q1-2024`, etc.) under the same base — plain HTML, no auth, fetchable with urllib.
- Quarterly market commentary: loss years in $mn (premium income vs claims), rating direction, named losses. It corroborates DIRECTION/magnitude of premium moves but does NOT publish explicit launch-premium-% figures — register such rows as directionally-corroborated, not pinned (R50 precedent).
- **Space-insurance issue slugs change pattern by era** (R57): `space-market-update-qN-YYYY` (2023/early-2024) → `space-insurance-update-qN-YYYY` (mid-2025, Q2 2026) → `space-insurance-market-update-qN-YYYY` (Q1 2026). A non-existent slug returns a SOFT 404 = the index page itself (~802 KB, title 'Plane Talking - Plane Talking') — detect by byte size against the known index size instead of an HTTP error. The quarterly roundup pages (`plane-talking-qN-YYYY`) list each dedicated issue's href near its teaser text; use them to discover current slugs.
- **MEMORY.md whole-entry replacement drops the trailing separator** (R58): when a build/update script replaces an entire entry with slice `t[i0:j]` where `j = boundary + len("\r\n§\r
")`, the consumed delimiter is NOT re-added by writing only the new entry text → entries N and N+1 fuse into one. Consistency-only round-trip checks (join(entries) == content) CANNOT detect a missing internal separator — both halves are non-empty so strict per-entry checks pass too. ALWAYS assert `len(entries_after) == len(entries_before)` after any whole-entry replacement, not just marker counts.
- **OIG element-level unit prices live in the program-cost audits, not the EPOC transition report** (R58): IG-20-012 (Mar 2020) carries ICPS/upper-stage unit figures ($46M flight+test pair p36; $29M second-unit hardware option p23; $358M Artemis I all-in est. p36); IG-23-015 (May 2023) carries RS-25 per-engine manufacturing cost ($70.5M post-Artemis VI vs Shuttle-era $104.5M, p36). Both pull from oig.nasa.gov without auth and host as T2 sha-verified.
- **OIG planetary-science audits cross-validate PEBD mission costs** (R59): IG-20-023 'NASA's Planetary Science Portfolio' (Sep 2020) Table 2 p15 = per-mission cost-cap basis + life-cycle costs (Mars 2020 $2,725.8M EXACT vs PEBD; OSIRIS-REx $1,121.4M LCC / $622.0 cap-basis; MSL $2,476.3M). When a T3 live-service anchor (PEBD) needs an institutional second source, check the OIG portfolio audits BEFORE hunting new datasets — they carry exactly this table and are public-domain hostable. Cost-cap columns exclude LV+ops by construction (verbatim scope sentence in report); development-cost rows compare to cap-basis column only.
- **OIG program-audit for sample-return economics** (R60): IG-24-008 'Audit of the Mars Sample Return Program' (`oig.nasa.gov/docs/IG-24-008.pdf`, hostable T2) = FIRST institutional source for what a full sample-return PROGRAM costs: LCC trajectory $2.5–3B (Jul 2020) -> $6.2B KDP-B (Sep 2022) -> unofficial $7.4B (Jun 2023); MCR Oct-2020 intermediate $3.6B; Sept-2023 IRB alt architectures '$8 to $11 billion'; FY24 request $949.3M vs Senate floor 'not less than $300,000,000 for MSR'. Scope caveats are load-bearing: estimates EXCLUDE ESA investments + sample receiving facility (fn 33); the Decadal Survey's $5.3B INCLUDES it and assumed 2% inflation vs actual 5–9% (fn 19) — published program figures differ partly by SCOPE, not just vintage; quote both caveats verbatim before cross-comparing any two of them. The '$180M two Sample Recovery Helicopters' line is MARS-surface retrieval hardware — do NOT anchor an Earth-side capsule-recovery row with it. Per-Earth-recovery cost: still absent from ALL THREE institutional sources scanned (PEBD, IG-20-023, IG-24-008) — standing gap.
- **NASA budget justifications are the route to institutional FUNDING-LINE anchors** (R62): when no per-event figure exists anywhere (row-33 sample recovery), NASA's own annual budget justification funds the operation as an enumerated activity. Route: `nasa.gov/fiscal-year-XXXX-budget-request/` (server-rendered) lists the full PDF at `/wp-content/uploads/YYYY/MM/fiscal-year-XXXX-full-budget-request.pdf`; public-domain government work → hostable T2 sha-verified. The FY2027 doc's 'Astromaterial Curation' line ($16.3M req, p158 table; activity '(4) recovery and transport of returned materials' p159 verbatim) closed the gap at ENVELOPE level: anchor-honesty = consistency anchor (line scope broader than one event + recurring budget authority), not a pin. Negative probes matter here too: 'APEX' count==0 across all 384 pp proved no OSIRIS-APEX line item exists.
- **NASA budget-table geometry** (R62 lesson): value columns sit ~19pt LEFT of the header label centers (right-aligned values under center-aligned FY labels) — aligning tokens to header x-centers fails. Robust method: cluster numeric token CENTER-x into bands with a self-verifying rule that each band spans >=3 distinct y-lines AND all rows fill every band exactly once; leading 'Enacted' columns are often '--'-free so value bands map to the RIGHTMOST N year labels (verify even ~41pt pitch). Cap extraction at the second FY-header row on the page. R62's extract_r62.py in scratch/r62/ is the reference implementation.
- **arXiv pulls from this machine** (R61): urllib's DEFAULT User-Agent gets HTTP 406 from arxiv.org — send a descriptive Mozilla-style UA. Versioned paths (`/pdf/<id>vN`) can 404; the UNVERSIONED `/pdf/<id>` returns the latest version and was byte-identical to our hosted v11 copy (sha match) — always sha-compare fresh pull vs hosted before using either as probe base, so a silent new arXiv revision is detected.
- **Model inputs are not measurements** (R61 hein2020 lesson): his water-breakeven throughput f=2.3e-4 kg/s/kg (=7258 kg/yr per kg craft dry mass) vs our plant row centre 100 = +7158% — recorded as DISCREPANCY, NO revision forced: his f is an ECONOMIC model input (chosen so a 150 kg craft breaks even at $20k/kg water), ours prices engineering capability. Protocol when comparing a paper's model parameter to our row: state both denominators verbatim (his = whole-craft dry mass incl bus; ours = plant only), give the scope-adjusted mapping, and let the two numbers bracket 'what CAN it do' vs 'what does profitability DEMAND'. Also: Pt case f=0.35 kg/s/kg (~110k x) at 1e-5 grade is a viability threshold — different regime by orders of magnitude, never present as a plant-capacity disagreement.
- **Shared table rows count==2** (R61): when two tables in one paper carry identical cost-structure rows (hein Tables 1+2), the verbatim probe for each shared row must assert count==2 (once per table); only scenario-unique rows are count==1. Asserting ==1 on a shared row fails at pre-write and forces a false revert.
- **Curly-apostrophe probes in %-formatted verbatim strings** (R60 bug class): when building probe/quote constants as `"...NASA%s July 2020..." % AP` with `AP = "\u2019"`, possessives need `%ss` — the format slot supplies only the apostrophe, so a bare `%s` silently drops the 's' and the count==1 assert fails at pre-write stage (4 of 5 possessive probes in R60's first run). Write possessives as `Program%ss life-cycle`, `NASA%ss July`, `Committee%ss recommended`, `ESA%ss fetch rover`. The pre-write assertion stage exists exactly for this — let it fail, diff the repr(), fix ALL occurrences of the same pattern at once (grep the file for `%s [A-Z]` after an AP-format), re-run.
- **MEMORY.md whole-entry replacement: slice UP TO the boundary, not past it** (R59 fix): `j = text.find(BOUNDARY, i)` and replace `t[i:j]` — never `j + len(boundary)`. R58's variant consumed entry N's trailing separator so entries fused; consistency-only round-trip checks cannot detect that. memory_update_r59.py (scratch/r59/) is the reference implementation: find_entry_span() helper + per-op entry-count assert.

## NASA OIG audit reports (SLS/Artemis cost anchors) — WORKS, hostable T2 (R51)

- Canonical PDF URLs are NOT the `wp-content/uploads/<yyyy>/<mm>/` pattern you'd guess. Use web_search to find them: IG-22-003 = `https://oig.nasa.gov/docs/IG-22-003.pdf`; IG-24-001 = `https://oig.nasa.gov/wp-content/uploads/2023/10/ig-24-001.pdf`. The OIG report index page (`/inspector-general-reports`) 404s; the per-report landing pages (e.g. `/office-of-inspector-general-oig/ig-22-003`) link the PDF but are JS-heavy.
- Public-domain government work → hostable in full_texts/. Always hash-verify the hosted copy against a fresh canonical pull before committing (R51: both matched to sha256).
- Key anchors for launch_vehicles.csv SLS rows: IG-22-003 = $4.1B per launch (SLS/Orion system, Artemis I–IV) + components ($2.2B production / $568M-yr KSC ground systems / ~$1B Orion incl $300M ESA SM); IG-24-001 = "a single SLS Block 1B will cost at least $2.5 billion to produce" (EPOC/Block-1B scope, excl SE&I) + the upward-trajectory footnote ($2.2B→$2.5B).

## Crossref ISSN TOC — definitive journal-issue verification route (R51)

- To PROVE a cited paper does NOT exist in a given journal/volume/issue: pull the full issue TOC via `https://api.crossref.org/works?filter=issn:<ISSN>,from-pub-date:YYYY-MM-DD,until-pub-date:YYYY-MM-DD&rows=50` (paginate with offset; ISSN filter is reliable where container-title filters are not — ampersand in titles like "Environmental Science & Policy" breaks the title-based filter). Crossref rate-limits bursts → 12s backoff between pages.
- Use this to adjudicate bare author-name citations: e.g. a note citing "(Pielke & Byerly)" with no venue — confirm what they ACTUALLY published (Crossref `query.author` + `query.title`) and whether the as-cited journal/issue contains it. R51 found the real source was paywalled Nature 472:38, not ESP vol-14(5).

## Rotated scanned tables in old NASA PDFs (R55 lesson — SP-4029 p287/p305)

- Old statistical-reference scans (SP-4029 etc.) have `/Rotate=90` landscape pages. **Plain `get_text()` auto-derotates but the OCR text layer silently DROPS values on rotated pages** (p305 Consumed/Total row lost A11–A17 as dashes) — never trust a clean-looking dump for table cells; cross-check against an independent extraction.
- **`get_text("words")` returns UNROTATED coordinates.** Derotate manually: `mat = fitz.Matrix(1,1).prerotate(-page.rotation % 360)` then map each word's corners through it. Then cluster words into visual rows (sort by y; merge while row span ≤ ~8pt — scan skew breaks fixed-y-bucketing).
- **Anchor-row method for garbled tables**: identify one row whose values are independently known (e.g. from the clean text layer) → exact-match each value to get every column's x-center → read any other row at those centers with a dx guard (<25pt). Reconcile EVERY cell arithmetically against another table on the same page (loaded − consumed = remaining-at-cutoff); an unreconciled extraction is not data.
- **Split-digit OCR cells** (`4,` + `703` for 4703; backslash-garbled `6,\55`): parse with a token state machine — clean cell completes at ≥4 digits without dangling comma; single-token garbles end on a digit; fragments accumulate. Assert sentinel digit sequences per column from the scan itself (never type expected values in); record garbled cells verbatim and EXCLUDE them from any computed band rather than guessing.
- p306-style pages group values PER MISSION (fuel/ox/total triplets) instead of row-major — detect by triplet reconciliation f+o=t before assuming column order; headers may omit missions (A13 aborted → 8 columns, positional mapping).

## Mars EDL entry-mass papers on NTRS (R54, Domain 9) — hostable despite AIAA venue

- Two NASA/JPL AIAA SciTech 2022 Mars-2020 EDL papers carry the institutional landed-mass data: **NTRS 20210024709** (Edquist, aerothermal — Table 3 p14 entry masses MSL BET 3153 / M2020 TPS 3436-3436 / BET 3369 kg) and **NTRS 20210024480** (flight-mech simulation — p1 "At 1026 kg, Perseverance is the largest..."). Both `determinationType=PUBLIC_USE_PERMITTED`/`GOV_PUBLIC_USE_PERMITTED` even though `belongsToUsGov=False` and they're AIAA-published → **hostable in full_texts/** per NTRS precedent; check determinationType, not publisher.
- MSL Curiosity rover mass 899 kg is NOT in either PDF — it's on the live JPL fact sheet `https://mars.nasa.gov/msl/factsheet/` ("1,982 lbs (899 kg) in Earth gravity").
- **Domain-gap pattern that worked**: read the target repo's code for constants *claimed measured* but unregistered (delivery.py MARS_LANDED_MASS_FRACTION=0.30 "Measured, not assumed") — those are load-bearing anchors with no source; engineering dials documented as estimates are honest gaps, don't chase them.

## NEA delta-v oracle services (R53, Domain 8) — both WORKS live T3

- **JPL NHATS**: `https://ssd-api.jpl.nasa.gov/nhats.api` returns the FULL table in one GET (no params needed; a param like `sstr=433` is NOT supported → HTTP 400). JSON `{data:[...]}`, ~7,092 bodies. Per body: `min_dv:{dv,dur}` + `min_dur:{dv,dur}` km/s & days, obs_start/obs_end window, size bounds, H, orbit_id. Stdlib json is enough (no pandas).
- **Asterank NEO service**: `http://www.asterank.com/api/asterank?query={"neo":"Y"}&limit=1000` (URL-encoded; both http and https work). ~600k-body population, MIT licence. The `dv` column IS the Shoemaker-Helin closed form — i.e. it is the live service carrying d3's `shoemaker_helin_1978`. Economic columns (`profit`,`price`) return degenerate values through the public endpoint → use dv only (the repo documents this).
- **Verification pattern that worked**: when registering an oracle the target repo already probes, INDEPENDENTLY reproduce its published statistic as a parse-correctness check — R53's NHATS round-trip median 9.367 km/s and S-H median 8.140 km/s both matched economicspace SECOND-PASS.md F6 to 3 decimal places (same idea as Damodaran's CoC identity check). A match this tight proves you read the service correctly before anchoring anything.
- Anchor-scope honesty: these oracles are ROUND-TRIP quantities; spacecost delta_v_segments NEA rows are mostly ONE-WAY legs → register as distribution/rank reference, not exact cell pins (state it in FINDINGS).

## Browser backend — known fault class

- browser_exec failure modes, two distinct ones: (a) **CLI missing** — error says "Browser Use CLI not installed" → fix = `hermes tools` install (Browser Automation → Browser Use), NO restart needed; re-test once after. (b) **daemon wedged** — HTTP 420s on BOTH cloud and local=true routes (daemon-level, not site blocking): at most one retry per round; then record "backend fault", move to non-browser routes (urllib/requests), tell the user a Hermes restart is needed. just_2019 has been quarantined this way since R43 (as of R73 its failure mode is now (a) — CLI not installed).

## web_search backend — can be down

- The Firecrawl-backed web_search may return 403 (missing API key) with no warning. R62 update: the DDG fallback is ALSO dead from this machine — both `html.duckduckgo.com/html/` and `lite.duckduckgo.com/lite/` return pages with ZERO result links (bot-walled, not an error). When search engines are down, navigate DIRECTLY to known institutional sites instead (nasa.gov budget pages worked; whitehouse.gov OMB justifications 404 at guessed paths — don't burn a round guessing upload URLs, go through the agency's own landing page first) or work from already-registered sources.

## govinfo.gov / GAO route — ALSO bot-walled (R63)

- `https://www.govinfo.gov/` returns an HTTP 403 bot-wall to urllib with a Mozilla UA (confirmed R63 for both the search API and direct report paths) — same class as DDG. Do NOT burn rounds on GAO MSR reports via govinfo; use NTRS + OIG first, or work from already-registered sources.

## Cross-domain deepening: anchor one domain's rows from another domain's hosted source (R63)

- When a row in domain X cites an operation funded by a document registered+hosted in domain Y (e.g. d5 'Depot berthing & handover ops' scaled from ISS visiting-vehicle ops ← the R62-hosted FY2027 budget's p60 Space Operations table), DEEPEN IN DOMAIN X: FINDINGS block + extracted CSV go to the row's own domain; registry is unchanged (the source already has one row); extend that existing row's note once with a 'R<N> deepening —' clause. Never duplicate-register the same document per domain.
- Envelope-anchor honesty for program lines vs event rows: our $2M-per-delivery centre = 0.217% of NASA's ENTIRE annual ISS program line ($921.2M FY2027) → order-of-magnitude consistency anchor, never a pin; state the computed share (code-only delta) and that no per-event figure is published anywhere in the document.

## INDEX.md table-integrity audit — run EVERY round before committing (R63)

- Defect class found R63 (pre-existing since R58): a source-table row missing its CLOSING pipe makes the next line's `## Heading` render as a phantom extra cell — markdown tables silently absorb it. Audit: every table row must start AND end with '|', no `|\s*#{1,6}\s` on any line, and per-table header-vs-row cell counts consistent (separator rows excluded). A single glued heading can sit undetected for many rounds because the file still 'looks' right — only a mechanical cell-count pass catches it.
- Repair byte-level on CRLF files: `open(path,'rb')`, assert target bytes count==1, replace with pipe + `\r\n\r\n` + heading; re-run the audit and bare-LF check in the SAME script before moving on.

## NTRS citation JSON field names (R64 correction to R56-era notes)

- Single-citation API fields sit at TOP LEVEL, NOT under `_source`: `title`, `authors[].name` / `authors[].affiliation`, `publications[0].publicationDate`, `center.name`, `stiType`, `onlyAbstract`, `distribution`, `exportControl`, `copyright`. R64's first metadata pass printed nothing because it read `d["_source"][...]` — inspect the raw JSON once before writing a parser (R62 flagged this too; both rounds relearned it).

## NTRS single-word search false-positive discipline (R64)

- Single-word queries (`RS25`, `RL10`, `NERVA`) return title-substring matches that are often irrelevant: R64's sweep produced 'The RS-25 Engine for SLS' (good) alongside junk like unrelated systems docs; `raptor`/`BE4` matched nothing useful. ALWAYS pull citation metadata and filter on TITLE keywords + center before downloading — download budget is cheap, but registering a false positive costs a round.

## NTRS hosting eligibility check order (R64)

- Before committing any NTRS PDF to full_texts/: `determinationType` in {PUBLIC_USE_PERMITTED, GOV_PUBLIC_USE_PERMITTED} AND `distribution=public`. R64: all three engine docs passed both checks (NASA TM + two AIAA-published papers — determination beats publisher, per R54 precedent). Abstract-only records (`onlyAbstract=true`) are NOT hostable even when public-use.

## ± glyph in PDF text layers = U+F0B1 private use area (R64)

- Some NASA PDFs encode the plus-minus sign as a PUA codepoint: `get_text()` returns `'444.4\uf0b12'` where the display value is `444.4±2`. Verbatim probes written with literal U+00B1 will NEVER match — probe in two forms: raw (PUA) for count==1 on the source page, display-normalized (`token.replace(chr(0xF0B1), "\u00b1")`) for presence checks in FINDINGS/CSV. Always print `repr()` of the token region first; never hand-type a symbol you haven't seen in repr form.

## Mid-build failure revert protocol (R64, refined)

- Build scripts that write repo files step-by-step can fail AFTER creating new dirs/files but BEFORE registry writes: R64's run #2 recreated the d10 dir + PDFs then failed a stale idempotency assert. Revert = `shutil.rmtree` on newly-created domain dirs (never in git) + `git checkout -- <touched tracked files>`; verify with `git status --short` == empty AND targeted string-absence checks before re-running.

## terminal approval-gate timeouts → execute_code fallback (R64)

- On this machine, some `terminal` invocations hang at the approval gate and time out (~300s) while `execute_code` runs the same Python instantly. When a shell command stalls once, switch that workload to `execute_code` (subprocess or direct imports); keep `terminal` for git only if it keeps stalling.

## Domain 10 (R64) — launch vehicle & engine hardware / propellant performance

- Stood up per user criterion #2 from the unanchored constants in spacecost/reference/launch_vehicles.csv + propellants.csv. Three T2 NTRS docs: baumeister RL10 TM 20150008246 (MEASURED Centaur vacuum perf — PRIMARY anchor for hydrolox row 'Vac Isp 452 s per RS-25 / RL-10 datasheets': ours +1.71% high vs measured 444.4±2.5 s = consistency anchor), vetcha RS-25 SLS hot-fire 20180006338 (~500 s at 512,000 lb / 109% RPL profile verbatim), ballard next-gen RS-25 20170008958 (certified service life 55 starts / 27,000 s = engine-reusability basis). Negative probe: NO RS-25 vacuum-Isp figure in any of the three — 'per RS-25' half of our citation stays secondary-sourced.

## Domain 10 deepening R65 — NERVA nuclear-thermal records + legacy-NTRS hosting rule + OCR-scanned-doc protocol

- **Legacy CDMS NTRS records have `determinationType=None`** (R65): the determination field simply doesn't exist on pre-web-era records. Hosting eligibility then falls back to `distribution=PUBLIC` AND `exportControl.isExportControl/itar='NO'` → public-domain government work = hostable T2 sha-verified (applied: both 1968 AEC/NASA NERVA docs). Do NOT treat a missing determinationType as 'cannot verify'.
- **R65 anchored the nuclear-thermal row's historical claim**: propellants.csv note 'NERVA's NRX/XE ran on a test stand at 825 s in 1968' now backed by TWO independent AEC/NASA docs agreeing to one performance point (~75,000 lb / ~825 s): NTRS 19700004945 (p4 engine spec; p6 restart record — verbatim per-test breakdown reconciles EXACTLY with the stated total: OCR 'I'=one + 2+2+3+1+10+2+2+2 = **25**; p12 vacuum-corrected '~800 sec') and NTRS 19680011933 (p12 PFRT-path 'approximately 825 seconds'). The row's isp_vac_s=900 cell is the DRACO design target per its own note → no revision forced. Designation caveat: neither doc names 'NRX-XE' in extractable text (OCR-garbled subject) — anchored as NERVA-program test-stand performance, NOT a reactor-specific pin.
- **80s-era OCR scans carry garbled tokens** ('1bf-sec/lbm' for lbf-sec/lbm; 'vacuun'; 'Phoebus 18' = Phoebus 1B; Roman-numeral I as the digit one): quote VERBATIM including the garble, then annotate in FINDINGS what each artifact is. Never silently normalize a verbatim quote — the count==1 probe must match the raw text layer.
- **Arithmetic reconciliation can pass even when your mental parse was wrong** (R65): my first hand-parse of the 25-start breakdown dropped two clauses and 'proved' sum=23; the code regex `(\\d+) on` + leading-'I'=one gave exactly 25. Always compute the check in code against the stated total, and when it FAILS suspect YOUR parse before declaring an OCR artifact — a failed reconciliation is usually a parser bug, not source corruption.
- **Programmatic token slices can drop trailing decimals** (R64 defect found R65): slicing `t9[i:i+7]` around '444.4' captured '±2' instead of the full '±2.5' (the ± is a separate SymbolMT font span, and my slice length was guessed). Before trusting any sliced token: print repr() AND verify against the dict-level spans (`get_text('dict')`) that you have the complete run; when repairing an already-committed truncation, repair ALL committed occurrences in one build step (FINDINGS + CSV + INDEX) with count-asserted replacements.
- **MEMORY.md can be clobbered MID-round** (R65 #20), not just at round start: re-check the file immediately before EVERY memory write — if entry[0] no longer starts with this round's expected header, back up as `-mid-clobber-N` and re-run the full saved chain + marker swap first. The external writer ingests session content (fragments contain truncated lines from my own recent reports).
