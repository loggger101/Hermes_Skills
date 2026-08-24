---
name: mattpocock-finishing-a-development-branch
description: "Complete git branches with merge or PR options."
version: 1.0.0
author: Adapted from obra/superpowers
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, merge, pr, cleanup, worktrees, branch-management]
    related_skills: [mattpocock-yeet, mattpocock-using-git-worktrees, github-pr-workflow]
---

## When to Use

Use when implementation is complete, all tests pass, and you need to decide how to integrate the work (merge locally, push as PR, or keep as-is).

## What This Skill Does

Completes a development branch with a clear decision flow: verify tests → detect environment → present options → execute choice → clean up.

## Process

### Step 1: Verify Tests
Run the project's full test suite:
```bash
pytest tests/ -v
```
If tests fail, report failures and stop. If tests pass, continue.

### Step 2: Detect Environment
```bash
GIT_DIR=$(git rev-parse --git-dir 2>/dev/null && pwd -P)
GIT_COMMON=$(git rev-parse --git-common-dir 2>/dev/null && pwd -P)
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

### Step 3: Determine Base Branch
The base branch is whatever this work forked from — usually named in the plan or conversation. Confirm before merging.

### Step 4: Present Options
```
Implementation complete. What would you like to do?
1. Merge back to <base> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
Which option?
```

### Step 5: Execute Choice
- **Option 1 (Merge)**: `git checkout <base> && git pull && git merge <branch>`, verify tests on merged result, cleanup worktree, delete branch
- **Option 2 (PR)**: `git push -u origin <branch>`, create PR against base branch, keep worktree
- **Option 3 (Keep)**: report and preserve branch + worktree

### Step 6: Cleanup Workspace
- If normal repo (`GIT_DIR == GIT_COMMON`): no worktree to clean up
- If worktree under `.worktrees/` or `worktrees/`: `git worktree remove "$WORKTREE_PATH" && git worktree prune`
- Otherwise: leave in place (host environment owns it)

## AspireCURES Context

After the executor agent finishes rendering all 9 disease pages and passes validation, use this skill to present the final integration options: merge the render changes to main, push as a PR for human review, or keep the branch. If merging, clean up the `.worktrees/` directory.
