---
description: "High-value git recipes distilled from tiimgreen/github-cheat-sheet (MIT) — fixup/autosquash, PR checkout, revert"
source_repos: tiimgreen/github-cheat-sheet (MIT), verified against local git 2.x behavior on Windows
tested_version: clone @ 2026-09-05; recipes are stable git semantics, not version-sensitive. Round 2 (2026-09-10): every recipe re-executed live in a scratch repo on git 2.54.0.windows.1 + PR refspec verified against the real upstream repo (183 PR branches incl. closed)
verified_date: "2026-09-10"
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

## Find an earlier commit by what its message said
```bash
git show :/query-words         # opens the MOST RECENT commit whose subject matches (case-sensitive)
```
The `:/` prefix switches git's revision parsing into "search commit messages" mode — no log grep needed. Verified on git 2.54: `git show ":/setup typo in file"` returned exactly that commit with its diff stat.

## Search tracked content across the whole repo (boolean, per-line)
```bash
git grep -e alpha --and -e beta          # lines containing BOTH patterns
git grep -e zeta  --or  -e gamma         # either pattern
git grep -e a     --not -e x             # matches minus exclusions
git grep '(alpha|zeta) gamma'            # regex alternation works; parenthesized GROUPS do not (rc=1, git 2.54)
```
Semantics verified live: each boolean operator is evaluated PER LINE against the working tree (default rev = HEAD). Multiple `-e` patterns with no operator are implicitly OR'd. Bare `git grep word pattern2` without `-e` treats the second arg as a path/rev and fails — always use `-e`.

## See which branches are merged vs not
```bash
git branch --merged      # branches fully contained in HEAD (safe to delete)
git branch --no-merged   # branches with unmerged work (the "what's still open" list)
```
Verified: after merging `feat-thing`, it appeared under `--merged` and a fresh `unmerged-br` only under `--no-merged`. Pair with the cleanup alias below.

## Empty commits as deliberate markers
```bash
git commit --allow-empty -m "marker: phase two starts"
```
Legitimate uses (not noise): marking where a bulk of work begins, recording non-code decisions in history, or the very first commit before any file exists (`git init` + `--allow-empty`). Verified live.

## Styled status and log (alias-ready)
```bash
git status -sb                       # branch + tracking info on line 1 — the compact form for scripts/agents
git config --global alias.lg "log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
```
The `lg` format string was executed verbatim from the cheat sheet — renders a colored graph with short sha, decorations, subject, relative date, author.

## Aliases that earn their space (all verified by running them)
```bash
git config --global alias.cm commit
git config --global alias.co checkout
git config --global alias.st 'status -sb'
git config --global alias.ac '!git add -A && git commit'          # ! prefix = run as shell, not git subcommand
git config --global alias.cleanup '!git branch --merged | grep -v "*" | xargs git branch -d'   # deletes merged branches except current
```
`cleanup` was executed live: it deleted both merged feature branches and left `* main` untouched. The `!` prefix matters — without it the pipe is passed to git as arguments.

## Housekeeping config worth knowing (accepted by this machine's git)
- `git config --global help.autocorrect 15` — on a typo (`git comit`) git waits 1.5 s then runs the corrected command; abort with Ctrl-C in that window. Default is **0 = no auto-run** (verified: instant error, 0.15 s). Negative value = run immediately without waiting.
- `git config --global color.ui 1` — force colored output even when piped through a pager-less terminal.

## Windows-specific notes for this machine
- `core.autocrlf=true` + `.gitattributes text=auto` is the standing config here — never commit CRLF-normalized diffs by hand; let git do it.
- OneDrive-backed repos (`C:\Users\Owner\OneDrive\Documents\GitHub`) can show phantom index churn: if `git status` shows mass deletions that aren't real, verify with `git ls-files -d | head` before acting — re-run after a short wait; the cloud placeholder sync usually settles.
- Long paths are fine (core.longpaths default on modern git); avoid them in *tool* arguments anyway (MSYS path translation is disabled for native tools here).

## What was deliberately left out of this file
The cheat sheet's GitHub-web sections (URL params, compare patterns, gists-as-repos, keyboard shortcuts) are NOT dropped — they live in the sibling `github-web-ui-tricks.md`, re-verified there on 2026-09-10. What stays excluded: GUI/gitk tips and generic "Git resources" link lists (books/videos/articles) — low reuse value for an agent-driven workflow, and the full list remains in the clone if ever needed.
