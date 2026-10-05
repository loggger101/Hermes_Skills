---
description: "Using Skill Seekers 3.10.0 to draft skill material from a codebase, docs, PDFs and more: offline run on a tiny project (3 s), what it generates, what is boilerplate, and how to finish it into a Hermes skill"
source_repo: yusufkaraaslan/Skill_Seekers (MIT)
tested_version: skill-seekers 3.10.0 pip-installed in a uv Python 3.12 venv (252 MB) on Windows; `detect` and `create ./proj --enhance-level 0` run on a 2-file Python project; web/PDF/video/GitHub sources and AI enhancement NOT run
verified_date: "2026-10-05"
---

# Skill Seekers as a draft generator for skills

Skill Seekers (`pip install skill-seekers`, 3.10.0 on 2026-09-30, MIT, Python `>=3.10`, classifiers to 3.13) turns sources into structured skill material. Its README claims **18 source types**: documentation sites, GitHub repositories, local codebases, PDF, Word, EPUB,
Jupyter, OpenAPI/Swagger, AsciiDoc, PPTX, RSS, man pages, Confluence, Notion, Slack/Discord exports, HTML, and video (with transcription), plus 40 MCP tools and packaging targets for several agents (`skill-seekers package output/x --target claude`).
Treat the output as a **first draft of references**, not a finished skill.

```bash
pip install skill-seekers
skill-seekers detect ./proj --json                        # how a source will be classified, creates nothing
skill-seekers create ./proj --enhance-level 0 --output out --non-interactive    # no AI enhancement; fully local
skill-seekers create <url|owner/repo|file.pdf|notebook.ipynb|openapi.yaml>      # other sources (not run here)
skill-seekers scan ./my-app --out configs/scanned/        # AI-driven: one config per detected framework (needs an agent; not run)
```

## What happened on a tiny project (offline)

Input: a two-file Python package (`tidekit/__init__.py` with two documented functions), a README and a test file.

- `detect ./proj --json` returned `{"type": "local", "suggested_name": "proj", "valid": true, ...}`.
- `create ... --enhance-level 0` finished in **3 s** with exit 0 and **no network or AI agent**: it analysed 2 files (Python 100%), found 1 markdown file, and wrote `out/SKILL.md` (68 lines), `out/code_analysis.json`, and `out/references/` with `api_reference/*.md`,
  `dependencies/` (`dependency_graph.dot`, `.json`, `.mmd`, `statistics.json`) and `documentation/` (index and extraction summary). Log noise included a PyMuPDF `fitz` deprecation warning.
- **The API reference was good**: per file, each function with its signature (`highs(day: datetime) -> list[datetime]`), docstring text and a parameter table (name, type, default).
- **The generated `SKILL.md` was boilerplate**: frontmatter `name: proj`, `description: Local codebase analysis for proj`, an empty `doc_version:`; the same generic "When to Use This Skill" bullets for any codebase; a checklist of analyses performed; the absolute local path; and a project overview parsed from the README as
  `**tidekit**: **tidekit**` (the real README sentence was lost).
- The frontmatter is not Hermes-shaped: no `version`, `author`, `platforms`, `metadata.hermes`, and the description is not a trigger-style summary within the repo's 59-character limit.

## How to turn the draft into a skill in this repo

1. Keep the generated `references/` (API reference, dependency graph) after skimming for errors; they save the mechanical part.
2. **Rewrite `SKILL.md` by hand** to the repo format (see `SKILL.md` of this skill): trigger-style description under 59 characters, `When to Use`, `What This Skill Does`, procedure, pitfalls, verification, and a `## References` list pointing at the generated files.
3. Replace the generic "When to Use" with the real tasks users bring; delete the absolute path; state the library version and the date the draft was generated.
4. Run a claim through the code before writing it as a fact (`living-docs-governance/references/doc-example-verification.md`), and register the skill (`tools/gen-*` indexes, counts, router lane).
5. For web/PDF sources, check licensing before redistributing generated text (`space-data-pipelines/references/space-data-licensing-audit.md` for the data-licence approach).

## When it is worth using

- A library with good docstrings and no skill yet: the API-reference extraction and dependency graph are real time savers.
- Many sources to normalise (docs site plus repo plus PDF): its merge mode and chunking for RAG (`--chunk-for-rag`) are the point; evaluate them on your own sources first.
- Not worth it when the knowledge is procedural and experience-based (a workflow, a set of pitfalls): that has to be written from running the work, as the starred-repo reviews in this ledger do.
