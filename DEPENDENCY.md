# Cross-Skill Dependency Graph

This document maps how Hermes skills reference each other. Every prose mention of another skill uses `skill_view(name='...')` so the runtime loads the referenced skill's context automatically.

> **Last updated**: August 2026 — Round 2 expansion pass added `skill_view()` routing to 24 additional skills and expanded 5 thin skills.

## Edge Types

| Symbol | Meaning |
|--------|---------|
| → | Depends on (must load first) |
| ⇒ | Composes with (used alongside for combined output) |
| ↔ | Bidirectional (mutual references, load either when needed) |

## Graph

```
                    autonomous-ai-agents
                           │
              ┌────────────┼────────────┐
              │            │            │
    ┌─────────▼──┐  ┌─────▼──┐  ┌──────▼──────┐
    │cronjob     │  │opencode │  │claude-code │
    │(preparer)  │  │(exec?) │  │(PR/agent) │
    └────┬───────┘  └─────┬──┘  └──────┬──────┘
         │                  │            │
         ▼                  │            │
┌──────────────────────────────────────────────────┐
│ autonomous-repo-cronjob → github-issues           │
│ (prepares JSON)       → github-pr-workflow       │
│                       → github-auth              │
│                       → ocr-and-documents        │
│                       → arxiv                    │
│                       → skill_view(mattpocock-   │
│                         subagent-driven-         │
│                         development)              │
└──────────────────────────────────────────────────┘
         │
         ▼
    github-pr-workflow → github-auth
         │              → github-code-review
         ▼              → requesting-code-review
    github-code-review → github-auth
         │              → skill_view(mattpocock-
         │                code-review)
         ▼
    requesting-code-review
         │
         ▼
    mattpocock-evidence-driven
         │  → mattpocock-tdd
         │  → mattpocock-security-review
         │  → requesting-code-review
         │  → mattpocock-code-review
         ▼
    mattpocock-spec-driven-development
         │  → mattpocock-to-tickets
         │  → mattpocock-codebase-design
         │  → mattpocock-tdd
         │  → requesting-code-review
         │  → mattpocock-gh-fix-ci
         ▼
    systematic-debugging
         │  → mattpocock-diagnosing-bugs
         │  → test-driven-development
         ▼
    test-driven-development
         │  → mattpocock-ask-if-underspecified
         │  → mattpocock-handoff
         ▼
    [leaf implementation]

                    devops
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼──┐  ┌─────▼────┐  ┌─────▼──────┐
    │docker │  │ssh-remote│  │rest-api-   │
    │-       │  │          │  │client      │
    │containers│ (for     │  │            │
    │         │ remote) │  │            │
    └────┬────┘  └─────┬────┘  └─────┬──────┘
         │             │              │
         │             │              │
         ▼             ▼              ▼
    (references    (SSH to        (REST APIs)
     ssh-remote)    remote host)

                    research
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼──┐  ┌─────▼────┐  ┌─────▼─────┐
    │arxiv  │  │grounded- │  │llm-wiki   │
    │       │  │citations │ │           │
    └────┬──┘  └─────┬────┘ └─────┬─────┘
         │           │             │
         ▼           │             │
    ocr-and-         │             │
    documents        │             │
         │           │             │
         │           │             │
         └───────────┼─────────────┘
                     │
                     ▼
              research-paper-
              writing
                    │
                    ▼
              (references/ dir)

                    productivity
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼──┐  ┌─────▼────┐  ┌─────▼─────┐
    │ocr-   │  │document- │  │weekly-  │
    │and-   │  │to-action │  │review   │
    │documents│  items     │  planning │
    └────┬──┘  └──────┬──┘  └──────┬──┘
         │            │            │
         ▼            ▼            ▼
    pdf,docx,      ocr-and-     obsidian,
    powerpoint      documents    notion,
                    │            │
                    ▼            ▼
              google-workspace  email-inbox-
                    │            triage
                    ▼            │
              gmail search      ▼
              syntax ref     himalaya
                    │
                    ▼
                  (external)

                    creative
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼──┐  ┌─────▼────┐  ┌─────▼──────┐
    │claude-│  │sketch    │  │design-md   │
    │design │  │          │  │            │
    └────┬──┘  └─────┬────┘  └─────┬──────┘
         │           │             │
         │  ┌────────┘             │
         │  │                      │
         ▼  ▼                      ▼
    popular-web-designs    architecture-
                           diagram

                    security
                       │
    ┌─────────────┬──▼──┐
    │             │     │
    │             │    │
    ▼             ▼    ▼
  mattpocock-   openai  (static
  security-    security-  analysis)
  review       best-
               practices

                    software-development
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
    │                  │                  │
    ▼                  ▼                  ▼
  mattpocock-   test-             requesting-
  spec-driven    driven-           code-
  development    development       review
                 │                    │
                 ▼                    │
            mattpocock-               │
            diagnosing-bugs           │
                 │                    │
                 ▼                    │
            systematic-              │
            debugging                │
                 │                   │
                 └────────┬──────────┘
                          │
                          ▼
                   mattpocock-evidence-
                   driven
```

## Dependency Edges (machine-readable)

### Tier 1: GitHub Core Cluster (7 skills)
```
github/github-auth → (external: OAuth/device flow)
github/github-repo-management → skill_view(name='github-auth')
github/github-issues → skill_view(name='github-auth')
github/github-pr-workflow → skill_view(name='github-auth')
github/github-code-review → skill_view(name='github-auth'), skill_view(name='mattpocock-code-review')
github/github-issue-to-pr → skill_view(name='github-auth'), skill_view(name='requesting-code-review')
                          → skill_view(name='mattpocock-gh-fix-ci'), skill_view(name='github-pr-workflow')
github/mattpocock-gh-fix-ci → skill_view(name='github-auth'), skill_view(name='systematic-debugging')
```

