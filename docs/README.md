# Reference Documentation (Knowledge Layer)

This directory holds **verified reference material** that is *not* a skill: API references,
working code patterns, and gotchas extracted from the owner's starred-repo deep dives
(41 repos, 2026-09-05/06). Skills tell an agent *how to work*; this layer tells it
*what actually exists in these libraries and what breaks*.

## Contents

| Doc | What you get | Verified |
|---|---|---|
| [space-astro/brahe-api-reference.md](./space-astro/brahe-api-reference.md) | brahe 1.7.0 full module map + working propagation / Horizons-SPK snippets (Ceres recipe for any small body) | live run, Windows py3.11, 2026-09-06 |
| [space-astro/skyfield-api-reference.md](./space-astro/skyfield-api-reference.md) | skyfield **1.55 breaking changes** (load() contract), de430s.bsp 404 on both JPL mirrors, phase-angle trap with numbers | live run, Windows py3.11, 2026-09-06 |
| [space-astro/openscvx-patterns.md](./space-astro/openscvx-patterns.md) | OpenSCvx core problem pattern (State/dynamics/Problem.solve), Hohmann example constants, autotuner class map | source-read from cloned repo, 2026-09-05 |
| [data-science/polars-pymc-api-reference.md](./data-science/polars-pymc-api-reference.md) | polars lazy-first idioms + join `validate=` cardinality checks; pymc sample() nutpie Rust-NUTS auto-select (line-anchored) | source-read from cloned repos, 2026-09-05 |
| [space-astro/catalog-data-sources.md](./space-astro/catalog-data-sources.md) | astroquery async-first API map (SBDB `covariance=` flag = orbital uncertainty in one call; Horizons all-43-quantities bloat gotcha), pds4_tools metadata-with-array, cumulus pvl/cmr-client, space-map Chebyshev binary ephemeris schema | source-read from cloned repos, 2026-09-06 |
| [data-science/optimization-toolkit.md](./data-science/optimization-toolkit.md) | nyx-py (LIVE — round-1 correction), pygmo2 UDA contract, mesa v3 two blockers (py≥3.12 + API rewrite), z3 FPRef/regex sorts, Pyomo dae/gdp/mpec, CamPyRoS ray_alt serial shim | source-read from cloned repos, 2026-09-06 |
| [webdev/frontend-tooling.md](./webdev/frontend-tooling.md) | nicegui `ui.run()` full 33-param list (verified from source — corrects the "71" claim), Front-End-Checklist MCP rule package, HTMLHint's 34 rules, gods-eye-view Cesium layout + test-everything discipline | source-read from cloned repos, 2026-09-06 |
| [devops/git-workflow-recipes.md](./devops/git-workflow-recipes.md) | fixup+autosquash, PR checkout refspecs, safe revert of merged PRs, bulk-stage deletions; Windows/OneDrive index-churn notes for this machine | distilled from MIT cheat-sheet clone + local git behavior, 2026-09-06 |

## How these references are maintained

1. **Source of truth is the clone**, not this doc: `%LOCALAPPDATA%\Temp\starred-dive\<repo>`
   (read-only clones of all 41 starred repos). If a library releases, re-read its examples/
   and module docstrings before trusting any snippet here.
2. **Snippets are run, not copied.** Every code block marked `verified` was executed in an
   isolated venv (`%LOCALAPPDATA%\Temp\star-scan\venv`) on the owner's machine; the output
   is quoted next to it. Network-dependent snippets (Horizons SPK fetch) were run live too.
3. **Re-verify before relying**: `pip install <lib>` in a fresh venv, paste the snippet,
   compare against the quoted output. If numbers differ by more than rounding, the library
   changed — update this doc and note the version + date at the top of each file.
4. **Version pinning matters.** skyfield 1.55 broke every pre-2026 tutorial (see its doc).
   Each reference states the exact tested version; do not port snippets across major versions.

## Lookup order for this layer

Task → [DESCRIPTION.md](../DESCRIPTION.md) quick table → `grep -ri <term> docs/` here →
skill's own references dir → clone under `%LOCALAPPDATA%\Temp\starred-dive\`.
