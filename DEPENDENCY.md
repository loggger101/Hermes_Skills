# Skill Relationships

This document maps dependencies and relationships between skills based on `related_skills` metadata in each SKILL.md frontmatter.

## Hub Skills (referenced by many other skills)

### `hermes-agent`
Referenced by: `cron-job-authoring`, `hermes-agent-skill-authoring`, `doc-coauthoring`

### `systematic-debugging`
Referenced by: `mattpocock-diagnosing-bugs`, `test-driven-development`

### `github-pr-workflow`
Referenced by: `mattpocock-finishing-a-development-branch`, `mattpocock-gh-fix-ci`, `mattpocock-yeet`, `requesting-code-review`

### `github-issues`
Referenced by: `mattpocock-to-tickets`, `github-issue-to-pr`

### `requesting-code-review`
Referenced by: `mattpocock-code-review`, `mattpocock-evidence-driven`, `mattpocock-multi-agent-code-review`, `mattpocock-security-review`

### `sketch`
Referenced by: `frontend-design`

### `claude-design`
Referenced by: `frontend-design`

### `popular-web-designs`
Referenced by: `frontend-design`

### `test-driven-development`
Referenced by: `requesting-code-review`, `mattpocock-tdd`, `mattpocock-evidence-driven`, `mattpocock-spec-driven-development`

### `spy/subagent-driven-development`
Referenced by: `requesting-code-review`

### `plan`
Referenced by: `requesting-code-review`, `test-driven-development`

## Skill Chains

### Development Workflow
```
mattpocock-spec-driven-development
  → mattpocock-to-tickets
    → mattpocock-using-git-worktrees
      → mattpocock-yeet (commit+push+PR)
      → mattpocock-finishing-a-development-branch (merge/PR)
        → mattpocock-gh-fix-ci (fix CI)

mattpocock-code-review
  → requesting-code-review (verification pipeline)
```

### Research Workflow
```
mattpocock-research
  → parallel-cli
  → arxiv
  → grounded-citations
```

### Document Co-Authoring
```
doc-coauthoring
  → mattpocock-writing-for-agents
    → hermes-agent-skill-authoring
```

## Category Relationships

### autonomous-ai-agents → software-development
- `hermes-agent` references `cron-job-authoring`
- `claude-code`, `codex`, `opencode` are delegation targets

### devops → software-development
- `docker-containers` ↔ `ssh-remote`
- `rest-api-client` ↔ `ssh-remote`
- `sqlite-queries` (standalone)

### creative → productivity
- `sketch` → `popular-web-designs`, `claude-design`

### github → autonomous-ai-agents
- `github-pr-workflow` ↔ `autonomous-repo-cronjob`

### mlops → huggingface-trackio
- `huggingface-hub` ↔ `huggingface-trackio`

### productivity → research
- `obsidian` ↔ `llm-wiki`
- `meeting-action-items` ↔ `document-to-action-items`

## Notes

- Some cross-references are bidirectional (skill A lists skill B, and vice versa)
- The `mattpocock-*` skills form an opinionated methodology layer that builds on top of the standard Hermes skills
- Pre-existing skills were authored by a different agent and may reference different skill sets
