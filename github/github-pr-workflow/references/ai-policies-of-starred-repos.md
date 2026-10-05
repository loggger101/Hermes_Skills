---
description: "Per-repo AI-contribution rules found in 18 of the owner's 166 starred repos (disclose, no agents, no Co-Authored-By vs required Co-authored-by, PRs paused) and the check to run before any agent PR"
source_repo: gradle/gradle AI_POLICY.md + a scan of every starred repo's root contributor docs (GitHub API, read-only)
tested_version: "Scan run 2026-10-05 over 166 starred repos: root and .github files named AI_POLICY*, AGENTS.md, CLAUDE.md, CONTRIBUTING*, CODE_OF_CONDUCT.md, GOVERNANCE.md searched for AI/LLM/Co-authored-by wording (44 had any match; 23 files in 21 repos looked like policy; 18 are tabulated and two more mentioned in passing). Policies in PR templates, docs sites or org-level .github repos were not searched. Wording below is paraphrased"
verified_date: "2026-10-05"
---

# AI-contribution policies in the starred repos

`agent-contribution-guardrails.md` has the general pre-flight checks. This is the concrete, per-repo version: the
rules differ, and two of them contradict each other on the commit trailer that agent harnesses add by default.

## The conflict to know first: `Co-Authored-By` trailers

| Repo | Rule |
|---|---|
| gradle/gradle (`AI_POLICY.md`) | **Do not** add AI tools as commit co-authors (examples named: Claude, Copilot, Cursor). Disclose significant AI involvement in the PR conversation, not the commit history; the DCO `Signed-off-by` is a human attestation and tools cannot sign it |
| SeleniumHQ/selenium | **Do not** add `Co-Authored-By` tags for AI tools; disclosure belongs in the PR description |
| zauberzeug/nicegui | **Do** include a `Co-authored-by:` trailer for AI assistance (they note some agents drop existing ones when amending or rebasing) |

So the default "end commits with Co-Authored-By" behaviour is wrong for two repos and required by a third. Read the target's
contributor docs first, then choose the trailer; a user instruction or the repo's rule overrides the harness default.

## Policy summary (paraphrased)

| Repo | Stance | Key requirements |
|---|---|---|
| pola-rs/polars | **Agents forbidden** | Agents may not post issues, PRs, comments, reviews or reactions; all AI use disclosed (tool and extent); AI-generated PRs only for accepted issues (drive-by PRs closed); no AI on "good first issue"; AI code must be verified by human use |
| delgan/loguru | Welcome, controlled | Disclose AI-generated or significantly refined content at submission; describe problems in your own words; review and test output; **fully automated contributions by autonomous agents prohibited** |
| SeleniumHQ/selenium | Welcome, human in the loop | Author reads and can explain everything; disclose substantial AI parts (tool + what) in the PR description; **no autonomous agents opening PRs, pushing or posting reviews without direct human approval**; no AI co-author tag |
| react-navigation/react-navigation | Welcome, disclose | State the tool and extent for any code change; human must understand all code; **all issue/PR text written by a human** (AI may help with drafting or translation) |
| pytorch/pytorch | Welcome, contain it | AI-generated content in comments, issues or PRs must be clearly marked (quote or code block) with human commentary; do not paste raw AI replies to questions; only the pytorchbot automations are exempt |
| gradle/gradle | Welcome, human-owned | Understand and explain what you submit; disclose significant AI involvement in the PR; engage with review; low-effort or abandoned AI PRs may be closed and future contributions restricted |
| pytest-dev/pytest | Welcome | Policy is about human effort: understand what you ship and stand behind it; reviewers invest in real effort (details in the `AI/LLM-Assisted Contributions Policy` section of `CONTRIBUTING.rst`) |
| tech-leads-club/agent-skills | Welcome, issue first | Say an agent was involved; understand every line; PRs without a linked issue may be closed (they were receiving a stream of automated PRs) |
| simple-icons/simple-icons | Welcome, disclose | Any AI tool use must be clearly disclosed in the PR |
| alibaba/open-code-review | Welcome | Do not commit unread model output; see the "AI-Assisted Development" rules in `CONTRIBUTING.md` |
| pydantic/pydantic | Welcome, certify | Certify you fully understand the code; PRs may be closed at will, including mass submissions across repos and AI-written descriptions that are incoherent |
| mesa/mesa (`CODE_OF_CONDUCT.md`) | Welcome, engage | Understand and defend your work; low-effort AI submissions without personal engagement are not acceptable |
| heygen-com/hyperframes | Welcome | No disclosure needed; you are responsible for correctness; AI tests must test real behaviour |
| longbridge/gpui-kit | Fully embraced | Even 100% AI-written PRs accepted if focused, tested, reviewed by you |
| igorbarinov/awesome-data-engineering | Neutral | Looks for evidence the project is real and used, whoever wrote the code |
| **ripienaar/free-for-dev** | **Rejects AI edits** | AI-generated edits closed without discussion; PRs must use the template |
| **streamlit/streamlit** | **Outside PRs paused** | Not accepting PRs from outside the maintainer team because AI tools raised volume; detailed issues are the way to contribute |

Separately, `alirezarezvani/claude-skills` lists `Co-Authored-By:` among things its contribution guide discusses, and
`Imbad0202/academic-research-skills` excludes features designed to evade AI-text detection.

## Check before an agent opens a PR or issue upstream

1. In the target repo, read `CONTRIBUTING*`, `AI_POLICY*`, `AGENTS.md`, `CODE_OF_CONDUCT.md` and the PR template; search
   for `AI`, `LLM`, `agent`, `Co-authored`. `gh api repos/OWNER/REPO/contents/` lists the candidates.
2. If agents may not interact (polars, loguru, selenium without human approval, streamlit paused): stop. Hand the user a
   draft they can submit themselves, or an issue text, and say why.
3. If disclosure is required, disclose tool and extent in the PR body (not the commit unless the repo asks), and write the
   PR and issue prose by hand where the policy says so (react-navigation, loguru, pytorch).
4. Pick the trailer from the repo's rule (above), not the harness default.
5. Never batch PRs across repos (pydantic names this as spam) and keep one problem per PR.
6. The user, not the agent, submits anything a policy reserves for a human.
