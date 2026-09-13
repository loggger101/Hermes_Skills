---
name: cron-pipeline-watchdog
description: "Watch cron pipelines for stale jobs; retry and escalate."
version: v1.0.0
author: Hermes Agent (pattern distilled from juliensimon/space-datasets stale-checker.py, 2026-09-12)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cron, monitoring, watchdog, github-actions, pipelines]
    related_skills: [space-data-pipelines, cron-job-authoring]
---

## What This Skill Does

A daily "watchdog" job that keeps a fleet of scheduled pipeline runs healthy without human babysitting: it derives each job's expected cadence from its own schedule expression, detects staleness (including silent success-with-failed-status-push), auto-retries transient failures with persistent state, and escalates persistent ones to idempotent issues. Distilled source-read 2026-09-12 from `juliensimon/space-datasets/scripts/stale-checker.py` — a production watchdog over ~108 GitHub Actions workflows that runs daily at 21:00 UTC (after all regular jobs).

## When to Use

- You have N scheduled data pipelines / cron jobs and want one job that notices when they stop updating
- Failures are mostly transient (upstream API outages) but some need human attention — you want automatic retry for the former, a tracked issue for the latter
- Status tracking lives in a file (status.json-style) that can drift from reality because the *push* of status failed even though the job itself succeeded

## The state machine (per dataset/job)

```
stale?  = today - last_success > period + GRACE_DAYS   OR never succeeded
period  = derived from the schedule expression (see below), not hardcoded per job

if GHA/CI status == success:      → repair status file FROM THE RUN LOGS (job worked, status push failed)
elif in_progress:                 → skip this cycle
else (failed):
    if name in NO_RETRY set:      → escalate immediately (re-triggering is dangerous — e.g. rate-limited/authed upstreams that ban accounts)
    elif retries < MAX_RETRIES(2):→ trigger re-run, bump persistent retry state {name: {retries, first_failure, last_retry}}
    else:                         → create escalation issue (idempotent), stop retrying

recovered = in retry-state but no longer stale  → clear its retry entry
```

Key properties that make this safe to run unattended:
1. **Persistent state on disk** (`data/retry-state.json`-style, committed) — survives across daily runs; without it the watchdog retries forever or gives up after one cycle depending on which bug you hit first.
2. **Idempotent escalation**: before creating an issue, search open issues for its exact title (e.g. `[watchdog] <name> pipeline failing`); if one exists, do nothing. Same principle as any deduped alerting — the watchdog must never spam.
3. **NO_RETRY set** for jobs where a re-trigger has real cost: in the source repo this is `tle-history`, because Space-Track bans accounts that make more than ~2 requests/day. Any authed/rate-limited upstream belongs here, not in the retry path.
4. **Dry-run mode from day one** (`--dry-run` prints every intended action) — run it once manually before scheduling; this is how you verify the state machine without triggering 108 workflows at 2 AM.

## Deriving period from a schedule expression (the trick that removes per-job config)

No hardcoded cadence table — parse each workflow's cron field:
- day-of-week ≠ `*` → weekly (7 days)
- month field limited: comma list → n months; step `*/N` → 12/N times/year; single month → annual. period = max(1, 366 // n_months)
- day-of-month is a digit with month `*` → monthly (31 days)
- else daily

This means adding job #109 needs zero watchdog changes — the cadence comes from the schedule itself. GRACE_DAYS=1 absorbs one missed cycle before flagging (timezone drift, runner queueing).

## Repairing "succeeded but status not pushed"

The subtlest failure mode: the pipeline succeeded and uploaded its output, but the *status-file commit* failed on a push conflict — so next day's watchdog would see stale data and blindly re-run an expensive job. The fix (from `fix_stale_status`): query CI for the latest successful run, pull its logs, regex out the row-count line (`--rows (\d+)`), rewrite the status file from that ground truth instead of re-running anything. Generalizes to any "job output is authoritative; the bookkeeping file may lag" setup — always prefer recovering state from artifacts over redoing work.

## GitHub Actions wiring (source repo's shape)

```yaml
name: Watchdog
on: { schedule: [{ cron: '0 21 * * *' }], workflow_dispatch: {} }   # after all regular workflows finish
permissions: { contents: write, issues: write }
jobs:
  watchdog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - run: python scripts/stale-checker.py        # env: GH_TOKEN = ${{ secrets.GITHUB_TOKEN }}
      - name: Commit status and retry state         # only if something changed (git diff --cached --quiet)
```

Notes: `GH_TOKEN` from the built-in secret is enough for `gh run list / workflow run / issue create`; commit both the repaired status file AND the retry-state file in one conditional commit; write a markdown summary table to `$GITHUB_STEP_SUMMARY` so every daily run leaves a visible audit trail of what it found/did.

## Adapting outside GitHub Actions (e.g. Hermes cron)

The same state machine works with any scheduler:
- "CI status" → the job's last-run result record (Hermes cronjob history, systemd timers, APScheduler logs — whatever records success/failure per run).
- "trigger re-run" → `cronjob_manage` action or a direct invocation; keep NO_RETRY for anything authed.
- "escalate issue" → deliver='origin' message to the user's chat (the Hermes equivalent of an idempotent issue: check whether you already alerted within N days before alerting again).
- Keep the persistent state file + dry-run discipline identical — those two properties are what make it safe unattended regardless of platform.

## Pitfalls observed in the source repo

- A stale status.json entry that is *ahead* of reality (job failed but an earlier push succeeded) makes `find_stale` see green forever — the watchdog must also trust CI state over the file, not just the other way around; the repair path above handles exactly this.
- Cron parsing assumes 5-field expressions; anything else falls back to daily — a monthly job written as a date list in day-of-month will be treated as weekly and flagged early (harmless: one extra retry cycle).
- `gh run view --log` on large runs is slow (~60 s timeout set deliberately); the row-count regex scans line-by-line so it stops at first hit.
