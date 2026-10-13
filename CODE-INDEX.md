# CODE-INDEX

Flat index of all **200 code files** (52,257 lines total) in this second brain — one line each, grep-friendly.
Format: ``- `path` (kind, lang, N lines) — purpose _(owner)_``. Regenerate with `python tools/gen-code-index.py`.

## autonomous-ai-agents/hermes-agent

- `autonomous-ai-agents/hermes-agent/scripts/sync-installed-plugins.py` (script, python, 577 lines) — Sync the installed-plugins reference doc from the live Hermes environment

## autonomous-ai-agents/hermes-extensions

- `autonomous-ai-agents/hermes-extensions/templates/clock.mjs` (template, javascript, 51 lines) — Reference user widget: a live clock docked above the status bar. Copy to ~/.hermes/tui-widgets/clock.mjs, then…
- `autonomous-ai-agents/hermes-extensions/templates/plugin.js` (template, javascript, 97 lines) — Hermes desktop plugin template. Save as: \<hermes home>/desktop-plugins/\<id>/plugin.js (folder name == id) wher…

## creative/ascii-video

- `creative/ascii-video/tests/test_blend_modes.py` (test, python, 84 lines) — Run the blend-mode table that references/shaders.md teaches, on real arrays

## creative/comfyui

- `creative/comfyui/scripts/auto_fix_deps.py` (script, python, 225 lines)
- `creative/comfyui/scripts/check_deps.py` (script, python, 437 lines)
- `creative/comfyui/scripts/comfyui_setup.sh` (script, bash, 286 lines) — ComfyUI Setup — Install, launch, and verify using the official comfy-cli
- `creative/comfyui/scripts/extract_schema.py` (script, python, 315 lines)
- `creative/comfyui/scripts/fetch_logs.py` (script, python, 157 lines)
- `creative/comfyui/scripts/hardware_check.py` (script, python, 497 lines) — hardware_check.py — Detect whether this machine can realistically run ComfyUI locally
- `creative/comfyui/scripts/health_check.py` (script, python, 223 lines)
- `creative/comfyui/scripts/run_batch.py` (script, python, 243 lines)
- `creative/comfyui/scripts/run_workflow.py` (script, python, 796 lines)
- `creative/comfyui/scripts/ws_monitor.py` (script, python, 267 lines)
- `creative/comfyui/scripts/_common.py` (shared helper, python, 835 lines)
- `creative/comfyui/tests/conftest.py` (test, python, 64 lines) — Pytest configuration for the comfyui skill test suite
- `creative/comfyui/tests/test_check_deps.py` (test, python, 68 lines) — Tests for check_deps.py — focuses on parsing logic that doesn't need a server.
- `creative/comfyui/tests/test_cloud_integration.py` (test, python, 96 lines) — Integration tests against the live Comfy Cloud API
- `creative/comfyui/tests/test_common.py` (test, python, 443 lines) — Unit tests for _common.py — pure logic only, no network.
- `creative/comfyui/tests/test_extract_schema.py` (test, python, 182 lines) — Tests for extract_schema.py.
- `creative/comfyui/tests/test_run_workflow.py` (test, python, 210 lines) — Tests for run_workflow.py — focuses on logic that doesn't require a server.

## creative/diagram-design

- `creative/diagram-design/scripts/drawio_extract.py` (script, python, 875 lines) — Extract a normalized intermediate representation (IR) from a draw.io file
- `creative/diagram-design/scripts/mermaid_extract.py` (script, python, 1325 lines) — Extract a normalized intermediate representation (IR) from Mermaid text
- `creative/diagram-design/scripts/self_check.py` (script, python, 396 lines) — Self-check a generated diagram HTML file, with no third-party deps
- `creative/diagram-design/tests/test_self_check.py` (test, python, 93 lines) — scripts/self_check.py: every shipped example passes, and each rule fails on a planted

## creative/excalidraw

- `creative/excalidraw/scripts/upload.py` (script, python, 133 lines)

## creative/manim-video

- `creative/manim-video/scripts/setup.sh` (script, bash, 14 lines)

