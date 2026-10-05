---
description: "Prompt-cache placement rules and a route-bound context budget (usable = window - output - reserve - history) with the invalidation table run through oh-my-hermes 3.0.0's omh CLI"
source_repo: rlaope/oh-my-hermes (MIT) - omh-context-budget-review skill and its cache-placement.md / route-capacity.md references
tested_version: "omh 3.0.0 installed from git (commit 01d8f22) into a uv Python 3.12 venv on Windows 11; 8 budget-plan commands run on 2026-10-05 plus a 10-step rebind loop. Cache-placement rules are source-read (they describe provider behaviour, not something OMH measures)"
verified_date: "2026-10-05"
---

# Context budget and prompt-cache placement

Two ideas from oh-my-hermes' `omh-context-budget-review` that apply to any long Hermes session. The mechanics in section 2 were
run; section 1 is guidance, and the source itself says cache hit counters are provider telemetry that nothing here observes.

## 1. Keep the prompt prefix byte-stable (source-read)

Major providers cache prompt prefixes by exact bytes; one changed byte at position N re-bills everything from N on.

1. Assemble instruction surfaces in a **fixed order, most stable first**; regeneration must give identical bytes.
2. **Volatile values stay below the fold**: dates, token counts, git state, status lines belong in the first user turn or at
   the tail, never in files loaded at session start.
3. **Mid-run changes are appended messages**, not edits to the system prompt or a session-start file (a rewrite rebuilds the
   whole cache; the source cites NousResearch/hermes-agent#13631 and #4319 for this failure).
4. **Keep the tool set fixed mid-session**: choose it at start, avoid connecting or dropping tool servers, serialise tool
   payloads with sorted keys, prefer deferred tool loading where the host supports it.
5. **Fan-outs share a byte-identical preamble**: sibling prompts start with the same bytes and add unit-specific text after;
   stagger the first dispatch so it writes the cache the others read.

`hermes-agent/references/contributor-guide.md` carries the matching rule for Hermes code ("never break prompt caching").
Do not claim a hit rate or saving without the host's usage counters.

## 2. A route-bound budget (run)

A budget computed for one provider/model goes stale when the host switches route. `omh context budget-plan` binds a plan to
the route and recomputes on `rebind`.

```
usable_budget = context_window - max_output - compaction_reserve - retained_history
```

Results of eight commands in a clean store (window 200 000, output 8 000, reserve 4 000, history 20 000, must-keep estimate 30 000):

| Command | Usable budget | Action / reason |
|---|---|---|
| `prepare`, all four fields `observed` | **168 000** (observed) | `continue` / `none`, `stale: false` |
| `rebind`, same capacity values | 168 000 | `continue` (plan unchanged) |
| `rebind`, window 100 000 | 68 000 | `checkpoint_required` / `capacity_shrank`, `stale: true`, old plan id kept as `superseded_plan_id` |
| `rebind`, window 36 000 | 4 000 (below the 30 000 must-keep) | `overflow_recovery_required` |
| `rebind`, no capacity file | `unknown`, value null (nothing inherited from the previous route) | `capacity_unknown_hold` / `capacity_unknown` |
| `prepare`, every field class `assumed` | class `assumed`, **value null** | `capacity_unknown_hold` |
| `prepare`, no capacity and no provider | `unknown` | `capacity_unknown_hold` |
| 10 consecutive *changed* rebinds | | `rebind_loop_hold` / `rebind_limit` |

So: an `observed` field needs an `observed_at` clock; an `assumed` value is kept visible but never produces a number; and a
plan that goes stale is a prepared obligation (checkpoint, shrink the pack, or review capacity), not a compaction that happened.
The must-keep pack stores a digest, a token estimate and per-class counts, never the text.

## 3. Traps hit while running it

- **No `oh-my-hermes` distribution is published on PyPI** (`pip index versions` and `pip download` found nothing) although
  the skill's `compatibility` line says `pip install oh-my-hermes`. Install from git:
  `uv pip install git+https://github.com/rlaope/oh-my-hermes` (builds in about a minute; zero runtime dependencies; needs
  Python 3.11+). Binary: `omh` / `omh.exe`.
- **State goes to `~/.omh/runtime/context-budget-plans/<session digest>.json` by default**, even with `HERMES_HOME` pointed
  elsewhere. Use `omh --omh-home <dir> context ...` for an isolated run (global flag listed in `omh --help`; not exercised here); a default-home run creates `~/.omh` if it is
  absent, so remove it after experiments.
- **Errors are class names only**: any bad input prints `Context budget plan unavailable: BudgetPlanError` with exit 2. The
  reason codes exist in `context_budget_plan_capacity.py`: `invalid_capacity_schema`, `invalid_capacity_field`,
  `invalid_evidence_timestamp`, `observed_capacity_missing_clock`, `invalid_token_allowance`, `invalid_must_keep_schema`,
  `invalid_must_keep_metadata`, `invalid_must_keep_item_class`, ... Read the source when it fails.
- **`capacity.json` must contain `"schema_version": "route_capacity_input/v1"`**; the doc's field list omits it, and extra
  keys are rejected. Each of `context_window_tokens`, `max_output_tokens`, `compaction_reserve_tokens`,
  `retained_history_tokens` is exactly `{"value","class","source","observed_at"}`; values are integers up to 1e9; `source`
  is an opaque id matching `[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,127}` (no URLs, prose or credential-like text); `observed_at`
  is ISO-8601 with a timezone, at most 40 characters.
- **`--must-keep` JSON** is `{"digest": "sha256:<64 hex>", "estimated_tokens_total": N, "item_classes": {...}}` where each
  class is `{"count": n, "refs": [...]}` (refs no more than count, unique, same opaque-id rule). The closed class vocabulary
  is `prohibitions, decisions, open_questions, requirements, paths, pr_state, verification_gaps`. Omitting `item_classes`
  makes a later comparison report "unavailable", not zero.
- `status` takes `--session-ref` and `--json` but not `--executor-profile`.

## 4. Already-ported OMH skills

Three skills here come from this repo (`incident-response`, `application-threat-model`, `failure-signal-audit`), ported 2026-09-17. Upstream commits after that (2026-09-25 and 2026-09-30) touch the OMH skill-description style and the persona and reply-language boilerplate. A section-level comparison shows the ports omit the OMH boilerplate blocks (Runtime Evidence, Recovery Notes, Completion Checklist) and two of them are condensed (70 vs 141 and 68 vs 138 lines); the substance was not diffed line by line. The repo holds roughly 100 more `omh-*` skills
(release cut, tech-debt audit, IaC change, relational DB, skill scout and others); they are process prose that needs the
`omh` CLI, and were not individually reviewed.
