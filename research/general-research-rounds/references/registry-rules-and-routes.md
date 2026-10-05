---
description: "General_Research registry rules from its AGENTS.md/README that SKILL.md lacks (access classes, licence rule, log append-at-top, rejection, permanent ids) and fetch routes re-checked 2026-10-05"
source_repo: loggger101/General_Research (the owner's repo; AGENTS.md and README.md read at 7eb1ff3 / R118, 2026-10-05)
tested_version: "Rules are source-read from the repo. Seven fetch routes were requested live from this Windows machine with urllib on 2026-10-05, each with a default and a browser User-Agent; results below are those responses"
verified_date: "2026-10-05"
---

# General_Research: rules and routes since SKILL.md was written

`SKILL.md` already carries the round loop, `sources_domain.csv` vs `sources.csv`, `build_registry.py` / `validate.py`, and
the `csv.writer(newline='')` rule. The registry has since reached R118 (501 sources: T1 x143, T2 x208, T3 x60, T4 x90; queue
164). These rules are in the repo's `AGENTS.md` / `README.md` and not in the skill. Each exists because it broke in a past
round.

## Access classes (first word of `access_status`)

| Class | Use when |
|---|---|
| `full_text_hosted` | file is in `<domain>/full_texts/` **and** has a row in `full_texts_manifest.csv` (`domain_dir,id,file,,,license`; the build fills `bytes,sha256`) |
| `public_domain_excerpt_hosted` | public-domain document too large to commit; the passage is quoted in `FINDINGS.md` |
| `verified_live_not_pulled` | fetched and read here but not committed (also: pulled but not legally hostable) |
| `open_not_pulled` | open access but the publisher blocks this machine or the licence forbids hosting; metadata and abstract recorded |
| `open_service` | live database/API verified here; derived numbers committed (write `open_service`, not `open service`) |
| `skipped` | deliberately not hosted; the user's decision is recorded |
| `registered_not_pulled` | an upstream citation registered so the dependency is visible; DOI or landing page checked live, full text **not** read. When you pull it, re-class it and say what you read |

## Rules to apply

- **Licence comes from the file or its record**, not the journal's general policy or where the copy came from: the PDF's own
  licence statement, NTRS `copyright.determinationType`, the arXiv abs page, or Crossref for the DOI. arXiv's default licence,
  an author-homepage copy and "free to read" grant no right to redistribute; only CC-licensed arXiv versions qualify. A
  2026-09-26 audit found 20 files hosted on the wrong grounds, one logged "CC BY per journal policy" whose PDF said "All
  rights reserved". `validate.py` warns on non-redistributable hosted files.
- **Research log is append-at-top only**: one entry `- **Round N** (YYYY-MM-DD): ...` above the previous one, that exact
  label (not `**RN**`, not a heading). Never rewrite or reorder older entries (two earlier rewrites deleted rounds; restored
  from git).
- **Extracted data lives in `<domain>/extracted_data/`**, never a root folder, and every CSV needs a `source_id` column
  (blank only for the pipeline's own value or a local comparison; `a;b` for a row derived from two sources). A source no CSV
  cites needs "Context-only: <reason>" in its registry row.
- **INDEX.md domain tables** list the same ids in the same order as `sources_domain.csv`; header
  `| id | tier | source (short) | access | backs / could replace |`, five cells per row with a closing `|`, no blank line
  inside the table (a blank line split one table; rows with three cells made GitHub drop the extra cells).
- **Read tables by word coordinates and check totals.** Taking numbers from the text stream mixed values between wrapped
  rows (one revision candidate was built on it and withdrawn).
- **Before un-hosting a file, extract every number the repo uses from it**, with page locations, and record the removed
  copy's size and sha256 in `access_status`.
- **Rejecting a source is the owner's call** and deletes its domain and INDEX rows, hosted files, extracted data, FINDINGS
  write-ups, DOWNLOADS entry and any revision candidate resting on it alone; the only record left is its row in INDEX.md
  "Rejected sources". Its id is never reused. `validate.py` fails if the id is named elsewhere.
- **Revision candidates**: when a source contradicts an upstream cell add a `revision_candidates.csv` row (next `rc-NNN`,
  status `open`) with the current upstream value and the commit read. When upstream changes, update `status`,
  `checked_against`, `checked_date` instead of adding a row. Upstream repos stay read-only from here.
- **IDs are permanent and used in full** everywhere (INDEX, `source_id`, candidates); an abbreviation broke a cross-reference.

## Fetch routes re-checked 2026-10-05 (urllib, GET)

| Target | Default UA | Browser UA | Note |
|---|---|---|---|
| `arxiv.org/pdf/2203.11229v1` | 200 `application/pdf` | 200 | R118 recorded 406 here; not reproduced today (a different `Accept` header or client may be involved) |
| `export.arxiv.org/pdf/2203.11229v1` | 200 `application/pdf` | 200 | the route R118 used when other mirrors failed |
| `www.aanda.org/articles/aa/pdf/2022/06/aa43587-22.pdf` | **403** | **403** | publisher direct PDFs stay blocked; use the arXiv copy if its licence allows |
| `sbnarchive.psi.edu/pds3/.../SDSSTAX_V1_1/` | **403** | 200 `text/html` | UA-gated: needs a browser-style User-Agent |
| `repository.arizona.edu/handle/10150/191871` (a handle page; not confirmed to be the Tholen dissertation) | 200 `text/html` | **403** | reversed: the browser UA is the one blocked on this host |
| `esa.int` Ariane 6 overview | 200 | 200 | readable; its terms bar reproduction, so record a hash only |
| `api.crossref.org/works/<doi>` | 200 `application/json` | 200 | use it to read the licence of a DOI |
| DNS `web.archive.org` | fails (`getaddrinfo` 11001) | | `archive.org` itself resolves (207.241.224.2): no Wayback snapshot route from this machine |

So: try the **other** User-Agent before declaring a source blocked (the gate runs in either direction), and note which one
worked in `access_status`. A 403 for both agents is a real block. Re-test a route before relying on an old note: routes
change within days.
