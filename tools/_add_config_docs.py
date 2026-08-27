#!/usr/bin/env python
"""Add missing config references to aspirecures prompt."""
import json

p = '.hermes/cron/active/aspirecures-weekly.json'
d = json.load(open(p))

old = "  - date churn prevention (see below)\\n\\n== YOUR ROLE vs THE EXISTING CI PIPELINE =="
new = """  - date churn prevention (see below)\\n\\n== PER-PAGE CONFIG FIELDS (from tools/research/config.json defaults + per-page overrides) ==\\nThe config.json has a 'defaults' block that every page inherits, and each of the 9 disease pages\\nin data/research/<slug>.json can override individual settings:\\n  - article_query: Europe PMC free-text search query (page-specific boolean keyword expression; field tags like TITLE:, KW:, AUTH: are Europe-Pacific specific, simplifiedQuery strips them for WoS/Embase)\\n  - author_scope: BROAD disease clause ANDed with priority author list — wider than article_query, used in fetchPriorityAuthorArticles() to catch followed experts' papers. Falls back to trial_cond, then page title\\n  - trial_cond: The trial condition name used in ClinicalTrials.gov search (e.g. \"Alzheimer Disease\", \"Huntington Disease\", \"Multiple Sclerosis\")\\n  - recent_days: Recency window for articles (default 14). cutoff = TODAY - recent_days. Priority authors use priority_recent_days (default = recent_days)\\n  - max_fetch: Per-page cap on records per source (default 30). Alzheimer's sets its own max_fetch to avoid truncating its broader literature\\n  - max_priority_per_page: Max followed-author candidates gated per page (default 8). Capped to prevent same-surname author flooding\\n  - include_preprints: Boolean (default depends on config). When true, bioRxiv/medRxiv preprints (SRC:PPR) included with preprint:true flag and amber badge\\n  - priority_confidence_min: Lenient confidence threshold for priority-author candidates (default 0.6, vs 0.75 for regular). Both still pass same strict relevance gate\\n  - priority_authors: Array of {name, query} objects in config defaults. Each run runs an extra per-page author search\\n  - priority_recent_days: Wider recency window for priority authors (default = recent_days = 14)\\n  - max_tokens_per_run: Hard ceiling on Claude tokens (default 300000)\\n  - max_curations_per_run: Hard ceiling on Claude gate calls (default 200)\\n  - confidence_threshold: Confidence threshold for regular candidates (0.75)\\n  - trial_statuses: Set of recruiting trial statuses to fetch (default RECRUITING + ACTIVE_NOT_RECRUITING)\\n\\n== YOUR ROLE vs THE EXISTING CI PIPELINE =="

if old in d['prompt']:
    d['prompt'] = d['prompt'].replace(old, new)
    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print("Added per-page config fields to aspirecures prompt")
    print("  New prompt length:", len(d['prompt']))
else:
    print("ERROR: target string not found in prompt")
