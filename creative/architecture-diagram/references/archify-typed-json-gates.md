---
description: "Archify 3.0.1: typed-JSON diagrams (architecture, workflow, sequence, dataflow, lifecycle) rendered to standalone interactive HTML behind a four-gate finalize command; run live with a planted dangling-edge defect"
source_repo: tt-a1i/archify (MIT; based on Cocoon-AI/architecture-diagram-generator)
tested_version: cloned @ main 2026-10-05 (archify 3.0.1, `npm install` 33 MB, Node 22.23); `validate` and `finalize` run on the bundled web-app example and on a mutated copy; website/viewer/export-to-WebM paths not run
verified_date: "2026-10-05"
---

# Archify: diagrams as validated typed JSON

Archify turns a plain-language description or a real codebase into an interactive, standalone HTML diagram by having the agent write a **typed JSON candidate** and passing it through gates, instead of hand-drawing SVG.
Five diagram types: `architecture` (components, boundaries, infrastructure), `workflow` (processes, runbooks, CI/CD), `sequence` (call chains, async traces), `dataflow` (pipelines, lineage), `lifecycle` (states, retries). Output: self-contained HTML with inline SVG, dark/light themes, optional trace motion, and
PNG/JPEG/WebP/SVG/WebM export. Install as a skill with `npx skills add tt-a1i/archify -g`; the repo claims 130K+ installs on skills.sh (the project's claim). It descends from the same Cocoon-AI generator as this repo's `architecture-diagram` skill, adding schemas, validation and a delivery contract.

## The method worth copying

1. **Pick the type from the question** (what is it made of, what steps, what calls, where does data go, what state is it in); `archify guide "<scenario>" --json` helps when ambiguous. Mermaid input is read for topology and re-authored as JSON, not rendered mechanically.
2. **Write the whole candidate JSON directly** (positions, sizes, components, boundaries, connections, cards) from the schema and an example, citing source evidence for a real repo (`--repo-root`).
3. **Run one command**: `node bin/archify.mjs finalize <type> <candidate.json> <output.html> --quality showcase --json`. A passing receipt means four gates passed: `validate`, `deliver`, strict `check`, and a real-browser `browser-check`. A non-zero exit is never success; read the compact diagnostics and repair the named gate, with a repair limit.
4. Keep the candidate frozen during the run and keep each request in its own timestamped folder (`.archify/<type>-<slug>-<YYYYMMDD-HHMMSS>/`).

## Run live

```bash
cd archify && npm install                       # 33 MB of node_modules
node bin/archify.mjs validate architecture examples/web-app.architecture.json --json
node bin/archify.mjs finalize architecture examples/web-app.architecture.json out.html --quality showcase --json
```

- `validate` on the bundled example: `ok: true`, with the candidate's sha256 and `candidateFrozen: true`, in about 1 s.
- `finalize`: `status: pass`, `gates: {validate: pass, deliver: pass, check: pass, browser-check: pass}`, no diagnostics, in about **6 s**, producing a **762,310-byte** standalone `out.html` plus `out.finalize.json`, a summary receipt and a browser-check receipt (the browser check used the installed Chrome).
- Candidate shape (architecture): `schema_version`, `diagram_type`, `meta` (title, output, quality_profile), `components` (id, type such as `external/security/cloud/backend/database`, label, sublabel, `pos` and `size` in pixels), `boundaries`, `connections` (id, from, to, label, variant), `cards`.
- **Planted defect**: changing the first connection's `to` to a non-existent id made `validate` exit **1** with `ok: false`, `stage: "render"`, and a structured diagnostic `{code: "layout/constraint", severity: "error", message: "Connection \"HTTPS\" references unknown target \"does-not-exist\"."}`: a dangling edge cannot reach the HTML.

## Choosing among the diagram skills here

| Need | Skill |
|---|---|
| Fast dark SVG architecture sheet from this repo's skill | `architecture-diagram` |
| Many diagram types in an editorial style | `diagram-design` |
| Explorable isometric system atlas | `system-atlas` |
| Machine-validated, source-evidenced interactive HTML with delivery receipts, any of five types | Archify (this note) |
| Whiteboard-style / hand-drawn JSON | `excalidraw` |

Use Archify when correctness of the diagram matters (every edge points at a real component; the HTML actually renders in a browser) and a gate-and-receipt workflow is acceptable; use the lighter skills when speed matters more.
The same principle (a diagram or page is "done" only after a deterministic validator and a real-browser pass) appears in `awwwards-gsap-motion/references/acceptance-gates.md`.
