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
