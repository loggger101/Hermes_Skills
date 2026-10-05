# Skill Dependency Map

This document maps the relationship network between all **205 Hermes skills** in this repository. It is generated from the `related_skills` field in each skill's frontmatter.

**Network stats:** 553 `related_skills` cross-references across 205 skills (2 skills list no `related_skills` of their own).

## Hub Skills (referenced by 2+ other skills)

These are the core skills that serve as building blocks, referenced by many other skills:

| Skill | Referenced By (count) | Referencing Skills |
|-------|-----------------------|---------------------|
| `requesting-code-review` | 19 | architecture-metrics, codex, github-issue-to-pr, grilling-interview, hermes-agent-skill-authoring, mattpocock-code-review, mattpocock-evidence-driven, mattpocock-finishing-a-development-branch, mattpocock-security-review, mattpocock-spec-driven-development, mattpocock-subagent-driven-development, plan, ponytail, python-craft, receiving-code-review, sdlc-review, semgrep-rule-creator, simplify-code, skill-flow-router |
| `test-driven-development` | 18 | dispatching-parallel-agents, executing-plans, generating-python-installer, github-issue-to-pr, grilling-interview, mattpocock-subagent-driven-development, mattpocock-tdd, plan, property-based-testing, python-craft, python-data-science, requesting-code-review, rest-graphql-debug, simplify-code, skill-flow-router, systematic-debugging, test-infra-ml, windows-desktop-e2e |
| `systematic-debugging` | 16 | ast-grep, dispatching-parallel-agents, failure-signal-audit, github-issue-to-pr, inspecting-hermes-desktop-dom, mattpocock-diagnosing-bugs, mattpocock-gh-fix-ci, mattpocock-resolving-merge-conflicts, mattpocock-tdd, node-inspect-debugger, python-craft, python-data-science, python-debugpy, rest-graphql-debug, skill-flow-router, test-driven-development |
| `python-craft` | 13 | algorithms-python-catalog, build-systems-data, cli-tool-craft, evolutionary-ml, generating-python-installer, model-export-deploy, orbital-mechanics-data, ponytail, static-site-seo, streamlit-dashboards, system-design-scaling, test-infra-ml, verification-culture |
| `claude-design` | 12 | awwwards-gsap-motion, design-md, editorial-minimalism-ui, frontend-design, industrial-brutalist-ui, popular-web-designs, pretext, sketch, soft-premium-ui, songwriting-and-ai-music, stitch, teach |
| `excalidraw` | 11 | architecture-diagram, ascii-art, claude-design, design-md, diagram-design, p5js, popular-web-designs, pretext, research-paper-writing, sketch, system-atlas |
| `hermes-agent` | 11 | apple-reminders, claude-code, codex, cron-job-authoring, dynamic-workflow, hermes-bot-cloning, mattpocock-to-tickets, merge-reconciler, opencode, qmd, repowise |
| `mattpocock-subagent-driven-development` | 10 | dispatching-parallel-agents, executing-plans, grilling-interview, mattpocock-to-tickets, plan, requesting-code-review, research-paper-writing, spike, systematic-debugging, test-driven-development |
| `cron-job-authoring` | 9 | apple-reminders, cron-config-authoring, cron-pipeline-watchdog, findmy, hermes-bot-cloning, mattpocock-using-git-worktrees, mattpocock-yeet, product-price-monitor, watchers |
| `github-pr-workflow` | 9 | github-auth, github-code-review, github-issue-to-pr, github-issues, github-repo-management, mattpocock-finishing-a-development-branch, mattpocock-gh-fix-ci, mattpocock-using-git-worktrees, mattpocock-yeet |
| `grounded-citations` | 9 | blocked-page-recovery, general-research-rounds, literature-review, mattpocock-research, parallel-cli, pubmed-database, reddit-reading, rss-feeds, scholar-evaluation |
| `plan` | 9 | brainstorming, executing-plans, hermes-agent-skill-authoring, requesting-code-review, research-paper-writing, simplify-code, spike, systematic-debugging, test-driven-development |
| `python-data-science` | 9 | build-systems-data, evolutionary-ml, gget, huggingface-trackio, jupyter-notebook, orbital-mechanics-data, regex-vs-llm-structured-text, research-paper-writing, sql-for-data |
| `architecture-diagram` | 8 | claude-design, design-md, diagram-design, excalidraw, popular-web-designs, pretext, sketch, system-atlas |
| `design-taste-frontend` | 8 | awwwards-gsap-motion, editorial-minimalism-ui, full-output-enforcement, industrial-brutalist-ui, redesign-existing-projects, soft-premium-ui, static-site-patterns, stitch |
| `mattpocock-code-review` | 8 | mattpocock-diagnosing-bugs, mattpocock-evidence-driven, mattpocock-security-review, mattpocock-spec-driven-development, mattpocock-subagent-driven-development, mattpocock-tdd, mattpocock-to-tickets, receiving-code-review |
| `mattpocock-security-review` | 8 | application-threat-model, failure-signal-audit, mattpocock-code-review, mattpocock-evidence-driven, mattpocock-spec-driven-development, rest-api-client, security-audit, semgrep-rule-creator |
| `arxiv` | 7 | grounded-citations, literature-review, llm-wiki, mattpocock-research, pubmed-database, qmd, research-paper-writing |
| `github-auth` | 7 | github-code-review, github-issues, github-pr-workflow, github-repo-management, mattpocock-gh-fix-ci, mattpocock-yeet, wizard |
| `grilling-interview` | 7 | brainstorming, conversation-to-spec, issue-triage-state-machine, mental-models, one-three-one-rule, skill-flow-router, wayfinder-map-planning |
| `mattpocock-domain-modeling` | 7 | issue-triage-state-machine, living-docs-governance, mattpocock-codebase-design, mattpocock-handoff, mattpocock-spec-driven-development, mattpocock-to-tickets, mattpocock-writing-for-agents |
| `docx` | 6 | document-to-action-items, ocr-and-documents, pdf, powerpoint, website-audit, xlsx |
| `ocr-and-documents` | 6 | arxiv, document-to-action-items, general-research-rounds, grounded-citations, nano-pdf, pdf |
| `pdf` | 6 | document-to-action-items, docx, nano-pdf, ocr-and-documents, powerpoint, xlsx |
| `github-code-review` | 5 | github-auth, github-pr-workflow, mattpocock-code-review, receiving-code-review, requesting-code-review |
| `google-workspace` | 5 | box, email-inbox-triage, himalaya, meeting-action-items, weekly-review-planning |
| `mattpocock-codebase-design` | 5 | architecture-metrics, codebase-onboarding, mattpocock-domain-modeling, mattpocock-spec-driven-development, ponytail |
| `mattpocock-tdd` | 5 | mattpocock-code-review, mattpocock-codebase-design, mattpocock-diagnosing-bugs, mattpocock-evidence-driven, mattpocock-spec-driven-development |
| `mattpocock-to-tickets` | 5 | mattpocock-handoff, mattpocock-spec-driven-development, mattpocock-subagent-driven-development, skill-flow-router, wayfinder-map-planning |
| `mattpocock-writing-for-agents` | 5 | doc-coauthoring, mattpocock-ask-if-underspecified, mattpocock-domain-modeling, mattpocock-handoff, retro |
| `notion` | 5 | airtable, document-to-action-items, meeting-action-items, obsidian, weekly-review-planning |
| `obsidian` | 5 | apple-notes, knowledge-ops, llm-wiki, qmd, weekly-review-planning |
| `popular-web-designs` | 5 | claude-design, design-md, frontend-design, redesign-existing-projects, sketch |
| `verification-culture` | 5 | bit-identity-float-pipelines, failure-signal-audit, incident-response, retro, verification-before-completion |
| `youtube-content` | 5 | ascii-video, gif-search, manim-video, rss-feeds, songsee |
| `apple-notes` | 4 | apple-reminders, findmy, imessage, obsidian |
| `ascii-video` | 4 | manim-video, p5js, pretext, touchdesigner-mcp |
| `blogwatcher` | 4 | competitor-news-monitor, rss-feeds, watchers, youtube-content |
| `design-md` | 4 | claude-design, popular-web-designs, react-ecosystem, stitch |
| `github-issues` | 4 | github-auth, github-issue-to-pr, github-repo-management, mattpocock-to-tickets |
| `hermes-agent-skill-authoring` | 4 | cron-config-authoring, doc-coauthoring, mattpocock-code-review, mattpocock-writing-for-agents |
| `literature-review` | 4 | general-research-rounds, gget, pubmed-database, scholar-evaluation |
| `manim-video` | 4 | ascii-video, p5js, pygame, touchdesigner-mcp |
| `mattpocock-using-git-worktrees` | 4 | executing-plans, mattpocock-evidence-driven, mattpocock-finishing-a-development-branch, mattpocock-subagent-driven-development |
| `parallel-cli` | 4 | blocked-page-recovery, blogwatcher, competitor-news-monitor, mattpocock-research |
| `powerpoint` | 4 | docx, ocr-and-documents, pdf, xlsx |
| `simplify-code` | 4 | ast-grep, dynamic-workflow, ponytail, python-craft |
| `sketch` | 4 | architecture-diagram, frontend-design, popular-web-designs, spike |
| `ssh-remote` | 4 | docker-containers, pinggy-tunnel, rest-api-client, wizard |
| `weights-and-biases` | 4 | evaluating-llms-harness, evolutionary-ml, python-data-science, serving-llms-vllm |
| `xlsx` | 4 | docx, pdf, powerpoint, sql-for-data |
| `apple-reminders` | 3 | apple-notes, findmy, imessage |
| `astro-toolkit-selection` | 3 | economicspace-pipeline, optimization-modeling-pyomo, space-data-pipelines |
| `blocked-page-recovery` | 3 | general-research-rounds, reddit-reading, scrapling |
| `claude-code` | 3 | codex, hermes-agent, opencode |
| `codebase-onboarding` | 3 | living-docs-governance, repo-atlas, repowise |
| `codex` | 3 | claude-code, hermes-agent, opencode |
| `comfyui` | 3 | baoyu-infographic, songsee, songwriting-and-ai-music |
| `conversation-to-spec` | 3 | brainstorming, grilling-interview, skill-flow-router |
| `economicspace-pipeline` | 3 | astro-toolkit-selection, optimization-modeling-pyomo, space-data-pipelines |
| `evolutionary-ml` | 3 | algorithms-python-catalog, model-export-deploy, test-infra-ml |
| `findmy` | 3 | apple-reminders, imessage, maps |
| `github-repo-management` | 3 | code-wiki, codebase-inspection, github-auth |
| `huggingface-hub` | 3 | huggingface-trackio, llama-cpp, weights-and-biases |
| `huggingface-trackio` | 3 | huggingface-hub, python-data-science, weights-and-biases |
| `mattpocock-diagnosing-bugs` | 3 | mattpocock-gh-fix-ci, mattpocock-resolving-merge-conflicts, mattpocock-tdd |
| `mattpocock-evidence-driven` | 3 | mattpocock-diagnosing-bugs, mattpocock-subagent-driven-development, verification-before-completion |
| `mattpocock-finishing-a-development-branch` | 3 | executing-plans, mattpocock-subagent-driven-development, mattpocock-using-git-worktrees |
| `mattpocock-handoff` | 3 | mattpocock-ask-if-underspecified, mattpocock-to-tickets, mattpocock-writing-for-agents |
| `meeting-action-items` | 3 | decision-questionnaire, document-to-action-items, teams-meeting-pipeline |
| `p5js` | 3 | manim-video, pretext, pygame |
| `repowise` | 3 | architecture-metrics, fastmcp, repo-atlas |
| `sql-for-data` | 3 | duckdb-querying, sqlite-queries, system-design-scaling |
| `system-design-scaling` | 3 | algorithms-python-catalog, application-threat-model, incident-response |
| `airtable` | 2 | notion, weekly-review-planning |
| `architecture-metrics` | 2 | mattpocock-codebase-design, repowise |
| `ascii-art` | 2 | ascii-video, pretext |
| `code-wiki` | 2 | codebase-onboarding, repo-atlas |
| `competitor-news-monitor` | 2 | blogwatcher, rss-feeds |
| `cron-pipeline-watchdog` | 2 | incident-response, space-data-pipelines |
| `decision-questionnaire` | 2 | mental-models, one-three-one-rule |
| `docker-containers` | 2 | rest-api-client, ssh-remote |
| `document-to-action-items` | 2 | decision-questionnaire, meeting-action-items |
| `dogfood` | 2 | adversarial-ux-test, inspecting-hermes-desktop-dom |
| `email-inbox-triage` | 2 | himalaya, weekly-review-planning |
| `fastmcp` | 2 | mcporter, repowise |
| `himalaya` | 2 | email-inbox-triage, google-workspace |
| `humanizer` | 2 | no-ai-slop, songwriting-and-ai-music |
| `imessage` | 2 | apple-reminders, findmy |
| `llama-cpp` | 2 | huggingface-hub, serving-llms-vllm |
| `maps` | 2 | algorithms-python-catalog, product-price-monitor |
| `mattpocock-gh-fix-ci` | 2 | mattpocock-spec-driven-development, mattpocock-yeet |
| `mattpocock-research` | 2 | literature-review, scholar-evaluation |
| `mattpocock-spec-driven-development` | 2 | conversation-to-spec, mattpocock-to-tickets |
| `mattpocock-yeet` | 2 | mattpocock-finishing-a-development-branch, mattpocock-using-git-worktrees |
| `mcporter` | 2 | fastmcp, repowise |
| `node-inspect-debugger` | 2 | inspecting-hermes-desktop-dom, python-debugpy |
| `opencode` | 2 | claude-code, hermes-agent |
| `optimization-modeling-pyomo` | 2 | algorithms-python-catalog, astro-toolkit-selection |
| `orbital-mechanics-data` | 2 | astro-toolkit-selection, space-data-pipelines |
| `pubmed-database` | 2 | bioinformatics, gget |
| `redesign-existing-projects` | 2 | design-taste-frontend, full-output-enforcement |
| `rest-api-client` | 2 | rest-graphql-debug, system-design-scaling |
| `rest-graphql-debug` | 2 | har-derived-api-client, rest-api-client |
| `rss-feeds` | 2 | reddit-reading, watchers |
| `security-audit` | 2 | application-threat-model, mattpocock-security-review |
| `semgrep-rule-creator` | 2 | oss-forensics, security-audit |
| `serving-llms-vllm` | 2 | llama-cpp, weights-and-biases |
| `songwriting-and-ai-music` | 2 | humanizer, no-ai-slop |
| `space-data-pipelines` | 2 | cron-pipeline-watchdog, duckdb-querying |
| `spike` | 2 | brainstorming, sketch |
| `static-site-patterns` | 2 | publish-site, react-ecosystem |
| `static-site-seo` | 2 | publish-site, static-site-patterns |
| `test-infra-ml` | 2 | property-based-testing, verification-culture |
| `wayfinder-map-planning` | 2 | grilling-interview, skill-flow-router |

## Standalone Skills

No skill is fully standalone: every skill either lists `related_skills` or is referenced by another skill.

## Related Skills Validation

All 553 `related_skills` references in the repository resolve to existing in-repo skills. Verified against 205 unique skill names.

---
