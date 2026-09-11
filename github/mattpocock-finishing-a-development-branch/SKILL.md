---
name: mattpocock-finishing-a-development-branch
description: "Complete git branches with merge or PR options."
version: 2.0.0
author: Adapted from obra/superpowers v6.3.0 (worktree-safety restructure)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, merge, pr, cleanup, worktrees, branch-management]
    related_skills: [mattpocock-yeet, mattpocock-using-git-worktrees, github-pr-workflow, requesting-code-review]

---
<!-- source: obra/superpowers (skills/finishing-a-development-branch v6.3.0), adapted 2026-09-11 -->

## When to Use

Use when implementation is complete, all tests pass, and you need to decide how to integrate the work (merge locally, push as PR, or keep as-is). Also use after `skill_view(name='requesting-code-review')` passes — i.e., verification gates are green.

**Core principle:** Verify tests → Detect environment → Present options → Execute choice → Clean up. The integration decision is the user's; present the menu and wait.

## What This Skill Does

Completes a development branch with a clear, safety-first decision flow: verify the full suite on the tree being integrated, detect the environment (normal repo / linked worktree / detached HEAD), determine and confirm the base branch, present exactly three options (merge locally / push+PR / keep as-is — discard only ever via explicit typed confirmation), execute the choice with merged-result verification, then clean up ONLY worktrees this workflow owns.

## Process

### Step 1: Verify Tests
Run the project's FULL test suite (`pytest tests/ -q` / `npm test` / ...). If tests fail, report failures and STOP — the menu comes after a green suite ("tests passed earlier this session" proves only the tree it ran on; run it on the tree you're about to integrate).

### Step 2: Detect Environment
```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
# Capture NOW, while still inside the workspace — Step 5 changes directory before cleanup needs this value
WORKTREE_PATH=$(git rev-parse --show-toplevel)
BRANCH=$(git branch --show-current)   # empty = detached HEAD
```

| State | Menu | Cleanup |
|-------|------|---------|
| `GIT_DIR == GIT_COMMON` (normal repo) | Standard 3 options | No worktree to clean up |
| Linked worktree, named branch | Standard 3 options | Provenance-based (Step 6) |
| Detached HEAD (`BRANCH` empty) | Reduced 2 options — no merge | Externally managed: leave in place |

### Step 3: Determine Base Branch
The base is whatever this work forked from — usually named in the plan, conversation, or branch upstream. If not already known, ask: "This branch split from <best guess> — correct?" Confirm before merging; merging into the wrong base is expensive to undo.

### Step 4: Present Options (exactly as written)
```
Implementation complete. What would you like to do?
1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
Which option?
```
Detached HEAD: present exactly 2 options — "Push as new branch and create a PR" / "Keep as-is". **Do not offer to discard.** Discard exists only in response to an explicit user request for it (below). Wait for the answer.

### Step 5: Execute Choice
**Option 1 — Merge locally:** merge FIRST, verify success before removing anything:
```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
git checkout <base-branch> && git pull && git merge <feature-branch>
<test command on the merged result>
```
If tests fail on the merged result: STOP, leave worktree and branch in place, investigate — nothing was pushed, so it's local and recoverable. ("Probably flaky" is not a reason to continue.) Once green: clean up (Step 6), then `git branch -d <feature-branch>`.

**Option 2 — Push + PR:**
```bash
git push -u origin <feature-branch>        # detached HEAD: git push origin HEAD:refs/heads/<new-branch>
```
Create the PR against base with whatever forge tooling exists (its CLI if available, or the creation URL most forges print on push) — following the repo's PR template; report the URL. Use `skill_view(name='mattpocock-yeet')` / `github-pr-workflow`. **Keep the worktree** — PR feedback gets fixed there until the work lands. A rejected push means the remote moved: investigate, force-push only on explicit user request.

**Option 3 — Keep as-is:** report "Keeping branch <name>. Worktree preserved at <path>."

**If (and only if) the user explicitly asks to discard:** confirm first with a typed word:
```
This will permanently delete: Branch <name>, all commits <list>, worktree at <path>.
Type 'discard' to confirm.
```
Only that exact confirmation authorizes deletion, then clean up + `git branch -D`.

### Step 6: Cleanup Workspace (Option 1 and confirmed discards only)
Both callers have already cd'd to the main repo root — removal must run from OUTSIDE the worktree — using the values captured in Step 2.

- **Normal repo:** nothing to clean up. Done.
- **`WORKTREE_PATH` under `.worktrees/` or `worktrees/`:** this skill's family created it — we own cleanup: `git worktree remove "$WORKTREE_PATH" && git worktree prune`.
  - **If removal is REFUSED (contains modified/untracked files):** the worktree holds files that exist nowhere else. NEVER `--force` on your own initiative ("just finishing the cleanup" destroys them permanently). Show what's at stake and ask:
    ```bash
    git -C "$WORKTREE_PATH" status --porcelain -uall
    # 1. Commit them to <branch> before cleanup / 2. Move them into main repo root / 3. Delete (unrecoverable) — which?
    ```
- **Otherwise:** the host environment owns this workspace — leave it in place; use a platform workspace-exit tool if one exists.

## Decision Matrix

| Scenario | Recommended option |
|----------|-------------------|
| Small fix, no review needed | Option 1 (local merge) |
| Team workflow, needs review / CI is the verifier | Option 2 (push + PR) |
| WIP, needs more work | Option 3 (keep branch) |

## Pitfalls — Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Tests passed earlier this session" | Run the suite on the tree you are about to integrate. A green run only proves the tree it ran on. |
| "They obviously want it merged" | Integration is the user's decision. Present the menu and wait. |
| "'Yeah, get rid of it' counts as confirmation" | Only the typed word `discard` authorizes deletion. |
| "The PR is up, so the worktree is clutter now" | PR feedback gets fixed in that worktree. It stays until the work lands. |
| "This other worktree looks stale — I'll clean it too" | Clean up only worktrees under `.worktrees/` or `worktrees/`. Everything else belongs to the host. |
| "Removal refused — `--force` is just finishing the cleanup" | The refusal means files exist ONLY in that worktree. Show them and ask. |
| "The merged-result failure is probably flaky" | A failing merged result stops everything; branch and worktree stay put while you investigate. |
| "The base branch is obviously main" | Confirm the fork point or ask. Merging into the wrong base is expensive to undo. |

## Verification

- [ ] Full suite green on the tree being integrated (and on the merged result for Option 1)
- [ ] Base branch confirmed before merge/PR
- [ ] Menu presented exactly; user chose explicitly
- [ ] Worktree cleaned up only when owned by this workflow AND removal not refused
- [ ] Branch deleted locally (Option 1) — or PR created with proper description (Option 2)
- [ ] User confirmed the final state

## AspireCURES Context

After the executor agent finishes rendering all disease pages and passes validation, use this skill to present the final integration options: merge the render changes to main, push as a PR for human review, or keep the branch. If merging, clean up the `.worktrees/` directory — but if `git worktree remove` is refused (untracked render artifacts), show the user what's there before touching anything.
