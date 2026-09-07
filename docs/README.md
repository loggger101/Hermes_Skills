# Reference Documentation (Knowledge Layer)

**Reorganized 2026-09-07:** verified reference material now lives **inside its owning skill's
`references/` directory**, not in this flat layer. A doc sits next to the skill an agent loads for
the job, so loading the skill surfaces both *how to work* and *what actually exists / what breaks*.

## Where each reference lives now

| Reference | Owning skill (path) | What you get | Verified |
|---|---|---|---|
| brahe API reference | `data-science/astro-toolkit-selection/references/brahe-api-reference.md` | brahe 1.7.0 full module map + working propagation / Horizons-SPK snippets (Ceres recipe for any small body), Celestrak query builder, EKF/UKF/BLS estimation; cp311 win_amd64 wheel confirmed for this machine | live run, Windows py3.11, 2026-09-06 + re-check 2026-09-07 |
| skyfield API reference | `data-science/astro-toolkit-selection/references/skyfield-api-reference.md` | skyfield **1.55 breaking changes** (load() contract), de430s.bsp 404 on both JPL mirrors, phase-angle trap with numbers, osculating-elements solver for independent element checks | live run, Windows py3.11, 2026-09-06 + source-read 2026-09-07 |
| OpenSCvx patterns | `data-science/astro-toolkit-selection/references/openscvx-patterns.md` | core problem pattern (State/dynamics/Problem.solve), Hohmann example constants verbatim, autotuner class map; reality-check on the economicspace audit's stale "no transfer example" claim | source-read from cloned repo + live GitHub API, 2026-09-05 / 2026-09-07 |
| catalog & archive data sources | `data-science/astro-toolkit-selection/references/catalog-data-sources.md` | astroquery async-first API map (SBDB `covariance=` flag; Horizons all-43-quantities bloat gotcha; NEODyS full 6×6 covariance), pds4_tools metadata-with-array, cumulus pvl/cmr-client, space-map binary ephemeris schema | source-read from cloned repos, 2026-09-06 / 2026-09-07 |
| optimization & simulation toolkit | `data-science/astro-toolkit-selection/references/optimization-toolkit.md` | nyx-py (LIVE — round-1 correction), pygmo2 UDA contract, mesa v3 two blockers (py≥3.12 + API rewrite), z3 FPRef/regex sorts, Pyomo dae/gdp/mpec, CamPyRoS ray_alt serial shim | source-read from cloned repos, 2026-09-05 / 2026-09-07 |
| Δv oracles & economics sources | `data-science/economicspace-pipeline/references/dv-oracles-and-economics-sources.md` | external Δv oracles (NHATS; **Asterank schema change — dv column gone, per-element sigmas added**, live re-probe 2026-09-07) + nine soft-assumption data sources with exact fetch specs/colspecs | source-read + LIVE API probes, 2026-09-07 |
| polars + pymc API reference | `data-science/python-data-science/references/polars-pymc-api-reference.md` | polars lazy-first idioms + join `validate=` cardinality checks; pymc sample() nutpie Rust-NUTS auto-select (line-anchored) | source-read from cloned repos, 2026-09-05 |
| frontend tooling | `frontend-design/nicegui-app-builder/references/frontend-tooling.md` | nicegui `ui.run()` full 33-param list (verified from source — corrects the "71" claim), Front-End-Checklist MCP rule package, HTMLHint's 34 rules, gods-eye-view Cesium layout + test-everything discipline | source-read from cloned repos, 2026-09-05 / 2026-09-06 |
| git workflow recipes | `github/github-pr-workflow/references/git-workflow-recipes.md` | fixup+autosquash, PR checkout refspecs, safe revert of merged PRs, bulk-stage deletions; Windows/OneDrive index-churn notes for this machine | distilled from MIT cheat-sheet clone + local git behavior, 2026-09-06 |

Each owning skill's SKILL.md carries a `## References` section pointing at its files — start there.
The pre-reorganization layout (`docs/space-astro/`, `docs/data-science/`, …) is preserved in git
history (commit before the 2026-09-07 reorg); old paths resolve via `git log --follow`.

## Archived notes

| File | What it is |
|---|---|
| [archive/audit-notes-skills-repo-pass.md](./archive/audit-notes-skills-repo-pass.md) | Historical audit log of the 127-skill frontmatter pass (duplicate removal, broken related_skills fixes, body-section additions). Point-in-time record — do not treat as current state; SKILLS-INDEX.md + tools/audit-skills.py are. |

## How these references are maintained

1. **Source of truth is the clone**, not the doc: `%LOCALAPPDATA%\Temp\starred-dive\<repo>`
   (read-only clones of all 41 starred repos). If a library releases, re-read its examples/
   and module docstrings before trusting any snippet here.
2. **Snippets are run, not copied.** Every code block marked `verified` was executed in an
   isolated venv (`%LOCALAPPDATA%\Temp\star-scan\venv`) on the owner's machine; the output
   is quoted next to it. Network-dependent snippets (Horizons SPK fetch) were run live too.
3. **Re-verify before relying**: `pip install <lib>` in a fresh venv, paste the snippet,
   compare against the quoted output. If numbers differ by more than rounding, the library
   changed — update the doc and note the version + date at the top of each file.
4. **Version pinning matters.** skyfield 1.55 broke every pre-2026 tutorial (see its doc).
   Each reference states the exact tested version; do not port snippets across major versions.
5. **Live APIs rot faster than libraries** — the Asterank dv column vanished between two audit
   passes a day apart (documented in the Δv-oracles ref). Any claim about an external endpoint
   older than ~a week gets re-probed before being quoted again.

## Lookup order for this layer

Task → [DESCRIPTION.md](../DESCRIPTION.md) quick table → owning skill's `## References` section →
`grep -ri <term>` across the skills' references/ dirs → clone under `%LOCALAPPDATA%\Temp\starred-dive\`.
