# Skill Dependency Map

This document maps the relationship network between all **127 Hermes skills** in this repository. It is generated from the `related_skills` field in each skill's frontmatter.

**Network stats:** 310 `related_skills` cross-references across 125 skills (2 skills are standalone with no `related_skills` entries).

## Hub Skills (referenced by 2+ other skills)

These are the core skills that serve as building blocks, referenced by many other skills:

| Skill | Referenced By (count) | Referencing Skills |
|-------|-----------------------|---------------------|
| `requesting-code-review` | 13 | codex, github-issue-to-pr, hermes-agent-skill-authoring, mattpocock-code-review, mattpocock-evidence-driven, mattpocock-finishing-a-development-branch, mattpocock-multi-agent-code-review, mattpocock-security-review, mattpocock-subagent-driven-development, plan, python-craft, sdlc-review, simplify-code |
| `systematic-debugging` | 10 | github-issue-to-pr, inspecting-hermes-desktop-dom, mattpocock-diagnosing-bugs, mattpocock-resolving-merge-conflicts, mattpocock-tdd, node-inspect-debugger, python-craft, python-data-science, python-debugpy, test-driven-development |
| `python-craft` | 9 | build-systems-data, cli-tool-craft, evolutionary-ml, model-export-deploy, orbital-mechanics-data, static-site-seo, streamlit-dashboards, test-infra-ml, verification-culture |
| `test-driven-development` | 9 | github-issue-to-pr, mattpocock-tdd, plan, python-craft, python-data-science, requesting-code-review, simplify-code, systematic-debugging, test-infra-ml |
| `github-pr-workflow` | 9 | github-auth, github-code-review, github-issue-to-pr, github-issues, github-repo-management, mattpocock-finishing-a-development-branch, mattpocock-gh-fix-ci, mattpocock-using-git-worktrees, mattpocock-yeet |
| `excalidraw` | 8 | architecture-diagram, ascii-art, claude-design, design-md, p5js, popular-web-designs, pretext, sketch |
| `plan` | 7 | hermes-agent-skill-authoring, requesting-code-review, research-paper-writing, simplify-code, spike, systematic-debugging, test-driven-development |
| `hermes-agent` | 6 | autonomous-repo-cronjob, claude-code, codex, cron-job-authoring, merge-reconciler, opencode |
| `architecture-diagram` | 6 | claude-design, design-md, excalidraw, popular-web-designs, pretext, sketch |
| `claude-design` | 6 | design-md, frontend-design, popular-web-designs, pretext, sketch, songwriting-and-ai-music |
| `pdf` | 6 | document-to-action-items, docx, nano-pdf, ocr-and-documents, powerpoint, xlsx |
| `mattpocock-subagent-driven-development` | 6 | plan, requesting-code-review, research-paper-writing, spike, systematic-debugging, test-driven-development |
| `mattpocock-code-review` | 6 | mattpocock-diagnosing-bugs, mattpocock-evidence-driven, mattpocock-multi-agent-code-review, mattpocock-security-review, mattpocock-tdd, mattpocock-to-tickets |
| `sketch` | 5 | architecture-diagram, frontend-design, mattpocock-prototype, popular-web-designs, spike |
| `python-data-science` | 5 | build-systems-data, evolutionary-ml, huggingface-trackio, orbital-mechanics-data, sql-for-data |
| `google-workspace` | 5 | box, email-inbox-triage, himalaya, meeting-action-items, weekly-review-planning |
| `notion` | 5 | airtable, document-to-action-items, meeting-action-items, obsidian, weekly-review-planning |
| `ocr-and-documents` | 5 | arxiv, document-to-action-items, grounded-citations, nano-pdf, pdf |
| `docx` | 5 | document-to-action-items, ocr-and-documents, pdf, powerpoint, xlsx |
| `apple-notes` | 4 | apple-reminders, findmy, imessage, obsidian |
| `youtube-content` | 4 | ascii-video, gif-search, manim-video, songsee |
| `popular-web-designs` | 4 | claude-design, design-md, frontend-design, sketch |
| `ascii-video` | 4 | manim-video, p5js, pretext, touchdesigner-mcp |
| `xlsx` | 4 | docx, pdf, powerpoint, sql-for-data |
| `mattpocock-writing-for-agents` | 4 | doc-coauthoring, mattpocock-ask-if-underspecified, mattpocock-domain-modeling, mattpocock-handoff |
| `github-code-review` | 4 | github-auth, github-pr-workflow, mattpocock-code-review, requesting-code-review |
| `github-issues` | 4 | github-auth, github-issue-to-pr, github-repo-management, mattpocock-to-tickets |
| `github-auth` | 4 | github-code-review, github-issues, github-pr-workflow, github-repo-management |
| `mattpocock-tdd` | 4 | mattpocock-code-review, mattpocock-codebase-design, mattpocock-diagnosing-bugs, mattpocock-evidence-driven |
| `powerpoint` | 4 | docx, ocr-and-documents, pdf, xlsx |
| `parallel-cli` | 4 | blocked-page-recovery, blogwatcher, competitor-news-monitor, mattpocock-research |
| `arxiv` | 4 | grounded-citations, llm-wiki, mattpocock-research, research-paper-writing |
| `obsidian` | 3 | apple-notes, llm-wiki, weekly-review-planning |
| `apple-reminders` | 3 | apple-notes, findmy, imessage |
| `findmy` | 3 | apple-reminders, imessage, maps |
| `codex` | 3 | claude-code, hermes-agent, opencode |
| `claude-code` | 3 | codex, hermes-agent, opencode |
| `mattpocock-diagnosing-bugs` | 3 | mattpocock-gh-fix-ci, mattpocock-resolving-merge-conflicts, mattpocock-tdd |
| `manim-video` | 3 | ascii-video, p5js, touchdesigner-mcp |
| `comfyui` | 3 | baoyu-infographic, songsee, songwriting-and-ai-music |
| `huggingface-trackio` | 3 | huggingface-hub, python-data-science, weights-and-biases |
| `hermes-agent-skill-authoring` | 3 | doc-coauthoring, mattpocock-code-review, mattpocock-writing-for-agents |
| `mattpocock-using-git-worktrees` | 3 | mattpocock-evidence-driven, mattpocock-finishing-a-development-branch, mattpocock-subagent-driven-development |
| `huggingface-hub` | 3 | huggingface-trackio, llama-cpp, weights-and-biases |
| `mattpocock-to-tickets` | 3 | mattpocock-handoff, mattpocock-spec-driven-development, mattpocock-subagent-driven-development |
| `mattpocock-domain-modeling` | 3 | mattpocock-handoff, mattpocock-improve-codebase-architecture, mattpocock-writing-for-agents |
| `grounded-citations` | 3 | blocked-page-recovery, mattpocock-research, parallel-cli |
| `mattpocock-multi-agent-code-review` | 3 | mattpocock-evidence-driven, mattpocock-security-review, mattpocock-subagent-driven-development |
| `mattpocock-handoff` | 3 | mattpocock-ask-if-underspecified, mattpocock-to-tickets, mattpocock-writing-for-agents |
| `imessage` | 2 | apple-reminders, findmy |
| `opencode` | 2 | claude-code, hermes-agent |
| `ascii-art` | 2 | ascii-video, pretext |
| `design-md` | 2 | claude-design, popular-web-designs |
| `p5js` | 2 | manim-video, pretext |
| `spike` | 2 | mattpocock-prototype, sketch |
| `weights-and-biases` | 2 | evolutionary-ml, python-data-science |
| `evolutionary-ml` | 2 | model-export-deploy, test-infra-ml |
| `ssh-remote` | 2 | docker-containers, rest-api-client |
| `docker-containers` | 2 | rest-api-client, ssh-remote |
| `dogfood` | 2 | adversarial-ux-test, inspecting-hermes-desktop-dom |
| `himalaya` | 2 | email-inbox-triage, google-workspace |
| `email-inbox-triage` | 2 | himalaya, weekly-review-planning |
| `github-repo-management` | 2 | codebase-inspection, github-auth |
| `mattpocock-yeet` | 2 | mattpocock-finishing-a-development-branch, mattpocock-using-git-worktrees |
| `autonomous-repo-cronjob` | 2 | mattpocock-using-git-worktrees, mattpocock-yeet |
| `blogwatcher` | 2 | competitor-news-monitor, youtube-content |
| `serving-llms-vllm` | 2 | llama-cpp, weights-and-biases |
| `meeting-action-items` | 2 | document-to-action-items, teams-meeting-pipeline |
| `airtable` | 2 | notion, weekly-review-planning |
| `node-inspect-debugger` | 2 | inspecting-hermes-desktop-dom, python-debugpy |
| `mattpocock-improve-codebase-architecture` | 2 | mattpocock-codebase-design, mattpocock-domain-modeling |
| `mattpocock-security-review` | 2 | mattpocock-evidence-driven, mattpocock-multi-agent-code-review |
| `mattpocock-codebase-design` | 2 | mattpocock-improve-codebase-architecture, mattpocock-spec-driven-development |
| `mattpocock-finishing-a-development-branch` | 2 | mattpocock-subagent-driven-development, mattpocock-using-git-worktrees |

