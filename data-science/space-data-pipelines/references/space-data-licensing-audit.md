---
description: "Space-data licensing traps from space-datasets' own 2026-05-26 audit: ESA CC BY-NC, WDC Kyoto no-commercial, VizieR scientific-use terms, provider URL table"
source_repos: juliensimon/space-datasets LICENSE_AUDIT.md @ 5f886cd (read in full this pass)
tested_version: n/a — policy pages cited by the audit; re-verify a specific provider before relying on it for redistribution decisions
verified_date: "2026-09-12"
---

# Space Data Licensing Audit (from space-datasets' own LICENSE_AUDIT.md, 2026-05-26)

Method that made this audit trustworthy: verified each upstream provider's **actual policy page directly** rather than trusting the
dataset cards or scripts. Result: at least **30 datasets mis-licensed as cc-by-4.0 when upstream explicitly restricts commercial use**,
plus ~25 medium-risk; all 89 were relicensed in commit `e05a793`. Use this file whenever you republish space data — the default assumption
"NASA/ESA public API ⇒ CC-BY-4.0" is wrong for a large fraction of providers.

## The load-bearing rule

**The source license travels with the data.** Fetching ESA mission catalogs *via VizieR or HEASARC mirrors* does not strip the ESA restriction —
the mirror changes nothing about provenance terms. Same logic: CelesTrak's TLEs trace to US Space Force / USSPACECOM and ride on CelesTrak's
discretionary annual authorization, regardless of which format you pulled them in.

## HIGH risk (must not be cc-by-4.0)

| Provider | Correct license | Authoritative URL | Scope |
|---|---|---|---|
| **ESA Space Science Archives** (25 datasets: Gaia, XMM-Newton, Planck, Herschel, INTEGRAL + BepiColombo, Mars Express, Rosetta, Venus Express, ExoMars TGO, JUICE, Huygens, Solar Orbiter…) | `cc-by-nc-3.0` (CC BY-NC 3.0 **IGO**) | https://www.cosmos.esa.int/web/esdc/terms-and-conditions — exact quote: *"Data hosted in the ESA Space Science Archives are distributed under the CC BY-NC 3.0 IGO licence."* | ALL ESA space science archives incl. planetary + heliophysics; Gaia license page separately at https://www.cosmos.esa.int/web/gaia-users/license |
| **WDC Kyoto geomagnetic indices** (AE, Dst, substorm onsets via SuperMAG) | `cc-by-nc-4.0` or other + DOI citation per index | https://wdc.kugi.kyoto-u.ac.jp/wdc/Sec3.html — *"The WDC Kyoto does not allow commercial applications of the geomagnetic indices."* Redistribution allowed with attribution + data DOI (AE, Dst, ASY/SYM each have one) | Strictest in the catalog; audit considered removal from HF entirely |
| **SIDC SILSO sunspot numbers** | `cc-by-nc-4.0` (explicit on page) | https://www.sidc.be/SILSO/datafiles — required citation: *"Source: WDC-SILSO, Royal Observatory of Belgium, Brussels, DOI: 10.24414/qnza-ac80"* | sunspot datasets |
| **AAVSO VSX** (variable star catalog) | `other` + link to usage PDF | https://www.aavso.org/data-usage-guidelines (+ 2025-10-01 PDF): non-commercial research/educational only; redistribution discouraged without authorization | aavso-vsx |

## MEDIUM risk (label `license: other` with upstream policy link)

