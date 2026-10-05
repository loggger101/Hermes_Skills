# REFERENCES-INDEX

Flat index of all **463 reference documents** in this second brain — one line each, grep-friendly.
Format: ``- `path` — purpose _(owner skill)_``. Regenerate with `python tools/gen-references-index.py`.

## autonomous-ai-agents/cron-config-authoring

- `autonomous-ai-agents/cron-config-authoring/references/cronjob-config-patterns.md` — (no description)

## autonomous-ai-agents/cron-job-authoring

- `autonomous-ai-agents/cron-job-authoring/references/agent-vs-script-checklist.md` — Agent-vs-Script Checklist
- `autonomous-ai-agents/cron-job-authoring/references/credential-strategy.md` — Credential Strategy for Cron Jobs
- `autonomous-ai-agents/cron-job-authoring/references/cron-approval-mode.md` — Cron Approval Mode
- `autonomous-ai-agents/cron-job-authoring/references/delivery-discipline.md` — Delivery Discipline for Cron Jobs
- `autonomous-ai-agents/cron-job-authoring/references/drafting-guide.md` — Drafting Guide
- `autonomous-ai-agents/cron-job-authoring/references/drift-skip-error.md` — Drift Skip: Model/Provider Config Drift
- `autonomous-ai-agents/cron-job-authoring/references/guardrail-template.md` — Guardrail Template — No-Interaction Block for Cron Jobs
- `autonomous-ai-agents/cron-job-authoring/references/loop-engineering.md` — Loop Engineering (scheduled autonomous jobs)
- `autonomous-ai-agents/cron-job-authoring/references/output-alignment.md` — Output Alignment Reference
- `autonomous-ai-agents/cron-job-authoring/references/prompt-template.md` — Prompt Body Template
- `autonomous-ai-agents/cron-job-authoring/references/repo-cronjob.md` — Cron jobs that run against an existing repository
- `autonomous-ai-agents/cron-job-authoring/references/script-path-resolution.md` — Script Path Resolution Pitfalls
- `autonomous-ai-agents/cron-job-authoring/references/two-agent-architecture.md` — Two-Agent Architecture: Preparer vs. Commit Agent
- `autonomous-ai-agents/cron-job-authoring/references/vault-crypto-pattern.md` — Per-User Encrypted Secret Vault (verified from reconurge/flowsint @ 1820569)

## autonomous-ai-agents/hermes-agent

- `autonomous-ai-agents/hermes-agent/references/background-systems.md` — Durable & Background Systems
- `autonomous-ai-agents/hermes-agent/references/cli-reference.md` — Hermes CLI Reference
- `autonomous-ai-agents/hermes-agent/references/configuration.md` — Configuration, Toolsets & Voice
- `autonomous-ai-agents/hermes-agent/references/context-budget-and-cache-placement.md` — Prompt-cache placement rules and a route-bound context budget (usable = window - output - reserve - history) with the invalidation table run through oh-my-hermes 3.0.0's omh CLI
- `autonomous-ai-agents/hermes-agent/references/contributor-guide.md` — Contributor Quick Reference
- `autonomous-ai-agents/hermes-agent/references/cross-harness-skill-porting.md` — Cross-Harness Skill Porting — making one skill corpus auto-trigger on N agent runtimes
- `autonomous-ai-agents/hermes-agent/references/delegate-task-concurrency-diagnosis.md` — delegate_task: diagnosing "my batch was capped"
- `autonomous-ai-agents/hermes-agent/references/desktop-plugins.md` — Desktop App Plugins — UI Panes, Commands, Widgets
- `autonomous-ai-agents/hermes-agent/references/hindsight-memory-provider.md` — Hindsight as a Hermes memory provider: catalog install/update/pin, three modes, recall/retain config, why recall comes back empty, and bank/tag rules that prevent cross-user leaks
- `autonomous-ai-agents/hermes-agent/references/installed-plugins.md` — Installed Plugins — Live Environment Catalog
- `autonomous-ai-agents/hermes-agent/references/native-mcp.md` — Native MCP Client
- `autonomous-ai-agents/hermes-agent/references/petdex.md` — Petdex — Animated Pet Mascots
- `autonomous-ai-agents/hermes-agent/references/portal-auth-for-third-party-apps.md` — Nous Portal — authenticating third-party apps against the subscription
- `autonomous-ai-agents/hermes-agent/references/project-context-files.md` — Project Context Files
- `autonomous-ai-agents/hermes-agent/references/providers-and-models.md` — Providers & Model Aliases
- `autonomous-ai-agents/hermes-agent/references/python-agent-plugins.md` — Python Agent Plugins (the `~/.hermes/plugins/` system) — verified API notes
- `autonomous-ai-agents/hermes-agent/references/security-privacy.md` — Security & Privacy Toggles
- `autonomous-ai-agents/hermes-agent/references/slash-commands.md` — Slash Commands (In-Session)
- `autonomous-ai-agents/hermes-agent/references/themes.md` — Themes / Skins — Author a Hermes Color Theme
- `autonomous-ai-agents/hermes-agent/references/troubleshooting.md` — Troubleshooting
- `autonomous-ai-agents/hermes-agent/references/tui-widgets.md` — TUI Widgets — Live Panels for the Ink TUI Dock
- `autonomous-ai-agents/hermes-agent/references/webhooks.md` — Webhook Subscriptions
- `autonomous-ai-agents/hermes-agent/references/windows-quirks.md` — Windows-Specific Quirks

## autonomous-ai-agents/hermes-bot-cloning

- `autonomous-ai-agents/hermes-bot-cloning/references/free-model-discovery.md` — Free Model Discovery on Nous Portal

## autonomous-ai-agents/repowise

- `autonomous-ai-agents/repowise/references/codebase-intelligence-patterns.md` — Engineering patterns from repowise-dev/repowise (AGPL-3.0) — distillation contracts, decayed git signals, confidence-scored graphs, benchmark discipline, noise-free doc-drift detection; formulas + verified numbers

## communication/mental-models

- `communication/mental-models/references/models/activation-energy.md` — Change needs an upfront input larger than its running cost, so the barrier to starting is the thing to attack.
- `communication/mental-models/references/models/asymmetric-warfare.md` — The weaker side wins by refusing the stronger side's terms and changing what counts as winning.
- `communication/mental-models/references/models/bias-from-incentives.md` — People reach the conclusions their incentives point toward, sincerely and without noticing.
- `communication/mental-models/references/models/bottlenecks.md` — A system's throughput is set by its single tightest constraint; work spent anywhere else is wasted.
- `communication/mental-models/references/models/confirmation-bias.md` — We search for and weight evidence that supports what we already believe, and the search feels neutral from inside.
- `communication/mental-models/references/models/creative-destruction.md` — Growth arrives by destroying the thing that currently works, and incumbents defend the thing being destroyed.
- `communication/mental-models/references/models/emergence.md` — Aggregates have properties their parts don't, so understanding the components does not give you the whole.
- `communication/mental-models/references/models/feedback-loops.md` — Output that re-enters as input — reinforcing loops accelerate, balancing loops resist, and delay makes both unstable.
- `communication/mental-models/references/models/first-principles-thinking.md` — Strip a problem to what you know is true, then rebuild upward without borrowing anyone's conclusions.
- `communication/mental-models/references/models/framing.md` — The same facts presented differently produce different decisions — so the frame is a choice someone made.
- `communication/mental-models/references/models/index.md` — (no description)
- `communication/mental-models/references/models/inertia.md` — Things keep doing what they were doing; change requires a force, and mass determines how much.
- `communication/mental-models/references/models/inversion.md` — Approach a goal backward by asking what would guarantee failure, then avoid those things.
- `communication/mental-models/references/models/leverage.md` — Find the point where a small input produces a disproportionate output, and apply force there.
- `communication/mental-models/references/models/margin-of-safety.md` — Build for materially worse than your best estimate, because your estimate is an estimate.
- `communication/mental-models/references/models/randomness.md` — Much of what looks like signal is noise, and we build causal stories over both without noticing.
- `communication/mental-models/references/models/regression-to-the-mean.md` — Extreme results are followed by less extreme ones for statistical reasons, independent of anything you did.
- `communication/mental-models/references/models/sampling.md` — Small and self-selected samples lie confidently, and the people you can hear from are rarely the ones you need.
- `communication/mental-models/references/models/scarcity.md` — Not having enough of something captures attention and degrades judgement about everything else.
- `communication/mental-models/references/models/second-order-thinking.md` — Ask "and then what?" at least twice — the first-order winner is often the second-order loser.
- `communication/mental-models/references/models/social-proof.md` — We infer correct behaviour from what others do, most strongly exactly when we are least certain.
- `communication/mental-models/references/models/trade-offs.md` — The real cost of a choice is the best thing you gave up to make it, not the money you spent.

