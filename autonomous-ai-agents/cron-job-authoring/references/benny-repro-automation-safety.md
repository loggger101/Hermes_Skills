---
description: "Safety contract for recurring automations that read an external channel and open code changes, distilled from pstack's benny pack: fail-closed config, immutable source coordinates with preflight before every post, trusted-author marker verdicts, single-poster rule, credential-isolated children, no-confirmed-repro-no-fix, verify-mode when a PR already exists"
source_repo: backnotprop/pstack (MIT) - automations/benny/skills/reproduce-and-fix-issues + triage-issue-reports at main, 2026-11-04 (mirror of cursor/plugins/pstack by Poteto)
tested_version: "SOURCE-READ. The pack was read in full locally; its Slack/GitHub automations were not executed (no configured workspace). Rules below are quoted/condensed from the skill text, not measured"
verified_date: "2026-11-04"
---

# Repro-and-fix automation safety contract (pstack's benny pattern)

Benny is a standing automation that watches an issue-report channel, waits for a human triage verdict, then
reproduces the bug through the real app UI and opens a bounded draft PR. It is the most disciplined external
automation design I have read for exactly our problem class: **a cron/automation tick that touches a system with
credentials and a public audience.** Every rule below exists to prevent an agent from posting, fixing, or
retrying at the wrong moment; adopt them when authoring any automation that can write outside the repo.

## 1. Fail closed on configuration

> "Load the external Benny configuration supplied by the automation. If the config, required actions, control
> adapter, or completed feature map is missing, fail closed."

Missing input is not a reason to improvise. In Hermes terms: if `config`/required skills are absent, end the tick
with an explicit "no action taken" rather than degrading to best-effort behaviour (cf.
`references/guardrail-template.md`).

## 2. Freeze and re-verify source coordinates — never trust a timestamp you already have

Before any work: require trigger channel == configured channel; set `SOURCE_THREAD_TS` from
`trigger.thread_ts` else `trigger.ts`; require it non-empty; store both as **immutable**; read the thread back
and verify its root has exactly those coordinates; capture the permalink. Explicitly forbidden: substituting a
reply, operations or status-message timestamp.

Before *every* post to the source channel: re-read by the immutable coordinates → confirm parent exists, not
deleted, still in the source channel → send with `channel=`/`thread_ts=` from the frozen values → read again and
verify the new message really is a reply. **If any check fails, post nothing; never retry at root or in a fallback
channel.** This is the anti-pattern that turns one bad tick into public spam: fallback destinations.

## 3. Verdicts arrive as markers from an identity, not as vibes

Proceed only when all hold: author matches the configured `triage_identity_user_id`; message is a reply under the
frozen thread; it contains **exactly one** configured marker (`[benny:bug]`, `[benny:performance]`,
`[benny:other]`, optionally with `tracker=<url>`). Anything else — no verdict, untrusted author, two conflicting
markers, timeout — stops silently. The comment in the source is the point: *"This marker replaces private bot
identities and free-form verdict matching."* A machine-checkable token from a verified identity beats an LLM
judging whether a human "seemed to approve".

## 4. One poster; children get no way to post at all

- The coordinator is the only Slack/channel poster. Delegated analysis workers are read-only and return findings.
- A fix-phase code worker may edit **only when its environment provably excludes** channel credentials and every
  write action — otherwise the coordinator edits. "Provably" means by environment construction, not by instruction.
- Every child prompt must explicitly name the forbidden actions (`SendSlackMessage`, `PostToSlack`,
  `chat.postMessage`, "and all other Slack writes"). Never hand a child a token, posting instructions, source
  coordinates for posting, or permission to report externally; if a child *needs* write access to run, do not launch it.

This is the pattern our own cron jobs should copy when they fan out: capability removal beats behavioural prompting.

## 5. No confirmed repro → no authored fix; existing PRs switch you to verify-mode

- The exact discriminating symptom must appear **twice** through real UI interaction before a fix is written
  ("State inspection may confirm an observation. It must not inject or force the symptom.").
- If a pull request or commit already addresses it, switch to verification mode and do not author over it.
- Use `github.com` PR links (not API objects) in reports; keep captures, recordings, logs and tokens out of source control.

## 6. Borrowed principle citations

Benny's own skill text routes to pstack principles by name — `principle-guard-the-context-window` for delegated
analysis, plus `principle-sequence-verifiable-units`, `principle-fix-root-causes`, `principle-prove-it-works` across
repro/fix/verify. See `../../../../software-development/verification-culture/references/pstack-principle-steering.md`
for that vocabulary and how it maps onto the skills already in this catalog.

## What is *not* verified here

Nothing was executed: no Slack workspace, no app-control adapter, no PR opened. The value above is architectural —
these are design rules worth adopting, not measurements. If you implement one, treat "post nothing on any failed
check" as the acceptance test (plant a deleted-parent or wrong-channel case and prove silence).
