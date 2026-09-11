# CODE-INDEX

Flat index of all **127 code files** (29,864 lines total) in this second brain — one line each, grep-friendly.
Format: `- `path` (kind, lang, N lines) — purpose _(owner)_`. Regenerate with `python tools/gen-code-index.py`.

## autonomous-ai-agents/hermes-agent

- `autonomous-ai-agents/hermes-agent/templates/clock.mjs` (template, javascript, 51 lines)
- `autonomous-ai-agents/hermes-agent/templates/plugin.js` (template, javascript, 97 lines)

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
- `creative/comfyui/tests/test_cloud_integration.py` (test, python, 95 lines) — Integration tests against the live Comfy Cloud API
- `creative/comfyui/tests/test_common.py` (test, python, 443 lines) — Unit tests for _common.py — pure logic only, no network.
- `creative/comfyui/tests/test_extract_schema.py` (test, python, 184 lines) — Tests for extract_schema.py.
- `creative/comfyui/tests/test_run_workflow.py` (test, python, 210 lines) — Tests for run_workflow.py — focuses on logic that doesn't require a server.

## creative/diagram-design

- `creative/diagram-design/scripts/drawio_extract.py` (script, python, 897 lines) — Extract a normalized intermediate representation (IR) from a draw.io file
- `creative/diagram-design/scripts/mermaid_extract.py` (script, python, 1355 lines) — Extract a normalized intermediate representation (IR) from Mermaid text
- `creative/diagram-design/scripts/self_check.py` (script, python, 389 lines) — Self-check a generated diagram HTML file, with no third-party deps

## creative/excalidraw

- `creative/excalidraw/scripts/upload.py` (script, python, 133 lines)

## creative/manim-video

- `creative/manim-video/scripts/setup.sh` (script, bash, 14 lines)

## creative/p5js

- `creative/p5js/scripts/export-frames.js` (script, javascript, 179 lines)
- `creative/p5js/scripts/render.sh` (script, bash, 108 lines) — p5.js Skill — Headless Render Pipeline
- `creative/p5js/scripts/serve.sh` (script, bash, 28 lines) — p5.js Skill — Local Development Server
- `creative/p5js/scripts/setup.sh` (script, bash, 87 lines) — p5.js Skill — Dependency Verification

## creative/touchdesigner-mcp

- `creative/touchdesigner-mcp/scripts/setup.sh` (script, bash, 115 lines) — setup.sh — Automated setup for twozero MCP plugin for TouchDesigner

## data-science/economicspace-pipeline

- `data-science/economicspace-pipeline/scripts/asterank_sigma_probe.py` (script, python, 134 lines) — Asterank orbit-sigma + Shoemaker-Helin dv probe
- `data-science/economicspace-pipeline/scripts/nhats_rank_crosscheck.py` (script, python, 188 lines) — NHATS rank cross-check for the economicspace closed-form dv estimator

## data-science/python-data-science

- `data-science/python-data-science/references/big-data-patterns-verify.py` (script, python, 125 lines) — Verify the general big-data patterns for python-data-science reference doc

## data-science/regex-vs-llm-structured-text

- `data-science/regex-vs-llm-structured-text/scripts/hybrid_parser.py` (script, python, 176 lines) — Hybrid structured-text parser: regex first, LLM only for flagged edge cases
- `data-science/regex-vs-llm-structured-text/tests/test_hybrid_parser.py` (test, python, 160 lines) — Tests for the hybrid regex/LLM structured-text parser

## data-science/space-data-pipelines

- `data-science/space-data-pipelines/scripts/pipeline_skeleton.py` (script, python, 206 lines) — Runnable reference implementation of the space-datasets pipeline pattern

## devops/sqlite-queries

- `devops/sqlite-queries/tests/conftest.py` (test, python, 54 lines) — Shared fixtures: a small deterministic SQLite DB exercising users/orders/FKs.
- `devops/sqlite-queries/tests/test_sqlite_queries.py` (test, python, 258 lines) — Verify the sqlite-queries skill's documented workflow against real SQLite behavior