## creative/p5js

- `creative/p5js/scripts/export-frames.js` (script, javascript, 179 lines) — p5.js Skill — Headless Frame Export
- `creative/p5js/scripts/render.sh` (script, bash, 108 lines) — p5.js Skill — Headless Render Pipeline
- `creative/p5js/scripts/serve.sh` (script, bash, 28 lines) — p5.js Skill — Local Development Server
- `creative/p5js/scripts/setup.sh` (script, bash, 87 lines) — p5.js Skill — Dependency Verification

## creative/system-atlas

- `creative/system-atlas/assets/build.mjs` (script, javascript, 104 lines) — Builds \<outDir>/SYSTEM.md and \<outDir>/atlas.html from data.mjs (same folder)
- `creative/system-atlas/assets/data.example.mjs` (script, javascript, 87 lines) — Single source of truth for one atlas. Copy to \<atlas home>/data.mjs and edit

## creative/touchdesigner-mcp

- `creative/touchdesigner-mcp/scripts/setup.sh` (script, bash, 115 lines) — setup.sh — Automated setup for twozero MCP plugin for TouchDesigner

## creative/ui-ux-pro-max

- `creative/ui-ux-pro-max/scripts/core.py` (script, python, 1450 lines)
- `creative/ui-ux-pro-max/scripts/design_system.py` (script, python, 1836 lines)
- `creative/ui-ux-pro-max/scripts/reasoning_contract.py` (script, python, 119 lines) — Closed, non-executable grammar for design-system decision rules.
- `creative/ui-ux-pro-max/scripts/search.py` (script, python, 255 lines)

## data-science/algorithms-python-catalog

- `data-science/algorithms-python-catalog/scripts/algorithms_verify.py` (script, python, 504 lines) — Re-runnable verification harness for data-science/algorithms-python-catalog

## data-science/economicspace-pipeline

- `data-science/economicspace-pipeline/scripts/asterank_sigma_probe.py` (script, python, 162 lines) — Asterank orbit-sigma + Shoemaker-Helin dv probe
- `data-science/economicspace-pipeline/scripts/nhats_rank_crosscheck.py` (script, python, 218 lines) — NHATS rank cross-check for the economicspace closed-form dv estimator

## data-science/evolutionary-ml

- `data-science/evolutionary-ml/tests/test_skill_snippets.py` (test, python, 104 lines) — Run the code SKILL.md teaches and assert the claims its prose makes about it

## data-science/lunar-gis-projections

- `data-science/lunar-gis-projections/scripts/cap_grid_verify.py` (script, python, 248 lines) — Verify AEGIS cap-grid tiling invariants + LGRS converter logic (stdlib only)
- `data-science/lunar-gis-projections/scripts/lps_projection_verify.py` (script, python, 131 lines) — Verify the south-pole Lunar Polar Stereographic (LPS) projection math used by nasa/aegis (AEGIS)

## data-science/optimization-modeling-pyomo

- `data-science/optimization-modeling-pyomo/scripts/pyomo_patterns_verify.py` (script, python, 174 lines) — Live-verify the Pyomo patterns documented in this skill

## data-science/polars-pipelines

- `data-science/polars-pipelines/references/big-data-patterns-verify.py` (script, python, 299 lines) — Verify the general big-data patterns for python-data-science reference doc
- `data-science/polars-pipelines/references/polars-v2-verify.py` (script, python, 589 lines) — Live verification of polars 2.0.0rc1 behavior claims (from docs/source/releases/upgrade/2.md)

## data-science/regex-vs-llm-structured-text

- `data-science/regex-vs-llm-structured-text/scripts/hybrid_parser.py` (script, python, 172 lines) — Hybrid structured-text parser: regex first, LLM only for flagged edge cases
- `data-science/regex-vs-llm-structured-text/tests/test_hybrid_parser.py` (test, python, 159 lines) — Tests for the hybrid regex/LLM structured-text parser

## data-science/space-data-pipelines

