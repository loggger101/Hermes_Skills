---
name: repo-atlas
description: "In-repo atlas docs + drift check so agents orient fast."
version: 1.0.0
author: Hermes Agent (ported from cathrynlavery/repo-atlas, MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [onboarding, documentation, codebase-map, agents-md, drift-check, context]
    related_skills: [codebase-onboarding, code-wiki, living-docs-governance, repowise]
---

<!-- source: cathrynlavery/repo-atlas (MIT), read + generator run live 2026-10-05; generator patched for utf-8 -->

# Repo Atlas

## What This Skill Does

Builds a persistent, in-repo context system under `docs/atlas/` so an engineer or agent can find the right
file without searching. Two parts: a stdlib-only generator that writes the mechanical docs (directory tree,
entrypoints, file stats, 14-day changelog) and fails CI when they drift, plus a guided set of hand-written
docs (architecture, domain model, critical flows, state sources of truth, dependencies, gotchas, tests).

## When to Use

- "Map this repo", "create atlas docs", or a repo that agents keep re-exploring from scratch every session
- You want an orientation layer that survives across sessions and is checked by CI, not a one-off summary
- Not for a one-time read of an unfamiliar repo (use `codebase-onboarding`), generated browsable wiki pages with diagrams (`code-wiki`), or governance of an existing docs set (`living-docs-governance`)

## Hard constraints

- Do not change product or runtime behaviour. Everything lives in the repo; no hosted tooling; Python 3 stdlib only.
- Every doc cites real paths, real functions and real gotchas. Generic filler is the failure mode.

## Procedure

1. **Reconnaissance.** Top-level tree; repo type (app, API, library, monorepo, CLI, infra); languages and frameworks; entrypoints, build configs, CI files; read 5-10 key files.
2. **Run the generator.** Copy `scripts/generate_atlas.py` to `<repo>/scripts/atlas/generate_atlas.py` (it locates the repo root as three parents up, so the path matters). Edit the CONFIGURATION block: `IGNORE_NAMES` (exact path-segment match), `TREE_ANNOTATIONS`, `ENTRYPOINT_NAMES`, `ENTRYPOINT_PATH_PATTERNS` (fnmatch, e.g. `cmd/*/main.go`), `ENTRYPOINT_CONTENT_MARKERS`, `CHANGELOG_DAYS` (default 14). Then `python scripts/atlas/generate_atlas.py --write`. Run `--write` a **second** time before trusting `--check` (see Pitfalls).
3. **Hand-extend `repo-map.md`** with a *Where to look for X* router (10-15 task-to-file rows) and a *Danger zones* table (fragile files and why).
4. **Write the manual docs** (50-150 lines each, templates in `references/atlas-templates.md`): `00_README`, `01_ARCHITECTURE`, `02_DOMAIN_MODEL`, `03_CRITICAL_FLOWS` (top 3-5 flows as `file:function` chains), `04_STATE_SOURCES_OF_TRUTH` (every store, who writes it, which wins on conflict), `05_EXTERNAL_DEPENDENCIES`, `06_GOTCHAS`, `07_TEST_MATRIX`.
5. **Add the agent on-ramp** to the repo's `CLAUDE.md` / `AGENTS.md`: where the atlas is and why; a two-agent loop (Agent A loads `repo-map.md`, then the domain doc, then source, then implements; Agent B reviews the diff against `06_GOTCHAS`, re-walks the affected flow in `03_CRITICAL_FLOWS`, confirms tests per `07_TEST_MATRIX`); rules: read the atlas before coding, update it when architecture changes, regenerate after structural changes.
6. **Wire the drift gate.** `make atlas-generate` -> `--write`, `make atlas-check` -> `--check` (and the same two as npm scripts if there is a `package.json`). `--check` exits non-zero on STALE or MISSING files.
7. **Verify.** Generate succeeds; check exits 0 straight after; every doc has repo-specific paths; `git diff` shows no runtime code changed.

## Pitfalls (found running it, Windows, Python 3.14)

- **Upstream crashes on non-ASCII commit subjects on Windows.** It wrote with the platform default encoding (cp1252), so an em dash or emoji in a commit message raised `UnicodeEncodeError` mid-`--write`, after `repo-map.md` was already written and before the changelog. The bundled copy is patched (`encoding="utf-8"`). If you pull a newer upstream copy, re-check this.
- **The first successful `--write` is not a fixed point.** `repo-map.md` describes the repo including the atlas files being created in the same run, so an immediate `--check` reported STALE on `repo-map.md` (probably the file stats, not confirmed). A further `--write` settles it. Observed sequence: `--check` rc 1 after the first successful write, rc 0 after the next write, rc 1 again after adding a source file.
- **The changelog doc goes stale by design** as new commits land inside the 14-day window, so wiring `atlas-check` as a blocking CI gate makes every merge need a regenerate. Either regenerate in the merge flow, or gate only `repo-map.md` (drop the changelog from the checked set).
- The `*Generated:` date line is stripped before comparison, so date changes alone do not trigger STALE.
- On Windows the CI-file row of the Entrypoints table printed with backslashes (`.github\workflows\ci.yml`) while other rows used forward slashes; cosmetic, and the doc is generated, so do not hand-edit it.
- Hand-written docs are not drift-checked. The only protection is rule 5's "update the atlas when architecture changes"; pair with `living-docs-governance` if that needs teeth.

## Verification

- `python scripts/atlas/generate_atlas.py --write` twice, then `--check` exits 0 (`Atlas files are up to date.`)
- Add or remove a source file; `--check` exits 1 naming `docs\atlas\repo-map.md` as STALE
- Spot-check three paths cited in each manual doc exist (`ls`), and that no non-doc file appears in `git status`

## References

- `references/atlas-templates.md` - structure and example skeleton for each of the manual atlas docs (from cathrynlavery/repo-atlas, MIT)
- `scripts/generate_atlas.py` - the generator (stdlib only; patched to read and write UTF-8)
