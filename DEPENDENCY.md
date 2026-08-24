# Skill Dependency Map

This document maps the relationship network between all 127 Hermes skills in this repository. It is generated from the `related_skills` field in each skill's frontmatter.

## Hub Skills (referenced by 2+ other skills)

These are the core skills that serve as building blocks, referenced by many other skills:

| Hub Skill | References | Referenced By |
||------------|----------------|------------------------------------------------------------|
|| [requesting-code-review](productivity/docx/SKILL.md) | 11 | github-issue-to-pr, mattpocock-code-review, mattpocock-finishing-a-development-branch, mattpocock-security-review, hermes-agent-skill-authoring, mattpocock-evidence-driven, mattpocheck-multi-agent-code-review, mattpocock-subagent-driven-development, plan, python-craft, simplify-code |
|| [systematic-debugging](software-development/systematic-debugging/SKILL.md) | 10 | mattpocock-resolving-merge-conflicts, python-data-science, github-issue-to-pr, inspecting-hermes-desktop-dom, mattpocock-diagnosing-bugs, mattpocock-tdd, node-inspect-debugger, python-craft, python-debugpy, test-driven-development |
|| [python-craft](software-development/python-craft/SKILL.md) | 9 | static-site-seo, build-systems-data, evolutionary-ml, model-export-deploy, orbital-mechanics-data, cli-tool-craft, streamlit-dashboards, test-infra-ml, verification-culture |
|| [test-driven-development](software-development/test-driven-development/SKILL.md) | 9 | python-data-science, github-issue-to-pr, mattpocock-tdd, plan, python-craft, requesting-code-review, simplify-code, systematic-debugging, test-infra-ml |
|| [github-pr-workflow](github/github-pr-workflow/SKILL.md) | 9 | github-auth, github-code-review, github-issue-to-pr, github-issues, github-repo-management, mattpocock-finishing-a-development-branch, mattpocock-gh-fix-ci, mattpocock-yeet, mattpocock-using-git-worktrees |
|| [excalidraw](creative/excalidraw/SKILL.md) | 7 | architecture-diagram, ascii-art, claude-design, design-md, p5js, pretext, sketch |
|| [plan](software-development/plan/SKILL.md) | 7 | research-paper-writing, hermes-agent-skill-authoring, requesting-code-review, simplify-code, spike, systematic-debugging, test-driven-development |
|| [hermes-agent](autonomous-ai-agents/hermes-agent/SKILL.md) | 6 | autonomous-repo-cronjob, claude-code, codex, cron-job-authoring, merge-reconciler, opencode |
|| [pdf](productivity/pdf/SKILL.md) | 6 | document-to-action-items, docx, nano-pdf, ocr-and-documents, powerpoint, xlsx |
|| [mattpocock-subagent-driven-development](software-development/mattpocock-subagent-driven-development/SKILL.md) | 6 | research-paper-writing, plan, requesting-code-review, spike, systematic-debugging, test-driven-development |
|| [mattpocock-code-review](github/mattpocock-code-review/SKILL.md) | 6 | mattpocock-security-review, mattpocock-diagnosing-bugs, mattpocock-evidence-driven, mattpocock-multi-agent-code-review, mattpocock-tdd, mattpocock-to-tickets |
|| [python-data-science](data-science/python-data-science/SKILL.md) | 5 | build-systems-data, evolutionary-ml, orbital-mechanics-data, sql-for-data, huggingface-trackio |
|| [ocr-and-documents](productivity/ocr-and-documents/SKILL.md) | 5 | document-to-action-items, nano-pdf, pdf, arxiv, grounded-citations |
|| [docx](productivity/docx/SKILL.md) | 5 | document-to-action-items, ocr-and-documents, pdf, powerpoint, xlsx |
|| [sketch](creative/sketch/SKILL.md) | 4 | architecture-diagram, mattpocock-prototype, frontend-design, spike |
|| [popular-web-designs](frontend-design/popular-web-designs/SKILL.md) | 4 | claude-design, design-md, sketch, frontend-design |
|| [claude-design](creative/claude-design/SKILL.md) | 4 | design-md, pretext, sketch, frontend-design |
|| [xlsx](productivity/xlsx/SKILL.md) | 4 | sql-for-data, docx, pdf, powerpoint |
|| [mattpocock-writing-for-agents](software-development/mattpocock-writing-for-agents/SKILL.md) | 4 | doc-coauthoring, mattpocock-handoff, mattpocock-ask-if-underspecified, mattpocock-domain-modeling |
|| [google-workspace](productivity/google-workspace/SKILL.md) | 4 | email-inbox-triage, box, meeting-action-items, weekly-review-planning |
|| [github-code-review](github/github-code-review/SKILL.md) | 4 | github-auth, github-pr-workflow, mattpocock-code-review, requesting-code-review |
|| [github-issues](github/github-issues/SKILL.md) | 4 | github-auth, github-issue-to-pr, github-repo-management, mattpocock-to-tickets |
|| [github-auth](github/github-auth/SKILL.md) | 4 | github-code-review, github-issues, github-pr-workflow, github-repo-management |
|| [mattpocock-tdd](software-development/mattpocock-tdd/SKILL.md) | 4 | mattpocock-code-review, mattpocock-codebase-design, mattpocock-diagnosing-bugs, mattpocock-evidence-driven |
|| [powerpoint](productivity/powerpoint/SKILL.md) | 4 | docx, ocr-and-documents, pdf, xlsx |
|| [arxiv](research/arxiv/SKILL.md) | 4 | grounded-citations, llm-wiki, mattpocock-research, research-paper-writing |
|| [obsidian](note-taking/obsidian/SKILL.md) | 3 | apple-notes, weekly-review-planning, llm-wiki |
|| [codex](autonomous-ai-agents/codex/SKILL.md) | 3 | claude-code, hermes-agent, opencode |
|| [claude-code](autonomous-ai-agents/claude-code/SKILL.md) | 3 | codex, hermes-agent, opencode |
|| [mattpocock-diagnosing-bugs](software-development/mattpocock-diagnosing-bugs/SKILL.md) | 3 | mattpocock-resolving-merge-conflicts, mattpocock-gh-fix-ci, mattpocock-tdd |
|| [architecture-diagram](creative/architecture-diagram/SKILL.md) | 3 | claude-design, design-md, pretext |
|| [hermes-agent-skill-authoring](software-development/hermes-agent-skill-authoring/SKILL.md) | 3 | doc-coauthoring, mattpocock-code-review, mattpocock-writing-for-agents |
|| [notion](productivity/notion/SKILL.md) | 3 | document-to-action-items, meeting-action-items, weekly-review-planning |
|| [mattpocock-to-tickets](software-development/mattpocock-to-tickets/SKILL.md) | 3 | mattpocock-handoff, mattpocock-spec-driven-development, mattpocock-subagent-driven-development |
|| [mattpocock-domain-modeling](software-development/mattpocock-domain-modeling/SKILL.md) | 3 | mattpocock-handoff, mattpocock-improve-codebase-architecture, mattpocock-writing-for-agents |
|| [mattpocock-multi-agent-code-review](software-development/mattpocock-multi-agent-code-review/SKILL.md) | 3 | mattpocock-security-review, mattpocock-evidence-driven, mattpocock-subagent-driven-development |
|| [mattpocock-handoff](productivity/mattpocock-handoff/SKILL.md) | 3 | mattpocock-ask-if-underspecified, mattpocock-to-tickets, mattpocock-writing-for-agents |
|| [opencode](autonomous-ai-agents/opencode/SKILL.md) | 2 | claude-code, hermes-agent |
|| [spike](software-development/spike/SKILL.md) | 2 | mattpocock-prototype, sketch |
|| [ascii-video](media/ascii-video/SKILL.md) | 2 | p5js, touchdesigner-mcp |
|| [manim-video](creative/manim-video/SKILL.md) | 2 | p5js, touchdesigner-mcp |
|| [weights-and-biases](mlops/weights-and-biases/SKILL.md) | 2 | evolutionary-ml, python-data-science |
|| [evolutionary-ml](data-science/evolutionary-ml/SKILL.md) | 2 | model-export-deploy, test-infra-ml |
|| [huggingface-trackio](huggingface-trackio/SKILL.md) | 2 | python-data-science, huggingface-hub |
|| [ssh-remote](devops/ssh-remote/SKILL.md) | 2 | docker-containers, rest-api-client |
|| [dogfood](dogfood/dogfood/SKILL.md) | 2 | adversarial-ux-test, inspecting-hermes-desktop-dom |
|| [himalaya](email/himalaya/SKILL.md) | 2 | email-inbox-triage, google-workspace |
|| [github-repo-management](github/github-repo-management/SKILL.md) | 2 | codebase-inspection, github-auth |
|| [mattpocock-yeet](github/mattpocock-yeet/SKILL.md) | 2 | mattpocock-finishing-a-development-branch, mattpocock-using-git-worktrees |
|| [mattpocock-using-git-worktrees](software-development/mattpocock-using-git-worktrees/SKILL.md) | 2 | mattpocock-finishing-a-development-branch, mattpocock-subagent-driven-development |
|| [autonomous-repo-cronjob](autonomous-ai-agents/autonomous-repo-cronjob/SKILL.md) | 2 | mattpocock-yeet, mattpocock-using-git-worktrees |
|| [grounded-citations](research/grounded-citations/SKILL.md) | 2 | blocked-page-recovery, mattpocock-research |
|| [node-inspect-debugger](software-development/node-inspect-debugger/SKILL.md) | 2 | inspecting-hermes-desktop-dom, python-debugpy |
|| [mattpocock-improve-codebase-architecture](software-development/mattpocock-improve-codebase-architecture/SKILL.md) | 2 | mattpocock-codebase-design, mattpocock-domain-modeling |
|| [mattpocock-security-review](security/mattpocock-security-review/SKILL.md) | 2 | mattpocock-evidence-driven, mattpocock-multi-agent-code-review |
|| [mattpocock-codebase-design](software-development/mattpocock-codebase-design/SKILL.md) | 2 | mattpocock-improve-codebase-architecture, mattpocock-spec-driven-development |
|| [mattpocock-finishing-a-development-branch](github/mattpocock-finishing-a-development-branch/SKILL.md) | 2 | mattpocock-subagent-driven-development, mattpocock-using-git-worktrees |

