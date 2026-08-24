# Skill Dependency Map
This document maps the relationship network between all **127 Hermes skills** in this repository. It is generated from the `related_skills` field in each skill's frontmatter.
**Network stats:** 337 `related_skills` cross-references across 127 skills (2 skills are standalone with no `related_skills` entries).
## Hub Skills (referenced by 2+ other skills)
These are the core skills that serve as building blocks, referenced by many other skills:
| Skill | Referenced By (count) | Referencing Skills |
|-------|-----------------------|---------------------|
| `requesting-code-review` | 14 | codex, github-issue-to-pr, hermes-agent-skill-authoring, mattpocock-code-review, mattpocock-evidence-driven, mattpocock-finishing-a-development-branch, mattpocock-multi-agent-code-review, mattpocock-security-review, mattpocock-spec-driven-development, mattpocock-subagent-driven-development, plan, python-craft, sdlc-review, simplify-code |
| `systematic-debugging` | 11 | github-issue-to-pr, inspecting-hermes-desktop-dom, mattpocock-diagnosing-bugs, mattpocock-gh-fix-ci, mattpocock-resolving-merge-conflicts, mattpocock-tdd, node-inspect-debugger, python-craft, python-data-science, python-debugpy, test-driven-development |
| `test-driven-development` | 10 | github-issue-to-pr, mattpocock-subagent-driven-development, mattpocock-tdd, plan, python-craft, python-data-science, requesting-code-review, simplify-code, systematic-debugging, test-infra-ml |
| `excalidraw` | 9 | architecture-diagram, ascii-art, claude-design, design-md, p5js, popular-web-designs, pretext, research-paper-writing, sketch |
| `github-pr-workflow` | 9 | github-auth, github-code-review, github-issue-to-pr, github-issues, github-repo-management, mattpocock-finishing-a-development-branch, mattpocock-gh-fix-ci, mattpocock-using-git-worktrees, mattpocock-yeet |
| `python-craft` | 9 | build-systems-data, cli-tool-craft, evolutionary-ml, model-export-deploy, orbital-mechanics-data, static-site-seo, streamlit-dashboards, test-infra-ml, verification-culture |
| `hermes-agent` | 8 | apple-reminders, autonomous-repo-cronjob, claude-code, codex, cron-job-authoring, mattpocock-to-tickets, merge-reconciler, opencode |
| `mattpocock-code-review` | 7 | mattpocock-diagnosing-bugs, mattpocock-evidence-driven, mattpocock-multi-agent-code-review, mattpocock-security-review, mattpocock-spec-driven-development, mattpocock-tdd, mattpocock-to-tickets |
| `mattpocock-subagent-driven-development` | 7 | mattpocock-to-tickets, plan, requesting-code-review, research-paper-writing, spike, systematic-debugging, test-driven-development |
| `plan` | 7 | hermes-agent-skill-authoring, requesting-code-review, research-paper-writing, simplify-code, spike, systematic-debugging, test-driven-development |
| `architecture-diagram` | 6 | claude-design, design-md, excalidraw, popular-web-designs, pretext, sketch |
| `claude-design` | 6 | design-md, frontend-design, popular-web-designs, pretext, sketch, songwriting-and-ai-music |
| `github-auth` | 6 | github-code-review, github-issues, github-pr-workflow, github-repo-management, mattpocock-gh-fix-ci, mattpocock-yeet |
| `pdf` | 6 | document-to-action-items, docx, nano-pdf, ocr-and-documents, powerpoint, xlsx |
| `python-data-science` | 6 | build-systems-data, evolutionary-ml, huggingface-trackio, orbital-mechanics-data, research-paper-writing, sql-for-data |
| `docx` | 5 | document-to-action-items, ocr-and-documents, pdf, powerpoint, xlsx |
| `google-workspace` | 5 | box, email-inbox-triage, himalaya, meeting-action-items, weekly-review-planning |
| `mattpocock-domain-modeling` | 5 | mattpocock-handoff, mattpocock-improve-codebase-architecture, mattpocock-spec-driven-development, mattpocock-to-tickets, mattpocock-writing-for-agents |
| `mattpocock-tdd` | 5 | mattpocock-code-review, mattpocock-codebase-design, mattpocock-diagnosing-bugs, mattpocock-evidence-driven, mattpocock-spec-driven-development |
| `notion` | 5 | airtable, document-to-action-items, meeting-action-items, obsidian, weekly-review-planning |
| `ocr-and-documents` | 5 | arxiv, document-to-action-items, grounded-citations, nano-pdf, pdf |
| `sketch` | 5 | architecture-diagram, frontend-design, mattpocock-prototype, popular-web-designs, spike |
| `apple-notes` | 4 | apple-reminders, findmy, imessage, obsidian |
| `arxiv` | 4 | grounded-citations, llm-wiki, mattpocock-research, research-paper-writing |
| `ascii-video` | 4 | manim-video, p5js, pretext, touchdesigner-mcp |
| `github-code-review` | 4 | github-auth, github-pr-workflow, mattpocock-code-review, requesting-code-review |
| `github-issues` | 4 | github-auth, github-issue-to-pr, github-repo-management, mattpocock-to-tickets |
| `mattpocock-writing-for-agents` | 4 | doc-coauthoring, mattpocock-ask-if-underspecified, mattpocock-domain-modeling, mattpocock-handoff |
| `parallel-cli` | 4 | blocked-page-recovery, blogwatcher, competitor-news-monitor, mattpocock-research |
| `popular-web-designs` | 4 | claude-design, design-md, frontend-design, sketch |
| `powerpoint` | 4 | docx, ocr-and-documents, pdf, xlsx |
| `xlsx` | 4 | docx, pdf, powerpoint, sql-for-data |
| `youtube-content` | 4 | ascii-video, gif-search, manim-video, songsee |
| `apple-reminders` | 3 | apple-notes, findmy, imessage |
| `claude-code` | 3 | codex, hermes-agent, opencode |
| `codex` | 3 | claude-code, hermes-agent, opencode |
| `comfyui` | 3 | baoyu-infographic, songsee, songwriting-and-ai-music |
| `cron-job-authoring` | 3 | apple-reminders, findmy, product-price-monitor |
| `findmy` | 3 | apple-reminders, imessage, maps |
| `grounded-citations` | 3 | blocked-page-recovery, mattpocock-research, parallel-cli |
| `hermes-agent-skill-authoring` | 3 | doc-coauthoring, mattpocock-code-review, mattpocock-writing-for-agents |
| `huggingface-hub` | 3 | huggingface-trackio, llama-cpp, weights-and-biases |
| `huggingface-trackio` | 3 | huggingface-hub, python-data-science, weights-and-biases |
| `manim-video` | 3 | ascii-video, p5js, touchdesigner-mcp |
| `mattpocock-diagnosing-bugs` | 3 | mattpocock-gh-fix-ci, mattpocock-resolving-merge-conflicts, mattpocock-tdd |
| `mattpocock-handoff` | 3 | mattpocock-ask-if-underspecified, mattpocock-to-tickets, mattpocock-writing-for-agents |
| `mattpocock-multi-agent-code-review` | 3 | mattpocock-evidence-driven, mattpocock-security-review, mattpocock-subagent-driven-development |
| `mattpocock-security-review` | 3 | mattpocock-evidence-driven, mattpocock-multi-agent-code-review, mattpocock-spec-driven-development |
| `mattpocock-to-tickets` | 3 | mattpocock-handoff, mattpocock-spec-driven-development, mattpocock-subagent-driven-development |
| `mattpocock-using-git-worktrees` | 3 | mattpocock-evidence-driven, mattpocock-finishing-a-development-branch, mattpocock-subagent-driven-development |
| `obsidian` | 3 | apple-notes, llm-wiki, weekly-review-planning |
| `weights-and-biases` | 3 | evolutionary-ml, python-data-science, serving-llms-vllm |
| `airtable` | 2 | notion, weekly-review-planning |
| `ascii-art` | 2 | ascii-video, pretext |
| `autonomous-repo-cronjob` | 2 | mattpocock-using-git-worktrees, mattpocock-yeet |
| `blogwatcher` | 2 | competitor-news-monitor, youtube-content |
| `design-md` | 2 | claude-design, popular-web-designs |
| `docker-containers` | 2 | rest-api-client, ssh-remote |
| `dogfood` | 2 | adversarial-ux-test, inspecting-hermes-desktop-dom |
| `email-inbox-triage` | 2 | himalaya, weekly-review-planning |
| `evolutionary-ml` | 2 | model-export-deploy, test-infra-ml |
| `github-repo-management` | 2 | codebase-inspection, github-auth |
| `himalaya` | 2 | email-inbox-triage, google-workspace |
| `imessage` | 2 | apple-reminders, findmy |
| `llama-cpp` | 2 | huggingface-hub, serving-llms-vllm |
| `mattpocock-codebase-design` | 2 | mattpocock-improve-codebase-architecture, mattpocock-spec-driven-development |
| `mattpocock-evidence-driven` | 2 | mattpocock-diagnosing-bugs, mattpocock-subagent-driven-development |
| `mattpocock-finishing-a-development-branch` | 2 | mattpocock-subagent-driven-development, mattpocock-using-git-worktrees |
| `mattpocock-gh-fix-ci` | 2 | mattpocock-spec-driven-development, mattpocock-yeet |
| `mattpocock-improve-codebase-architecture` | 2 | mattpocock-codebase-design, mattpocock-domain-modeling |
| `mattpocock-yeet` | 2 | mattpocock-finishing-a-development-branch, mattpocock-using-git-worktrees |
| `meeting-action-items` | 2 | document-to-action-items, teams-meeting-pipeline |
| `node-inspect-debugger` | 2 | inspecting-hermes-desktop-dom, python-debugpy |
| `opencode` | 2 | claude-code, hermes-agent |
| `p5js` | 2 | manim-video, pretext |
| `serving-llms-vllm` | 2 | llama-cpp, weights-and-biases |
| `spike` | 2 | mattpocock-prototype, sketch |
| `ssh-remote` | 2 | docker-containers, rest-api-client |
## Standalone Skills
The following 2 skills have no `related_skills` entries of their own (they do not reference other skills). These are genuinely standalone — no other skill references them either:
- `evaluating-llms-harness`
- `xurl`
## Related Skills Validation
All 337 `related_skills` references in the repository resolve to existing in-repo skills. Verified against 127 unique skill names.

---

*Last generated: 2026-08-24 from live frontmatter analysis of all 127 skills.*