## devops/watchers

- `devops/watchers/scripts/watch_github.py` (script, python, 169 lines) — Watch GitHub activity — issues, pulls, releases, or commits — with dedup
- `devops/watchers/scripts/watch_http_json.py` (script, python, 131 lines) — Watch any JSON endpoint that returns a list of objects; dedup by ID field
- `devops/watchers/scripts/watch_rss.py` (script, python, 121 lines) — Watch an RSS 2.0 or Atom feed; print new items to stdout, silent on empty
- `devops/watchers/scripts/_watermark.py` (shared helper, python, 148 lines) — Shared watermark helper used by the three watcher scripts

## devops/wizard

- `devops/wizard/template.sh` (script, bash, 204 lines) — A wizard walks a human through a manual procedure, step by step

## github/github-auth

- `github/github-auth/scripts/gh-env.sh` (script, bash, 66 lines) — GitHub environment detection helper for Hermes Agent skills
- `github/github-auth/scripts/git-credential-token.py` (script, python, 65 lines) — Print the first unambiguous GitHub token in a git credential-store file.

## mcp/fastmcp

- `mcp/fastmcp/scripts/scaffold_fastmcp.py` (script, python, 56 lines) — Copy a FastMCP starter template into a working file.
- `mcp/fastmcp/templates/api_wrapper.py` (template, python, 54 lines)
- `mcp/fastmcp/templates/database_server.py` (template, python, 77 lines)
- `mcp/fastmcp/templates/file_processor.py` (template, python, 55 lines)

## media/youtube-content

- `media/youtube-content/scripts/fetch_transcript.py` (script, python, 124 lines)

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
- `productivity/powerpoint/tests/test_powerpoint_skill.py` (test, python, 475 lines) — End-to-end tests for the powerpoint skill helper scripts

## productivity/xlsx

- `productivity/xlsx/scripts/csv_to_xlsx.py` (script, python, 104 lines) — Convert a CSV file to a styled .xlsx workbook with type inference
- `productivity/xlsx/scripts/xlsx_create.py` (script, python, 259 lines) — Create an .xlsx workbook from a JSON spec
- `productivity/xlsx/scripts/xlsx_edit.py` (script, python, 263 lines) — Edit an existing .xlsx workbook in place (or to --out)
- `productivity/xlsx/scripts/xlsx_read.py` (script, python, 160 lines) — Read an .xlsx workbook: inventory, JSON/CSV dumps, formula listing
- `productivity/xlsx/scripts/xlsx_recalc.py` (script, python, 111 lines) — Recalculate a workbook's formulas headlessly with LibreOffice
- `productivity/xlsx/scripts/xlsx_restructure.py` (script, python, 337 lines) — Reference-aware row/column insert and delete for .xlsx workbooks
- `productivity/xlsx/scripts/xlsx_to_csv.py` (script, python, 69 lines) — Export one sheet of an .xlsx workbook to CSV
- `productivity/xlsx/tests/test_xlsx_skill.py` (test, python, 542 lines) — End-to-end tests for the xlsx skill helper scripts

## research/arxiv

- `research/arxiv/scripts/search_arxiv.py` (script, python, 114 lines) — Search arXiv and display results in a clean format

## research/blocked-page-recovery

- `research/blocked-page-recovery/scripts/recover_page.py` (script, python, 241 lines) — Recover a blocked / paywalled / WAF'd page from third-party copies

## research/grounded-citations

- `research/grounded-citations/scripts/sources.py` (script, python, 678 lines) — Citation ledger for grounded answers and documents
- `research/grounded-citations/scripts/_hermes_home.py` (shared helper, python, 23 lines) — Resolve HERMES_HOME for standalone skill scripts

## security/oss-forensics

- `security/oss-forensics/scripts/evidence-store.py` (script, python, 313 lines)

## software-development/ast-grep