- `data-science/space-data-pipelines/scripts/pipeline_skeleton.py` (script, python, 256 lines) — Runnable reference implementation of the space-datasets pipeline pattern
- `data-science/space-data-pipelines/tests/test_pipeline_skeleton.py` (test, python, 183 lines) — scripts/pipeline_skeleton.py offline: the helpers and validation gate against stubbed HTTP,

## devops/rest-api-client

- `devops/rest-api-client/scripts/ssrf_guard_verify.py` (script, python, 288 lines) — Live-verification harness for the Flowsint outbound-HTTP hardening patterns

## devops/sqlite-queries

- `devops/sqlite-queries/tests/conftest.py` (test, python, 55 lines) — Shared fixtures: a small deterministic SQLite DB exercising users/orders/FKs.
- `devops/sqlite-queries/tests/test_sqlite_queries.py` (test, python, 275 lines) — Verify the sqlite-queries skill's documented workflow against real SQLite behavior

## devops/system-design-scaling

- `devops/system-design-scaling/scripts/availability_math.py` (script, python, 132 lines) — Availability math — verifies the "nines" downtime tables and sequence/parallel
- `devops/system-design-scaling/scripts/lru_cache_o1.py` (script, python, 129 lines) — O(1) LRU cache — implements the design doc from donnemartin/system-design-primer's
- `devops/system-design-scaling/scripts/shortlink_base62.py` (script, python, 115 lines) — Base62 URL shortener — implements + verifies the pastebin/Bit.ly pattern from
- `devops/system-design-scaling/scripts/topk_mapreduce_sim.py` (script, python, 108 lines) — Top-k-per-group via two-stage MapReduce — simulates the sales_rank case study from
- `devops/system-design-scaling/tests/test_scripts.py` (test, python, 121 lines) — The four worked-example scripts: their built-in self-tests run, and are not vacuous

## devops/watchers

- `devops/watchers/scripts/watch_github.py` (script, python, 187 lines) — Watch GitHub activity — issues, pulls, releases, or commits — with dedup
- `devops/watchers/scripts/watch_http_json.py` (script, python, 169 lines) — Watch any JSON endpoint that returns a list of objects; dedup by ID field
- `devops/watchers/scripts/watch_rss.py` (script, python, 141 lines) — Watch an RSS 2.0 or Atom feed; print new items to stdout, silent on empty
- `devops/watchers/scripts/_watermark.py` (shared helper, python, 207 lines) — Shared watermark helper used by the three watcher scripts
- `devops/watchers/tests/test_watchers.py` (test, python, 367 lines) — The watcher scripts and their shared watermark, offline

## devops/wizard

- `devops/wizard/template.sh` (script, bash, 204 lines) — A wizard walks a human through a manual procedure, step by step

## github/github-auth

- `github/github-auth/scripts/gh-env.sh` (script, bash, 66 lines) — GitHub environment detection helper for Hermes Agent skills
- `github/github-auth/scripts/git-credential-token.py` (script, python, 65 lines) — Print the first unambiguous GitHub token in a git credential-store file.

## github/github-code-review

- `github/github-code-review/scripts/scan_bypasses.py` (script, python, 79 lines) — invariant: hits are Pass F candidates, never findings; always exit 0 so a detector cannot block the review
- `github/github-code-review/tests/test_scan_bypasses.py` (test, python, 80 lines) — scripts/scan_bypasses.py: every category fires on an added line, never on context or

## mcp/fastmcp

