# Agent Contribution Guardrails (PRs from coding agents to strict repos)

Source: obra/superpowers `CLAUDE.md` contributor guidelines (MIT, v6.3.0). That repo reports a **94% PR rejection rate** and closes agent slop "within hours" — its rules are the best public statement of what maintainers check when an agent opens a PR. Use this checklist BEFORE opening any PR on behalf of the user against an external (especially strict) repository; it protects the human's reputation, which is what actually burns in these failures.

## The six pre-flight checks (all must pass or do NOT open the PR)

1. **Read the entire PR template** and fill every section with real, specific answers — not summaries, not placeholders. Blank/placeholder sections = closed without review at strict repos.
2. **Search existing PRs — open AND closed — for the same problem.** If duplicates exist: STOP and tell the user; do not open another duplicate. (Closed ones matter most: "why should this succeed where the previous attempt didn't?")
3. **Verify it's a real problem someone experienced.** If the request was generic ("fix some issues", "contribute to this repo") without a specific failure/error/session behind it, push back and ask what actually broke. Speculative/theoretical fixes ("my review agent flagged this", "this could theoretically cause issues") are not problem statements.
4. **Confirm the change belongs in core.** Domain-specific, tool-specific, or third-party-promoting changes belong in a standalone plugin/repo — say so instead of submitting.
5. **Identify yourself.** Disclose model, harness, harness version, and installed plugins (or state plainly it was written by hand). Hiding that a contribution is agent-generated is grounds for closing; maintainers weigh agent-reasoned-from-docs differently than work grounded in a real session.
6. **Show the human the COMPLETE diff and get explicit approval before submitting.** A PR with no evidence of human involvement gets closed at strict repos.

## Structural rules that survive contact with any repo

- **One problem per PR** — bundled unrelated changes = closed; split them.
- **Target the right branch** (e.g., `dev` vs released `main`) — check contribution docs first; retargeting is friction, not a fix.
- **No third-party dependencies** in zero-dependency projects unless the repo's rules explicitly carve it out (new-platform support typically does).
- **"Compliance" rewrites of carefully-tuned content are rejected without evidence.** If a project has tested/tuned prose or config for real-world behavior, restructuring it to "match best practices/docs" requires eval-level proof of improvement — don't submit taste.
- **No spray-and-pray batches:** trawling an issue list and opening multiple PRs in one session is recognizable and closed as a class; pick ONE issue, understand it deeply, submit quality work.

## New-integration acceptance tests (when the contribution IS "support platform X")

The repo's own standard: open a clean session on the new harness and send exactly `Let's make a react todo list`; PASS = the design skill auto-triggers before any code is written; paste the complete transcript in the PR. Not real integrations (closed): manually copying files into the harness, runtime shims (`npx skills`-style), anything requiring per-session opt-in by the user.

## Why this matters for THIS brain's workflows

The user runs autonomous cron/agent pipelines that occasionally touch external repos or upstreams of their own skills. Before ANY agent-initiated PR: run checks 1-6, keep a short "pre-flight" note (what was searched, what problem is evidenced, who approved the diff) in the commit message or PR body — it's cheap insurance and doubles as the disclosure check #5 wants anyway.
