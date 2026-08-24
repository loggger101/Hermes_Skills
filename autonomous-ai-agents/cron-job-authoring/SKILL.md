---
name: cron-job-authoring
description: "Author autonomous cron prompts with guardrails."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cron, scheduling, autonomous, guardrails, prompt-design, no-interaction]
    category: autonomous-ai-agents
    related_skills: [hermes-agent]

---

# Cron Job Authoring

## What This Skill Does

Teaches the pattern for writing prompts for cron jobs that run autonomously on a schedule with no human present. Covers the no-interaction guardrail pattern (never use `clarify`, never prompt for credentials, never present interactive UI), credential handling (skip-and-record strategy when credentials are missing), delivery discipline (the cron system auto-delivers the final response; never call `send_message` yourself), and structural conventions (phased prompts, scorecards, blocked-item handling). Includes troubleshooting for common failures like `[drift_skip]` errors and `approvals.cron_mode` blocking.

Writing prompts for cron jobs that run on a schedule with no human present requires different discipline than writing prompts for interactive sessions. The job cannot ask questions, wait for approvals, or pause for credentials. Every decision point that would normally trigger a `clarify` or a prompt must be resolved in the prompt itself — either with a rule ("skip and note"), a fallback, or an explicit blocker record.

This skill covers the guardrail pattern, credential handling, delivery discipline, and the structural conventions that keep scheduled runs finishing instead of stalling.

## When to Use

- You are creating a new cron job via `cronjob(action='create', ...)` or `hermes cron create`.
- You are editing an existing job's prompt via `cronjob(action='edit', ...)` or `hermes cron edit`.
- You are reviewing whether an existing job's prompt is safe to run autonomously.
- You are troubleshooting a cron job that stalled, hung, or delivered nothing because it hit an interactive prompt.

## The No-Interaction Guardrail Pattern

Every autonomous cron job prompt should open with an explicit autonomy section that rules out the interactive behaviors a normal session would use. Place it early — ideally right after any cross-profile or security notes and before the first phased instruction — so the agent sees it before it starts making decisions.

### Minimum guardrail block

```
=== AUTONOMY & NO-INTERACTION GUARDRAILS ===
This job runs autonomously on a schedule with no human present. You must NEVER pause to ask the user for anything — no API keys, no tokens, no credentials, no confirmations, no clarifications, and no manual intervention of any kind. If at any point you would normally want to use the clarify tool, do NOT use it — instead record the gap as an unresolved item and continue.

Specifically:
- Never prompt for API tokens or keys. If a step requires an external service token you do not already have access to in the environment, skip that verification step, note it as unverified, and move on. Do not attempt to obtain the token by any means (no web searches for how to get one, no prompting, no interactive flows).
- Never present any interactive UI to the user. No clarify calls; no computer-use dialogs that require a human response; no browser flows that would open a consent/password/payment screen. If a tool you invoke would surface a dialog, abort that action and note it as blocked.
- If the runtime itself raises a prompt on your behalf (e.g. an MCP server asking for an OAuth login or a missing key), treat it as a hard blocker for that step — record it and continue. You are not the person who can authorize it.
- When a referenced external service/tool requires credentials you do not have, evaluate what you CAN verify without them and mark the credential-dependent checks as unverified with the reason "credential not available — manual verification needed."
```

Note: the exact wording of the header doesn't matter — pick one (`AUTONOMY & NO-INTERACTION GUARDRAILS` is fine) and use it consistently. The key is that the block is present, early, and specific.

### Why each rule exists

| Rule | What it prevents |
|------|-----------------|
| Never pause to ask | A cron job that calls `clarify` hangs waiting for a user who isn't there. The run times out or delivers nothing. |
| Never prompt for API tokens | A job that web-searches for how to obtain a token, or attempts any interactive OAuth flow, is doing work the user didn't authorize and may expose the session to consent screens. |
| Never present interactive UI | Computer-use dialogs, browser consent screens, and payment prompts all require a human. A cron job that triggers one blocks until timeout. |
| Runtime-raised prompts are blockers | MCP servers, credential pools, and OAuth flows can raise their own prompts. The agent cannot authorize them — treating them as blockers keeps the rest of the audit running. |
| Credential-dependent checks → unverified | A skill audit or verification pass should still report on what it CAN check (structure, trigger, steps, pitfalls) even when it can't reach an auth-gated endpoint. Marking the gap explicitly is better than skipping the skill entirely or stalling. |

## Credential Handling

When a cron job's work touches external services, the prompt must tell the agent exactly what to do when credentials are missing. The options, in priority order:

