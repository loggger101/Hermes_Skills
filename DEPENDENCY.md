# Skill Dependency Map

This document maps the relationship network between all **253 Hermes skills** in this repository. It is generated from the `related_skills` field in each skill's frontmatter.

**Network stats:** 816 `related_skills` cross-references across 253 skills (2 skills list no `related_skills` of their own).

## Hub Skills (referenced by 2+ other skills)

These are the core skills that serve as building blocks, referenced by many other skills:

| Skill | Referenced By (count) | Referencing Skills |
|-------|-----------------------|---------------------|
| `test-driven-development` | 20 | dispatching-parallel-agents, executing-plans, generating-python-installer, github-issue-to-pr, grilling-interview, mattpocock-subagent-driven-development, mattpocock-tdd, plan, property-based-testing, python-craft, python-data-science, python-toolchain-notes, requesting-code-review, rest-graphql-debug, simplify-code, skill-flow-router, structured-llm-outputs, systematic-debugging, test-infra-ml, windows-desktop-e2e |
| `python-craft` | 19 | algorithms-python-catalog, build-systems-data, cli-tool-craft, evolutionary-ml, generating-python-installer, model-export-deploy, orbital-mechanics-data, ponytail, python-numerics-gotchas, python-toolchain-notes, rust-crate-picks, static-site-seo, streamlit-dashboards, structured-llm-outputs, system-design-interview-patterns, system-design-scaling, test-infra-ml, verification-culture, windows-agent-shell |
| `requesting-code-review` | 19 | architecture-metrics, codex, github-issue-to-pr, grilling-interview, hermes-agent-skill-authoring, mattpocock-code-review, mattpocock-evidence-driven, mattpocock-finishing-a-development-branch, mattpocock-security-review, mattpocock-spec-driven-development, mattpocock-subagent-driven-development, plan, ponytail, python-craft, receiving-code-review, sdlc-review, semgrep-rule-creator, simplify-code, skill-flow-router |
| `systematic-debugging` | 19 | ast-grep, dispatching-parallel-agents, failure-signal-audit, git-on-sync-clients, github-issue-to-pr, inspecting-hermes-desktop-dom, mattpocock-diagnosing-bugs, mattpocock-gh-fix-ci, mattpocock-resolving-merge-conflicts, mattpocock-tdd, node-inspect-debugger, python-craft, python-data-science, python-debugpy, python-toolchain-notes, rest-graphql-debug, skill-flow-router, test-driven-development, windows-agent-shell |
| `hermes-agent` | 16 | apple-reminders, claude-code, codex, context-budget-planning, cron-job-authoring, cross-harness-skill-porting, dynamic-workflow, hermes-bot-cloning, hermes-extensions, hermes-integrations, mattpocock-to-tickets, merge-reconciler, opencode, qmd, repowise, unsloth-gguf |
| `github-pr-workflow` | 14 | agent-oss-contributions, ci-gate-design, feature-flag-lifecycle, git-on-sync-clients, github-auth, github-code-review, github-issue-to-pr, github-issues, github-repo-management, mattpocock-finishing-a-development-branch, mattpocock-gh-fix-ci, mattpocock-using-git-worktrees, mattpocock-yeet, skill-intake-and-release |
| `python-data-science` | 14 | build-systems-data, evolutionary-ml, experiment-design, gget, huggingface-trackio, jupyter-notebook, ml-cv-library-notes, orbital-mechanics-data, polars-pipelines, python-numerics-gotchas, python-plotting, regex-vs-llm-structured-text, research-paper-writing, sql-for-data |
| `cron-job-authoring` | 13 | apple-reminders, autonomous-loop-design, context-budget-planning, cron-config-authoring, cron-pipeline-watchdog, experiment-design, findmy, hermes-bot-cloning, mattpocock-using-git-worktrees, mattpocock-yeet, product-price-monitor, secret-vault-pattern, watchers |
| `claude-design` | 12 | awwwards-gsap-motion, design-md, editorial-minimalism-ui, frontend-design, industrial-brutalist-ui, popular-web-designs, pretext, sketch, soft-premium-ui, songwriting-and-ai-music, stitch, teach |
| `design-taste-frontend` | 12 | awwwards-gsap-motion, editorial-minimalism-ui, frontend-library-picks, full-output-enforcement, industrial-brutalist-ui, react-library-notes, redesign-existing-projects, soft-premium-ui, static-site-patterns, stitch, ui-ux-pro-max, web-perf-audit |
| `grounded-citations` | 12 | ai-research-integrity, ai-search-optimization, blocked-page-recovery, general-research-rounds, literature-review, mattpocock-research, paper-citation-workflow, parallel-cli, pubmed-database, reddit-reading, rss-feeds, scholar-evaluation |
| `excalidraw` | 11 | architecture-diagram, ascii-art, claude-design, design-md, diagram-design, p5js, popular-web-designs, pretext, research-paper-writing, sketch, system-atlas |
| `mattpocock-subagent-driven-development` | 10 | dispatching-parallel-agents, executing-plans, grilling-interview, mattpocock-to-tickets, plan, requesting-code-review, research-paper-writing, spike, systematic-debugging, test-driven-development |
| `verification-culture` | 10 | autonomous-loop-design, bit-identity-float-pipelines, ci-gate-design, failure-signal-audit, incident-response, modular-monolith-migration, one-authority-per-fact, pinned-data-contracts, retro, verification-before-completion |
| `architecture-diagram` | 9 | claude-design, design-md, diagram-design, excalidraw, hyperframes-video, popular-web-designs, pretext, sketch, system-atlas |
| `plan` | 9 | brainstorming, executing-plans, hermes-agent-skill-authoring, requesting-code-review, research-paper-writing, simplify-code, spike, systematic-debugging, test-driven-development |
| `arxiv` | 8 | grounded-citations, literature-review, llm-wiki, mattpocock-research, paper-citation-workflow, pubmed-database, qmd, research-paper-writing |
| `grilling-interview` | 8 | brainstorming, conversation-to-spec, issue-triage-state-machine, mental-models, multi-agent-deliberation, one-three-one-rule, skill-flow-router, wayfinder-map-planning |
| `hermes-agent-skill-authoring` | 8 | cron-config-authoring, cross-harness-skill-porting, doc-coauthoring, hermes-extensions, mattpocock-code-review, mattpocock-writing-for-agents, skill-intake-and-release, skill-library-audits |
| `mattpocock-code-review` | 8 | mattpocock-diagnosing-bugs, mattpocock-evidence-driven, mattpocock-security-review, mattpocock-spec-driven-development, mattpocock-subagent-driven-development, mattpocock-tdd, mattpocock-to-tickets, receiving-code-review |
| `mattpocock-security-review` | 8 | application-threat-model, failure-signal-audit, mattpocock-code-review, mattpocock-evidence-driven, mattpocock-spec-driven-development, rest-api-client, security-audit, semgrep-rule-creator |
| `space-data-pipelines` | 8 | astro-library-notes, cron-pipeline-watchdog, duckdb-querying, enricher-pipeline-architecture, lunar-gis-projections, open-data-catalog-sources, pinned-data-contracts, polars-pipelines |
| `github-auth` | 7 | github-code-review, github-issues, github-pr-workflow, github-repo-management, mattpocock-gh-fix-ci, mattpocock-yeet, wizard |
| `mattpocock-domain-modeling` | 7 | issue-triage-state-machine, living-docs-governance, mattpocock-codebase-design, mattpocock-handoff, mattpocock-spec-driven-development, mattpocock-to-tickets, mattpocock-writing-for-agents |
| `research-paper-writing` | 7 | ai-research-integrity, autoreason-refinement, conference-review-criteria, grounded-citations, human-evaluation-design, ml-experiment-patterns, paper-citation-workflow |
| `astro-toolkit-selection` | 6 | astro-library-notes, economicspace-pipeline, lunar-gis-projections, optimization-modeling-pyomo, rust-crate-picks, space-data-pipelines |
| `bit-identity-float-pipelines` | 6 | astro-library-notes, one-authority-per-fact, pinned-data-contracts, polars-pipelines, python-numerics-gotchas, z3-solver |
| `docx` | 6 | document-to-action-items, ocr-and-documents, pdf, powerpoint, website-audit, xlsx |
| `economicspace-pipeline` | 6 | astro-library-notes, astro-toolkit-selection, open-data-catalog-sources, optimization-modeling-pyomo, pinned-data-contracts, space-data-pipelines |
| `failure-signal-audit` | 6 | ci-gate-design, feature-flag-lifecycle, one-authority-per-fact, python-toolchain-notes, secret-vault-pattern, systematic-debugging |
| `github-code-review` | 6 | agent-oss-contributions, github-auth, github-pr-workflow, mattpocock-code-review, receiving-code-review, requesting-code-review |
| `manim-video` | 6 | ascii-video, hyperframes-video, p5js, pygame, remotion-video, touchdesigner-mcp |
| `mattpocock-codebase-design` | 6 | architecture-metrics, codebase-onboarding, mattpocock-domain-modeling, mattpocock-spec-driven-development, modular-monolith-migration, ponytail |
| `mattpocock-writing-for-agents` | 6 | doc-coauthoring, mattpocock-ask-if-underspecified, mattpocock-domain-modeling, mattpocock-handoff, repo-agent-instructions, retro |
| `ocr-and-documents` | 6 | arxiv, document-to-action-items, general-research-rounds, grounded-citations, nano-pdf, pdf |
| `pdf` | 6 | document-to-action-items, docx, nano-pdf, ocr-and-documents, powerpoint, xlsx |
| `popular-web-designs` | 6 | claude-design, design-md, frontend-design, redesign-existing-projects, sketch, ui-ux-pro-max |
| `sql-for-data` | 6 | duckdb-querying, polars-pipelines, python-numerics-gotchas, sqlite-queries, system-design-interview-patterns, system-design-scaling |
| `static-site-patterns` | 6 | ai-search-optimization, frontend-library-picks, js-tooling-notes, publish-site, react-ecosystem, web-perf-audit |
| `system-design-scaling` | 6 | algorithms-python-catalog, application-threat-model, feature-flag-lifecycle, incident-response, modular-monolith-migration, system-design-interview-patterns |
| `ai-research-integrity` | 5 | autoreason-refinement, conference-review-criteria, human-evaluation-design, paper-citation-workflow, research-paper-writing |
| `ascii-video` | 5 | hyperframes-video, manim-video, p5js, pretext, touchdesigner-mcp |
| `codebase-onboarding` | 5 | living-docs-governance, modular-monolith-migration, repo-agent-instructions, repo-atlas, repowise |
| `design-md` | 5 | claude-design, popular-web-designs, react-ecosystem, stitch, ui-ux-pro-max |
| `evolutionary-ml` | 5 | algorithms-python-catalog, experiment-design, ml-cv-library-notes, model-export-deploy, test-infra-ml |
| `fastmcp` | 5 | hermes-extensions, hermes-integrations, mcporter, repowise, structured-llm-outputs |
| `github-issues` | 5 | agent-oss-contributions, github-auth, github-issue-to-pr, github-repo-management, mattpocock-to-tickets |
| `google-workspace` | 5 | box, email-inbox-triage, himalaya, meeting-action-items, weekly-review-planning |
| `huggingface-hub` | 5 | huggingface-trackio, llama-cpp, open-data-catalog-sources, unsloth-gguf, weights-and-biases |
| `literature-review` | 5 | general-research-rounds, gget, paper-citation-workflow, pubmed-database, scholar-evaluation |
| `mattpocock-tdd` | 5 | mattpocock-code-review, mattpocock-codebase-design, mattpocock-diagnosing-bugs, mattpocock-evidence-driven, mattpocock-spec-driven-development |
| `mattpocock-to-tickets` | 5 | mattpocock-handoff, mattpocock-spec-driven-development, mattpocock-subagent-driven-development, skill-flow-router, wayfinder-map-planning |
| `notion` | 5 | airtable, document-to-action-items, meeting-action-items, obsidian, weekly-review-planning |
| `obsidian` | 5 | apple-notes, knowledge-ops, llm-wiki, qmd, weekly-review-planning |
| `orbital-mechanics-data` | 5 | astro-library-notes, astro-toolkit-selection, lunar-gis-projections, open-data-catalog-sources, space-data-pipelines |
| `publish-site` | 5 | ai-search-optimization, frontend-library-picks, js-tooling-notes, react-ecosystem, react-library-notes |
| `python-numerics-gotchas` | 5 | experiment-design, ml-cv-library-notes, polars-pipelines, python-plotting, z3-solver |
| `react-ecosystem` | 5 | browser-automation, frontend-library-picks, js-tooling-notes, react-library-notes, remotion-video |
| `static-site-seo` | 5 | ai-search-optimization, frontend-library-picks, publish-site, static-site-patterns, web-perf-audit |
| `youtube-content` | 5 | ascii-video, gif-search, manim-video, rss-feeds, songsee |
| `apple-notes` | 4 | apple-reminders, findmy, imessage, obsidian |
| `blogwatcher` | 4 | competitor-news-monitor, rss-feeds, watchers, youtube-content |
| `ci-gate-design` | 4 | one-authority-per-fact, pinned-data-contracts, skill-intake-and-release, skill-library-audits |
| `cron-pipeline-watchdog` | 4 | autonomous-loop-design, enricher-pipeline-architecture, incident-response, space-data-pipelines |
| `dispatching-parallel-agents` | 4 | autoreason-refinement, context-budget-planning, mattpocock-subagent-driven-development, multi-agent-deliberation |
| `dogfood` | 4 | adversarial-ux-test, browser-automation, inspecting-hermes-desktop-dom, web-perf-audit |
| `experiment-design` | 4 | autonomous-loop-design, feature-flag-lifecycle, human-evaluation-design, ml-experiment-patterns |
| `frontend-design` | 4 | frontend-library-picks, react-ecosystem, react-library-notes, ui-ux-pro-max |
| `github-repo-management` | 4 | code-wiki, codebase-inspection, git-on-sync-clients, github-auth |
| `human-evaluation-design` | 4 | ai-research-integrity, conference-review-criteria, ml-experiment-patterns, research-paper-writing |
| `living-docs-governance` | 4 | one-authority-per-fact, repo-agent-instructions, repo-atlas, skill-library-audits |
| `mattpocock-using-git-worktrees` | 4 | executing-plans, mattpocock-evidence-driven, mattpocock-finishing-a-development-branch, mattpocock-subagent-driven-development |
| `mcporter` | 4 | fastmcp, hermes-extensions, hermes-integrations, repowise |
| `p5js` | 4 | hyperframes-video, manim-video, pretext, pygame |
| `parallel-cli` | 4 | blocked-page-recovery, blogwatcher, competitor-news-monitor, mattpocock-research |
| `powerpoint` | 4 | docx, ocr-and-documents, pdf, xlsx |
| `rest-api-client` | 4 | enricher-pipeline-architecture, rest-graphql-debug, secret-vault-pattern, system-design-scaling |
| `security-audit` | 4 | application-threat-model, mattpocock-security-review, secret-vault-pattern, skill-intake-and-release |
| `simplify-code` | 4 | ast-grep, dynamic-workflow, ponytail, python-craft |
| `sketch` | 4 | architecture-diagram, frontend-design, popular-web-designs, spike |
| `ssh-remote` | 4 | docker-containers, pinggy-tunnel, rest-api-client, wizard |
| `verification-before-completion` | 4 | ci-gate-design, git-on-sync-clients, structured-llm-outputs, windows-agent-shell |
| `weights-and-biases` | 4 | evaluating-llms-harness, evolutionary-ml, python-data-science, serving-llms-vllm |
| `xlsx` | 4 | docx, pdf, powerpoint, sql-for-data |
| `apple-reminders` | 3 | apple-notes, findmy, imessage |
| `architecture-metrics` | 3 | mattpocock-codebase-design, modular-monolith-migration, repowise |
| `autoreason-refinement` | 3 | ai-research-integrity, ml-experiment-patterns, research-paper-writing |
| `awwwards-gsap-motion` | 3 | design-taste-frontend, hyperframes-video, remotion-video |
| `blocked-page-recovery` | 3 | general-research-rounds, reddit-reading, scrapling |
| `claude-code` | 3 | codex, hermes-agent, opencode |
| `codex` | 3 | claude-code, hermes-agent, opencode |
| `comfyui` | 3 | baoyu-infographic, songsee, songwriting-and-ai-music |
| `conversation-to-spec` | 3 | brainstorming, grilling-interview, skill-flow-router |
| `decision-questionnaire` | 3 | mental-models, multi-agent-deliberation, one-three-one-rule |
| `duckdb-querying` | 3 | open-data-catalog-sources, polars-pipelines, python-numerics-gotchas |
| `findmy` | 3 | apple-reminders, imessage, maps |
| `frontend-library-picks` | 3 | js-tooling-notes, react-library-notes, web-perf-audit |
| `huggingface-trackio` | 3 | huggingface-hub, python-data-science, weights-and-biases |
| `llama-cpp` | 3 | huggingface-hub, serving-llms-vllm, unsloth-gguf |
| `mattpocock-diagnosing-bugs` | 3 | mattpocock-gh-fix-ci, mattpocock-resolving-merge-conflicts, mattpocock-tdd |
| `mattpocock-evidence-driven` | 3 | mattpocock-diagnosing-bugs, mattpocock-subagent-driven-development, verification-before-completion |
| `mattpocock-finishing-a-development-branch` | 3 | executing-plans, mattpocock-subagent-driven-development, mattpocock-using-git-worktrees |
| `mattpocock-handoff` | 3 | mattpocock-ask-if-underspecified, mattpocock-to-tickets, mattpocock-writing-for-agents |
| `mattpocock-yeet` | 3 | agent-oss-contributions, mattpocock-finishing-a-development-branch, mattpocock-using-git-worktrees |
| `meeting-action-items` | 3 | decision-questionnaire, document-to-action-items, teams-meeting-pipeline |
| `one-authority-per-fact` | 3 | ci-gate-design, pinned-data-contracts, repo-agent-instructions |
| `optimization-modeling-pyomo` | 3 | algorithms-python-catalog, astro-toolkit-selection, z3-solver |
| `repowise` | 3 | architecture-metrics, fastmcp, repo-atlas |
| `scholar-evaluation` | 3 | ai-research-integrity, conference-review-criteria, human-evaluation-design |
| `serving-llms-vllm` | 3 | llama-cpp, unsloth-gguf, weights-and-biases |
| `skill-intake-and-release` | 3 | cross-harness-skill-porting, hermes-agent-skill-authoring, skill-library-audits |
| `test-infra-ml` | 3 | ml-cv-library-notes, property-based-testing, verification-culture |
| `website-audit` | 3 | ai-search-optimization, experiment-design, web-perf-audit |
| `airtable` | 2 | notion, weekly-review-planning |
| `algorithms-python-catalog` | 2 | maps, rust-crate-picks |
| `application-threat-model` | 2 | mattpocock-security-review, secret-vault-pattern |
| `ascii-art` | 2 | ascii-video, pretext |
| `brainstorming` | 2 | multi-agent-deliberation, ponytail |
| `code-wiki` | 2 | codebase-onboarding, repo-atlas |
| `competitor-news-monitor` | 2 | blogwatcher, rss-feeds |
| `cron-config-authoring` | 2 | autonomous-loop-design, cron-job-authoring |
| `cross-harness-skill-porting` | 2 | enricher-pipeline-architecture, hermes-agent |
| `docker-containers` | 2 | rest-api-client, ssh-remote |
| `document-to-action-items` | 2 | decision-questionnaire, meeting-action-items |
| `dynamic-workflow` | 2 | autonomous-loop-design, dispatching-parallel-agents |
| `email-inbox-triage` | 2 | himalaya, weekly-review-planning |
| `enricher-pipeline-architecture` | 2 | cross-harness-skill-porting, space-data-pipelines |
| `har-derived-api-client` | 2 | browser-automation, static-site-patterns |
| `hermes-extensions` | 2 | cross-harness-skill-porting, hermes-integrations |
| `hermes-integrations` | 2 | context-budget-planning, hermes-agent |
| `himalaya` | 2 | email-inbox-triage, google-workspace |
| `humanizer` | 2 | no-ai-slop, songwriting-and-ai-music |
| `hyperframes-video` | 2 | manim-video, remotion-video |
| `imessage` | 2 | apple-reminders, findmy |
| `inspecting-hermes-desktop-dom` | 2 | computer-use, hermes-extensions |
| `maps` | 2 | algorithms-python-catalog, product-price-monitor |
| `mattpocock-gh-fix-ci` | 2 | mattpocock-spec-driven-development, mattpocock-yeet |
| `mattpocock-research` | 2 | literature-review, scholar-evaluation |
| `mattpocock-spec-driven-development` | 2 | conversation-to-spec, mattpocock-to-tickets |
| `mental-models` | 2 | multi-agent-deliberation, one-three-one-rule |
| `model-export-deploy` | 2 | ml-cv-library-notes, unsloth-gguf |
| `multi-agent-deliberation` | 2 | autoreason-refinement, skill-library-audits |
| `nicegui-app-builder` | 2 | python-plotting, react-ecosystem |
| `no-ai-slop` | 2 | humanizer, ui-ux-pro-max |
| `node-inspect-debugger` | 2 | inspecting-hermes-desktop-dom, python-debugpy |
| `one-three-one-rule` | 2 | mental-models, multi-agent-deliberation |
| `open-data-catalog-sources` | 2 | lunar-gis-projections, space-data-pipelines |
| `opencode` | 2 | claude-code, hermes-agent |
| `pinned-data-contracts` | 2 | ci-gate-design, open-data-catalog-sources |
| `ponytail` | 2 | rust-crate-picks, simplify-code |
| `pubmed-database` | 2 | bioinformatics, gget |
| `python-debugpy` | 2 | node-inspect-debugger, python-toolchain-notes |
| `python-plotting` | 2 | ml-experiment-patterns, python-numerics-gotchas |
| `redesign-existing-projects` | 2 | design-taste-frontend, full-output-enforcement |
| `repo-atlas` | 2 | one-authority-per-fact, repo-agent-instructions |
| `rest-graphql-debug` | 2 | har-derived-api-client, rest-api-client |
| `rss-feeds` | 2 | reddit-reading, watchers |
| `scrapling` | 2 | algorithms-python-catalog, browser-automation |
| `secret-vault-pattern` | 2 | hermes-integrations, skill-intake-and-release |
| `semgrep-rule-creator` | 2 | oss-forensics, security-audit |
| `skill-library-audits` | 2 | hermes-agent-skill-authoring, skill-intake-and-release |
| `songwriting-and-ai-music` | 2 | humanizer, no-ai-slop |
| `spike` | 2 | brainstorming, sketch |
| `streamlit-dashboards` | 2 | nicegui-app-builder, python-plotting |
| `wayfinder-map-planning` | 2 | grilling-interview, skill-flow-router |
| `windows-desktop-e2e` | 2 | browser-automation, windows-agent-shell |

## Standalone Skills

No skill is fully standalone: every skill either lists `related_skills` or is referenced by another skill.

## Related Skills Validation

All 816 `related_skills` references in the repository resolve to existing in-repo skills. Verified against 253 unique skill names.

---
