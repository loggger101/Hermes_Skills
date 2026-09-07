---
description: "High-value git recipes distilled from tiimgreen/github-cheat-sheet (MIT) — fixup/autosquash, PR checkout, revert"
source_repos: tiimgreen/github-cheat-sheet (MIT), verified against local git 2.x behavior on Windows
tested_version: clone @ 2026-09-05; recipes are stable git semantics, not version-sensitive
verified_date: "2026-09-06"
---

# Git Workflow Recipes (distilled from github-cheat-sheet)

The cheat sheet is a wall of one-liners; this file keeps only the recipes that earn their space.
Full source: `%LOCALAPPDATA%\Temp\starred-dive\tiimgreen\github-cheat-sheet\README.md`.

## Fixup + autosquash — repair an earlier commit without rewriting history by hand
```bash
git commit --fixup=<sha>            # stage your fix, then this (creates "fixup! <original subject>")
git rebase -i --autosquash <sha>^   # the todo list auto-arranges each fixup under its target; just save it
```
Use for: a typo in an already-pushed-but-unmerged commit, a missing file added after the fact. The `-i` is only there because rebase needs to open the editor — with `--autosquash` you can accept the default list unchanged (or set `GIT_SEQUENCE_EDITOR=true` to skip it entirely).

## Check out a pull request locally
```bash
git fetch origin refs/pull/<N>/head          # one PR -> FETCH_HEAD; diff/merge/test without touching branches
# or make ALL PRs available as local remote-tracking branches:
git config --local remote.origin.fetch '+refs/pull/*/head:refs/remotes/origin/pr/*'
git fetch origin                              # now `git checkout pr/<N>` works for any open/closed PR
```

## Revert a merged pull request safely
GitHub's **Revert button** (on the merge commit of the PR) creates a new PR containing the inverse diff — safe on protected branches where force-push/rebase is forbidden. Locally, `git revert -m 1 <merge-sha>` does the same for octopus/merge commits (`-m 1` = keep first parent).

## Bulk-stage deletions you already did with rm
```bash
git rm $(git ls-files -d)     # stage every file deleted from disk but still tracked — no per-file typing
```

## Jump back to the previous branch
```bash
git checkout -                # toggles between last two branches (like cd - for branches)
```

## Windows-specific notes for this machine
- `core.autocrlf=true` + `.gitattributes text=auto` is the standing config here — never commit CRLF-normalized diffs by hand; let git do it.
- OneDrive-backed repos (`C:\Users\Owner\OneDrive\Documents\GitHub`) can show phantom index churn: if `git status` shows mass deletions that aren't real, verify with `git ls-files -d | head` before acting — re-run after a short wait; the cloud placeholder sync usually settles.
- Long paths are fine (core.longpaths default on modern git); avoid them in *tool* arguments anyway (MSYS path translation is disabled for native tools here).

## What was deliberately left out of this file
The cheat sheet's GitHub-web sections (keyboard shortcuts, emoji codes, Pages metadata) and the `gitk`/GUI tips — low reuse value for an agent-driven workflow. The full list stays in the clone if ever needed.
