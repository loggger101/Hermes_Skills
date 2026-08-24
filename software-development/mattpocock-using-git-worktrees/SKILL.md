---
name: mattpocock-using-git-worktrees
description: "Set up isolated git worktrees for feature work."
version: 1.0.0
author: Adapted from obra/superpowers
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, worktrees, isolation, branching, feature-work]
    related_skills: [autonomous-repo-cronjob, mattpocock-yeet, github-pr-workflow, mattpocock-finishing-a-development-branch]
---

## When to Use

Use when starting feature work that needs isolation from the current workspace, or before executing implementation plans — ensures an isolated workspace exists. Also use when you need to work on multiple branches simultaneously without stashing.

## What This Skill Does

Sets up an isolated git worktree so that feature work does not interfere with the main working tree. Loads `skill_view(name='mattpocock-yeet')` for the commit+push+PR workflow once the worktree is ready, and `skill_view(name='github-pr-workflow')` for the full PR lifecycle.

## Overview

**Core principle:** Detect existing isolation first. Then use native tools. Then fall back to git. Never fight the harness.

**Announce at start:** "I'm using an isolated git worktree to set up a clean workspace for this feature."

## Prerequisites

- Git 2.5+ (worktree support)
- A git repository with at least one commit
- `.worktrees/` listed in `.gitignore`

## Process

### Step 0: Detect Existing Isolation

Before creating anything, check if you're already in an isolated workspace:

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

If `GIT_DIR != GIT_COMMON` (and not a submodule): You are already in a linked worktree — skip creation.

If `GIT_DIR == GIT_COMMON` (or in a submodule): You are in a normal repo checkout.

### Step 1: Create Isolated Workspace

Prefer your platform's native worktree tools. Fall back to `git worktree add` only when no native tool is available.

#### Git Worktree Fallback

```bash
mkdir -p .worktrees
git worktree add ".worktrees/$BRANCH_NAME" -b "$BRANCH_NAME"
cd ".worktrees/$BRANCH_NAME"
```

**Safety:** Verify `.worktrees/` is in `.gitignore` before creating. An unignored worktree directory commits the whole tree into the repo.

#### Platform-native isolation

| Platform | Native tool | Notes |
|----------|------------|-------|
| VS Code | `code --add` to a new window | Uses workspaces, not worktrees |
| Cursor | `/new` workspace | Creates a scoped working directory |
| JetBrains | "Add Project" | Full project isolation |
| Claude Code | `-w` flag | Auto-managed worktrees |

### Step 2: Project Setup

```bash
# Python
pip install -r requirements.txt
# Or with uv
uv sync
```

### Step 3: Verify Clean Baseline

Run the test suite to ensure the workspace starts clean. If tests fail, report and ask before proceeding.

```bash
# Python
python -m pytest --tb=short -q
# Node
npm test
# Rust
cargo test
```

### 4. Work in the isolated environment

Make changes, run tests, commit — all isolated from the main working tree.

### 5. Clean up

After the worktree branch is merged:

```bash
git worktree remove ".worktrees/$BRANCH_NAME"
git worktree prune
git branch -D "$BRANCH_NAME"
```

## Pitfalls

- **Unignored `.worktrees/`**: If `.worktrees/` is not in `.gitignore`, the worktree directory gets committed — use `git check-ignore .worktrees` to verify
- **Dirty worktrees**: Worktrees inherit a clean state — if the main branch has uncommitted changes, they don't appear in the worktree
- **Multiple worktrees on same branch**: Git prevents this by default — use `git worktree add --force` if you need to override
- **File watcher conflicts**: Some IDEs watch both the main repo and the worktree — configure excludes to prevent duplicate indexing
- **Disk space**: Each worktree doesn't duplicate the `.git` directory, but does copy working files

## Verification

- [ ] Current `GIT_DIR != GIT_COMMON` (confirmed in an isolated worktree)
- [ ] `.worktrees/` is present in `.gitignore`
- [ ] Test suite passes in the clean worktree baseline
- [ ] Branch name is descriptive and follows repo conventions
- [ ] Worktree was removed and pruned after merge

## AspireCURES Context

Your two-agent split benefits from worktree isolation: the preparer agent runs in one worktree (collecting/gating), the executor agent in another (merging/rendering/committing). Use worktrees to prevent the preparer's JSON output from interfering with the executor's branch checkout. The `.worktrees/` directory should be in `.gitignore`.