## creative/architecture-diagram

- `creative/architecture-diagram/references/archify-typed-json-gates.md` — Archify 3.0.1: typed-JSON diagrams (architecture, workflow, sequence, dataflow, lifecycle) rendered to standalone interactive HTML behind a four-gate finalize command; run live with a planted dangling-edge defect

## creative/ascii-video

- `creative/ascii-video/references/architecture.md` — Architecture Reference
- `creative/ascii-video/references/composition.md` — Composition & Brightness Reference
- `creative/ascii-video/references/effects.md` — Effect Catalog
- `creative/ascii-video/references/inputs.md` — Input Sources
- `creative/ascii-video/references/optimization.md` — Optimization Reference
- `creative/ascii-video/references/scenes.md` — Scene System & Creative Composition
- `creative/ascii-video/references/shaders.md` — Shader Pipeline & Composable Effects
- `creative/ascii-video/references/troubleshooting.md` — Troubleshooting Reference

## creative/awwwards-gsap-motion

- `creative/awwwards-gsap-motion/references/acceptance-gates.md` — Acceptance gates for motion-heavy pages: slopscan rule list, honest perf measurement (DPR, GPU, prod build), serve-don't-file://, fallback-payload check

## creative/baoyu-infographic

- `creative/baoyu-infographic/references/analysis-framework.md` — Infographic Content Analysis Framework
- `creative/baoyu-infographic/references/base-prompt.md` — (no description)
- `creative/baoyu-infographic/references/layouts/bento-grid.md` — bento-grid
- `creative/baoyu-infographic/references/layouts/binary-comparison.md` — binary-comparison
- `creative/baoyu-infographic/references/layouts/bridge.md` — bridge
- `creative/baoyu-infographic/references/layouts/circular-flow.md` — circular-flow
- `creative/baoyu-infographic/references/layouts/comic-strip.md` — comic-strip
- `creative/baoyu-infographic/references/layouts/comparison-matrix.md` — comparison-matrix
- `creative/baoyu-infographic/references/layouts/dashboard.md` — dashboard
- `creative/baoyu-infographic/references/layouts/dense-modules.md` — dense-modules
- `creative/baoyu-infographic/references/layouts/funnel.md` — funnel
- `creative/baoyu-infographic/references/layouts/hierarchical-layers.md` — hierarchical-layers
- `creative/baoyu-infographic/references/layouts/hub-spoke.md` — hub-spoke
- `creative/baoyu-infographic/references/layouts/iceberg.md` — iceberg
- `creative/baoyu-infographic/references/layouts/isometric-map.md` — isometric-map
- `creative/baoyu-infographic/references/layouts/jigsaw.md` — jigsaw
- `creative/baoyu-infographic/references/layouts/linear-progression.md` — linear-progression
- `creative/baoyu-infographic/references/layouts/periodic-table.md` — periodic-table
- `creative/baoyu-infographic/references/layouts/story-mountain.md` — story-mountain
- `creative/baoyu-infographic/references/layouts/structural-breakdown.md` — structural-breakdown
- `creative/baoyu-infographic/references/layouts/tree-branching.md` — tree-branching
- `creative/baoyu-infographic/references/layouts/venn-diagram.md` — venn-diagram
- `creative/baoyu-infographic/references/layouts/winding-roadmap.md` — winding-roadmap
- `creative/baoyu-infographic/references/structured-content-template.md` — Structured Content Template
- `creative/baoyu-infographic/references/styles/aged-academia.md` — aged-academia
- `creative/baoyu-infographic/references/styles/bold-graphic.md` — bold-graphic
- `creative/baoyu-infographic/references/styles/chalkboard.md` — chalkboard
- `creative/baoyu-infographic/references/styles/claymation.md` — claymation
- `creative/baoyu-infographic/references/styles/corporate-memphis.md` — corporate-memphis
- `creative/baoyu-infographic/references/styles/craft-handmade.md` — craft-handmade (DEFAULT)
- `creative/baoyu-infographic/references/styles/cyberpunk-neon.md` — cyberpunk-neon
- `creative/baoyu-infographic/references/styles/hand-drawn-edu.md` — hand-drawn-edu
- `creative/baoyu-infographic/references/styles/ikea-manual.md` — ikea-manual
- `creative/baoyu-infographic/references/styles/kawaii.md` — kawaii
- `creative/baoyu-infographic/references/styles/knolling.md` — knolling
- `creative/baoyu-infographic/references/styles/lego-brick.md` — lego-brick
- `creative/baoyu-infographic/references/styles/morandi-journal.md` — morandi-journal
- `creative/baoyu-infographic/references/styles/origami.md` — origami
- `creative/baoyu-infographic/references/styles/pixel-art.md` — pixel-art
- `creative/baoyu-infographic/references/styles/pop-laboratory.md` — pop-laboratory
- `creative/baoyu-infographic/references/styles/retro-pop-grid.md` — retro-pop-grid
- `creative/baoyu-infographic/references/styles/storybook-watercolor.md` — storybook-watercolor
- `creative/baoyu-infographic/references/styles/subway-map.md` — subway-map
- `creative/baoyu-infographic/references/styles/technical-schematic.md` — technical-schematic
- `creative/baoyu-infographic/references/styles/ui-wireframe.md` — ui-wireframe

## creative/comfyui

- `creative/comfyui/references/official-cli.md` — comfy-cli Command Reference
- `creative/comfyui/references/rest-api.md` — ComfyUI REST + WebSocket API Reference
- `creative/comfyui/references/template-integrity.md` — ComfyUI Workflow-Template Integrity
- `creative/comfyui/references/workflow-format.md` — ComfyUI Workflow JSON Format

## creative/design-md

- `creative/design-md/references/antd-v6-design-md-exemplar.md` — Ant Design v6 as a real DESIGN.md exemplar and its theming API (ConfigProvider token/algorithm/components/cssVar), plus what its AGENTS.md teaches about agent-facing repo rules

## creative/design-taste-frontend

- `creative/design-taste-frontend/references/appendices.md` — design-taste-frontend appendices: install commands per design system, canonical doc links, Apple Liquid Glass web approximation
- `creative/design-taste-frontend/references/image-first-workflow.md` — Image-first web design-to-code workflow distilled from taste-skill's imagegen/image-to-code/brandkit skills - generate, analyze, implement; per-section frames; consistency rules
- `creative/design-taste-frontend/references/impeccable-detector.md` — impeccable 4.1.0: a deterministic anti-slop detector CLI for UI (npx impeccable detect) run live on planted-slop and clean HTML, plus its PRODUCT.md-first workflow and 24 commands
- `creative/design-taste-frontend/references/scroll-animation-skeletons.md` — GSAP canonical skeletons for design-taste-frontend: sticky-stack, horizontal-pan, scroll-reveal stagger (start/pin/scrub rules)

## creative/diagram-design