## MLOps Pipeline Skill Chain

```
build-systems-data ─> python-data-science ─> huggingface-hub ─> huggingface-trackio
model-export-deploy ─> evolutionary-ml ─> python-data-science
orbital-mechanics-data ─> python-data-science
evolutionary-ml ─> test-infra-ml ─> python-data-science
sql-for-data ─> python-data-science
test-infra-ml ─> python-data-science
cli-tool-craft ─> python-craft
build-systems-data ─> python-craft
evolutionary-ml ─> python-craft
model-export-deploy ─> python-craft
orbital-mechanics-data ─> python-craft
static-site-seo ─> python-craft
streamlit-dashboards ─> python-craft
verification-culture ─> python-craft
```

## GitHub Workflow Skill Chain

```
github-auth ─> github-pr-workflow ─> github-code-review, github-issues, github-repo-management
github-auth ─> github-code-review ─> mattpocock-code-review
github-auth ─> github-issues ─> github-issue-to-pr, mattpocock-to-tickets
github-auth ─> github-repo-management
github-pr-workflow ─> github-code-review, github-issues, github-repo-management, mattpocock-yeet, mattpocock-using-git-worktrees
mattpocock-yeet ─> autonomous-repo-cronjob
mattpocock-using-git-worktrees ─> autonomous-repo-cronjob, mattpocock-subagent-driven-development
mattpocock-finishing-a-development-branch ─> mattpocock-subagent-driven-development, mattpocock-using-git-worktrees
```