## Standalone Skills

The following 2 skills have no `related_skills` entries of their own (they do not reference other skills). These are genuinely standalone — no other skill references them either:

- `evaluating-llms-harness`
- `xurl`

## Software Development Methodology Chain

```
plan ─> mattpocock-subagent-driven-development, requesting-code-review, test-driven-development
systematic-debugging ─> mattpocock-subagent-driven-development, plan, test-driven-development
test-driven-development ─> mattpocock-subagent-driven-development, plan, systematic-debugging
mattpocock-tdd ─> mattpocock-code-review, mattpocock-diagnosing-bugs, systematic-debugging, test-driven-development
mattpocock-code-review ─> github-code-review, hermes-agent-skill-authoring, mattpocock-tdd, requesting-code-review
mattpocock-subagent-driven-development ─> mattpocock-finishing-a-development-branch, mattpocock-multi-agent-code-review, mattpocock-to-tickets, mattpocock-using-git-worktrees, requesting-code-review
mattpocock-evidence-driven ─> mattpocock-code-review, mattpocock-multi-agent-code-review, mattpocock-security-review, mattpocock-tdd, mattpocock-using-git-worktrees, requesting-code-review
```

## GitHub Workflow Skill Chain

```
hermes-agent ─> claude-code, codex, opencode
github-pr-workflow ─> github-auth, github-code-review
mattpocock-yeet ─> autonomous-repo-cronjob, github-pr-workflow
mattpocock-using-git-worktrees ─> autonomous-repo-cronjob, github-pr-workflow, mattpocock-finishing-a-development-branch, mattpocock-yeet
mattpocock-finishing-a-development-branch ─> github-pr-workflow, mattpocock-using-git-worktrees, mattpocock-yeet, requesting-code-review
```