- `creative/diagram-design/references/animation.md` — Optional animation
- `creative/diagram-design/references/doctor.md` — Environment doctor
- `creative/diagram-design/references/export.md` — Export to PNG / SVG
- `creative/diagram-design/references/import-drawio.md` — Import from draw.io
- `creative/diagram-design/references/import-mermaid.md` — Import from Mermaid
- `creative/diagram-design/references/onboarding.md` — Onboarding — generate your skin from a design source
- `creative/diagram-design/references/output-spec.md` — Draw.io import output spec — format × size × detail × audience
- `creative/diagram-design/references/primitive-annotation.md` — Annotation Callout (italic-serif aside)
- `creative/diagram-design/references/primitive-icons.md` — Icons (primitive)
- `creative/diagram-design/references/primitive-sketchy.md` — Sketchy Filter (hand-drawn variant)
- `creative/diagram-design/references/primitive-terminal.md` — Terminal Window (CLI-chrome variant)
- `creative/diagram-design/references/profiles.md` — Client profiles
- `creative/diagram-design/references/semantic-patterns.md` — Semantic patterns
- `creative/diagram-design/references/style-guide.md` — Style Guide
- `creative/diagram-design/references/type-architecture.md` — Architecture
- `creative/diagram-design/references/type-bar.md` — Bar / Column Chart
- `creative/diagram-design/references/type-data-flow.md` — Data Flow
- `creative/diagram-design/references/type-db-schema.md` — Database Schema
- `creative/diagram-design/references/type-dependency.md` — Dependency Graph
- `creative/diagram-design/references/type-deployment.md` — Deployment
- `creative/diagram-design/references/type-dp-integration.md` — DP integration
- `creative/diagram-design/references/type-dp-security-matrix.md` — DP security matrix
- `creative/diagram-design/references/type-er.md` — ER / Data Model
- `creative/diagram-design/references/type-fishbone.md` — Fishbone / Ishikawa (root-cause)
- `creative/diagram-design/references/type-flowchart.md` — Flowchart
- `creative/diagram-design/references/type-gantt.md` — Gantt Chart
- `creative/diagram-design/references/type-high-level.md` — High-Level
- `creative/diagram-design/references/type-it-state.md` — IT current-state
- `creative/diagram-design/references/type-journey.md` — User Journey Map
- `creative/diagram-design/references/type-kanban.md` — Kanban Board
- `creative/diagram-design/references/type-layers.md` — Layer Stack
- `creative/diagram-design/references/type-line.md` — Line Chart
- `creative/diagram-design/references/type-loop.md` — Loop
- `creative/diagram-design/references/type-medallion.md` — Medallion
- `creative/diagram-design/references/type-nested.md` — Nested Containment
- `creative/diagram-design/references/type-org-chart.md` — Org Chart / Responsibility Map
- `creative/diagram-design/references/type-polar.md` — Polar Chart
- `creative/diagram-design/references/type-process.md` — Process
- `creative/diagram-design/references/type-pyramid.md` — Pyramid / Funnel
- `creative/diagram-design/references/type-quadrant.md` — Quadrant
- `creative/diagram-design/references/type-radar.md` — Radar / Spider
- `creative/diagram-design/references/type-sankey.md` — Sankey / Flow-Quantity
- `creative/diagram-design/references/type-scatter.md` — Scatter Plot
- `creative/diagram-design/references/type-sequence.md` — Sequence
- `creative/diagram-design/references/type-state.md` — State Machine
- `creative/diagram-design/references/type-story-map.md` — User Story Map
- `creative/diagram-design/references/type-swimlane.md` — Swimlane
- `creative/diagram-design/references/type-timeline.md` — Timeline
- `creative/diagram-design/references/type-tree.md` — Tree / Hierarchy
- `creative/diagram-design/references/type-treemap.md` — Treemap
- `creative/diagram-design/references/type-uml-class.md` — UML Class Diagram
- `creative/diagram-design/references/type-venn.md` — Venn / Set Overlap
- `creative/diagram-design/references/type-wardley.md` — Wardley Map

## creative/excalidraw

- `creative/excalidraw/references/colors.md` — Excalidraw Color Palette
- `creative/excalidraw/references/dark-mode.md` — Excalidraw Dark Mode Diagrams
- `creative/excalidraw/references/examples.md` — Excalidraw Diagram Examples

## creative/full-output-enforcement

- `creative/full-output-enforcement/references/llm-truncation-remediation.md` — Why models truncate/lazily answer and how to force complete outputs — root causes, parameter tuning, prompt templates; claims verified against primary sources where possible

## creative/manim-video

- `creative/manim-video/references/animation-design-thinking.md` — Animation Design Thinking
- `creative/manim-video/references/animations.md` — Animations Reference
- `creative/manim-video/references/camera-and-3d.md` — Camera and 3D Reference
- `creative/manim-video/references/decorations.md` — Decorations and Visual Polish
- `creative/manim-video/references/equations.md` — Equations and LaTeX Reference
- `creative/manim-video/references/graphs-and-data.md` — Graphs, Plots, and Data Visualization
- `creative/manim-video/references/mobjects.md` — Mobjects Reference
- `creative/manim-video/references/paper-explainer.md` — Paper Explainer Workflow
- `creative/manim-video/references/production-quality.md` — Production Quality Checklist
- `creative/manim-video/references/rendering.md` — Rendering Reference
- `creative/manim-video/references/scene-planning.md` — Scene Planning Reference
- `creative/manim-video/references/troubleshooting.md` — Troubleshooting
- `creative/manim-video/references/updaters-and-trackers.md` — Updaters and Value Trackers
- `creative/manim-video/references/visual-design.md` — Visual Design Principles

## creative/no-ai-slop

- `creative/no-ai-slop/references/community-pattern-proposals.md` — no-ai-slop: community pattern proposals & measured behavior (mined 2026-09-15)
- `creative/no-ai-slop/references/eval.md` — No AI slop eval

## creative/p5js

- `creative/p5js/references/animation.md` — Animation
- `creative/p5js/references/color-systems.md` — Color Systems
- `creative/p5js/references/core-api.md` — Core API Reference
- `creative/p5js/references/creative-coding-ecosystem.md` — Creative-coding libraries from awesome-creative-coding with npm versions (2026-10-05), the p5.js 1.x vs 2.x state, and what to reach for per task
- `creative/p5js/references/export-pipeline.md` — Export Pipeline
- `creative/p5js/references/interaction.md` — Interaction
- `creative/p5js/references/shapes-and-geometry.md` — Shapes and Geometry
- `creative/p5js/references/troubleshooting.md` — Troubleshooting
- `creative/p5js/references/typography.md` — Typography
- `creative/p5js/references/visual-effects.md` — Visual Effects
- `creative/p5js/references/webgl-and-3d.md` — WebGL and 3D

## creative/pretext

- `creative/pretext/references/patterns.md` — Pretext Patterns

## creative/static-site-seo

- `creative/static-site-seo/references/agent-ready-and-ai-search.md` — Agent-Ready Sites & the AI-Search Layer (AEO/GEO)
- `creative/static-site-seo/references/programmatic-pages-quality-gates.md` — Programmatic / Generated Pages: Quality Gates (for templated page families)

## creative/stitch

- `creative/stitch/references/taste-standard-design-system.md` — Worked example of the Stitch DESIGN.md output format - the Taste Standard design system

## creative/system-atlas

- `creative/system-atlas/references/design-language.md` — Atlas design language
- `creative/system-atlas/references/process-and-lessons.md` — Process and lessons

## creative/touchdesigner-mcp

