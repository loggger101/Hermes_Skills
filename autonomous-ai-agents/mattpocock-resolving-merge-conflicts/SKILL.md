---
name: mattpocock-resolving-merge-conflicts
description: "Resolve git merge conflicts by tracing each side's intent."
version: 1.1.0
author: Adapted from mattpocock/skills
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [merge-conflicts, git, rebase, conflict-resolution]
    related_skills: [merge-reconciler, systematic-debugging, mattpocock-diagnosing-bugs]
---

## What This Skill Does

Resolves git merge conflicts by tracing each side's intent rather than blindly accepting one version. Classifies each conflict hunk as complementary (keep both), overlapping (merge intents), or contradictory (pick one and note the trade-off). Runs automated checks after resolution. Loads `skill_view(name='systematic-debugging')` for diagnosing broken state and `skill_view(name='merge-reconciler')` for conflicts between agent branches.

## When to Use

Use when the user needs to resolve an in-progress git merge or rebase conflict, or reports a "merge conflict" error. This skill loads `skill_view(name='systematic-debugging')` for diagnosing any broken state that emerges from a poorly resolved merge.

## Preparation

Before touching conflict markers, ensure you understand what's being merged:

```bash
git status                    # see conflicting files
git log --oneline --all --graph -20  # visualize branch topology
git diff HEAD --name-only     # all changed files
```

If rebasing, also check:
```bash
git reflog                    # see where the rebase started
git log -p --root..HEAD       # full history of what's being rebased
```

## The Process

### 1. See the current state
Check `git status`, history, and the conflicting files. Identify which branches/commits are in conflict.

### 2. Find the primary sources for each conflict
Read commit messages, check PRs, check original issues/tickets. Understand deeply why each change was made and what the original intent was.

```bash
# For each conflicting commit, see full context
git log -p -1 <commit-hash>
# Check the PR that introduced it
gh pr view --web --repo <owner>/<repo>
```

**Key principle**: Every conflict resolves to one of three cases:
- **Complementary** — both sides add something different, keep both
- **Overlapping** — both touch the same lines, need to preserve intent from both
- **Contradictory** — one side replaces what the other does, pick the newer/more correct approach

### 3. Resolve each hunk
Preserve both intents where possible. Where incompatible, pick the one matching the merge's stated goal and note the trade-off. Do **not** invent new behaviour. Always resolve; never `--abort`.

For each conflict:
```
<<<<<<< HEAD
(our version)
=======
(their version)
>>>>>>> branch-name
```

- Ask: what was each author trying to achieve?
- Ask: which version better matches the surrounding code's conventions?
- Merge by hand: take the best from each, or pick one with confidence

### 4. Run automated checks
Typecheck, then tests, then format. Fix anything the merge broke.

```bash
# After resolving all conflicts
git add .
<run project tests>
<run linter/formatter>
<run typecheck>
```

### 5. Finish the merge/rebase
Stage everything and commit. If rebasing, continue until all commits are rebased.

```bash
# For a merge:
git commit  # completes the merge commit

# For a rebase:
git add .
git rebase --continue
# Repeat until rebase completes, then:
git rebase --skip  # if nothing to commit
```

## Conflict Resolution Patterns

### Pattern: Added vs Modified (same function)
```
<<<<<<< HEAD
def process(data):
    return data.strip()
=======
def process(data, normalize=False):
    if normalize:
        data = data.strip()
    return data
>>>>>>> feature
```
**Resolution**: Take the feature branch's enhanced version — it's backward compatible (default arg).

### Pattern: Modified vs Deleted (same line)
```
<<<<<<< HEAD
import { oldHelper } from './utils'
=======
// (file deleted by their side)
>>>>>>> feature
```
**Resolution**: Check if the import is still used. If not, remove it.

### Pattern: Competing additions
```
<<<<<<< HEAD
// Validation
const isValid = email.includes('@')
=======
// Sanitize
const cleanEmail = email.trim()
>>>>>>> feature
```
**Resolution**: Keep both — they serve different purposes. Order matters: sanitize first, then validate.

## Pitfalls

- **Accepting blindly** — `git checkout --theirs .` resolves markers but may lose your side's work
- **Overwriting the wrong side** — check which side is `HEAD`/`ours` vs incoming `theirs` with `git status`
- **Not testing after** — conflicts can introduce subtle bugs; always run tests
- **Resolving on the wrong branch** — confirm `git branch` before committing the merge
- **Forgetting to set merge tool** — `git config merge.tool vimdiff` for in-terminal resolution

## Verification

- [ ] `git status` shows clean merge/commit state
- [ ] No conflict markers remain (`search_files` pattern `<<<<<<<`)
- [ ] Automated checks pass (typecheck, tests, format)
- [ ] Both sides' intents are preserved where possible
- [ ] Trade-offs for contradictory hunks are documented
- [ ] Re-test after merging to confirm no regressions

## AspireCURES Context

Your commit agent (executor) may hit merge conflicts when applying the preparer agent's JSON report into the disease pages branch. Use this skill to resolve each hunk by tracing back to the originating research finding or pipeline change, never inventing new behavior. Run the disease-page validation tests after each resolution. For conflicts spanning large sections, use `skill_view(name='merge-reconciler')` as a neutral third-party mediator.