### Tier 2: Evidence-Driven Validation (5 skills)
```
mattpocock-evidence-driven → skill_view(name='mattpocock-tdd')
                          → skill_view(name='mattpocock-security-review')
                          → skill_view(name='requesting-code-review')
                          → skill_view(name='mattpocock-code-review')
mattpocock-spec-driven-development → skill_view(name='mattpocock-to-tickets')
                          → skill_view(name='mattpocock-codebase-design')
                          → skill_view(name='mattpocock-tdd')
                          → skill_view(name='requesting-code-review')
                          → skill_view(name='mattpocock-gh-fix-ci')
mattpocock-to-tickets → skill_view(name='github-issues')
matppocock-subagent-driven-development → skill_view(name='mattpocock-using-git-worktrees')
                          → skill_view(name='mattpocock-finishing-a-development-branch')
```

### Tier 3: Devops Toolchain (2 skills)
```
docker-containers → skill_view(name='ssh-remote')
rest-api-client → skill_view(name='ssh-remote')
```

### Tier 4: Research Pipeline (4 skills)
```
arxiv → skill_view(name='ocr-and-documents')
grounded-citations → skill_view(name='research-paper-writing')
ocr-and-documents → skill_view(name='pdf'), skill_view(name='docx'), skill_view(name='powerpoint')
nano-pdf → skill_view(name='pdf'), skill_view(name='ocr-and-documents')
```

### Tier 5: Productivity (5 skills)
```
google-workspace → skill_view(name='himalaya'), skill_view(name='weekly-review-planning')
document-to-action-items → skill_view(name='ocr-and-documents'), skill_view(name='pdf'), skill_view(name='docx')
                        → skill_view(name='notion'), skill_view(name='xlsx')
weekly-review-planning → skill_view(name='obsidian'), skill_view(name='notion'), skill_view(name='email-inbox-triage')
doc-coauthoring → skill_view(name='mattpocock-writing-for-agents')
```

### Tier 6: Creative (5 skills)
```
claude-design → skill_view(name='popular-web-designs'), skill_view(name='design-md')
design-md → skill_view(name='popular-web-designs')
sketch → skill_view(name='claude-design'), skill_view(name='popular-web-designs'), skill_view(name='excalidraw')
pretext → skill_view(name='ascii-art'), skill_view(name='ascii-video'), skill_view(name='p5js')
```

### Tier 7: Security (2 skills)
```
mattpocock-security-review → skill_view(name='requesting-code-review')
                            → skill_view(name='mattpocock-code-review')
```

### Tier 8: Code Review Cluster (4 skills)
```
mattpocock-code-review → skill_view(name='test-driven-development')
requesting-code-review → skill_view(name='mattpocock-security-review')
mattpocock-multi-agent-code-review → skill_view(name='mattpocock-security-review')
                                    → skill_view(name='requesting-code-review')
```

## Load Order (topological)

When a task spans multiple skills, load in this order to satisfy dependencies:

1. **Auth first**: `github-auth` (all other GitHub skills depend on it)
2. **Infrastructure**: `ssh-remote`, `docker-containers`, `rest-api-client`
3. **Content extraction**: `arxiv`, `ocr-and-documents`, `web_extract`
4. **Planning**: `mattpocock-to-tickets`, `mattpocock-codebase-design`, `mattpocock-domain-modeling`
5. **Implementation**: `mattpocock-tdd`, `mattpocock-code-review`, `requesting-code-review`
6. **Quality gates**: `mattpocock-security-review`, `mattpocock-evidence-driven`, `mattpocock-spec-driven-development`
7. **Execution**: `github-pr-workflow`, `github-issue-to-pr`, `mattpocock-gh-fix-ci`
8. **Design**: `popular-web-designs`, `design-md`, `claude-design`, `sketch`, `pretext`
9. **Documentation**: `doc-coauthoring`, `mattpocock-writing-for-agents`, `mattpocock-handoff`

## AspireCURES Pipeline Flow

```
autonomous-repo-cronjob (preparer)
  │  collects from arxiv, ocr-and-documents, web_extract
  │  gates with Claude
  │  emits JSON report
  │  → skill_view(mattpocock-subagent-driven-development)
  │    for parallel disease-page processing
  ▼
github/github-pr-workflow (executor)
  │  → skill_view(name='github-auth')
  │  → skill_view(name='github-code-review')
  │    → skill_view(name='requesting-code-review')
  │      → skill_view(name='mattpocock-evidence-driven')
  │        → skill_view(name='mattpocock-tdd')
  │        → skill_view(name='mattpocock-security-review')
  │        → skill_view(name='mattpocock-code-review')
  │  → skill_view(name='mattpocock-gh-fix-ci') [if CI fails]
  ▼
Commits & PR opened
  │
  ▼
Validation via evidence-driven gates
  → skill_view(name='mattpocock-spec-driven-development')
```

## Leaf Nodes (no skill_view dependencies)

These skills are self-contained and do not reference other skills via `skill_view()`:

`hermes-agent`, `computer-use`, `claude-code`, `codex`, `opencode`, `autonomous-repo-cronjob`, `merge-reconciler`, `dogfood`, `mattpocock-handoff`, `plan`, `spike`, `sketch` (standalone), `popul...[truncated]