- `creative/touchdesigner-mcp/references/3d-scene.md` — 3D Scene Reference
- `creative/touchdesigner-mcp/references/animation.md` — Animation Reference
- `creative/touchdesigner-mcp/references/audio-reactive.md` — Audio-Reactive Reference
- `creative/touchdesigner-mcp/references/dat-scripting.md` — DAT-Based Scripting Reference
- `creative/touchdesigner-mcp/references/external-data.md` — External Data Reference
- `creative/touchdesigner-mcp/references/geometry-comp.md` — Geometry COMP Reference
- `creative/touchdesigner-mcp/references/glsl.md` — GLSL Reference
- `creative/touchdesigner-mcp/references/layout-compositor.md` — Layout Compositor Reference
- `creative/touchdesigner-mcp/references/mcp-tools.md` — twozero MCP Tools Reference
- `creative/touchdesigner-mcp/references/midi-osc.md` — MIDI / OSC Reference
- `creative/touchdesigner-mcp/references/network-patterns.md` — TouchDesigner Network Patterns
- `creative/touchdesigner-mcp/references/operator-tips.md` — Operator Tips
- `creative/touchdesigner-mcp/references/operators.md` — TouchDesigner Operator Reference
- `creative/touchdesigner-mcp/references/panel-ui.md` — Panel & UI Reference
- `creative/touchdesigner-mcp/references/particles.md` — Particles Reference
- `creative/touchdesigner-mcp/references/pitfalls.md` — TouchDesigner MCP — Pitfalls & Lessons Learned
- `creative/touchdesigner-mcp/references/postfx.md` — Post-FX Reference
- `creative/touchdesigner-mcp/references/projection-mapping.md` — Projection Mapping Reference
- `creative/touchdesigner-mcp/references/python-api.md` — TouchDesigner Python API Reference
- `creative/touchdesigner-mcp/references/replicator.md` — Replicator COMP Reference
- `creative/touchdesigner-mcp/references/troubleshooting.md` — TouchDesigner Troubleshooting (twozero MCP)

## data-science/algorithms-python-catalog

- `data-science/algorithms-python-catalog/references/algorithms-from-scratch.md` — Algorithms From Scratch (verified)
- `data-science/algorithms-python-catalog/references/catalog-map.md` — TheAlgorithms/Python — Catalog Map & Decision Guide
- `data-science/algorithms-python-catalog/references/graph-algorithms-library-map.md` — Shortest path, assignment, flow, SCC, MST, topo-sort: the pathfinding crate's algorithm list mapped to scipy.sparse.csgraph / networkx calls, with live-verified traps
- `data-science/algorithms-python-catalog/references/llm-vs-expert-puzzle-solving.md` — What Norvig's Advent of Code 2025 LLM notebook measured (LLMs: all correct, ~5x more code, ~3x slower; missed input-specific shortcuts) and how to prompt for better; a verified puzzle-utilities block

## data-science/astro-toolkit-selection

- `data-science/astro-toolkit-selection/references/brahe-api-reference.md` — brahe 1.7.0 API reference — module map + verified propagation/SPK snippets
- `data-science/astro-toolkit-selection/references/catalog-data-sources.md` — astroquery + pds4_tools + cumulus — catalog/archive access for the small-body pipeline
- `data-science/astro-toolkit-selection/references/egobox-bayesian-optimization.md` — EGObox 0.38.0 (Rust EGO / Bayesian optimization with Python bindings Egor and Gpx), run live: README example reproduced, seed behaviour, evaluation count, Branin, surrogate behaviour
- `data-science/astro-toolkit-selection/references/hifitime-time-scales.md` — hifitime 4.3.1 (Rust + pip) for time scales, run live and cross-checked against astropy 8.0.1: correct scale offsets, but a 1-second TAI->UTC error at leap-second boundaries and UTC subtraction that ignores the leap second
- `data-science/astro-toolkit-selection/references/openscvx-patterns.md` — OpenSCvx patterns — State/Control/dynamics core loop, Hohmann constants, autotuners
- `data-science/astro-toolkit-selection/references/optimization-toolkit.md` — nyx-py / pygmo2 / mesa v3 / z3 / Pyomo / CamPyRoS — optimization & simulation toolkit
- `data-science/astro-toolkit-selection/references/orekit-python-notes.md` — Orekit from Python via orekit-jpype 13.1.9: pip-only setup with jdk4py, import-after-initVM rule, what works without data files, data setup helpers
- `data-science/astro-toolkit-selection/references/pykep-v3-notes.md` — pykep 3 (ESA trajectory design): Linux-only PyPI wheels, API map (Lambert, Lagrangian propagation, legs, trajopt, planets), where it fits vs brahe/OpenSCvx/pygmo
- `data-science/astro-toolkit-selection/references/rebound-n-body-notes.md` — REBOUND + REBOUNDx N-body notes: install reality on Windows (rebound wheel yes, reboundx sdist-only), units/G gotcha, Yarkovsky and radiation-force parameters, ASSIST pointer
- `data-science/astro-toolkit-selection/references/skyfield-api-reference.md` — skyfield 1.55 API reference — breaking changes, de430s.bsp 404, phase-angle trap
- `data-science/astro-toolkit-selection/references/spacekit-notes.md` — spacekit.js (typpo): browser 3D solar-system viewer on three.js; Orbit/Ephem run headless in Node and checked against astropy: planet presets are two-body, Saturn drifts to 1.5 AU by 1900
- `data-science/astro-toolkit-selection/references/spiceypy-notes.md` — SpiceyPy 8.2 notes: kernel-load discipline, error classes, 80-char kernel-pool truncation, SPICE's own AU, asteroid NAIF ids

## data-science/bit-identity-float-pipelines

- `data-science/bit-identity-float-pipelines/references/hashing-floats-xxhash.md` — Choosing and using a hash for bit-identity checks: xxh3 vs sha256 measured on this machine, canonical byte layout for float arrays (-0.0, NaN, endianness, order, dtype)

## data-science/build-systems-data

- `data-science/build-systems-data/references/data-engineering-tool-map.md` — Data-engineering tool picks from awesome-data-engineering with PyPI freshness and a Python 3.14 install trap (pip silently installs an old great-expectations 0.18 and luigi 3.6)

## data-science/economicspace-pipeline