1. **Skip and record.** If the step is a verification (link rot check against an auth-gated endpoint, live API call test), skip it and mark it unverified with the reason. Continue with everything else.
2. **Use what's available.** If the environment has SOME credentials (e.g. a read-only token) but not others, scope the work to what the available credentials allow and note the rest as out of scope.
3. **Hard blocker → record and continue.** If a step is foundational (can't proceed without it), record it as a blocked item and continue with non-dependent work. Don't stop the whole job.

Never: attempt to obtain credentials, search for how to get them, enter interactive OAuth flows, or prompt the user.

## Delivery Discipline

The cron system handles delivery automatically. The agent's job is to produce its final output as its last response — never to call `send_message`, `clarify`, or any delivery tool itself. The prompt should reinforce this:

```
IMPORTANT: You are running as a scheduled cron job. Your final response will be automatically delivered to the user — do NOT use send_message or try to deliver the output yourself. Just produce your report/output as your final response and the system handles the rest.
```

This matters because some agents have a habit of trying to "help" by delivering early or summarizing mid-run. In a cron context that produces duplicate or partial deliveries.

## Structural Conventions

### Phased prompts

For multi-phase jobs (audit, scan, report), structure the prompt as numbered phases with clear entry/exit criteria. Each phase should be self-contained enough that if a later phase can't run, earlier phases still produced value.

### Scorecards and tables

When the job produces an evaluation or audit, use a consistent table shape so the user can scan it. Example columns: item | profile | criterion scores | overall | notes. Keep one row per evaluated unit.

### Blocked items

Always include a "Blocked" or "Flagged for Human Review" section. The difference:
- **Blocked** = the job tried and couldn't proceed (cross-profile write refused, credential missing, tool blocked). Record the reason and the recommended next step.
- **Flagged for human review** = the job found something that needs judgment (structural failure, accuracy concern, speculative fix). Don't auto-fix; describe and recommend.

### Silent vs. delivered runs

Some jobs are watchdogs that should stay silent when nothing changed (e.g. `wakeAgent: false` gates, empty stdout). Design the prompt so the agent knows when to produce output and when to stay quiet — don't let it deliver "nothing to report" noise on every tick.

## Pitfalls

- **Putting guardrails at the end of the prompt.** The agent reads top-down. If the no-interaction rules come after Phase 4, the agent may have already called `clarify` in Phase 1. Put them early.
- **Assuming the agent knows cron constraints.** A normal session agent doesn't inherently know it's running autonomously. The prompt must say so explicitly — don't rely on the agent inferring it from context.
- **Over-specifying verification steps that need credentials.** If a criterion requires an auth-gated check, either make it optional (mark unverified when missing) or drop it from the auto-run criteria and leave it for manual review.
- **Letting blocked items terminate the job.** One blocked credential check shouldn't kill the whole audit. Design phases so blocked items are recorded and the job continues.
- **Forgetting the delivery reminder.** Without it, some agents will try to deliver mid-run or use `send_message`, producing duplicate or partial outputs.
- **Editing the prompt file directly without also updating the job's in-memory state.** On this system, the canonical job definition lives in `cron/jobs.json`. Editing that file is what persists across scheduler restarts. If you also touch a separate prompt file, verify they don't drift.
- **Assuming `hermes cron run` fires immediately.** The command schedules the next tick; if the cron gateway isn't running, nothing executes. Start the gateway first (`hermes gateway run`), then trigger. A stale "already being fired" execution row blocks re-firing — clear it from `cron/executions.db` before retrying.
- **Forgetting to pin the job's provider/model.** Cron jobs detect when the global inference config drifts (provider/model change between job creation and fire) and **auto-skip unpinned jobs** to prevent unintended spend. The run fails with `RuntimeError: [drift_skip]` visible in `errors.log` and `last_error` in `cron/jobs.json`. Fix: pin the job explicitly — `hermes cron edit <job_id> --provider <provider> --model <model>` — then re-run. When creating a new job, pin it at creation time if it must run on a specific model regardless of future global config changes. See `references/drift-skip-error.md`.
- **Cron approval mode blocks terminal calls silently.** When `approvals.cron_mode: deny` (the default), any tool call that triggers the dangerous-command gate — typically `terminal` with a command matching a Tier-2/Tier-3 pattern — is **blocked** in cron context with no human present to approve it. The agent sees `BLOCKED: Command was flagged (…) and auto-approved by smart approval` in logs, or in some cases the command fails with exit code 127 because the shell can't find the binary. Fix: set `approvals.cron_mode: approve` in `config.yaml` via `hermes config set approvals.cron_mode approve`. This auto-approves all flagged commands in cron sessions. Note: `execute_code` is **hard-blocked** in all cron contexts regardless of this setting — the auditor and other cron jobs must use `terminal` instead. See `references/cron-approval-mode.md`.
- **Assuming the agent needs an API key.** When the cron job's task involves a step that the repository's CI pipeline gates behind an environment variable like `ANTHROPIC_API_KEY` (e.g. `const KEY = process.env.ANTHROPIC_API_KEY;`), do NOT attempt to provide a key or skip the step entirely. The agent **is** the model — it substitutes its own reasoning for the API-key-gated step. Document this substitution explicitly in the prompt body: "When the pipeline checks for `ANTHROPIC_API_KEY`, the agent substitutes its own Claude judgments for the Claude-curate step." Failing to document this leads to the agent either fabricating a fake key or incorrectly skipping the curation step entirely.

## References

- `references/guardrail-template.md` — annotated copy-paste starter for the no-interaction guardrail block, with notes on each rule's purpose.
- `references/credential-strategy.md` — decision tree for what to do when a cron job hits missing credentials, with worked examples.
- `references/delivery-discipline.md` — why the delivery reminder matters, what goes wrong without it, and the exact wording to use.
- `references/drift-skip-error.md` — troubleshooting the `[drift_skip]` error when a job's provider/model drifts from global config and gets auto-skipped.
- `references/cron-approval-mode.md` — configuring `approvals.cron_mode` in `config.yaml` to auto-approve dangerous terminal commands in cron jobs.

## Verification

After editing a cron job prompt, verify:

1. The guardrail block is present and near the top (before the first phased instruction).
2. The delivery reminder is present (for LLM-driven jobs, not no_agent script jobs).
3. Every verification criterion that needs external access is either optional (mark-unverified) or explicitly scoped to what's available without credentials.
4. Blocked-item handling is specified — the agent knows to record and continue, not stop.
5. No step tells the agent to call `clarify`, `send_message`, or any interactive tool.

Run the job once manually (`hermes cron run <job_id>`) and watch the session transcript for any `clarify` calls, tool loops on unsupported skills, or stalled tool results — these are signs the guardrails aren't comprehensive enough.
