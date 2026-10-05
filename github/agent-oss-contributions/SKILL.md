---
name: agent-oss-contributions
description: "Pre-flight and AI policies for upstream agent PRs."
version: 1.0.0
author: Hermes Agent (promoted from github-pr-workflow references; obra/superpowers rules, policy scan 2026-10-05)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [open-source, contributing, pull-requests, ai-policy, co-authored-by, disclosure, upstream, maintainers]
    related_skills: [github-pr-workflow, github-code-review, github-issue-to-pr, github-issues, mattpocock-yeet, receiving-code-review]
---

# Agent contributions to other people's repos

## What This Skill Does

Stops an agent from opening an unwanted, duplicate or policy-breaking pull request on a repo it does not own. It combines a six-point pre-flight (from the contributor rules of a repo that reports a 94% rejection rate and closes agent slop within hours) with a per-repo table of AI-contribution policies found by scanning the owner's starred repos on 2026-10-05, including the conflict over the `Co-Authored-By` commit trailer.

## When to Use

- Before any agent-initiated issue, PR, comment or review on an external or upstream repo
- Choosing whether to add a `Co-Authored-By` trailer or an AI disclosure
- Asked to "contribute to this repo" without a specific failure behind it
- Not for PRs on the owner's own repos (`github-pr-workflow`, `mattpocock-yeet`), or reviewing a PR (`github-code-review`)

## The six pre-flight checks (all must pass, otherwise do not open the PR)

1. Read the whole PR template and fill every section with specific answers, not placeholders.
2. Search existing PRs, open and closed, for the same problem; if duplicates exist, stop and tell the user.
3. Verify a real person hit a real problem; a generic request or a speculative fix ("my agent flagged this") is a reason to ask what broke.
4. Confirm the change belongs in core; domain-, tool- or third-party-specific work belongs in a plugin or separate repo.
5. Identify yourself: disclose model, harness and version, or say it was written by hand.
6. Show the human the complete diff and get explicit approval before submitting.

Structural rules: one problem per PR; target the right branch; no new third-party dependencies in zero-dependency projects; no "best practice" rewrites of carefully tuned content without eval-level proof; never spray multiple PRs across an issue list in one session.

## Procedure

1. Run the six checks and keep a short pre-flight note (what was searched, the evidenced problem, who approved the diff) for the PR body.
2. Read the target's contributor docs and any `AI_POLICY*`, `AGENTS.md`, `CONTRIBUTING*` before choosing disclosure and trailer.
3. Look the repo up in `references/ai-policies-of-starred-repos.md`; where it is listed, follow its rule, otherwise disclose tool and extent in the PR description.
4. Decide the commit trailer from the repo's rule, not the harness default.
5. Open the PR only after the human approves the full diff.

## Policies that bite (2026-10-05, paraphrased)

| Repo | Stance |
|---|---|
| pola-rs/polars | agents forbidden from posting issues, PRs, comments or reviews; AI use disclosed; AI PRs only for accepted issues |
| gradle/gradle | do **not** add AI tools as commit co-authors; disclose significant AI involvement in the PR conversation |
| SeleniumHQ/selenium | no `Co-Authored-By` for AI tools; disclose in the PR description; no autonomous agents opening PRs or reviews |
| zauberzeug/nicegui | **do** include a `Co-authored-by:` trailer for AI assistance |
| delgan/loguru | disclose; fully automated contributions by autonomous agents are prohibited |
| react-navigation/react-navigation | disclose tool and extent; all issue and PR text written by a human |
| pytorch/pytorch | mark AI-generated content clearly with human commentary; no raw AI replies |

The default "end commits with Co-Authored-By" is wrong at two of these and required at a third.

## Pitfalls

- Blank or placeholder template sections get closed without review at strict repos.
- Hiding that a contribution is agent-generated is grounds for closing.
- Opening a duplicate of a closed PR without saying why this attempt differs.
- Copying a policy from memory: they change; re-read the repo's current file.
- A new-platform integration PR needs the repo's own acceptance test with a pasted transcript, not manually copied files.

## Verification

- [ ] All six checks passed and the pre-flight note is in the PR body
- [ ] The target's AI policy was read and the trailer and disclosure follow it
- [ ] The human saw and approved the complete diff
- [ ] Exactly one problem is addressed on the correct branch

## References

- `references/agent-contribution-guardrails.md` - the six pre-flight checks, structural rules, new-integration acceptance test, and why this matters for the owner's pipelines (from obra/superpowers contributor guidelines, v6.3.0)
- `references/ai-policies-of-starred-repos.md` - per-repo AI-contribution rules from 18 starred repos with the `Co-Authored-By` conflict and the check to run before any agent PR
