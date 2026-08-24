# Drafting Guide

How to turn the research from `references/agent-vs-script-checklist.md` and the
repo's own documentation into the prompt body produced by `references/prompt-template.md`.

## Phase 1: Read the repo's three-layer stack

### Layer 1: The CI workflow (`.github/workflows/*.yml`)
This is the **canonical run sequence**. Read it end-to-end. Every `step:` block becomes
a step in your prompt. Note:
- The cron schedule (mirror it).
- `fetch-depth: 0` or `fetch-depth: 1` (the comments in the workflow usually explain why).
- Node version pins (the repo may have migrated off EOL versions — document the current one).
- Env var sources (`${{ secrets.X }}` → note which are required vs optional).
- The commit message format (other systems may watch for it).
- Any conditional logic (commit-if-changed: `if [ -n "$(git status --porcelain)" ]`).

### Layer 2: The main pipeline script (`tools/research/fetch_curate.mjs`)
This is the **source of truth for internal logic**. Read the header comments (usually
20-50 lines), then the key functions:
- The key-gated branch (`if (!KEY)` / `const CURATE = !!KEY`) — what runs without the key?
- The per-entity processing function (`processPage`) — the append-only merge, the
  signature comparison, the sort order.
- The dedup class (`Dedup`) — PMID + DOI + normalized title.
- The country normalization (`COUNTRY_FIX`, `COUNTRY_SET`, `countryFromAffiliation`).
- The structural validation (`toCandidate`) — real id, English, abstract ≥ 80, date window.
- The Claude gate call (`verdict()`) — the forced-tool structure, the system prompt,
  the retry logic.
- The signature/dedup (`canon()`, `dataSig()`, `UNRENDERED` map) — THIS is the
  date-churn prevention.

For each function, extract the **rationale** the comments give. "This is why X matters"
comments are guardrail material.

### Layer 3: The config + docs (`config.json`, `README.md`, `TODO.md`, `MAINTENANCE.md`)
- `config.json` — per-entity queries, relevance rules, thresholds, spend caps.
  READ THE `_comment` field — it explains non-obvious decisions.
- `README.md` — the high-level data flow, what each section does.
- `TODO.md` — what's open, what's decided, what guardrails exist. Each TODO item
  typically maps to a guardrail in your prompt.
- `MAINTENANCE.md` — operational context, rebuild order, Git-on-sync-client hazards.

## Phase 2: Map the CI steps to prompt steps

Create a table:

| CI step (from workflow) | What it does | Why it matters | Your prompt step |
|---|---|---|---|
| checkout (fetch-depth: 0) | Full git history | pagedate.pl walks commits | Step 1: git fetch --unshallow |
| setup-node@v4 | Node 24 | script needs global fetch | Env check |
| fetch_curate.mjs | Fetch + Claude-curate | The core pipeline | Step 2 + Step 6 |
| render.pl | Inject sections into HTML | Idempotent, marker-guarded | Step 8 |
| render-ads.pl | Re-inject ad rail | Resolves start/end dates | Step 9 |
| gen-sitemap.pl | Refresh lastmod | Disease dates ← generated | Step 10 |
| schema.pl | Refresh JSON-LD dateModified | dateModified ← generated | Step 11 |
| dedash.pl | Strip em/en dashes | House style | Step 12 |
| gen-feeds.pl | Rebuild RSS | lastBuildDate = newest item date | Step 13 |
| verify.sh | Health check | Refs resolve, no orphans | Step 14 |
| commit-if-changed | git commit + push | Only if diff exists | Step 15 |

For each step, the WHY column becomes the rationale text in your prompt.

## Phase 3: Identify the key-gated split

Find the line: `const KEY = process.env.ANTHROPIC_API_KEY;` or similar.
Find: `const CURATE = !!KEY;` or `if (!KEY) { ...maintenance... }`.

The maintenance-only branch is what runs without the key. Document every function call
in it — these are the steps the script STILL does when the agent substitutes for the key.

Everything else (fetch + Claude-curate + append-only merge) is what the AGENT must do.

**Critical:** The maintenance branch must NOT be skipped. It refreshes trial statuses
(which prevents advertising closed trials as "Recruiting") and re-checks retractions.
Document WHY this matters — it's almost always tied to a specific TODO.md item that
was a bug fix.

## Phase 4: Extract guardrails from TODO.md

Every TODO.md item that says "fixed" or "done" with a date was a bug that was caught
by running the pipeline. These become guardrails in your prompt. Pattern:

> "C8's first implementation compared the object against itself ... and reported 'no change'
> for everything"

→ Guardrail: "The signature must be taken BEFORE the maintenance passes run, because they
   mutate the stored arrays in place."

> "lint-feed.pl now ERRORs on markup in any rendered string, in both forms"

→ Guardrail: "Never store HTML markup in article titles or summaries. Europe PMC returns
   journal titles with italicized gene names as <i>GBA</i> — strip at ingest."

## Phase 5: Document the data file shape

Read the renderer (`render.pl` or equivalent) for each field:
- IS it rendered? (Does it appear on the page?) → counts as a data change
- IS it stored but NOT rendered? → EXCLUDE from the date-churn signature
- Does it drive any logic? (statusRaw → colour, id → dedup, date → sort)

The `UNRENDERED` map in the script is the canonical list. If you can't find one,
look for fields in the JSON that the renderer never reads — those are likely
unrendered and should be excluded from the signature.

## Phase 6: Write the failure modes

Scan the script and docs for `catch`, `warn`, `skip`, `error` patterns. Each one is a
failure mode. For each, write:
1. The scenario
2. The expected behavior (skip, best-effort, warn)
3. The agent's response (don't commit, investigate, retry, etc.)

Look for:
- API rate limits / 429 → retry with backoff
- API 500s → best-effort, skip that source
- Corrupt JSON → lint-feed.pl errors, don't commit
- render.pl skips → non-zero exit, don't commit
- Sync client issues (OneDrive mmap, conflict copies) — from MAINTENANCE.md
- git push conflicts — from the workflow's push step

## Phase 7: Match the serializer

The script writes JSON in a specific format. Find it:
- `JSON.stringify(obj, null, 2)` = 2-space indent, no sorted keys, `: ` separator
- `JSON::PP->new->pretty` or `JSON::PP->new->canonical` = 3-space indent, sorted keys

The agent must match this EXACTLY. If the agent's write format differs, the byte-level
date-churn check (if one exists) will see the cosmetic difference as a content change
and re-date everything on the first run.

## Phase 8: Build the output format

Look at what the script prints for its summary, and what the CI workflow echoes. Use
that as your model:

```
Research pipeline — model X, window 14d, 9 pages, spend cap 200/300000
  csf1r-alsp        +1 article(s) +0 trial(s)  (total 15/8)  updated -> 2026-08-25
  aars1aars2         +0 article(s) +0 trial(s)  (total 10/3)  no change (still 2026-08-18)
Done. 12 gate call(s), ~45320 Claude tokens this run.
```

The cronjob agent's output format should mirror this shape so regular readers of the
CI logs can quickly parse the cronjob's output too.