- `software-development/ast-grep/install.sh` (script, bash, 286 lines) — install.sh - install the ast-grep binary on POSIX systems (macOS, Linux, WSL, Git Bash)
- `software-development/ast-grep/scripts/ast_grep_helper.py` (script, python, 761 lines) — ast-grep-helper: a thin LLM-friendly wrapper around `sg` (ast-grep)
- `software-development/ast-grep/tests/smoke.sh` (test, bash, 212 lines) — Smoke test for the ast-grep skill on POSIX (macOS / Linux / WSL / Git Bash)

## software-development/code-quality-signal

- `software-development/code-quality-signal/scripts/quality_signal.py` (script, python, 366 lines) — Code quality signal: 5 ungameable root-cause metrics on a Python codebase

## software-development/generating-python-installer

- `software-development/generating-python-installer/scripts/analyze_dlls.py` (script, python, 136 lines) — DLL dependency footprint analyzer for a Nuitka standalone dist folder

## software-development/github

- `software-development/github/scripts/gh-env.sh` (script, bash, 66 lines) — GitHub environment detection helper for Hermes Agent skills
- `software-development/github/scripts/git-credential-token.py` (script, python, 65 lines) — Print the first unambiguous GitHub token in a git credential-store file.

## software-development/systematic-debugging

- `software-development/systematic-debugging/scripts/find_polluter.sh` (script, bash, 80 lines) — Bisection-style polluter finder: which test creates unwanted files/state?

## web-development/har-derived-api-client

- `web-development/har-derived-api-client/scripts/har_capture.py` (script, python, 72 lines) — Record a HAR file while driving a website with Playwright
- `web-development/har-derived-api-client/scripts/har_capture_cdp.py` (script, python, 135 lines) — Capture a HAR from a browser you connect to over CDP (not one you launch)
- `web-development/har-derived-api-client/scripts/har_to_client.py` (script, python, 147 lines) — Distill a HAR file into an API summary an agent can turn into a client

## Repo-level tooling (`tools/`, `.hermes/cron/`)

- `tools/_index_output.py` (shared helper, python, 61 lines) — Shared write-guard for the index generators (gen-*.py, regen-dependency-map.py)
- `.hermes/cron/templates/repo-automation.py` (template, python, 69 lines) — Repo Automation Cronjob Template (Two-Agent Split)
- `.hermes/cron/templates/skill-watchdog.py` (template, python, 47 lines) — Skill Watchdog Cronjob Template
- `.hermes/cron/validate-cronjobs.py` (repo tooling, python, 153 lines) — Validate cronjob JSON config files for structural correctness + cross-consistency
- `.hermes/cron/validate-skill-refs.py` (repo tooling, python, 56 lines) — Lightweight JSON + skill-ref validator (no_agent-compatible).
- `tools/audit-skills.py` (repo tooling, python, 429 lines)
- `tools/check-links.py` (repo tooling, python, 125 lines) — Broken-link checker for this second brain (stdlib only)
- `tools/gen-code-index.py` (repo tooling, python, 173 lines) — Regenerate CODE-INDEX.md from live code files (flat, grep-friendly)
- `tools/gen-references-index.py` (repo tooling, python, 100 lines) — Rebuild REFERENCES-INDEX.md from every skill's references/ directory
- `tools/gen-skills-index.py` (repo tooling, python, 159 lines) — Regenerate SKILLS-INDEX.md from live skill frontmatter (flat, grep-friendly)
- `tools/regen-dependency-map.py` (repo tooling, python, 101 lines) — Regenerate DEPENDENCY.md from live related_skills frontmatter (same format as repo convention).
- `tools/run-skill-tests.py` (repo tooling, python, 133 lines) — Discover and run every pytest suite that ships inside a skill, one command
- `tools/sync-hermes-skills.py` (repo tooling, python, 961 lines)
- `tools/verify-all.py` (repo tooling, python, 128 lines) — Run every health gate in this repo and report one verdict

---
*127 code files: 88 scripts, 7 shared helpers, 14 tests. Keep in sync when adding/removing/renaming code (conventions: README 'Verification' section + tools/audit-skills.py).*
