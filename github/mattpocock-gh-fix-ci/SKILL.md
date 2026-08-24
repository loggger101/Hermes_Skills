---
name: mattpocock-gh-fix-ci
description: "Debug failing GitHub Actions checks on a PR."
version: 1.1.0
author: Adapted from openai/skills
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github-actions, ci, debugging, gh-cli, failure-analysis]
    related_skills: [github-pr-workflow, mattpocock-diagnosing-bugs]
---

## When to Use

Use when the user reports a CI failure, asks to "fix the build", "debug CI", or needs to unblock a failing PR.

## What This Skill Does

Debugs failing GitHub Actions checks using the `gh` CLI. Fetches run logs, summarizes the failure context, proposes a fix. Loads `skill_view(name='systematic-debugging')` for root-cause analysis when the failure isn't immediately obvious.

## Prerequisites

- Authenticated with GitHub (run `skill_view(name='github-auth')` if not)
- `gh` CLI installed and authenticated
- Repository is a git repo with GitHub remote

## Process

### 1. Fetch the failing run
```bash
gh run list --limit 20  # find recent runs
gh run view {run_id}
```

### 2. Get job details
```bash
gh run view {run_id} --jobs
```
This shows each job in the run, its status, and how long it took. Focus on jobs that show `failure` or `cancelled`.

### 3. Fetch specific log
```bash
gh run view {run_id} --log
# Or for a specific job:
gh run job view {job_id} --log
```

For large logs, pipe to grep or save to a file:
```bash
gh run view {run_id} --log > ci-failure.log
grep -i "error\|failed\|exception\|traceback" ci-failure.log
```

### 4. Identify the failure point
Look for the red step (the last step that failed). Extract the error message — look for:
- Compiler/linker errors
- Test failures with stack traces
- Missing dependencies
- Permission denied / authentication errors
- Timeout / resource exhaustion

**Key distinction**: Did your change introduce this failure, or was it pre-existing?
```bash
# Check if the failure exists on the base branch too
gh pr checks --base main  # compare against base
```

### 5. Propose fix
Categorize the failure and apply the right remedy:

| Failure Type | Diagnosis | Fix |
|---|---|---|
| Missing dependency | `ModuleNotFoundError`, `command not found` | Add to requirements/install script |
| Test failure | Assertion error, test name in logs | Fix the code or update the test |
| Lint/type failure | Linter output in logs | Run formatter/linter locally |
| Timeout | Run killed after N seconds | Optimize the step or increase timeout |
| Flaky test | Passes on rerun | Retry, or quarantine with `flake8-unittest` markers |
| Permission denied | 403, `Permission to access` | Check `GITHUB_TOKEN` scopes |
| Build error | Compiler errors | Fix compilation |

### 6. Apply and verify
```bash
# Fix the issue, then push
git add .
git commit -m "fix: resolve CI failure in step-name"
git push

# Re-run the specific job
gh run re-run-failed-jobs {run_id}
# Or re-run the entire workflow
gh run rerun {run_id}
```

## Advanced Debugging

### Download artifacts
```bash
gh run download {run_id} --name {artifact-name}
```

### View workflow file
```bash
# Find the workflow file from the run
gh api repos/{owner}/{repo}/actions/runs/{run_id} --jq '.path'
# Then read it
gh api repos/{owner}/{repo}/contents/{path} | jq -r '.content' | base64 -d
```

### Compare two runs
```bash
diff <(gh run view {run_a} --log) <(gh run view {run_b} --log)
```

## Pitfalls

- **Assuming the failure is yours** — always check if it's a pre-existing baseline failure
- **Not checking the full log** — the error often appears early but the root cause is a line above it
- **Rerunning without fixing** — flaky tests need investigation, not just retries
- **Ignoring cache issues** — stale caches can cause intermittent failures; try `--no-cache`
- **Missing context** — read the full step output, not just the summary line

## AspireCURES Context

The weekly cronjob pipeline may fail CI if a data source API changes format or a disease page rendering error occurs. Use to diagnose: fetch Actions run logs, identify which of the 9 disease pages failed, and trace whether it's a data-source change or code regression. For systematic root-cause analysis when the logs aren't clear, load `skill_view(name='mattpocock-diagnosing-bugs')`.
