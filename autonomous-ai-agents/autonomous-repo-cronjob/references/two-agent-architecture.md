# Two-Agent Architecture: Preparer vs. Commit Agent

When a cronjob must NOT write to the repo directly, split the work across two agent
roles. The cronjob produces a report; a separate commit agent consumes it.

## Why Split?

1. **Read-only safety** — The cronjob runs unattended on a schedule. If it has write access
   to the repo, a bug in the merge logic (or an API hiccup) can corrupt production data
   files silently. A read-only preparer eliminates this risk.

2. **Context limits** — The preparer's context holds candidate papers, abstracts, gate
   judgments, and existing data for dedup. That's a lot of content. By emitting a structured
   report, only the APPROVED items (not the full reasoning chain) propagate to the commit
   agent, keeping its context focused on the actual merge + render + validate work.

3. **Separation of concerns** — The preparer's job is judgment (gate, summarize, reject).
   The commit agent's job is precision (match serializer, compute signature, run render
   pipeline, handle git conflicts). Splitting lets each agent specialize.

4. **Debuggability** — The report is an artifact. If the commit agent fails, you can inspect
   the preparer's output offline, correct a verdict, and re-run the commit agent without
   re-hitting the APIs.

## The Report Structure

```json
{
  "run_date": "YYYY-MM-DD",
  "agent_role": "preparer",
  "mode": "MODE_B (agent-as-model)",
  "pages": [
    {
      "slug": "...",
      "relevance_rule": "...",           // exact string from config.json
      "maintenance_changes": {            // from Phase 1 maintenance pass
        "status_refresh": [...],
        "retractions_flagged": [...],
        "country_normalized": [...],
        "dates_clamped": [...],
        "data_signature_changed": true
      },
      "new_articles": [ ...approved items with verdict+summary... ],
      "new_trials":   [ ... ],
      "rejected_candidates": [ ...with reasons... ]
    }
  ],
  "commit_instructions": {
    "_purpose": "For the downstream commit agent ONLY. NOT written to data files.",
    "merge_steps": [ ...exact field stripping + sorting rules... ],
    "canonical_signature_algorithm": [ ...verbatim canon() + dataSig()... ],
    "render_pipeline_order": [ ... ],
    "health_checks": [ ... ],
    "commit_rules": [ ... ],
    "known_failure_responses": [ ... ]
  }
}
```

## Field Stripping Rules (CRITICAL)

The commit agent MUST strip these fields before writing to data/research/*.json:

- The entire `verdict` object (on_topic, credible, appropriate, confidence, etc.)
- `threshold_met`, `reason` (from inside verdict)
- `commit_instructions` (the whole block)
- `source` (transparency field, not stored data)
- Any `_`-prefixed field (`_abstract`, `_pmid`, `_doi`, `_priority`, `_summary`)
  — these are scratch fields used during curation but never stored

Only these fields survive in the data files:
- Articles: id, title, authors, journal, date, oa, country, preprint, retracted, url, summary
- Trials: id, nct, title, status, statusRaw, registry, location, countries, date, url, summary, outcome

## The Commit Agent's Job

1. Run Phase 1 (maintenance pass) itself — fresh trial statuses
2. For each page with maintenance changes: verify, re-run signature comparison
3. For each page with new items: merge per the stripping + sorting rules
4. Bump `generated` only if the canonical signature changed (before vs after merge)
5. Run the render pipeline in EXACT order:
   render.pl → render-ads.pl → gen-sitemap.pl → schema.pl → dedash.pl → gen-feeds.pl
6. Run health checks: lint-feed.pl + verify.sh (both must pass)
7. Commit + push IF git diff is non-empty; else print "No changes this run."

## When to Use This Pattern

✅ The user says "don't edit the repo, just prepare a report"
✅ The pipeline is complex enough that the commit agent benefits from fresh context
✅ Per-run context limits make it risky to have one agent do everything
✅ The user wants to inspect/review the report before committing

❌ Simple scripts where agent-writes-file directly is cleaner
❌ When the user explicitly wants the cronjob to do everything end-to-end
