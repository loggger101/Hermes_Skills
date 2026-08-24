# Drift Skip: Model/Provider Config Drift

## Error signature

When a cron job is **unpinned** (no explicit `model`/`provider` in `cron/jobs.json`) and the global inference config changes between job creation and fire, the scheduler **auto-skips** the run to prevent unintended spend.

### Log output (errors.log)

```
RuntimeError: [drift_skip] Skipped to prevent unintended spend: global inference config drifted since this job was created
(provider 'nous' -> 'opencode-free'; model 'upstage/solar-pro4:free' -> 'laguna-s-2.1-free'),
and this job is unpinned. No inference call was made. To run on the new config,
on the host running Hermes pin it explicitly:
  hermes cron edit <job_id> --provider <provider> --model <model>
(or pin the original values to keep them). This alert is sent once;
the job stays skipped until the config is pinned or restored. See #44585.
```

### jobs.json state

```json
{
  "last_status": "error",
  "last_error": "RuntimeError: [drift_skip] ...",
  "failure_streak": 1,
  "drift_alerted": true
}
```

## Fix

```bash
# Pin to the current global config
hermes cron edit 43f3d955cb55 --provider opencode-free --model laguna-s-2.1-free

# Or pin to preserve the original config
hermes cron edit 43f3d955cb55 --provider nous --model upstage/solar-pro4:free

# Then re-run
hermes cron run 43f3d955cb55
```

## Prevention

Always set `--provider` and `--model` when creating a new cron job if it must run on a specific model:

```bash
hermes cron add \
  --provider opencode-free \
  --model laguna-s-2.1-free \
  --schedule "every 360m" \
  --name "Skill Auditor" \
  --prompt "..."
```

## Key fields in jobs.json

| Field | Purpose |
|---|---|
| `provider` / `model` | Pinned values for this job (null = follows global default) |
| `provider_snapshot` / `model_snapshot` | Original creation-time config (for drift comparison) |
| `drift_alerted` | Set true after first skip; prevents repeated alerts |
| `failure_streak` | Increments on each failed run; resets on success |