## Software Development Methodology Chain

```
plan ─> systematic-debugging
plan ─> test-driven-development
plan ─> subagent-driven-development
plan ─> requesting-code-review
systematic-debugging ─> test-driven-development (mutual)
test-driven-development ─> systematic-debugging (mutual)
mattpocock-tdd ─> mattpocock-code-review, mattpocock-diagnosing-bugs, mattpocock-evidence-driven, mattpocock-codebase-design
mattpocock-code-review ─> mattpocock-security-review, mattpocock-diagnosing-bugs, mattpocock-evidence-driven, mattpocock-multi-agent-code-review, mattpocock-tdd, mattpocock-to-tickets
mattpocock-subagent-driven-development ─> mattpocock-to-tickets, mattpocock-multi-agent-code-review, mattpocock-using-git-worktrees, mattpocock-finishing-a-development-branch, requesting-code-review
mattpocock-evidence-driven ─> mattpocock-code-review, mattpocock-diagnosing-bugs, mattpocock-multi-agent-code-review, mattpocock-security-review, mattpocock-tdd
```

## Document Processing Chain

```
docx ─> pdf
docx ─> powerpoint
docx ─> xlsx
docx ─> ocr-and-documents
docx ─> document-to-action-items
pdf ─> docx, powerpoint, xlsx, ocr-and-documents, nano-pdf
powerpoint ─> docx, pdf, xlsx, ocr-and-documents
xlsx ─> docx, pdf, powerpoint, sql-for-data
ocr-and-documents ─> pdf, docx, powerpoint, xlsx, document-to-action-items, arxiv, grounded-citations
```

## Creative & Visualization Chain

```
sketch ─> architecture-diagram, claude-design, frontend-design, spike, pretext, design-md
excalidraw ─> architecture-diagram, ascii-art, claude-design, design-md, p5js, pretext, sketch
claude-design ─> design-md, pretext, sketch, frontend-design
p5js ─> ascii-video, manim-video
```

## Research Chain

```
arxiv ─> grounded-citations, llm-wiki, mattpocock-research, research-paper-writing
grounded-citations ─> blocked-page-recovery, mattpocock-research
blogwatcher ─> competitor-news-monitor
mattpocock-research ─> mattpocock-writing-for-agents
```

## Related Skills Validation

All `related_skills` references in the repository resolve to existing in-repo skills. Verified against 127 unique skill names.

---

*Last generated: from live frontmatter analysis of all 127 skills.*
