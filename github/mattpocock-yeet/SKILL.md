---
name: mattpocock-yeet
description: "Git workflow: stage, commit, push, open PR."
version: 1.1.0
author: Adapted from openai/skills
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, pr, commit, push, github-cli, staging]
    related_skills: [github-pr-workflow, autonomous-repo-cronjob, github-auth, mattpocock-gh-fix-ci]

---

## When to Use

Use when the user wants to go from local changes to a reviewable PR without running each git step manually.

## What This Skill Does

Automates: creates a branch, commits staged changes, pushes, and opens a draft PR with a structured description.

## Prerequisites

- Git repository initialized with remote `origin`
- Authenticated with GitHub (run `skill_view(name='github-auth')` if not)
- `gh` CLI installed for PR creation (optional — can use `git push` + manual PR)

## Process

### 1. Create a feature branch
```bash
git checkout -b feature/{descriptive-name}
```
Use a descriptive name that reflects the change: `feature/add-disease-page-pancreatic-cancer` or `fix/arxiv-api-format-change`.

### 2. Stage changes
```bash
git add .
# Or stage specific files:
git add src/parser.py src/renderer.py
```

### 3. Commit with conventional message
```bash
git commit -m "{type}: {clear message}"
```

**Type prefix:**
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation only
- `refactor:` — code restructuring (no behavior change)
- `chore:` — maintenance, tooling

Examples:
```
feat: add pancreatic cancer disease page with 12 research summaries
fix: handle arxiv API rate limit with retry logic
docs: update weekly cronjob setup instructions
```

### 4. Push to remote
```bash
git push -u origin feature/{branch-name}
```
The `-u` flag sets up tracking so future `git push`/`git pull` work without arguments.

### 5. Open a PR
```bash
gh pr create --fill
```
`--fill` auto-populates the PR title and description from the commit message. For a draft PR (not ready for review):
```bash
gh pr create --fill --draft
```

For a structured PR body, pass `--body`:
```bash
gh pr create \
  --title "feat: add pancreatic cancer disease page" \
  --body "## Problem\nArxiv API changed format...\n## Approach\n...\n## Tests\n..." \
  --label "disease-page"
```

## Post-PR Workflow

After opening the PR:
1. CI will start automatically — monitor with `skill_view(name='mattpocock-gh-fix-ci')` if it fails
2. Add reviewers: `gh pr edit --add-reviewer @user`
3. For AspireCURES: each disease page update should be its own commit so reviewers can see the full scope per disease

## Common Fixes for Merge Conflicts

If `git push` fails with "updates were rejected":
```bash
git pull --rebase origin main  # rebase onto latest main
# resolve any conflicts, then:
git push --force-with-lease     # safe force push
```

If you need to amend the last commit:
```bash
git add .
git commit --amend
git push --force-with-lease
```

## Pitfalls

- **Committing secrets** — check `git diff` before committing; use `git secrets` or `trufflehog`
- **Vague commit messages** — "fix stuff" or "update" doesn't help reviewers
- **Forgetting `--set-upstream`** — first push needs `-u`, otherwise future pushes require the full branch name
- **Squashing when you shouldn't** — if the PR has multiple logical commits, keep them separate for review
- **Not pulling latest** — always `git pull --rebase origin main` before pushing to avoid conflicts

## AspireCURES Context

Maps to the commit agent's workflow. After the executor merges changes and validates output, use this to create the commit and open a PR. Each disease-page update should be its own commit: `feat: add {disease-name} page with 12 research summaries`.
