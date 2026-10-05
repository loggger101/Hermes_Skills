# Skill Dependency Map

This document maps the relationship network between all **229 Hermes skills** in this repository. It is generated from the `related_skills` field in each skill's frontmatter.

**Network stats:** 677 `related_skills` cross-references across 229 skills (2 skills list no `related_skills` of their own).

## Hub Skills (referenced by 2+ other skills)

These are the core skills that serve as building blocks, referenced by many other skills:

| Skill | Referenced By (count) | Referencing Skills |
|-------|-----------------------|---------------------|
| `test-driven-development` | 20 | dispatching-parallel-agents, executing-plans, generating-python-installer, github-issue-to-pr, grilling-interview, mattpocock-subagent-driven-development, mattpocock-tdd, plan, property-based-testing, python-craft, python-data-science, python-toolchain-notes, requesting-code-review, rest-graphql-debug, simplify-code, skill-flow-router, structured-llm-outputs, systematic-debugging, test-infra-ml, windows-desktop-e2e |
| `requesting-code-review` | 19 | architecture-metrics, codex, github-issue-to-pr, grilling-interview, hermes-agent-skill-authoring, mattpocock-code-review, mattpocock-evidence-driven, mattpocock-finishing-a-development-branch, mattpocock-security-review, mattpocock-spec-driven-development, mattpocock-subagent-driven-development, plan, ponytail, python-craft, receiving-code-review, sdlc-review, semgrep-rule-creator, simplify-code, skill-flow-router |
| `python-craft` | 17 | algorithms-python-catalog, build-systems-data, cli-tool-craft, evolutionary-ml, generating-python-installer, model-export-deploy, orbital-mechanics-data, ponytail, python-numerics-gotchas, python-toolchain-notes, rust-crate-picks, static-site-seo, streamlit-dashboards, structured-llm-outputs, system-design-scaling, test-infra-ml, verification-culture |
| `systematic-debugging` | 17 | ast-grep, dispatching-parallel-agents, failure-signal-audit, github-issue-to-pr, inspecting-hermes-desktop-dom, mattpocock-diagnosing-bugs, mattpocock-gh-fix-ci, mattpocock-resolving-merge-conflicts, mattpocock-tdd, node-inspect-debugger, python-craft, python-data-science, python-debugpy, python-toolchain-notes, rest-graphql-debug, skill-flow-router, test-driven-development |
| `python-data-science` | 14 | build-systems-data, evolutionary-ml, experiment-design, gget, huggingface-trackio, jupyter-notebook, ml-cv-library-notes, orbital-mechanics-data, polars-pipelines, python-numerics-gotchas, python-plotting, regex-vs-llm-structured-text, research-paper-writing, sql-for-data |
| `hermes-agent` | 13 | apple-reminders, claude-code, codex, cron-job-authoring, dynamic-workflow, hermes-bot-cloning, hermes-extensions, mattpocock-to-tickets, merge-reconciler, opencode, qmd, repowise, unsloth-gguf |
| `claude-design` | 12 | awwwards-gsap-motion, design-md, editorial-minimalism-ui, frontend-design, industrial-brutalist-ui, popular-web-designs, pretext, sketch, soft-premium-ui, songwriting-and-ai-music, stitch, teach |
| `cron-job-authoring` | 12 | apple-reminders, autonomous-loop-design, cron-config-authoring, cron-pipeline-watchdog, experiment-design, findmy, hermes-bot-cloning, mattpocock-using-git-worktrees, mattpocock-yeet, product-price-monitor, secret-vault-pattern, watchers |
| `design-taste-frontend` | 11 | awwwards-gsap-motion, editorial-minimalism-ui, frontend-library-picks, full-output-enforcement, industrial-brutalist-ui, react-library-notes, redesign-existing-projects, soft-premium-ui, static-site-patterns, stitch, ui-ux-pro-max |
| `excalidraw` | 11 | architecture-diagram, ascii-art, claude-design, design-md, diagram-design, p5js, popular-web-designs, pretext, research-paper-writing, sketch, system-atlas |
| `github-pr-workflow` | 11 | agent-oss-contributions, feature-flag-lifecycle, github-auth, github-code-review, github-issue-to-pr, github-issues, github-repo-management, mattpocock-finishing-a-development-branch, mattpocock-gh-fix-ci, mattpocock-using-git-worktrees, mattpocock-yeet |
| `mattpocock-subagent-driven-development` | 10 | dispatching-parallel-agents, executing-plans, grilling-interview, mattpocock-to-tickets, plan, requesting-code-review, research-paper-writing, spike, systematic-debugging, test-driven-development |
| `architecture-diagram` | 9 | claude-design, design-md, diagram-design, excalidraw, hyperframes-video, popular-web-designs, pretext, sketch, system-atlas |
| `grounded-citations` | 9 | blocked-page-recovery, general-research-rounds, literature-review, mattpocock-research, parallel-cli, pubmed-database, reddit-reading, rss-feeds, scholar-evaluation |
| `plan` | 9 | brainstorming, executing-plans, hermes-agent-skill-authoring, requesting-code-review, research-paper-writing, simplify-code, spike, systematic-debugging, test-driven-development |
| `mattpocock-code-review` | 8 | mattpocock-diagnosing-bugs, mattpocock-evidence-driven, mattpocock-security-review, mattpocock-spec-driven-development, mattpocock-subagent-driven-development, mattpocock-tdd, mattpocock-to-tickets, receiving-code-review |
| `mattpocock-security-review` | 8 | application-threat-model, failure-signal-audit, mattpocock-code-review, mattpocock-evidence-driven, mattpocock-spec-driven-development, rest-api-client, security-audit, semgrep-rule-creator |
| `arxiv` | 7 | grounded-citations, literature-review, llm-wiki, mattpocock-research, pubmed-database, qmd, research-paper-writing |
| `github-auth` | 7 | github-code-review, github-issues, github-pr-workflow, github-repo-management, mattpocock-gh-fix-ci, mattpocock-yeet, wizard |
| `grilling-interview` | 7 | brainstorming, conversation-to-spec, issue-triage-state-machine, mental-models, one-three-one-rule, skill-flow-router, wayfinder-map-planning |
| `mattpocock-domain-modeling` | 7 | issue-triage-state-machine, living-docs-governance, mattpocock-codebase-design, mattpocock-handoff, mattpocock-spec-driven-development, mattpocock-to-tickets, mattpocock-writing-for-agents |
| `verification-culture` | 7 | autonomous-loop-design, bit-identity-float-pipelines, failure-signal-audit, incident-response, modular-monolith-migration, retro, verification-before-completion |
| `docx` | 6 | document-to-action-items, ocr-and-documents, pdf, powerpoint, website-audit, xlsx |
| `github-code-review` | 6 | agent-oss-contributions, github-auth, github-pr-workflow, mattpocock-code-review, receiving-code-review, requesting-code-review |
| `manim-video` | 6 | ascii-video, hyperframes-video, p5js, pygame, remotion-video, touchdesigner-mcp |
| `mattpocock-codebase-design` | 6 | architecture-metrics, codebase-onboarding, mattpocock-domain-modeling, mattpocock-spec-driven-development, modular-monolith-migration, ponytail |
| `ocr-and-documents` | 6 | arxiv, document-to-action-items, general-research-rounds, grounded-citations, nano-pdf, pdf |
| `pdf` | 6 | document-to-action-items, docx, nano-pdf, ocr-and-documents, powerpoint, xlsx |
| `popular-web-designs` | 6 | claude-design, design-md, frontend-design, redesign-existing-projects, sketch, ui-ux-pro-max |
| `ascii-video` | 5 | hyperframes-video, manim-video, p5js, pretext, touchdesigner-mcp |
| `astro-toolkit-selection` | 5 | astro-library-notes, economicspace-pipeline, optimization-modeling-pyomo, rust-crate-picks, space-data-pipelines |
| `design-md` | 5 | claude-design, popular-web-designs, react-ecosystem, stitch, ui-ux-pro-max |
| `evolutionary-ml` | 5 | algorithms-python-catalog, experiment-design, ml-cv-library-notes, model-export-deploy, test-infra-ml |
| `github-issues` | 5 | agent-oss-contributions, github-auth, github-issue-to-pr, github-repo-management, mattpocock-to-tickets |
| `google-workspace` | 5 | box, email-inbox-triage, himalaya, meeting-action-items, weekly-review-planning |
| `hermes-agent-skill-authoring` | 5 | cron-config-authoring, doc-coauthoring, hermes-extensions, mattpocock-code-review, mattpocock-writing-for-agents |
| `mattpocock-tdd` | 5 | mattpocock-code-review, mattpocock-codebase-design, mattpocock-diagnosing-bugs, mattpocock-evidence-driven, mattpocock-spec-driven-development |
| `mattpocock-to-tickets` | 5 | mattpocock-handoff, mattpocock-spec-driven-development, mattpocock-subagent-driven-development, skill-flow-router, wayfinder-map-planning |
| `mattpocock-writing-for-agents` | 5 | doc-coauthoring, mattpocock-ask-if-underspecified, mattpocock-domain-modeling, mattpocock-handoff, retro |
| `notion` | 5 | airtable, document-to-action-items, meeting-action-items, obsidian, weekly-review-planning |
| `obsidian` | 5 | apple-notes, knowledge-ops, llm-wiki, qmd, weekly-review-planning |
| `python-numerics-gotchas` | 5 | experiment-design, ml-cv-library-notes, polars-pipelines, python-plotting, z3-solver |
| `react-ecosystem` | 5 | browser-automation, frontend-library-picks, js-tooling-notes, react-library-notes, remotion-video |
| `sql-for-data` | 5 | duckdb-querying, polars-pipelines, python-numerics-gotchas, sqlite-queries, system-design-scaling |
| `system-design-scaling` | 5 | algorithms-python-catalog, application-threat-model, feature-flag-lifecycle, incident-response, modular-monolith-migration |
| `youtube-content` | 5 | ascii-video, gif-search, manim-video, rss-feeds, songsee |
| `apple-notes` | 4 | apple-reminders, findmy, imessage, obsidian |
| `bit-identity-float-pipelines` | 4 | astro-library-notes, polars-pipelines, python-numerics-gotchas, z3-solver |
| `blogwatcher` | 4 | competitor-news-monitor, rss-feeds, watchers, youtube-content |
| `codebase-onboarding` | 4 | living-docs-governance, modular-monolith-migration, repo-atlas, repowise |
| `economicspace-pipeline` | 4 | astro-library-notes, astro-toolkit-selection, optimization-modeling-pyomo, space-data-pipelines |
| `failure-signal-audit` | 4 | feature-flag-lifecycle, python-toolchain-notes, secret-vault-pattern, systematic-debugging |
| `fastmcp` | 4 | hermes-extensions, mcporter, repowise, structured-llm-outputs |
| `frontend-design` | 4 | frontend-library-picks, react-ecosystem, react-library-notes, ui-ux-pro-max |
| `huggingface-hub` | 4 | huggingface-trackio, llama-cpp, unsloth-gguf, weights-and-biases |
| `literature-review` | 4 | general-research-rounds, gget, pubmed-database, scholar-evaluation |
| `mattpocock-using-git-worktrees` | 4 | executing-plans, mattpocock-evidence-driven, mattpocock-finishing-a-development-branch, mattpocock-subagent-driven-development |
| `p5js` | 4 | hyperframes-video, manim-video, pretext, pygame |
| `parallel-cli` | 4 | blocked-page-recovery, blogwatcher, competitor-news-monitor, mattpocock-research |
| `powerpoint` | 4 | docx, ocr-and-documents, pdf, xlsx |
| `publish-site` | 4 | frontend-library-picks, js-tooling-notes, react-ecosystem, react-library-notes |
| `simplify-code` | 4 | ast-grep, dynamic-workflow, ponytail, python-craft |
| `sketch` | 4 | architecture-diagram, frontend-design, popular-web-designs, spike |
| `space-data-pipelines` | 4 | astro-library-notes, cron-pipeline-watchdog, duckdb-querying, polars-pipelines |
| `ssh-remote` | 4 | docker-containers, pinggy-tunnel, rest-api-client, wizard |
| `static-site-patterns` | 4 | frontend-library-picks, js-tooling-notes, publish-site, react-ecosystem |
| `weights-and-biases` | 4 | evaluating-llms-harness, evolutionary-ml, python-data-science, serving-llms-vllm |
| `xlsx` | 4 | docx, pdf, powerpoint, sql-for-data |
| `apple-reminders` | 3 | apple-notes, findmy, imessage |
| `architecture-metrics` | 3 | mattpocock-codebase-design, modular-monolith-migration, repowise |
| `awwwards-gsap-motion` | 3 | design-taste-frontend, hyperframes-video, remotion-video |
| `blocked-page-recovery` | 3 | general-research-rounds, reddit-reading, scrapling |
| `claude-code` | 3 | codex, hermes-agent, opencode |
| `codex` | 3 | claude-code, hermes-agent, opencode |
| `comfyui` | 3 | baoyu-infographic, songsee, songwriting-and-ai-music |
| `conversation-to-spec` | 3 | brainstorming, grilling-interview, skill-flow-router |
| `cron-pipeline-watchdog` | 3 | autonomous-loop-design, incident-response, space-data-pipelines |
| `dogfood` | 3 | adversarial-ux-test, browser-automation, inspecting-hermes-desktop-dom |
| `findmy` | 3 | apple-reminders, imessage, maps |
| `github-repo-management` | 3 | code-wiki, codebase-inspection, github-auth |
| `huggingface-trackio` | 3 | huggingface-hub, python-data-science, weights-and-biases |
| `llama-cpp` | 3 | huggingface-hub, serving-llms-vllm, unsloth-gguf |
| `mattpocock-diagnosing-bugs` | 3 | mattpocock-gh-fix-ci, mattpocock-resolving-merge-conflicts, mattpocock-tdd |
| `mattpocock-evidence-driven` | 3 | mattpocock-diagnosing-bugs, mattpocock-subagent-driven-development, verification-before-completion |
| `mattpocock-finishing-a-development-branch` | 3 | executing-plans, mattpocock-subagent-driven-development, mattpocock-using-git-worktrees |
| `mattpocock-handoff` | 3 | mattpocock-ask-if-underspecified, mattpocock-to-tickets, mattpocock-writing-for-agents |
| `mattpocock-yeet` | 3 | agent-oss-contributions, mattpocock-finishing-a-development-branch, mattpocock-using-git-worktrees |
| `mcporter` | 3 | fastmcp, hermes-extensions, repowise |
| `meeting-action-items` | 3 | decision-questionnaire, document-to-action-items, teams-meeting-pipeline |
| `optimization-modeling-pyomo` | 3 | algorithms-python-catalog, astro-toolkit-selection, z3-solver |
| `orbital-mechanics-data` | 3 | astro-library-notes, astro-toolkit-selection, space-data-pipelines |
| `repowise` | 3 | architecture-metrics, fastmcp, repo-atlas |
| `rest-api-client` | 3 | rest-graphql-debug, secret-vault-pattern, system-design-scaling |
| `security-audit` | 3 | application-threat-model, mattpocock-security-review, secret-vault-pattern |
| `serving-llms-vllm` | 3 | llama-cpp, unsloth-gguf, weights-and-biases |
| `static-site-seo` | 3 | frontend-library-picks, publish-site, static-site-patterns |
| `test-infra-ml` | 3 | ml-cv-library-notes, property-based-testing, verification-culture |
| `airtable` | 2 | notion, weekly-review-planning |
| `algorithms-python-catalog` | 2 | maps, rust-crate-picks |
| `application-threat-model` | 2 | mattpocock-security-review, secret-vault-pattern |
| `ascii-art` | 2 | ascii-video, pretext |
| `code-wiki` | 2 | codebase-onboarding, repo-atlas |
| `competitor-news-monitor` | 2 | blogwatcher, rss-feeds |
| `cron-config-authoring` | 2 | autonomous-loop-design, cron-job-authoring |
| `decision-questionnaire` | 2 | mental-models, one-three-one-rule |
| `docker-containers` | 2 | rest-api-client, ssh-remote |
| `document-to-action-items` | 2 | decision-questionnaire, meeting-action-items |
| `duckdb-querying` | 2 | polars-pipelines, python-numerics-gotchas |
| `dynamic-workflow` | 2 | autonomous-loop-design, dispatching-parallel-agents |
| `email-inbox-triage` | 2 | himalaya, weekly-review-planning |
| `experiment-design` | 2 | autonomous-loop-design, feature-flag-lifecycle |
| `frontend-library-picks` | 2 | js-tooling-notes, react-library-notes |
| `har-derived-api-client` | 2 | browser-automation, static-site-patterns |
| `himalaya` | 2 | email-inbox-triage, google-workspace |
| `humanizer` | 2 | no-ai-slop, songwriting-and-ai-music |
| `hyperframes-video` | 2 | manim-video, remotion-video |
| `imessage` | 2 | apple-reminders, findmy |
| `inspecting-hermes-desktop-dom` | 2 | computer-use, hermes-extensions |
| `maps` | 2 | algorithms-python-catalog, product-price-monitor |
| `mattpocock-gh-fix-ci` | 2 | mattpocock-spec-driven-development, mattpocock-yeet |
| `mattpocock-research` | 2 | literature-review, scholar-evaluation |
| `mattpocock-spec-driven-development` | 2 | conversation-to-spec, mattpocock-to-tickets |
| `model-export-deploy` | 2 | ml-cv-library-notes, unsloth-gguf |
| `nicegui-app-builder` | 2 | python-plotting, react-ecosystem |
| `no-ai-slop` | 2 | humanizer, ui-ux-pro-max |
| `node-inspect-debugger` | 2 | inspecting-hermes-desktop-dom, python-debugpy |
| `opencode` | 2 | claude-code, hermes-agent |
| `ponytail` | 2 | rust-crate-picks, simplify-code |
| `pubmed-database` | 2 | bioinformatics, gget |
| `python-debugpy` | 2 | node-inspect-debugger, python-toolchain-notes |
| `redesign-existing-projects` | 2 | design-taste-frontend, full-output-enforcement |
| `rest-graphql-debug` | 2 | har-derived-api-client, rest-api-client |
| `rss-feeds` | 2 | reddit-reading, watchers |
| `scrapling` | 2 | algorithms-python-catalog, browser-automation |
| `semgrep-rule-creator` | 2 | oss-forensics, security-audit |
| `songwriting-and-ai-music` | 2 | humanizer, no-ai-slop |
| `spike` | 2 | brainstorming, sketch |
| `streamlit-dashboards` | 2 | nicegui-app-builder, python-plotting |
| `wayfinder-map-planning` | 2 | grilling-interview, skill-flow-router |

## Standalone Skills

No skill is fully standalone: every skill either lists `related_skills` or is referenced by another skill.

## Related Skills Validation

All 677 `related_skills` references in the repository resolve to existing in-repo skills. Verified against 229 unique skill names.

---
