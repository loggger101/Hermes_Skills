---
description: "gpui-kit 0.7 (Rust desktop UI on GPUI): layering, features, headless UI testing, and its tested-recipe documentation pattern; source-read"
source_repo: longbridge/gpui-kit (Apache-2.0 per crates.io)
tested_version: README, examples/ai_recipes/README.md and crates.io metadata read; NOT compiled (no Rust toolchain, GPU UI needs a desktop build)
verified_date: "2026-10-05"
---

# gpui-kit: Rust desktop apps on GPUI

crates.io: `gpui-kit` 0.7.1 and `gpui-component` 0.7.1 (both 2026-10-05, Apache-2.0), `gpui` 0.2.2 (2025-10-22). The repo is from Longbridge; the README says it was built for and
refined in their commercial desktop app (Longbridge Pro). GitHub reports the repository license as NOASSERTION (a docs licence file sits beside `LICENSE-APACHE`), so read both before reuse.

## Layers (applications depend on one crate)

| Crate | Role |
|---|---|
| `gpui-kit` | the single dependency; pins the matching GPUI release and re-exports GPUI, base, component and assets |
| `gpui-component` | complete styled UI system (75+ components: forms, navigation, overlays, data display, editing, feedback, layout) with semantic themes and sizes |
| `gpui-base` | unstyled behaviour, state and infrastructure, for teams building their own design system |
| `gpui-shell` (separate) | JavaScript extension runtime hosted by the Rust app, capabilities granted one at a time |

Stated capabilities: GPU rendering aimed at 120 FPS; virtual-scrolling data tables over hundreds of thousands of rows; virtual lists with variable item sizes; a code editor (Tree-sitter highlighting, LSP diagnostics/completion/hover, stable at 200K lines);
serialisable dock layout; Markdown/HTML rendering and charts; AccessKit accessibility; WebAssembly target `wasm32-unknown-unknown`; macOS, Windows and Linux. These are the project's claims, not measured here.

## UI integration testing

Components are rendered in **headless windows**, with pointer and keyboard input driven programmatically, and tests assert state, focus, layout and accessibility. The recipe test types into an input, checks the owner receives the change,
forces an unrelated redraw, and types again: it catches dropped subscriptions and state-lifetime regressions (the common GPUI bug classes).

## Documentation that cannot drift (pattern worth copying)

- **Tested consumer recipes**: complete sources in a workspace crate that imports *only* the public crate, compiled and interaction-tested (`cargo test -p gpui-kit-recipes`, `cargo run -p gpui-kit-recipes`). Use one wherever a reader must combine components, keep state, or import a trait for a call to work.
- **Contextual fragments**: short snippets for one API detail, labelled with their context so nobody mistakes them for a whole app; do not mint a recipe per component.
- `recipes.json` maps canonical source files to the doc fragments; `script/check-ai-recipes --sync` rewrites only the fenced code between matching markers, and `script/check-ai docs` fails if source and docs disagree.
- **Acceptance table**: each change type names its required command and its evidence (`check-ai docs | rust | shell | all`), and a PR states what was verified and what remains untested. The README is explicit that these gates make failures reproducible but "do not establish an AI model success rate."

Applies beyond Rust: see `living-docs-governance/references/doc-example-verification.md` for the Node-based checker that does the same job for JavaScript examples.

## Choosing

Rust desktop app wanting a ready component set and tests: `gpui-kit`. Python desktop tools: `nicegui-app-builder/references/python-gui-toolkits.md`.
Check the GPUI release pin and your platform GPU backend before committing; GPUI is a young framework, so expect breaking changes between 0.x releases.
