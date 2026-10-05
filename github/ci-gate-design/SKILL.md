---
name: ci-gate-design
description: "CI that proves claims: no always-skip checks."
version: 1.0.0
author: Hermes Agent (from the knowledge vault's ci-gates page, read across 9 of the owner's repos, 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ci, github-actions, gates, canary, reproducibility, workflow, bot-commits, fetch-depth]
    related_skills: [github-pr-workflow, failure-signal-audit, verification-culture, one-authority-per-fact, pinned-data-contracts, verification-before-completion]
---

# CI as gates

## What This Skill Does

States eight rules for GitHub Actions workflows taken from the comments of nine of the owner's repos (16 workflows). The shared idea: a workflow exists to **prove a claim the repo makes about itself**, so a check that cannot fail is a defect, not a nicety. It also covers the bot-commit blind spot and the drift to watch in action and runtime versions.

## When to Use

- Writing or reviewing a workflow, or deciding what CI should prove
- A check always skips, is always red, or went green on a broken input
- Bot or scheduled jobs commit to `main`
- Not for debugging a failing run (`github-pr-workflow`, `references/ci-troubleshooting.md`), gating a backlog with ratchets (`github-pr-workflow/references/ci-ratchets-and-release-pipeline.md`), or auditing for masked failures in code (`failure-signal-audit`)

## The eight rules

1. **A check that always skips does not exist.** Make it run: check out the dependency at the pinned tag instead of pip-installing (a pip install leaves reference data behind and the check skips), install the exact versions a metadata file recorded and set an env var that turns the skip into a failure, install Node so a "no node, skip" path is never taken, and run harnesses in a job that has their optional engines.
2. **A gate that is red by construction is crying wolf, so run it as a report** (`continue-on-error`), for example a cross-platform hash check on a runner that is expected to differ. The gate that refuses should be a different, reliable one.
3. **Committed output must equal what the generator makes.** Rebuild and diff; check `git status --porcelain` rather than `git diff` so an untracked generated file fails too.
4. **Test what the consumer gets, not the tree.** Build the wheel, install it in a fresh venv and run the consumer contract from a directory where the source is not importable; run CLIs with no data present.
5. **Keep the network out of the merge path; give third parties a scheduled canary.** The pull-request suite is pure; a live-data job runs on a schedule or by hand and is deliberately not `continue-on-error`: a canary that cannot go red is a cron job.
6. **Dates come from git history, so fetch all of it** (`fetch-depth: 0`); a shallow clone dates every page to the tip commit.
7. **Test on Linux and Windows and on the oldest and newest Python.** If output is pinned (for example CRLF), only the other OS proves the pin holds.
8. **Workflow inputs reach the shell through `env`,** never through `${{ }}` substitution into a script, so an input cannot inject a command.

## Bot commits

A push made with the Actions token starts no workflow. Bot commits (formatters, sitemap jobs, scheduled feeds) were the one kind of commit on `main` that CI never saw: a stale-dated page failed the verifier for a week without anything going red. Fix: a `workflow_run` trigger that re-runs the verifier after each bot run; it observes rather than blocks. A formatter commit also does not trigger path-filtered jobs that depend on its output.

## Procedure

1. For each workflow write the claim it proves in one line; if you cannot, delete it.
2. For each check ask "what makes this skip, and does the skip print the same clean line as a pass?" and convert skips into failures or visible reports.
3. Plant a defect and watch the check go red before trusting it.
4. Pin action majors and runtime versions deliberately and review them on a schedule.
5. Add `workflow_run` or a scheduled re-check for any job that commits with the Actions token.

## Drift to watch

- Action majors diverge across repos (checkout v4, v5, v7), and v4 with setup-python v5 targets deprecated Node 20.
- `ubuntu-latest` moves: an old Python leg can fail at setup when the image changes; pin `ubuntu-24.04` for that leg.
- Node versions reach end of life; move the workflow before the runner does.

## Pitfalls

- A skipped step reported as success.
- Running a hand-run gate "when somebody remembers" instead of in CI.
- Testing the checkout instead of the built artifact.
- A shallow clone silently dating generated content.

## Verification

- [ ] Each workflow states the claim it proves
- [ ] No check can skip while printing success; skips are failures or visible warnings
- [ ] Planted defects turn each gate red
- [ ] Bot-committed content is re-verified by a triggered workflow