## Data Science Chain

```
python-craft ─> requesting-code-review, simplify-code, systematic-debugging, test-driven-development
python-data-science ─> huggingface-trackio, systematic-debugging, test-driven-development, weights-and-biases
evolutionary-ml ─> python-craft, python-data-science, weights-and-biases
build-systems-data ─> python-craft, python-data-science
model-export-deploy ─> evolutionary-ml, python-craft
orbital-mechanics-data ─> python-craft, python-data-science
static-site-seo ─> python-craft
streamlit-dashboards ─> python-craft
test-infra-ml ─> evolutionary-ml, python-craft, test-driven-development
verification-culture ─> cli-tool-craft, python-craft, test-infra-ml
```

## Research Chain

```
arxiv ─> ocr-and-documents
grounded-citations ─> arxiv, ocr-and-documents, research-paper-writing
blogwatcher ─> competitor-news-monitor, parallel-cli
mattpocock-research ─> arxiv, grounded-citations, parallel-cli
parallel-cli ─> grounded-citations
```

## Document Processing Chain

```
docx ─> pdf, powerpoint, xlsx
pdf ─> docx, ocr-and-documents, powerpoint, xlsx
powerpoint ─> docx, pdf, xlsx
xlsx ─> docx, pdf, powerpoint
ocr-and-documents ─> docx, pdf, powerpoint
```

## Creative & Visualization Chain

```
sketch ─> architecture-diagram, claude-design, excalidraw, popular-web-designs, spike
excalidraw ─> architecture-diagram
claude-design ─> architecture-diagram, design-md, excalidraw, popular-web-designs
p5js ─> ascii-video, excalidraw, manim-video
comfyui ─> baoyu-infographic
architecture-diagram ─> excalidraw, sketch
ascii-art ─> excalidraw
ascii-video ─> ascii-art, manim-video, youtube-content
design-md ─> architecture-diagram, claude-design, excalidraw, popular-web-designs
pretext ─> architecture-diagram, ascii-art, ascii-video, claude-design, excalidraw, p5js
manim-video ─> ascii-video, p5js, youtube-content
```

## MLOps Chain

```
huggingface-hub ─> huggingface-trackio, llama-cpp
huggingface-trackio ─> huggingface-hub, python-data-science
llama-cpp ─> huggingface-hub, serving-llms-vllm
weights-and-biases ─> huggingface-hub, huggingface-trackio, serving-llms-vllm
```

## Productivity Chain

```
airtable ─> notion
notion ─> airtable
box ─> google-workspace
google-workspace ─> himalaya
docx ─> pdf, powerpoint, xlsx
pdf ─> docx, ocr-and-documents, powerpoint, xlsx
powerpoint ─> docx, pdf, xlsx
xlsx ─> docx, pdf, powerpoint
maps ─> findmy
obsidian ─> apple-notes, notion
notion ─> airtable
session-librarian ─> weekly-review-planning
document-to-action-items ─> docx, meeting-action-items, notion, ocr-and-documents, pdf
meeting-action-items ─> google-workspace, notion, teams-meeting-pipeline
teams-meeting-pipeline ─> meeting-action-items
weekly-review-planning ─> airtable, email-inbox-triage, google-workspace, notion, obsidian
```

## Apple Ecosystem Chain

```
apple-reminders ─> apple-notes, findmy, imessage
apple-notes ─> apple-reminders, obsidian
findmy ─> apple-notes, apple-reminders, imessage
imessage ─> apple-notes, apple-reminders, findmy
```

## Autonomous Agents & Delegation

```
hermes-agent ─> claude-code, codex, opencode
autonomous-repo-cronjob ─> hermes-agent
cron-job-authoring ─> hermes-agent
mattpocock-subagent-driven-development ─> mattpocock-finishing-a-development-branch, mattpocock-multi-agent-code-review, mattpocock-to-tickets, mattpocock-using-git-worktrees, requesting-code-review
merge-reconciler ─> hermes-agent, mattpocock-resolving-merge-conflicts
mattpocock-resolving-merge-conflicts ─> mattpocock-diagnosing-bugs, merge-reconciler, systematic-debugging
```

## Related Skills Validation

All 308 `related_skills` references in the repository resolve to existing in-repo skills. Verified against 127 unique skill names.

---

*Last generated: 2026-08-24 from live frontmatter analysis of all 127 skills.*
