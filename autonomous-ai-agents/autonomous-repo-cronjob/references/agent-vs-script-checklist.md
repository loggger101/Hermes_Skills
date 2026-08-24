# Agent-vs-Script Checklist

When a cronjob agent substitutes its own model access for a key-gated step in
an existing pipeline script, use this checklist to decide which pieces of internal
logic the **agent must replicate** vs. which the **script still handles** on its own.

## The Script Still Does (free, keyless steps)

Read the script to find the `if (!KEY)` branch. Everything in the FALSE branch
of the key check, plus everything before/after the curation call, runs regardless:

- [ ] **Trial status refresh** (re-reads the registry API for every published trial)
- [ ] **Retraction re-check** (re-queries for published article PMIDs)
- [ ] **Country normalization** (re-normalizes stored labels through COUNTRY_FIX map)
- [ ] **Future-date clamping** (clampFuture on stored dates)
- [ ] **Priority-author search** (if keyless — some pipelines gate this, some don't)
- [ ] **Structural validation** of candidates (the script does this before curation)
- [ ] **Append-only merge** into the data file (if the script can write without the key)

**Key principle:** The script's maintenance-only mode is NOT a no-op. It prevents
the pages from advertising a stopped trial as "Recruiting" indefinitely. The agent
must let it run (or replicate its logic manually if running the script isn't an option).

## The Agent Must Replicate (logic the script would have done with the key)

Everything in the `if (KEY)` / curation branch must be done by the agent:

- [ ] **Candidate collection** — run the same queries the script uses (read them from
  config.json: `article_query`, `trial_cond`, priority-author clause)
- [ ] **Cross-source union + dedup** — PMID AND DOI (and normalized title for
  cross-registry). Same paper from two databases = one entry.
- [ ] **The Claude gate** — for each candidate, decide:
  - on_topic (per the page's STRICT `relevance` rule in config.json)
  - credible (peer-reviewed or legit preprint server)
  - appropriate (patient-family appropriate, not sensational)
  - confidence ≥ threshold (0.75 normal, 0.60 for priority-author candidates)
- [ ] **Summary writing** — 65-95 words, house style, no em/en dashes, never medical advice
- [ ] **The append-only merge** — add approved items, keep existing, sort newest-first
- [ ] **The date-churn signature** — bump `generated`/date ONLY if canonical signature
  changed (excluding `generated` itself + unrendered fields)
- [ ] **Scratch-field stripping** — drop `_`-prefixed fields before writing to disk

## The Critical Handoff

The script writes the data file in its own JSON format (e.g. `JSON.stringify(x, null, 2)`
vs. Perl's `JSON::PP` with 3-space indent + sorted keys + `\" : \"` separators). If the
agent writes the file after the script ran, the agent must match the script's serializer
OR the byte-level date-churn check will see a cosmetic format difference as a content
change and re-date everything.

**Options:**
1. Let the script write the file (run it, let it handle Mode A writes, then the agent
   patches the file directly with new items — but must match the script's format).
2. Have the agent write the file entirely (skip the script's write, do everything
   manually — but must replicate ALL the script's normalization, de-dashing, etc.).

Option 1 is less error-prone. Document which serializer the script uses and match it.

## Decision Tree

```
Does the script's key-gated branch write to the data file?
  → YES: The agent must replicate the write logic, including format + signature check.
     If the agent's write format differs from the script's, the date-churn check
     fires on every run. Either match the script's serializer or do ALL writes
     the agent's way (never mix).
  → NO (the script only gates the API call, writes always): Let the script handle
     Mode A maintenance passes + writes. The agent only needs to inject the curated
     items afterward, matching the script's output format exactly.

Does the script strip em/en dashes before writing?
  → If the agent writes summaries, the agent must ALSO strip them (there is no
    automated deDash when the agent is the gatekeeper).
```

## What This Session Taught

The aspirecures repo's `fetch_curate.mjs` has this exact split:
- Mode A (no key): runs `recheckRetractions()`, `refreshTrialStatuses()`, country
  normalization, date clamping — writes the file. (TODO.md C7, fixed 2026-08-17.)
- Mode B (with key): ALSO runs `fetchArticles()` → `verdict()` → append-only merge.

When the cronjob agent substitutes for the key, the agent:
1. Lets Mode A run (the script writes refreshed statuses/retractions).
2. Collects candidates separately (using `check_queries.pl` as a starting point).
3. Gates each candidate itself.
4. Merges into the JSON, matching `JSON.stringify(x, null, 2)` format (2-space indent).
5. Computes the canonical signature (sorted keys, excluding `generated` +
   `trials[].countries`) to decide whether to bump `generated`.

The critical detail most agents miss: **the script's Mode A pass MUTATES the stored
arrays in place** (refreshTrialStatuses mutates `existingTrials`), so the signature
must be taken BEFORE Mode A runs, not after — otherwise it compares the object with
itself and always reports "no change." This is documented at fetch_curate.mjs:813-818.

### Two-Agent Split (Preparer vs. Commit Agent)

A critical pattern: the cronjob agent is a **PREPARER**, not an **EXECUTOR**. The agent
does NOT write to the repo's data files directly. Instead:

1. **Preparer Agent (the cronjob)** collects candidates, gates them, and emits a JSON
   report to stdout containing: approved new articles/trials with full verdict + summary,
   maintenance changes from Phase 1, rejected candidates, and a `commit_instructions` block.

2. **Commit Agent (downstream)** consumes the report and performs the actual repo edits:
   merges into data/research/*.json, then runs render.pl → render-ads.pl → gen-sitemap.pl
   → schema.pl → dedach.pl → gen-feeds.pl → lint-feed.pl → verify.sh → commit + push.

This split is used when:
- The user explicitly wants the cronjob to NOT touch repo files: "i dont want the cronjob
  to make any acctual edits to the repo rather i want it to prepare the articles and their
  in-website frameworks, with this report i want to be able to give it to another agent."
- Per-run context is limited (the report carries the full decision chain forward).
- The commit agent needs fresh context to run the full render pipeline and handle git
  conflicts.

The `commit_instructions` block must contain: exact merge field-stripping rules, the
canonical signature algorithm (verbatim canon() + dataSig() from the script), the exact
render pipeline order with line-number refs, the lint-feed.pl validation matrix, failure
responses, and the commit-if-changed logic.

### Autonomous Mode ≠ Non-Reasoning

The agent runs with NO user present and must NOT ask for API keys, confirmation, or
clarification. But it MUST still reason fully: sort candidates, evaluate on-topic relevance
against strict config.json rules, write 65-95 word summaries, apply confidence thresholds,
and self-validate. The constraint is on INTERACTION, not INTELLIGENCE.

If an API key for a PAID optional source is absent → silently skip that source, continue
with free sources. If a free API returns 429/500 → retry once with backoff, then skip that
source for that page. Do NOT fabricate data. Do NOT stop and wait for input.

### Exact Serializer Format

The script uses `JSON.stringify(x, null, 2)` for data files (2-space indent, `: ` and `,`
separators, no key sorting). The commit agent must match this EXACTLY — or do ALL writes
the agent's way (never mix). The signature computation excludes `generated` + `trials[].countries`
but INCLUDES `trials[].registry`, `articles.country`, `trials.location`, etc. (fields that
render.pl actually reads).

### Self-Validation Layer

The preparer agent should self-validate its approved items against `lint-feed.pl`'s rules
BEFORE emitting the report. This prevents the commit agent from hitting a lint-feed.pl failure:

- Article id: `^(?:PMID:\d+|DOI:\S+)$`  (lint-feed.pl:168-169)
- Trial id: `^(?:NCT:NCT\d+|ISRCTN:\S+)$`  (lint-feed.pl:198-199)
- Trial nct must match id: if id="NCT:NCT06000000", nct="NCT06000000"  (lint-feed.pl:205-209)
- statusRaw must be in render.pl's `%SCLASS` table  (lint-feed.pl:55-60 reads it, 222-224 checks it)
- NO HTML markup in any rendered field — check BOTH raw `<i>` AND escaped `&lt;i&gt;`  (lint-feed.pl:107-112, 184-191, 227-233)
- NO em/en dashes in any rendered field  (lint-feed.pl:91, 185-188, 228-232)
- No duplicate id within a page  (lint-feed.pl:157-162)
- Article url must be https://  (lint-feed.pl:174-175)
- Trial url must be https://  (lint-feed.pl:201-202)

If any approved item fails → move it to `rejected_candidates` with reason
"validation_failed: <check>". This pre-validates the report so the commit agent's
lint-feed.pl run will pass.

### lint-feed.pl Validation Matrix

| Check | What it validates | Critical failure if missed |
|---|---|---|
| JSON parseability | File must be valid JSON | Page ships stale content (silent!) |
| slug ↔ filename | data slug must match filename | Wrong disease attribution |
| generated date | Must be YYYY-MM-DD, not future | Page says "Updated" in future |
| id format | PMID:\d+ or DOI:\S+ (articles), NCT:NCT\d+ or ISRCTN:\S+ (trials) | Dedup breaks |
| nct ↔ id match | If id="NCT:NCT06000000", nct="NCT06000000" | Page prints wrong accession |
| statusRaw ∈ %SCLASS | Read from render.pl at load time | Unstyled status chip |
| HTML markup | raw `<i>` AND escaped `&lt;i&gt;` | Literal "<i>GBA</i>" on page |
| em/en dashes | All rendered text fields | House style violation |
| duplicate id | No id appears twice | Same paper shown twice |
| summary present | Articles MUST have summary | Bare citation, not patient-friendly |

### lint-feed.pl vs. verify.sh

- **lint-feed.pl**: validates the DATA JSON files (parseability, ids, statuses, markup,
  dashes, no dups, summaries present). Catches the silent failure: corrupt JSON → render.pl
  skips the page → stale content ships while looking fine (lint-feed.pl:16-22).
- **verify.sh**: validates the RENDERED SITE (refs resolve, no orphans, ad rail matches
  slots.json, registration backend tests, external links have target=_blank+noopener,
  ac-research:start marker present). Checks absolute URLs AND og:url/twitter:url meta tags
  against the host from tools/site.pl.

Both must pass. lint-feed.pl catches data corruption; verify.sh catches build/reference issues.