- `data-science/economicspace-pipeline/references/data-sources-environment-entrypoints.md` — Data sources, environment & entry points (economicspace)
- `data-science/economicspace-pipeline/references/defect-classes-and-traps.md` — Defect classes, code traps & performance (economicspace)
- `data-science/economicspace-pipeline/references/dv-oracles-and-economics-sources.md` — External delta-v oracles + soft-assumption data sources — Asterank two-mode API correction (2026-09-07 re-probe #2), NHATS, per-element sigmas; 2026-09-12 deep pass adds keyless HF mirrors + licensing traps
- `data-science/economicspace-pipeline/references/load-bearing-assumptions.md` — Load-bearing model assumptions (economicspace)
- `data-science/economicspace-pipeline/references/low-thrust-screening-prospector.md` — How Karmanplus/prospector screens asteroids for low-thrust reachability: tiered solvers, errors-must-point-low rule, Edelbaum + intercept bracket (formula run live), validation vs Dawn/Psyche/Hayabusa2/DART, pixi/conda-forge install
- `data-science/economicspace-pipeline/references/yfinance-live-behaviour.md` — yfinance 1.7.0 as economicspace uses it (Ticker.history 5d on HG/GC/SI/PL/PA=F): failures are logged not raised, last bar can be an in-progress session, TIO=F data conflicts with the pipeline's CNY note

## data-science/evolutionary-ml

- `data-science/evolutionary-ml/references/ga-tuning-measured.md` — GA Tuning — Measured Lessons (CR-pipeline, 2026-09)

## data-science/jupyter-notebook

- `data-science/jupyter-notebook/references/notebook-tooling.md` — Notebook tooling run live (jupytext, nbformat, nbconvert, papermill, nbmake, nbdiff): text round-trips, validation, execution failures, parameter injection traps, tests, diffs

## data-science/optimization-modeling-pyomo

- `data-science/optimization-modeling-pyomo/references/formulations-and-algorithms.md` — Pyomo Formulations & Algorithms — measured from source + live execution
- `data-science/optimization-modeling-pyomo/references/pyomo-source-patterns.md` — Design Patterns Mined from Pyomo Source (portable to any Python project)

## data-science/orbital-mechanics-data

- `data-science/orbital-mechanics-data/references/economicspace-library-landscape.md` — Library landscape for the economicspace pipeline

## data-science/python-data-science

- `data-science/python-data-science/references/autograd-notes.md` — HIPS/autograd 1.9.1 on numpy 2.5: grad/jacobian/hessian usage, scipy.optimize integration, and the errors you hit (int input, non-scalar output, in-place assignment, sqrt at 0). Run live.
- `data-science/python-data-science/references/big-data-patterns.md` — Verified big-data patterns (duckdb ad-hoc SQL, polars lazy joins with cardinality checks, parquet row groups, incremental dedup) — all run on 200k-row fixtures, cross-checked against pandas
- `data-science/python-data-science/references/dask-notes.md` — dask 2026.8.0 DataFrame: when it helps (not at 4M rows), laziness, head() semantics, meta warnings, determinism; measured on this machine
- `data-science/python-data-science/references/experiment-design-sample-size.md` — Experiment Design & Sample Size (A/B test statistics)
- `data-science/python-data-science/references/gensim-notes.md` — gensim 4.4.0 (topic models, Word2Vec) install reality (no cp314 wheel) and a verified small run in a 3.11 venv: reproducibility, OOV errors, LDA
- `data-science/python-data-science/references/open3d-notes.md` — Open3D 0.20.0 for point clouds and meshes from Python: install size, headless geometry/ICP/IO checks run live, and the silent-failure traps (missing file returns an empty cloud)
- `data-science/python-data-science/references/plotly-notes.md` — plotly.py 7.1.0 for reports: HTML size (embedded JS 4.8 MB vs CDN 7.6 KB), JSON size, NaN handling, static export via kaleido 1.4 (needs Chrome), default browser renderer; run live
- `data-science/python-data-science/references/polars-pymc-api-reference.md` — polars + pymc API references — verified line-numbered facts from cloned sources
- `data-science/python-data-science/references/polars-v2-engine-and-breaking-changes.md` — polars 2.0 (rc) engine architecture + every breaking change live-verified on polars==2.0.0rc1 — streaming-by-default, row-order semantics, OOC spilling internals, GPU beta
- `data-science/python-data-science/references/seaborn-0-13-notes.md` — seaborn 0.13.2 on pandas 3.0 / matplotlib 3.11 / Python 3.14: 24 common calls run; deprecations that vanish in 0.14 (palette without hue, ci, distplot, shade), calls that fail, and new warnings
- `data-science/python-data-science/references/supervision-cv-notes.md` — roboflow supervision 0.30.7 (computer-vision utilities): Detections filtering/NMS, zones, line counting, annotators, run live on synthetic arrays; OpenCV optional, ByteTrack deprecated, silent empty result on bad input
- `data-science/python-data-science/references/sympy-notes.md` — sympy 1.14.0 for derivations feeding numeric code: exactness traps (Float vs Rational, nsimplify), equality, solve return shapes, lambdify broadcasting; run live

## data-science/space-data-pipelines

- `data-science/space-data-pipelines/references/belt-gradient-analysis-patterns.md` — Debiasing an asteroid taxonomy analysis (loggger101/asteroid-belt-gradient): published-labels-only rule, family collapse, size-complete vs inverse-completeness weighting, KS+Bonferroni, reproducibility layout; headline numbers
- `data-science/space-data-pipelines/references/data-gov-catalog-api.md` — catalog.data.gov search API as of 2026-10-05: the CKAN /api/3/action endpoints are gone (404); /search + /api/* replace them. Parameters, pagination, response shape, traps. Live-probed.
- `data-science/space-data-pipelines/references/flowsint-pipeline-patterns.md` — Flowsint Pipeline Architecture Patterns (verified from reconurge/flowsint @ 1820569, v1.2.12)
- `data-science/space-data-pipelines/references/hf-mirror-catalog.md` — All 230 keyless Hugging Face space/astro/physics mirrors from juliensimon/space-datasets — load_dataset one-liner, no API keys; grouped by domain
- `data-science/space-data-pipelines/references/lunar-gis-patterns-aegis.md` — Lunar GIS patterns from nasa/aegis (AEGIS): LPS projection math, GeoTIFF custom-CRS reconstruction, lgrs-verified port
- `data-science/space-data-pipelines/references/shared-library-internals.md` — hf_dataset_utils internals from juliensimon/space-datasets (230 pipelines): retry budget, TAP clients, HEASARC HTTP-200 failures, MAST keyset pagination, LFS recovery, watchdog
- `data-science/space-data-pipelines/references/source-parser-families.md` — Per-source parsing families from space-datasets (round-15): TLE two-line-element char positions + epoch century rule, PDS3/PDS4 fixed-width colspecs, GOES netCDF status pivot, Wikidata SPARQL dedup, HTML fixture testing
- `data-science/space-data-pipelines/references/space-data-licensing-audit.md` — Space-data licensing traps from space-datasets' own 2026-05-26 audit: ESA CC BY-NC, WDC Kyoto no-commercial, VizieR scientific-use terms, provider URL table

## data-science/sql-for-data

- `data-science/sql-for-data/references/sql-tooling-sqlglot-sqlfluff.md` — SQL tooling from awesome-db-tools, run live: sqlglot 30.21 transpile/parse/AST (silent semantic changes, unknown functions pass through) and sqlfluff 4.4 lint/fix; plus the migration/schema tool map

## devops/incident-response

- `devops/incident-response/references/incident-command-method.md` — Live Incident Command Method

## devops/rest-api-client

- `devops/rest-api-client/references/public-api-discovery.md` — Finding free public APIs with the public-api-lists JSON feed (837 entries, 48 categories): schema, how to query it, measured link health, and metadata errors found (NASA auth, redirected Launch Library)
- `devops/rest-api-client/references/ssrf-guard-and-outbound-http-hardening.md` — SSRF Guard & Outbound-HTTP Hardening (verified from reconurge/flowsint @ 1820569, v1.2.12)

## devops/system-design-scaling

- `devops/system-design-scaling/references/asynchronism-communication-security.md` — Asynchronism, Communication & Security
- `devops/system-design-scaling/references/case-study-patterns.md` — Case-Study Patterns (8 Worked Designs → Reusable Recipes)
- `devops/system-design-scaling/references/databases-and-caching.md` — Databases, NoSQL & Caching — Trade-Off Tables
- `devops/system-design-scaling/references/feature-flag-lifecycle.md` — Feature flags as a lifecycle: flag types and lifespans, ring/linear/log/cohort rollout maths, kill-switch registry fields, stale-flag detection and the traps in alirezarezvani's three scripts
- `devops/system-design-scaling/references/latency-and-estimation.md` — Latency Numbers & Back-of-the-Envelope Estimation
- `devops/system-design-scaling/references/oo-design-interview-patterns.md` — Object-Oriented Design Interview Patterns (6 Worked Exercises)
- `devops/system-design-scaling/references/scaling-tradeoffs-and-topics.md` — Scaling Trade-Offs & Networking Topics

## doc-coauthoring/references

- `doc-coauthoring/references/decision-document-formats-adr-rfc-tdd.md` — Decision Document Formats: ADR vs RFC vs TDD (verified from tech-leads-club/agent-skills @ 0ab82f6)
- `doc-coauthoring/references/repo-documentation-maintenance.md` — Maintaining Repo Documentation (README, DEPENDENCY, audit notes)

## email/himalaya

- `email/himalaya/references/configuration.md` — Himalaya Configuration Reference
- `email/himalaya/references/message-composition.md` — Message Composition with MML (MIME Meta Language)

## frontend-design/nicegui-app-builder

- `frontend-design/nicegui-app-builder/references/frontend-tooling.md` — nicegui / Front-End-Checklist MCP / HTMLHint / dashy — frontend tooling reference from starred clones
- `frontend-design/nicegui-app-builder/references/python-gui-toolkits.md` — Choosing a Python GUI toolkit (NiceGUI, Streamlit, Dear PyGui, plus others as reviewed) with Dear PyGui 2.3.1 run live: crash-on-no-context and duplicate-tag behaviour

## github/github-code-review

- `github/github-code-review/references/large-changeset-review-protocol.md` — Reviewing a large diff without cutting corners: deterministic file list, rule grouping, per-file checklist, coverage accounting, position verification, noise filtering
- `github/github-code-review/references/pr-judge-protocol-tlc.md` — Evidence-First PR Judge Protocol (verified from tech-leads-club/agent-skills @ 0ab82f6)
- `github/github-code-review/references/review-output-template.md` — Review Output Template

## github/github-issues

- `github/github-issues/references/untrusted-repo-content.md` — Threat model for gh CLI output + stale-item policy — distilled from affaan-m/ECC github-ops (MIT)

## github/github-pr-workflow

- `github/github-pr-workflow/references/agent-contribution-guardrails.md` — Agent Contribution Guardrails (PRs from coding agents to strict repos)
- `github/github-pr-workflow/references/ai-policies-of-starred-repos.md` — Per-repo AI-contribution rules found in 18 of the owner's 166 starred repos (disclose, no agents, no Co-Authored-By vs required Co-authored-by, PRs paused) and the check to run before any agent PR
- `github/github-pr-workflow/references/ci-ratchets-and-release-pipeline.md` — CI Ratchets & Release Pipeline (verified from reconurge/flowsint @ 1820569)
- `github/github-pr-workflow/references/ci-troubleshooting.md` — CI Troubleshooting Quick Reference
- `github/github-pr-workflow/references/conventional-commits.md` — Conventional Commits Quick Reference
- `github/github-pr-workflow/references/git-workflow-recipes.md` — High-value git recipes distilled from tiimgreen/github-cheat-sheet (MIT) — fixup/autosquash, PR checkout, revert
- `github/github-pr-workflow/references/github-web-ui-tricks.md` — Verified GitHub web-UI + URL tricks from tiimgreen/github-cheat-sheet (MIT) — diff params, compare URLs, gists-as-repos, templates

## github/github-repo-management

- `github/github-repo-management/references/github-api-cheatsheet.md` — GitHub REST API Cheatsheet

## github/issue-triage-state-machine

- `github/issue-triage-state-machine/references/AGENT-BRIEF.md` — Writing Agent Briefs
- `github/issue-triage-state-machine/references/OUT-OF-SCOPE.md` — Out-of-Scope Knowledge Base

## huggingface-trackio/references

- `huggingface-trackio/references/alerts.md` — Trackio Alerts
- `huggingface-trackio/references/logging_metrics.md` — Logging Metrics with Trackio
- `huggingface-trackio/references/retrieving_metrics.md` — Retrieving Metrics with Trackio CLI

## mcp/fastmcp

- `mcp/fastmcp/references/fastmcp-cli.md` — FastMCP CLI Reference
- `mcp/fastmcp/references/mcp-server-design-patterns-tlc.md` — MCP Server Design Patterns (verified from tech-leads-club/agent-skills @ 0ab82f6)

## media/youtube-content

- `media/youtube-content/references/output-formats.md` — Output Format Examples

## mlops/accelerate

- `mlops/accelerate/references/custom-plugins.md` — Custom Plugins for Accelerate
- `mlops/accelerate/references/megatron-integration.md` — Megatron Integration with Accelerate
- `mlops/accelerate/references/performance.md` — Accelerate Performance Tuning

## mlops/evaluation

- `mlops/evaluation/evaluating-llms-harness/references/api-evaluation.md` — API Evaluation
- `mlops/evaluation/evaluating-llms-harness/references/benchmark-guide.md` — Benchmark Guide
- `mlops/evaluation/evaluating-llms-harness/references/custom-tasks.md` — Custom Tasks
- `mlops/evaluation/evaluating-llms-harness/references/distributed-eval.md` — Distributed Evaluation
- `mlops/evaluation/weights-and-biases/references/artifacts.md` — Artifacts & Model Registry Guide
- `mlops/evaluation/weights-and-biases/references/integrations.md` — Framework Integrations Guide
- `mlops/evaluation/weights-and-biases/references/sweeps.md` — Comprehensive Hyperparameter Sweeps Guide

## mlops/inference

- `mlops/inference/llama-cpp/references/advanced-usage.md` — GGUF Advanced Usage Guide
- `mlops/inference/llama-cpp/references/hub-discovery.md` — Hugging Face URL Workflows for llama.cpp
- `mlops/inference/llama-cpp/references/optimization.md` — Performance Optimization Guide
- `mlops/inference/llama-cpp/references/quantization.md` — GGUF Quantization Guide
- `mlops/inference/llama-cpp/references/server.md` — Server Deployment Guide
- `mlops/inference/llama-cpp/references/troubleshooting.md` — GGUF Troubleshooting Guide
- `mlops/inference/llama-cpp/references/unsloth-local-workflow.md` — Unsloth local workflow (unslothai/unsloth, Apache-2.0): LoRA fine-tuning -> GGUF export pipeline + `unsloth start hermes` one-command local-model bridge
- `mlops/inference/serving-llms-vllm/references/optimization.md` — Performance Optimization
- `mlops/inference/serving-llms-vllm/references/quantization.md` — Quantization Guide
- `mlops/inference/serving-llms-vllm/references/server-deployment.md` — Server Deployment Patterns
- `mlops/inference/serving-llms-vllm/references/troubleshooting.md` — Troubleshooting Guide

## note-taking/knowledge-ops

- `note-taking/knowledge-ops/references/rag-platform-capabilities-weknora.md` — Capability checklist for a document RAG/knowledge platform, taken from Tencent WeKnora's README (hybrid search, citations, KB edit/rollback, sync connectors, agent memory, RBAC, MCP) plus how to evaluate one; README-sourced, not run

## productivity/box

- `productivity/box/references/bulk-operations.md` — Bulk operations
- `productivity/box/references/cli-guide.md` — Box CLI guide
- `productivity/box/references/content-workflows.md` — Content workflows
- `productivity/box/references/hubs.md` — Box Hubs
- `productivity/box/references/oauth-setup.md` — OAuth setup
- `productivity/box/references/rest-api.md` — REST API fallback
- `productivity/box/references/sdk-development.md` — SDK development
- `productivity/box/references/search-and-ai.md` — Search, metadata, and Box AI
- `productivity/box/references/troubleshooting.md` — Troubleshooting
- `productivity/box/references/webhooks-and-events.md` — Webhooks and events

## productivity/docx

- `productivity/docx/references/revisions-and-comments.md` — Revisions and Comments — XML details

## productivity/google-workspace

- `productivity/google-workspace/references/daily-brief.md` — Daily Brief (Gmail + Calendar)
- `productivity/google-workspace/references/gmail-search-syntax.md` — Gmail Search Syntax

## productivity/notion

- `productivity/notion/references/block-types.md` — Notion Block Types

## productivity/ocr-and-documents

- `productivity/ocr-and-documents/references/formula-ocr-pix2tex.md` — Image of a math formula to LaTeX with pix2tex (LaTeX-OCR): usage, stale pinned dependencies, install resolution on Python 3.14 (dry-run only), alternatives

## productivity/pdf

- `productivity/pdf/references/forms.md` — Building Fillable Forms: spec format and workflow

## productivity/teach

- `productivity/teach/references/GLOSSARY-FORMAT.md` — GLOSSARY.md Format
- `productivity/teach/references/LEARNING-RECORD-FORMAT.md` — Learning Record Format
- `productivity/teach/references/MISSION-FORMAT.md` — MISSION.md Format
- `productivity/teach/references/RESOURCES-FORMAT.md` — RESOURCES.md Format

## productivity/website-audit

- `productivity/website-audit/references/cro-form-ux-checklists.md` — CRO / Form / UX Audit Frameworks (for website audit reports)

## productivity/xlsx

- `productivity/xlsx/references/restructuring.md` — Reference-aware restructuring (xlsx_restructure.py)

## research/general-research-rounds

- `research/general-research-rounds/references/registry-rules-and-routes.md` — General_Research registry rules from its AGENTS.md/README that SKILL.md lacks (access classes, licence rule, log append-at-top, rejection, permanent ids) and fetch routes re-checked 2026-10-05
- `research/general-research-rounds/references/source-access-notes.md` — Source access notes (verified from this machine)

## research/grounded-citations

- `research/grounded-citations/references/citation-formats.md` — Citation formats per output target
- `research/grounded-citations/references/grounding-rationale.md` — Why numbered ledger ids (grounding research basis)

## research/research-paper-writing

- `research/research-paper-writing/references/ai-research-integrity-checklist.md` — Seven failure modes of AI-assisted research (buggy code, fake citations, invented results, shortcuts, bug-as-insight, fabricated methods, frame-lock) as a pre-submission gate; plus live citation-API checks
- `research/research-paper-writing/references/autoreason-methodology.md` — Autoreason: Iterative Refinement Methodology
- `research/research-paper-writing/references/checklists.md` — Conference Paper Checklists
- `research/research-paper-writing/references/citation-workflow.md` — Citation Management & Hallucination Prevention
- `research/research-paper-writing/references/experiment-patterns.md` — Experiment Design Patterns
- `research/research-paper-writing/references/hermes-tool-patterns.md` — Hermes tool-usage patterns for the paper pipeline: experiment monitoring, parallel drafting, memory/todo state, cronjob monitoring, notification rules
- `research/research-paper-writing/references/human-evaluation.md` — Human Evaluation Guide for ML/AI Research
- `research/research-paper-writing/references/paper-types.md` — Paper Types Beyond Empirical ML
- `research/research-paper-writing/references/phase5-paper-drafting.md` — Phase 5: Paper Drafting (full procedure)
- `research/research-paper-writing/references/phase7-submission-prep.md` — Phase 7 submission preparation: venue checklists, anonymization, formatting, pre-compile validation, resubmission, camera-ready, arXiv strategy, code packaging
- `research/research-paper-writing/references/reviewer-guidelines.md` — Reviewer Guidelines & Evaluation Criteria
- `research/research-paper-writing/references/sources.md` — Source Bibliography
- `research/research-paper-writing/references/writing-guide.md` — ML Paper Writing Philosophy & Best Practices

## security/application-threat-model

- `security/application-threat-model/references/threat-model-method.md` — Application Threat Model Method

## security/mattpocock-security-review

- `security/mattpocock-security-review/references/repository-threat-modeling.md` — Repository-Grounded Threat Modeling (verified from tech-leads-club/agent-skills @ 0ab82f6)

## security/oss-forensics

- `security/oss-forensics/references/evidence-types.md` — Evidence Types Reference
- `security/oss-forensics/references/github-archive-guide.md` — GitHub Archive Query Guide (BigQuery)
- `security/oss-forensics/references/investigation-templates.md` — Investigation Templates
- `security/oss-forensics/references/recovery-techniques.md` — Deleted Content Recovery Techniques

## security/security-audit

- `security/security-audit/references/AI-AND-LLM.md` — AI, LLM, and Agent Hunting
- `security/security-audit/references/ATTACK-CLASSES.md` — Attack Classes
- `security/security-audit/references/CLIENT-SIDE.md` — Client-Side and Browser Hunting
- `security/security-audit/references/CLOUD-AND-DEPLOYMENT.md` — Cloud and Deployment Hunting
- `security/security-audit/references/DATA-ISOLATION-AND-LIFECYCLE.md` — Data Isolation and Lifecycle Hunting
- `security/security-audit/references/DESKTOP-MOBILE-AND-LOCAL-IPC.md` — Desktop, Mobile, and Local IPC Hunting
- `security/security-audit/references/HUNTING.md` — Vulnerability Hunting
- `security/security-audit/references/MEMORY-SAFETY-AND-BINARY.md` — Memory Safety, Binary, and Kernel Hunting
- `security/security-audit/references/PROTOCOLS-RPC-AND-MESSAGING.md` — Protocols, RPC, and Messaging Hunting
- `security/security-audit/references/RECONNAISSANCE.md` — Reconnaissance
- `security/security-audit/references/RESOURCE-EXHAUSTION-AND-AVAILABILITY.md` — Resource Exhaustion and Availability Hunting
- `security/security-audit/references/SUPPLY-CHAIN-AND-RELEASE.md` — Supply Chain and Release Hunting
- `security/security-audit/references/VALIDATION-AND-REPORTING.md` — Validation, Structured Output, Verification, and Reporting
- `security/security-audit/references/WEB-PROTOCOL-AND-AUTH.md` — HTTP-Protocol and Authentication Hunting

## security/semgrep-rule-creator

- `security/semgrep-rule-creator/references/quick-reference.md` — Semgrep Rule Quick Reference
- `security/semgrep-rule-creator/references/workflow.md` — Semgrep Rule Creation Workflow

## software-development/architecture-metrics

- `software-development/architecture-metrics/references/modular-design-principles-violations-and-split-criteria.md` — Modular Design Principles: Violations & Split/Merge Criteria (verified from tech-leads-club/agent-skills @ 0ab82f6)
- `software-development/architecture-metrics/references/modular-monolith-boundary-validation.md` — Modular Monolith & Boundary Validation (verified from tech-leads-club/agent-skills @ 0ab82f6)
- `software-development/architecture-metrics/references/monolith-decomposition-pipeline.md` — Monolith Decomposition Analysis Pipeline (verified from tech-leads-club/agent-skills @ 0ab82f6)
- `software-development/architecture-metrics/references/sentrux-architecture-notes.md` — Sentrux Architecture Notes (source-level findings)
- `software-development/architecture-metrics/references/strangler-fig-migration-patterns.md` — Strangler Fig Migration Patterns (verified from tech-leads-club/agent-skills @ 0ab82f6)

## software-development/ast-grep

- `software-development/ast-grep/references/cli.md` — CLI reference — `sg` / `ast-grep`
- `software-development/ast-grep/references/install.md` — Install ast-grep
- `software-development/ast-grep/references/patterns.md` — Pattern syntax — meta-variables and how patterns parse
- `software-development/ast-grep/references/pitfalls.md` — Pitfalls — what breaks patterns and how to fix them
- `software-development/ast-grep/references/recipes.md` — Recipes — copy-paste patterns by language
- `software-development/ast-grep/references/sgconfig.md` — sgconfig.yml — project configuration
- `software-development/ast-grep/references/yaml-rules.md` — YAML rule reference — atomic, relational, composite, transform, fix

## software-development/codebase-onboarding

- `software-development/codebase-onboarding/references/gradle-agent-rules.md` — Gradle 9.8 repo's own instructions for coding agents: wrapper only, never full build or clean, target subprojects, -q, language levels, Spock test rules, public-API annotations; source-read
- `software-development/codebase-onboarding/references/style-guides-and-enforcers.md` — Find the style guide a repo follows and the tool that enforces it: language -> canonical guide (from awesome-guidelines) -> enforcer with current version, plus config files to detect

## software-development/conversation-to-spec

- `software-development/conversation-to-spec/references/spec-document-reviewer-prompt.md` — Spec Document Reviewer Prompt Template

## software-development/dispatching-parallel-agents

- `software-development/dispatching-parallel-agents/references/discovery-interview-and-critique-protocols.md` — Discovery Interview & Critique Protocols (verified from tech-leads-club/agent-skills @ 0ab82f6)
- `software-development/dispatching-parallel-agents/references/multi-agent-deliberation-jury.md` — Multi-Agent Deliberation: the Jury Protocol (verified from tech-leads-club/agent-skills @ 0ab82f6)

## software-development/dogfood

- `software-development/dogfood/references/issue-taxonomy.md` — Issue Taxonomy

## software-development/failure-signal-audit

- `software-development/failure-signal-audit/references/regex-scanner-false-greens.md` — Case study: regex security/lint scanners that report score 100 or PASS on real defects (Terraform scanner, flag auditors); checklist for trusting a scanner's green

## software-development/hermes-agent-skill-authoring

- `software-development/hermes-agent-skill-authoring/references/audit-script-pattern.md` — Building Repo-Health Audit Scripts for Hermes Skill Repositories
- `software-development/hermes-agent-skill-authoring/references/behavioral-skill-testing.md` — Behavioral Skill Testing (RED-GREEN for Discipline Skills)
- `software-development/hermes-agent-skill-authoring/references/frontmatter-audit-pattern.md` — Frontmatter Audit Pattern
- `software-development/hermes-agent-skill-authoring/references/harness-audit-dual-judge-traps.md` — Harness Audit Protocol: Dual-Judge + Planted Traps (verified from tech-leads-club/agent-skills @ 0ab82f6)
- `software-development/hermes-agent-skill-authoring/references/related-skills-audit.md` — Auditing and Fixing `related_skills` References
- `software-development/hermes-agent-skill-authoring/references/section-header-standardization.md` — Section Header Standardization
- `software-development/hermes-agent-skill-authoring/references/skill-evolution-pipeline.md` — DSPy+GEPA skill-evolution pipeline (NousResearch/hermes-agent-self-evolution) — verified CLI, requirements, when NOT to use
- `software-development/hermes-agent-skill-authoring/references/skill-registry-security.md` — Skill registry supply-chain + installer security patterns, mined from tech-leads-club/agent-skills (MIT code / CC-BY-4.0 content)
- `software-development/hermes-agent-skill-authoring/references/skill-repo-release-engineering.md` — Skill-Repo Release Engineering (versioning, update channel, generated blocks)
- `software-development/hermes-agent-skill-authoring/references/skill-seekers-generated-drafts.md` — Using Skill Seekers 3.10.0 to draft skill material from a codebase, docs, PDFs and more: offline run on a tiny project (3 s), what it generates, what is boilerplate, and how to finish it into a Hermes skill

## software-development/living-docs-governance

- `software-development/living-docs-governance/references/doc-example-verification.md` — Verify technical docs by executing their code examples: 5-phase fact-check, example-to-test conversion rules, and a runnable Node example checker (scripts/check_doc_examples.py) proven on planted defects

## software-development/mattpocock-diagnosing-bugs

- `software-development/mattpocock-diagnosing-bugs/references/library-audit-methodology.md` — (no description)

## software-development/mattpocock-spec-driven-development

- `software-development/mattpocock-spec-driven-development/references/spec-driven-patterns-tlc.md` — Spec-Driven Development Patterns (verified from tech-leads-club/agent-skills @ 0ab82f6)
- `software-development/mattpocock-spec-driven-development/references/spec-implementation-eval-methodology.md` — Spec-Implementation Evaluation Methodology (verified from tech-leads-club/agent-skills @ 0ab82f6)

## software-development/plan

- `software-development/plan/references/plan-document-reviewer-prompt.md` — Plan Document Reviewer Prompt Template

## software-development/python-craft

- `software-development/python-craft/references/codon-compiler-notes.md` — Codon (exaloop) Python-to-native compiler: when it pays off, what differs from CPython, @codon.jit, CLI flags, @par, and the doc inconsistencies; Linux/macOS only
- `software-development/python-craft/references/gof-patterns-in-python.md` — Which GoF patterns collapse into Python features (function, callable, generator, singledispatch, Enum, dataclass.replace); 19 runnable idioms, all asserted
- `software-development/python-craft/references/logging-loguru.md` — Python logging with loguru 0.7.3: setup, brace-format traps, diagnose=True secret leak, rotation/retention, serialize, stdlib interception
- `software-development/python-craft/references/modern-python-tooling.md` — Modern Python tooling: uv, ruff, ty, PEP 723
- `software-development/python-craft/references/stdlib-traps-windows.md` — Python stdlib traps measured on Windows / Python 3.14.6: open() cp1252 default, csv blank lines, rename vs replace, rmtree read-only, strftime %-d, json NaN, naive/aware datetimes; plus facts that are no longer traps
- `software-development/python-craft/references/windows-path-separator-trap.md` — Windows os.path.relpath yields backslashes; cross-platform path-string comparison fails silently.

## software-development/repo-atlas

- `software-development/repo-atlas/references/atlas-templates.md` — Atlas Document Templates

## software-development/rust-crate-picks

- `software-development/rust-crate-picks/references/bumpalo-arena-notes.md` — bumpalo 3.20 bump-arena notes: trade-offs, the no-Drop rule, reset, features, Send but not Sync, API names; source-read
- `software-development/rust-crate-picks/references/gpui-kit-notes.md` — gpui-kit 0.7 (Rust desktop UI on GPUI): layering, features, headless UI testing, and its tested-recipe documentation pattern; source-read
- `software-development/rust-crate-picks/references/uom-units-notes.md` — uom 0.38 (Rust type-safe units of measure): features, design, usage; plus the Python analogue pint 0.26.1 run live (dimension errors, temperature offset trap, AU and year definitions)

## software-development/systematic-debugging

- `software-development/systematic-debugging/references/condition-based-waiting.md` — Condition-Based Waiting (Replace Arbitrary Timeouts)
- `software-development/systematic-debugging/references/defense-in-depth.md` — Defense in Depth (Make the Bug Structurally Impossible)
- `software-development/systematic-debugging/references/root-cause-tracing.md` — Root-Cause Tracing (Trace Backward to the Original Trigger)

## software-development/test-driven-development

- `software-development/test-driven-development/references/writing-good-tests.md` — Writing Good Tests (Honest-Test Discipline)

## software-development/verification-culture

- `software-development/verification-culture/references/autonomous-operator-protocol-tlc.md` — Autonomous Operator Protocol: Evidence-or-Stop (verified from tech-leads-club/agent-skills @ 0ab82f6)

## web-development/browser-automation

- `web-development/browser-automation/references/playwright-visual-regression.md` — Playwright screenshot (visual regression) suites: per-platform baselines, first-run and update-snapshots behavior, one-assert-per-test, file-level sharding, patterns from Ionic's e2e suite

## web-development/publish-site

- `web-development/publish-site/references/cloudflare-ci-wrangler-action.md` — Deploying to Cloudflare Workers/Pages from GitHub Actions with wrangler-action v4: inputs, outputs, permissions, preview-per-PR, secrets

## web-development/react-ecosystem

- `web-development/react-ecosystem/references/awesome-react-map.md` — awesome-react categories with npm latest version and last-modified date for each pick (snapshot 2026-10-05), plus stale/renamed flags
- `web-development/react-ecosystem/references/deckgl-notes.md` — deck.gl 9.4.0 (WebGL2/WebGPU large-scale data visualization): lockstep packages, layers/views model, basemap pairing, what works in Node vs browser (checked), pitfalls
- `web-development/react-ecosystem/references/react-native-core.md` — React Native 0.87.1 requirements (Node, React peer), what you can and cannot build per OS, the monorepo layout and agent conventions from its AGENTS.md; npm/README-sourced
- `web-development/react-ecosystem/references/react-native-navigation.md` — React Native navigation choices (React Navigation 7 stable vs 8 alpha vs Expo Router) with npm versions and the default-branch trap; source-read
- `web-development/react-ecosystem/references/zustand-v5-notes.md` — Zustand 5.0.15 traps run against React 19.3 + jsdom: fresh-object selector loops, removed equality arg, setState replace flag, persist shallow merge and dropped versions, async hydration

## web-development/static-site-patterns

- `web-development/static-site-patterns/references/web-interface-guidelines-ui-checklist.md` — Web Interface Guidelines (UI/UX Review Checklist) [PORTED]
