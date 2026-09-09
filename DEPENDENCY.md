# Skill Dependency Map
This document maps the relationship network between all **174 Hermes skills** in this repository. It is generated from the `related_skills` field in each skill's frontmatter.
**Network stats:** 409 `related_skills` cross-references across 174 skills (13 skills are standalone with no `related_skills` entries).
## Hub Skills (referenced by 2+ other skills)
These are the core skills that serve as building blocks, referenced by many other skills:
| Skill | Referenced By (count) | Referencing Skills |
|-------|-----------------------|---------------------|
| `requesting-code-review` | 18 | code-quality-signal, codex, github-issue-to-pr, hermes-agent-skill-authoring, mattpocock-code-review, mattpocock-evidence-driven, mattpocock-finishing-a-development-branch, mattpocock-multi-agent-code-review, mattpocock-security-review, mattpocock-spec-driven-development, mattpocock-subagent-driven-development, plan, python-craft, receiving-code-review, sdlc-review, semgrep-rule-creator, simplify-code, skill-flow-router |
| `test-driven-development` | 16 | generating-python-installer, github-issue-to-pr, mattpocock-subagent-driven-development, mattpocock-tdd, modern-python-tooling, plan, property-based-testing, python-craft, python-data-science, requesting-code-review, rest-graphql-debug, simplify-code, skill-flow-router, systematic-debugging, test-infra-ml, windows-desktop-e2e |
| `systematic-debugging` | 14 | ast-grep, github-issue-to-pr, inspecting-hermes-desktop-dom, mattpocock-diagnosing-bugs, mattpocock-gh-fix-ci, mattpocock-resolving-merge-conflicts, mattpocock-tdd, node-inspect-debugger, python-craft, python-data-science, python-debugpy, rest-graphql-debug, skill-flow-router, test-driven-development |
| `excalidraw` | 10 | architecture-diagram, ascii-art, claude-design, design-md, diagram-design, p5js, popular-web-designs, pretext, research-paper-writing, sketch |
| `python-craft` | 10 | build-systems-data, cli-tool-craft, evolutionary-ml, model-export-deploy, modern-python-tooling, orbital-mechanics-data, static-site-seo, streamlit-dashboards, test-infra-ml, verification-culture |
| `github-pr-workflow` | 9 | github-auth, github-code-review, github-issue-to-pr, github-issues, github-repo-management, mattpocock-finishing-a-development-branch, mattpocock-gh-fix-ci, mattpocock-using-git-worktrees, mattpocock-yeet |
| `hermes-agent` | 9 | apple-reminders, autonomous-repo-cronjob, claude-code, codex, cron-job-authoring, mattpocock-to-tickets, merge-reconciler, opencode, qmd |
| `mattpocock-code-review` | 8 | mattpocock-diagnosing-bugs, mattpocock-evidence-driven, mattpocock-multi-agent-code-review, mattpocock-security-review, mattpocock-spec-driven-development, mattpocock-tdd, mattpocock-to-tickets, receiving-code-review |
| `plan` | 8 | brainstorming, hermes-agent-skill-authoring, requesting-code-review, research-paper-writing, simplify-code, spike, systematic-debugging, test-driven-development |
| `architecture-diagram` | 7 | claude-design, design-md, diagram-design, excalidraw, popular-web-designs, pretext, sketch |
| `claude-design` | 7 | design-md, frontend-design, popular-web-designs, pretext, sketch, songwriting-and-ai-music, teach |
| `github-auth` | 7 | github-code-review, github-issues, github-pr-workflow, github-repo-management, mattpocock-gh-fix-ci, mattpocock-yeet, wizard |
| `mattpocock-subagent-driven-development` | 7 | mattpocock-to-tickets, plan, requesting-code-review, research-paper-writing, spike, systematic-debugging, test-driven-development |
| `python-data-science` | 7 | build-systems-data, evolutionary-ml, huggingface-trackio, orbital-mechanics-data, regex-vs-llm-structured-text, research-paper-writing, sql-for-data |
| `arxiv` | 6 | grounded-citations, literature-review, llm-wiki, mattpocock-research, qmd, research-paper-writing |
| `docx` | 6 | document-to-action-items, ocr-and-documents, pdf, powerpoint, website-audit, xlsx |
| `mattpocock-domain-modeling` | 6 | issue-triage-state-machine, mattpocock-handoff, mattpocock-improve-codebase-architecture, mattpocock-spec-driven-development, mattpocock-to-tickets, mattpocock-writing-for-agents |
| `pdf` | 6 | document-to-action-items, docx, nano-pdf, ocr-and-documents, powerpoint, xlsx |
| `github-code-review` | 5 | github-auth, github-pr-workflow, mattpocock-code-review, receiving-code-review, requesting-code-review |
| `google-workspace` | 5 | box, email-inbox-triage, himalaya, meeting-action-items, weekly-review-planning |
| `grilling-interview` | 5 | brainstorming, conversation-to-spec, issue-triage-state-machine, skill-flow-router, wayfinder-map-planning |
| `mattpocock-tdd` | 5 | mattpocock-code-review, mattpocock-codebase-design, mattpocock-diagnosing-bugs, mattpocock-evidence-driven, mattpocock-spec-driven-development |
| `mattpocock-to-tickets` | 5 | mattpocock-handoff, mattpocock-spec-driven-development, mattpocock-subagent-driven-development, skill-flow-router, wayfinder-map-planning |
| `mattpocock-writing-for-agents` | 5 | doc-coauthoring, mattpocock-ask-if-underspecified, mattpocock-domain-modeling, mattpocock-handoff, retro |
| `notion` | 5 | airtable, document-to-action-items, meeting-action-items, obsidian, weekly-review-planning |
| `ocr-and-documents` | 5 | arxiv, document-to-action-items, grounded-citations, nano-pdf, pdf |
| `popular-web-designs` | 5 | claude-design, design-md, frontend-design, redesign-existing-projects, sketch |
| `sketch` | 5 | architecture-diagram, frontend-design, mattpocock-prototype, popular-web-designs, spike |
| `apple-notes` | 4 | apple-reminders, findmy, imessage, obsidian |
| `ascii-video` | 4 | manim-video, p5js, pretext, touchdesigner-mcp |
| `cron-job-authoring` | 4 | apple-reminders, cron-config-authoring, findmy, product-price-monitor |
| `github-issues` | 4 | github-auth, github-issue-to-pr, github-repo-management, mattpocock-to-tickets |
| `grounded-citations` | 4 | blocked-page-recovery, literature-review, mattpocock-research, parallel-cli |
| `hermes-agent-skill-authoring` | 4 | cron-config-authoring, doc-coauthoring, mattpocock-code-review, mattpocock-writing-for-agents |
| `manim-video` | 4 | ascii-video, p5js, pygame, touchdesigner-mcp |
| `mattpocock-security-review` | 4 | mattpocock-evidence-driven, mattpocock-multi-agent-code-review, mattpocock-spec-driven-development, semgrep-rule-creator |
| `obsidian` | 4 | apple-notes, llm-wiki, qmd, weekly-review-planning |
| `parallel-cli` | 4 | blocked-page-recovery, blogwatcher, competitor-news-monitor, mattpocock-research |
| `powerpoint` | 4 | docx, ocr-and-documents, pdf, xlsx |
| `xlsx` | 4 | docx, pdf, powerpoint, sql-for-data |
| `youtube-content` | 4 | ascii-video, gif-search, manim-video, songsee |
| `apple-reminders` | 3 | apple-notes, findmy, imessage |
| `claude-code` | 3 | codex, hermes-agent, opencode |
| `codex` | 3 | claude-code, hermes-agent, opencode |
| `comfyui` | 3 | baoyu-infographic, songsee, songwriting-and-ai-music |
| `conversation-to-spec` | 3 | brainstorming, grilling-interview, skill-flow-router |
| `findmy` | 3 | apple-reminders, imessage, maps |
| `huggingface-hub` | 3 | huggingface-trackio, llama-cpp, weights-and-biases |
| `huggingface-trackio` | 3 | huggingface-hub, python-data-science, weights-and-biases |
| `mattpocock-diagnosing-bugs` | 3 | mattpocock-gh-fix-ci, mattpocock-resolving-merge-conflicts, mattpocock-tdd |
| `mattpocock-evidence-driven` | 3 | mattpocock-diagnosing-bugs, mattpocock-subagent-driven-development, verification-before-completion |
| `mattpocock-handoff` | 3 | mattpocock-ask-if-underspecified, mattpocock-to-tickets, mattpocock-writing-for-agents |
| `mattpocock-improve-codebase-architecture` | 3 | code-quality-signal, mattpocock-codebase-design, mattpocock-domain-modeling |
| `mattpocock-multi-agent-code-review` | 3 | mattpocock-evidence-driven, mattpocock-security-review, mattpocock-subagent-driven-development |
| `mattpocock-using-git-worktrees` | 3 | mattpocock-evidence-driven, mattpocock-finishing-a-development-branch, mattpocock-subagent-driven-development |
| `meeting-action-items` | 3 | decision-questionnaire, document-to-action-items, teams-meeting-pipeline |
| `p5js` | 3 | manim-video, pretext, pygame |
| `spike` | 3 | brainstorming, mattpocock-prototype, sketch |
| `ssh-remote` | 3 | docker-containers, rest-api-client, wizard |
| `weights-and-biases` | 3 | evolutionary-ml, python-data-science, serving-llms-vllm |
| `airtable` | 2 | notion, weekly-review-planning |
| `ascii-art` | 2 | ascii-video, pretext |
| `astro-toolkit-selection` | 2 | economicspace-pipeline, space-mission-computation-paradigms |
| `autonomous-repo-cronjob` | 2 | mattpocock-using-git-worktrees, mattpocock-yeet |
| `blogwatcher` | 2 | competitor-news-monitor, youtube-content |
| `design-md` | 2 | claude-design, popular-web-designs |
| `design-taste-frontend` | 2 | redesign-existing-projects, static-site-patterns |
| `docker-containers` | 2 | rest-api-client, ssh-remote |
| `document-to-action-items` | 2 | decision-questionnaire, meeting-action-items |
| `dogfood` | 2 | adversarial-ux-test, inspecting-hermes-desktop-dom |
| `email-inbox-triage` | 2 | himalaya, weekly-review-planning |
| `evolutionary-ml` | 2 | model-export-deploy, test-infra-ml |
| `github-repo-management` | 2 | codebase-inspection, github-auth |
| `himalaya` | 2 | email-inbox-triage, google-workspace |
| `imessage` | 2 | apple-reminders, findmy |
| `llama-cpp` | 2 | huggingface-hub, serving-llms-vllm |
| `mattpocock-codebase-design` | 2 | mattpocock-improve-codebase-architecture, mattpocock-spec-driven-development |
| `mattpocock-finishing-a-development-branch` | 2 | mattpocock-subagent-driven-development, mattpocock-using-git-worktrees |
| `mattpocock-gh-fix-ci` | 2 | mattpocock-spec-driven-development, mattpocock-yeet |
| `mattpocock-spec-driven-development` | 2 | conversation-to-spec, mattpocock-to-tickets |
| `mattpocock-yeet` | 2 | mattpocock-finishing-a-development-branch, mattpocock-using-git-worktrees |
| `node-inspect-debugger` | 2 | inspecting-hermes-desktop-dom, python-debugpy |
| `opencode` | 2 | claude-code, hermes-agent |
| `serving-llms-vllm` | 2 | llama-cpp, weights-and-biases |
| `simplify-code` | 2 | ast-grep, python-craft |
| `space-mission-computation-paradigms` | 2 | astro-toolkit-selection, economicspace-pipeline |
| `sql-for-data` | 2 | duckdb-querying, sqlite-queries |
| `test-infra-ml` | 2 | property-based-testing, verification-culture |
| `verification-culture` | 2 | retro, verification-before-completion |
| `wayfinder-map-planning` | 2 | grilling-interview, skill-flow-router |
## Standalone Skills
The following 10 skills have no `related_skills` entries of their own (they do not reference other skills). These are genuinely standalone — no other skill references them either:
- `bit-identity-float-pipelines`
- `evaluating-llms-harness`
- `fastmcp`
- `full-output-enforcement`
- `jupyter-notebook`
- `one-three-one-rule`
- `oss-forensics`
- `scrapling`
- `watchers`
- `xurl`
## Related Skills Validation
All 409 `related_skills` references in the repository resolve to existing in-repo skills. Verified against 174 unique skill names.

---

*Last generated: 2026-09-09 from live frontmatter analysis of all 174 skills.*