| Provider | Status | URL |
|---|---|---|
| **CelesTrak** (SATCAT, TLEs, constellation fleets ×14 datasets) | No formal CC license; redistribution rests on annual USSPACECOM authorization; published policy is purely operational. If DoD authorization lapses, downstream redistributions become problematic | https://celestrak.org/usage-policy.php — note lineage to US Space Force in README |
| **The Space Devs LL2** (launch manifests) | Permissive FAQ ("free to use… attribution encouraged") but NOT a formal license; embedded image URLs may be CC-BY-NC 2.0 | https://thespacedevs.com/llapi |
| **Minor Planet Center** | Freely available *if source clearly specified*, BUT: *"Inclusion of circulars or web pages in products of any description… is strictly prohibited"* — ambiguous about HF datasets; conservatively labeled `other` (only the freely-available CometEls.txt was pulled, not MPECs) | https://www.minorplanetcenter.net/iau/WWWPolicy.html |
| **IERS** (Earth orientation parameters) | No explicit license published; intergovernmental body, publicly distributed → `other` + disclaimer | https://www.iers.org |
| **JAXA MAXI** (X-ray source catalog via HEASARC mirror) | Only "copyright RIKEN/JAXA/MAXI team" — no declared license → `other` + citation; consider contacting the team before re-publishing | https://maxi.riken.jp |

## VizieR is NOT CC-BY-4.0 (applies to every catalog fetched through it)

VizieR's official terms are *"free of usage in a scientific context"* with mandatory citation — **explicitly not CC-BY**.
CC-BY permits commercial redistribution; VizieR defers commercial/derivative terms to each catalog's originating journal.
The audit relabeled all 37 non-ESA VizieR catalogs to `license: other` + `license_name: vizier-scientific-use` linking
https://cds.unistra.fr/vizier-org/licences_vizier.html. Per-catalog spot-check results worth knowing:

| Catalog | Verdict |
|---|---|
| Hipparcos (V/50) | Moved to ESA-NC group — it's an ESA SP-1200 publication, so CC BY-NC 3.0 IGO applies despite the VizieR route |
| APOGEE DR17 | `other` + SDSS Data Use Policy (AAS/IOP copyright on machine-readable tables) |
| IRAS FSC v2 | `other` + NASA/IPAC terms; explicit `(c)IRAS Faint Sources` marker visible on VizieR itself — the catalog page often carries the real rights holder in its description text, check it |
| Bright Star (V/50), Henry Draper (III/135A) | LOW risk — Yale Observatory / pre-1929 public domain; no action needed |
| RAVE DR6, NVSS, FIRST, ICRF3, Veron AGN | UNCLEAR — journal copyright but no restrictive language found; left cc-by-4.0 (re-check before commercial redistribution) |

## LOW risk / correctly labeled (~167 datasets)

- **US government work product = public domain** (17 USC §105): NASA PDS/GSFC/JPL SSD-CNEOS, NOAA SWPC, USGS Astropedia/planetarynames.
- **STScI/MAST**: *"Most MAST data are in the public domain with no use restrictions"* — https://archive.stsci.edu/publishing/data-use (HLSPs already CC-BY-4.0).
- Explicitly permissive: GFZ Kp index (**CC-BY-4.0** at https://kp.gfz.de/en/data), GWOSC LIGO/Virgo (**CC-BY-4.0**), GALAH DR4, PDG (RPP 2024 in Phys Rev D CC-BY-4.0), Jonathan McDowell GCAT (**CC-BY-4.0** at https://planet4589.org/space/gcat/web/intro/credits.html).
- **Space-Track**: USSPACECOM blanket approval for basic SSA + attribution required — the citation line must be in the README: *"Basic SSA data distributed under USSPACECOM blanket authorization via www.Space-Track.org."* (https://www.space-track.org/documentation)
- Wikidata: CC0, accurate as declared.

## Process rules to copy from this audit

1. Verify against the **provider's policy page**, never the dataset card or script comment — 30/222 cards were wrong.
2. When in doubt between `cc-by-4.0` and `other`, use `license: other` + `license_name` + `license_link` triplet with a link to the upstream terms; over-permissive labels are worse than under-permissive ones (the audit's one-line rationale: *"CC-BY-4.0 grants commercial use… our current label is a license-overreach"*).
3. Keep an authoritative URL table per provider in-repo and re-audit any NEW provider before publishing it.
4. Suggested CI check from the audit's own recommendations: flag any new dataset script declaring `cc-by-4.0` against a provider on the HIGH/MEDIUM list — cheap, catches regressions at push time.
