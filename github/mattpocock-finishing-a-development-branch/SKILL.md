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
    related_skills: [mattpocock-yeet, mattpocock-using-git-worktrees, github-pr-workflow, requesting-code-review]
---

## When to Use

Use when implementation is complete, all tests pass, and you need to decide how to integrate the work (merge locally, push as PR, or keep as-is). Also use after `skill_view(name='requesting-code-review')` passes — i.e., verification gates are green.

## What This Skill Does

Completes a development branch with a clear decision flow: verify tests → detect environment → present options → execute choice → clean up. Loads `skill_view(name='requesting-code-review')` for pre-merge verification, `skill_view(name='mattpocock-yeet')` for PR creation, and `skill_view(name='mattpocock-using-git-worktrees')` for worktree management.

## Prerequisites

- Implementation is complete
- Tests pass (run `skill_view(name='requesting-code-review')` first if not yet verified)
- Branch is rebased on or merged with base branch as needed

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

| Environment | `GIT_DIR` vs `GIT_COMMON` | Action |
|-------------|--------------------------|--------|
| Normal clone | Same | No worktree to clean up |
| Linked worktree | Different | Clean up worktree after integration |

### Step 3: Determine Base Branch
The base branch is whatever this work forked from — usually named in the plan or conversation. Confirm before merging.

### Step 4: Present Options

```
Implementation complete. Tests pass. What would you like to do?
1. Merge back to <base> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
Which option?
```

### Step 5: Execute Choice

- **Option 1 (Merge)**: `git checkout <base> && git pull && git merge <branch>`, verify tests on merged result, cleanup worktree, delete branch
- **Option 2 (PR)**: `git push -u origin <branch>`, create PR against base branch using `skill_view(name='mattpocock-yeet')`, keep worktree
- **Option 3 (Keep)**: report and preserve branch + worktree

### Step 6: Cleanup Workspace

| Environment | Cleanup |
|-------------|---------|
| Normal repo (`GIT_DIR == GIT_COMMON`) | No worktree to clean up |
| Worktree under `.worktrees/` or `worktrees/` | `git worktree remove "$WORKTREE_PATH" && git worktree prune` |
| Other | Leave in place (host environment owns it) |

## Decision Matrix

| Scenario | Recommended option |
|----------|-------------------|
| Small fix, no review needed | Option 1 (local merge) |
| Team workflow, needs review | Option 2 (push + PR) |
| WIP, needs more work | Option 3 (keep branch) |
| Worktree was temporary | Clean up after merge |

## Pitfalls

- **Dirty merge**: Always verify tests pass on the merged result, not just the branch in isolation
- **Unpushed changes**: If the branch has unpushed commits, the merge may fail or lose work
- **Forgotten worktrees**: Linked worktrees left behind clutter the filesystem — always clean up
- **Wrong base branch**: Merging to the wrong base can introduce unintended changes
- **No CI**: If the project relies on CI for verification, prefer Option 2 (PR) to let CI run

## Verification

- [ ] Tests pass on the merged result (for Option 1) or CI passes (for Option 2)
- [ ] Worktree cleaned up (if one was used)
- [ ] Branch deleted locally (if merged locally)
- [ ] PR created with proper description (if Option 2)
- [ ] User confirmed the final state

## AspireCURES Context

After the executor agent finishes rendering all disease pages and passes validation, use this skill to present the final integration options: merge the render changes to main, push as a PR for human review, or keep the branch. If merging, clean up the `.worktrees/` directory.