- `mcp/fastmcp/scripts/scaffold_fastmcp.py` (script, python, 73 lines) — Copy a FastMCP starter template into a working file.
- `mcp/fastmcp/templates/api_wrapper.py` (template, python, 54 lines)
- `mcp/fastmcp/templates/database_server.py` (template, python, 77 lines)
- `mcp/fastmcp/templates/file_processor.py` (template, python, 55 lines)
- `mcp/fastmcp/tests/test_scaffold_fastmcp.py` (test, python, 77 lines) — scripts/scaffold_fastmcp.py and the three templates it renders (api_wrapper, database_server,

## media/youtube-content

- `media/youtube-content/scripts/fetch_transcript.py` (script, python, 125 lines)

## productivity/docx

- `productivity/docx/scripts/docx_comments.py` (script, python, 289 lines) — MIT License. Part of the Hermes docx skill
- `productivity/docx/scripts/docx_create.py` (script, python, 177 lines) — MIT License. Part of the Hermes docx skill
- `productivity/docx/scripts/docx_edit.py` (script, python, 250 lines) — MIT License. Part of the Hermes docx skill
- `productivity/docx/scripts/docx_read.py` (script, python, 149 lines) — MIT License. Part of the Hermes docx skill
- `productivity/docx/scripts/docx_revisions.py` (script, python, 147 lines) — MIT License. Part of the Hermes docx skill
- `productivity/docx/scripts/docx_template.py` (script, python, 70 lines) — MIT License. Part of the Hermes docx skill
- `productivity/docx/scripts/docx_validate.py` (script, python, 156 lines) — MIT License. Part of the Hermes docx skill
- `productivity/docx/specs/build-audit-v2.py` (script, python, 411 lines) — Append additional audit chapters to website-audit.docx.
- `productivity/docx/specs/build-audit-v3.py` (script, python, 807 lines) — Build a comprehensive, verified audit report for loganmedwardsastrophy.com portfolio
- `productivity/docx/specs/build-audit.py` (script, python, 535 lines) — Build the website audit .docx directly with python-docx.
- `productivity/docx/specs/patch-audit.py` (script, python, 43 lines) — Patch website-audit.docx to fix two factual errors found during final review.
- `productivity/docx/scripts/docx_common.py` (shared helper, python, 94 lines) — MIT License. Shared helpers for the docx skill scripts
- `productivity/docx/tests/test_docx_skill.py` (test, python, 525 lines) — MIT License. End-to-end tests for the docx skill

## productivity/google-workspace

- `productivity/google-workspace/scripts/google_api.py` (script, python, 1225 lines) — Google Workspace API CLI for Hermes Agent
- `productivity/google-workspace/scripts/gws_bridge.py` (script, python, 111 lines) — Bridge between Hermes OAuth token and gws CLI
- `productivity/google-workspace/scripts/setup.py` (script, python, 514 lines) — Google Workspace OAuth2 setup for Hermes Agent
- `productivity/google-workspace/scripts/_hermes_home.py` (shared helper, python, 42 lines) — Resolve HERMES_HOME for standalone skill scripts

## productivity/maps

- `productivity/maps/scripts/maps_client.py` (script, python, 1297 lines)

## productivity/ocr-and-documents

- `productivity/ocr-and-documents/scripts/extract_marker.py` (script, python, 87 lines) — Extract text from documents using marker-pdf. High-quality OCR + layout analysis
- `productivity/ocr-and-documents/scripts/extract_pymupdf.py` (script, python, 98 lines) — Extract text from documents using pymupdf. Lightweight (~25MB), no models

## productivity/pdf

- `productivity/pdf/scripts/pdf_create.py` (script, python, 130 lines) — Create a PDF from a JSON spec using reportlab platypus
- `productivity/pdf/scripts/pdf_fill_form.py` (script, python, 97 lines) — Fill AcroForm fields from a UTF-8 JSON file; optionally flatten
- `productivity/pdf/scripts/pdf_form_layout.py` (script, python, 168 lines) — Validate a form-spec layout BEFORE building the PDF, with optional
- `productivity/pdf/scripts/pdf_make_form.py` (script, python, 145 lines) — Create a fillable AcroForm PDF from a JSON spec (reportlab canvas.acroForm)
- `productivity/pdf/scripts/pdf_merge.py` (script, python, 50 lines) — Merge multiple PDFs into one, optionally adding a bookmark per source file.
- `productivity/pdf/scripts/pdf_meta.py` (script, python, 115 lines) — Document metadata and file attachments for PDFs (pypdf)
- `productivity/pdf/scripts/pdf_page_image.py` (script, python, 99 lines) — Export PDF pages as PNG images at a chosen DPI
- `productivity/pdf/scripts/pdf_read.py` (script, python, 153 lines) — Read a PDF: per-page text, tables, metadata, or form fields. JSON to stdout.
- `productivity/pdf/scripts/pdf_secure.py` (script, python, 71 lines) — Encrypt or decrypt a PDF with passwords (AES-256 via pypdf)
- `productivity/pdf/scripts/pdf_split.py` (script, python, 84 lines) — Extract page ranges from a PDF, optionally rotating and/or compressing pages.
- `productivity/pdf/scripts/pdf_stamp.py` (script, python, 143 lines) — Stamp text or an image at coordinates onto selected PDF pages
- `productivity/pdf/scripts/pdf_watermark.py` (script, python, 51 lines) — Stamp/watermark every page of a PDF with page 1 of another PDF.
- `productivity/pdf/scripts/_raster.py` (shared helper, python, 76 lines) — Shared page rasterizer with a fallback chain: pypdfium2 -> pdftoppm
- `productivity/pdf/tests/test_pdf_skill.py` (test, python, 414 lines) — End-to-end tests for the pdf skill helper scripts. No network required.

## productivity/powerpoint

- `productivity/powerpoint/scripts/pptx_create.py` (script, python, 214 lines) — Create a .pptx presentation from a JSON deck spec
- `productivity/powerpoint/scripts/pptx_edit.py` (script, python, 436 lines) — Edit a .pptx in place (or save to --output)
- `productivity/powerpoint/scripts/pptx_from_template.py` (script, python, 88 lines) — Build a deck from a .pptx template (brand deck) and fill placeholders
- `productivity/powerpoint/scripts/pptx_read.py` (script, python, 131 lines) — Read a .pptx file: JSON outline, notes, or export embedded images
- `productivity/powerpoint/scripts/pptx_render.py` (script, python, 93 lines) — Render every slide of a .pptx to per-slide PNG images
- `productivity/powerpoint/tests/test_powerpoint_skill.py` (test, python, 474 lines) — End-to-end tests for the powerpoint skill helper scripts

## productivity/session-librarian

- `productivity/session-librarian/scripts/transcript_stats.py` (script, python, 154 lines) — Read-only, context-safe stats for a Claude Code session transcript (.jsonl)
- `productivity/session-librarian/tests/test_transcript_stats.py` (test, python, 97 lines) — scripts/transcript_stats.py on synthetic Claude Code transcripts: usage counted once per

## productivity/xlsx

- `productivity/xlsx/scripts/csv_to_xlsx.py` (script, python, 115 lines) — Convert a CSV file to a styled .xlsx workbook with type inference
- `productivity/xlsx/scripts/xlsx_create.py` (script, python, 270 lines) — Create an .xlsx workbook from a JSON spec
- `productivity/xlsx/scripts/xlsx_edit.py` (script, python, 274 lines) — Edit an existing .xlsx workbook in place (or to --out)
- `productivity/xlsx/scripts/xlsx_read.py` (script, python, 171 lines) — Read an .xlsx workbook: inventory, JSON/CSV dumps, formula listing
- `productivity/xlsx/scripts/xlsx_recalc.py` (script, python, 122 lines) — Recalculate a workbook's formulas headlessly with LibreOffice
- `productivity/xlsx/scripts/xlsx_restructure.py` (script, python, 348 lines) — Reference-aware row/column insert and delete for .xlsx workbooks
- `productivity/xlsx/scripts/xlsx_to_csv.py` (script, python, 80 lines) — Export one sheet of an .xlsx workbook to CSV
- `productivity/xlsx/tests/test_xlsx_skill.py` (test, python, 542 lines) — End-to-end tests for the xlsx skill helper scripts

## research/arxiv

- `research/arxiv/scripts/search_arxiv.py` (script, python, 114 lines) — Search arXiv and display results in a clean format

## research/blocked-page-recovery

- `research/blocked-page-recovery/scripts/recover_page.py` (script, python, 241 lines) — Recover a blocked / paywalled / WAF'd page from third-party copies

## research/grounded-citations

- `research/grounded-citations/scripts/sources.py` (script, python, 678 lines) — Citation ledger for grounded answers and documents
- `research/grounded-citations/scripts/_hermes_home.py` (shared helper, python, 23 lines) — Resolve HERMES_HOME for standalone skill scripts

## research/rss-feeds

- `research/rss-feeds/scripts/feed.py` (script, python, 320 lines) — Read RSS / Atom / JSON Feed sources and discover feeds behind a page URL
- `research/rss-feeds/tests/test_feed.py` (test, python, 176 lines) — scripts/feed.py against a local HTTP server: RSS 2.0, Atom, RSS 1.0 and JSON Feed parsing,

## security/oss-forensics

- `security/oss-forensics/scripts/evidence-store.py` (script, python, 389 lines)
- `security/oss-forensics/tests/test_evidence_store.py` (test, python, 122 lines) — scripts/evidence-store.py: the CLI round trip, and `verify` catching every kind of

## security/security-audit

- `security/security-audit/scripts/validate-coverage-ledger.cjs` (script, javascript, 872 lines) — Validates coverage-ledger.json and its canonical coverage IDs. Usage: node validate-coverage-ledger.cjs \<path-…
- `security/security-audit/scripts/validate-coverage-ledger.test.cjs` (script, javascript, 740 lines)
- `security/security-audit/scripts/validate-findings.cjs` (script, javascript, 773 lines) — Validates findings.json against report-schema.json. Usage: node validate-findings.cjs \<path-to-findings.json>
- `security/security-audit/scripts/validate-findings.test.cjs` (script, javascript, 672 lines)

## social-media/reddit-reading

- `social-media/reddit-reading/scripts/reddit.py` (script, python, 385 lines) — Read Reddit without a browser: listings, search, threads with comments, user pages

## software-development/architecture-metrics

- `software-development/architecture-metrics/scripts/architecture_metrics.py` (script, python, 639 lines) — Architecture metrics: levels, violations, blast radius, A/I/D distance,
- `software-development/architecture-metrics/scripts/evolution_metrics.py` (script, python, 258 lines) — Git evolution metrics: churn, change coupling, temporal hotspots, code age, bus factor
- `software-development/architecture-metrics/scripts/quality_signal.py` (script, python, 481 lines) — Code quality signal: 5 ungameable root-cause metrics on a Python codebase
- `software-development/architecture-metrics/scripts/session_gate.py` (script, python, 148 lines) — Session quality gate: save an architectural baseline before an agent session,
- `software-development/architecture-metrics/tests/test_architecture_metrics.py` (test, python, 243 lines) — The four architecture-metrics scripts on fixture projects

## software-development/ast-grep

- `software-development/ast-grep/install.sh` (script, bash, 286 lines) — install.sh - install the ast-grep binary on POSIX systems (macOS, Linux, WSL, Git Bash)
- `software-development/ast-grep/scripts/ast_grep_helper.py` (script, python, 796 lines) — ast-grep-helper: a thin LLM-friendly wrapper around `sg` (ast-grep)
- `software-development/ast-grep/tests/smoke.sh` (test, bash, 254 lines) — Smoke test for the ast-grep skill on POSIX (macOS / Linux / WSL / Git Bash)

## software-development/generating-python-installer

- `software-development/generating-python-installer/scripts/analyze_dlls.py` (script, python, 143 lines) — DLL dependency footprint analyzer for a Nuitka standalone dist folder

## software-development/living-docs-governance

- `software-development/living-docs-governance/scripts/check_doc_examples.py` (script, python, 138 lines) — Run the JavaScript examples in Markdown docs and compare printed output to the comments
- `software-development/living-docs-governance/tests/test_check_doc_examples.py` (test, python, 79 lines) — scripts/check_doc_examples.py: matching docs pass, drift fails, and a run that checks

## software-development/multi-agent-deliberation

- `software-development/multi-agent-deliberation/scripts/tally_jury.py` (script, python, 337 lines) — Ported (verbatim but for strict input validation in main(), round-257) from tech-leads-club/agent-skills (CC-B…
- `software-development/multi-agent-deliberation/tests/test_tally_jury.py` (test, python, 127 lines) — scripts/tally_jury.py: the verdict cascade, and bad input refused instead of defaulted.

## software-development/repo-atlas

- `software-development/repo-atlas/scripts/generate_atlas.py` (script, python, 652 lines)
- `software-development/repo-atlas/tests/test_generate_atlas.py` (test, python, 122 lines) — scripts/generate_atlas.py, installed the way its usage line says (scripts/atlas/ inside a

## software-development/systematic-debugging

- `software-development/systematic-debugging/scripts/find_polluter.sh` (script, bash, 80 lines) — Bisection-style polluter finder: which test creates unwanted files/state?

## web-development/har-derived-api-client

- `web-development/har-derived-api-client/scripts/har_capture.py` (script, python, 81 lines) — Record a HAR file while driving a website with Playwright
- `web-development/har-derived-api-client/scripts/har_capture_cdp.py` (script, python, 141 lines) — Capture a HAR from a browser you connect to over CDP (not one you launch)
- `web-development/har-derived-api-client/scripts/har_to_client.py` (script, python, 187 lines) — Distill a HAR file into an API summary an agent can turn into a client
- `web-development/har-derived-api-client/tests/test_har_to_client.py` (test, python, 141 lines) — scripts/har_to_client.py on synthetic HAR files: API filtering, {id} grouping, header and

## web-development/web-perf-audit

- `web-development/web-perf-audit/scripts/perf_audit.py` (script, python, 254 lines) — Zero-dependency static-site audit of the machine-checkable Front-End Performance Checklist items
- `web-development/web-perf-audit/scripts/perf_audit_verify.py` (script, python, 131 lines) — Self-test for perf_audit.py: one clean site must pass, and each rule must fire on a planted defect

## Repo-level tooling (`tools/`, `.hermes/cron/`)

- `tools/_index_output.py` (shared helper, python, 81 lines) — Shared write-guard for the index generators (gen-*.py, regen-dependency-map.py)
- `tools/_repo_files.py` (shared helper, python, 25 lines) — The repo's file list, shared by the gates that scan code (check-lint, check-script-syntax,
- `.hermes/cron/templates/repo-automation.py` (template, python, 66 lines) — Repo Automation Cronjob Template (Two-Agent Split)
- `.hermes/cron/templates/skill-watchdog.py` (template, python, 47 lines) — Skill Watchdog Cronjob Template
- `tools/tests/conftest.py` (test, python, 27 lines) — Shared helpers for the tooling's own unit tests (run by verify-all's 'tool unit tests' gate)
- `tools/tests/test_index_output.py` (test, python, 63 lines) — _index_output.emit(): the write-guard and --check behind every index generator
- `tools/tests/test_sync_git_steps.py` (test, python, 187 lines) — sync-hermes-skills.py: the git steps (round-257)
- `tools/tests/test_sync_hermes_skills.py` (test, python, 176 lines) — sync-hermes-skills.py: the pre-push decision and error propagation
- `tools/tests/test_sync_installed_plugins.py` (test, python, 115 lines) — sync-installed-plugins.py: skips are exit 77, unreadable live state is exit 2
- `tools/tests/test_validate_skill_refs.py` (test, python, 79 lines) — .hermes/cron/validate-skill-refs.py (verify-all gate 'cron: skill refs') on throwaway trees
- `tools/tests/test_verify_all.py` (test, python, 117 lines) — verify-all.py: gate verdicts (PASS / FAIL / SKIP) and the audit summariser
- `.hermes/cron/validate-cronjobs.py` (repo tooling, python, 267 lines) — Validate cronjob JSON config files for structural correctness + cross-consistency
- `.hermes/cron/validate-skill-refs.py` (repo tooling, python, 66 lines) — Lightweight JSON + skill-ref validator (no_agent-compatible).
- `tools/audit-skills.py` (repo tooling, python, 554 lines)
- `tools/check-links.py` (repo tooling, python, 207 lines) — Broken-link checker for this second brain (stdlib only)
- `tools/check-lint.py` (repo tooling, python, 239 lines) — Gate: the repo's Python is clean under `ruff check` and `ruff format --check`, and every
- `tools/check-router-coverage.py` (repo tooling, python, 150 lines) — Gate: the skill-flow-router must keep pace with the catalog it claims to map
- `tools/check-script-coverage.py` (repo tooling, python, 185 lines) — Gate: every script the repo ships is exercised by a test, or is in the untested ledger
- `tools/check-script-syntax.py` (repo tooling, python, 190 lines) — Gate: every script the repo ships must at least parse
- `tools/check-skill-pointers.py` (repo tooling, python, 147 lines) — Check that every skill pointer written in prose names a skill that exists
- `tools/gen-claude-plugin.py` (repo tooling, python, 172 lines) — Regenerate the Claude Code plugin manifests from live skill frontmatter
- `tools/gen-code-index.py` (repo tooling, python, 222 lines) — Regenerate CODE-INDEX.md from live code files (flat, grep-friendly)
- `tools/gen-references-index.py` (repo tooling, python, 111 lines) — Rebuild REFERENCES-INDEX.md from every skill's references/ directory
- `tools/gen-skills-index.py` (repo tooling, python, 184 lines) — Regenerate SKILLS-INDEX.md from live skill frontmatter (flat, grep-friendly)
- `tools/mutation-test-audit-gate.py` (repo tooling, python, 148 lines) — Mutation test for audit-skills.run_audit — the per-skill audit checks test themselves
- `tools/mutation-test-cron-gate.py` (repo tooling, python, 116 lines) — Mutation self-test for the cron threshold-key verification (round-36)
- `tools/mutation-test-doc-gate.py` (repo tooling, python, 518 lines) — Mutation test for verify-all.check_doc_counts — the doc-count gate tests itself
- `tools/mutation-test-drift-gates.py` (repo tooling, python, 222 lines) — Mutation self-test for the five index drift gates (`--check` of every generator)
- `tools/mutation-test-link-gate.py` (repo tooling, python, 174 lines) — Mutation self-test for check-links.py
- `tools/mutation-test-pointer-gate.py` (repo tooling, python, 191 lines) — Mutation self-test for check-skill-pointers.py (round-65)
- `tools/mutation-test-router-gate.py` (repo tooling, python, 195 lines) — Mutation self-test for check-router-coverage.py (round-43)
- `tools/mutation-test-script-gates.py` (repo tooling, python, 275 lines) — Mutation self-test for the three round-257 code gates: check-script-syntax.py,
- `tools/mutation-test-secret-gate.py` (repo tooling, python, 168 lines) — Mutation test for audit-skills.scan_repo_for_secrets — the secret scan tests itself
- `tools/mutation-test-selftest-gate.py` (repo tooling, python, 184 lines) — Mutation self-test for tools/run-self-tests.py (the self-test harness gate)
- `tools/mutation-test-skilltest-gate.py` (repo tooling, python, 233 lines) — Mutation self-test for run-skill-tests.py, the runner behind CI's skill-tests job
- `tools/regen-dependency-map.py` (repo tooling, python, 140 lines) — Regenerate DEPENDENCY.md from live related_skills frontmatter (same format as repo convention).
- `tools/run-self-tests.py` (repo tooling, python, 327 lines) — Discovery-based runner for the skill self-test harnesses (*_verify.py)
- `tools/run-skill-tests.py` (repo tooling, python, 354 lines) — Discover and run every test suite that ships inside a skill, one command
- `tools/sync-hermes-skills.py` (repo tooling, python, 1290 lines)
- `tools/verify-all.py` (repo tooling, python, 585 lines) — Run every health gate in this repo and report one verdict

---
*200 code files: 119 scripts, 8 shared helpers, 37 tests. Keep in sync when adding/removing/renaming code (conventions: README 'Verification' section + tools/audit-skills.py).*
