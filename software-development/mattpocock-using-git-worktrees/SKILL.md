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
    related_skills: [autonomous-repo-cronjob, mattpocock-yeet, github-pr-workflow]
---

## When to Use

Use when starting feature work that needs isolation from the current workspace, or before executing implementation plans — ensures an isolated workspace exists.

## Overview

**Core principle:** Detect existing isolation first. Then use native tools. Then fall back to git. Never fight the harness.

**Announce at start:** "I'm using an isolated git worktree to set up a clean workspace."

## Step 0: Detect Existing Isolation

Before creating anything, check if you're already in an isolated workspace:

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

If `GIT_DIR != GIT_COMMON` (and not a submodule): You are already in a linked worktree — skip creation.

If `GIT_DIR == GIT_COMMON` (or in a submodule): You are in a normal repo checkout.

## Step 1: Create Isolated Workspace

Prefer your platform's native worktree tools. Fall back to `git worktree add` only when no native tool is available.

### Git Worktree Fallback

```bash
mkdir -p .worktrees
git worktree add ".worktrees/$BRANCH_NAME" -b "$BRANCH_NAME"
cd ".worktrees/$BRANCH_NAME"
```

**Safety:** Verify `.worktrees/` is in `.gitignore` before creating. An unignored worktree directory commits the whole tree into the repo.

## Step 2: Project Setup

```bash
# Python
pip install -r requirements.txt
# Or with uv
uv sync
```

## Step 3: Verify Clean Baseline

Run the test suite to ensure the workspace starts clean. If tests fail, report and ask before proceeding.

## AspireCURES Context

Your two-agent split benefits from worktree isolation: the preparer agent runs in one worktree (collecting/gating), the executor agent in another (merging/rendering/committing). Use worktrees to prevent the preparer's JSON output from interfering with the executor's branch checkout. The `.worktrees/` directory should be in `.gitignore`.
