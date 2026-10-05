---
name: git-on-sync-clients
description: "Fix git in OneDrive/Drive folders: refs, mmap, copies."
version: 1.0.0
author: Hermes Agent (from the owner's aspirecures MAINTENANCE.md runbook and the knowledge vault's onedrive-synced-repos page, 2026-10)
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [git, onedrive, google-drive, sync-client, conflict-copies, mmap, stat-cache, windows, hygiene]
    related_skills: [github-pr-workflow, github-repo-management, systematic-debugging, windows-agent-shell, verification-before-completion]
---

# Git inside a sync client (OneDrive, Google Drive)

## What This Skill Does

Diagnoses and fixes the four unrelated ways a sync client breaks a git clone that lives in a synced folder, each with a different fix where the wrong one looks like success. The owner's repos live in `~\OneDrive\Documents\GitHub\` and two machines edit through that sync (`Loggg` and `DESKTOP-PJS73RO`), so all four have happened.

## When to Use

- `fatal: bad object refs/desktop.ini`, or a fetch that fails while `origin/main` looks current
- `git status` shows modified files with an empty diff, or a pull is blocked by "phantom" changes
- Every git command fails with `fatal: mmap failed: Invalid argument` or `error: read error while indexing`
- Files named `<name>-DESKTOP-PJS73RO.<ext>` appear, or `git branch` lists a `main-DESKTOP-PJS73RO` branch
- Not for ordinary git workflow (`github-pr-workflow`) or repo creation (`github-repo-management`)

## Diagnose first: which hazard is it?

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | `fatal: bad object refs/desktop.ini`; fetch fails but `HEAD...origin/main` says `0 0` | Drive drops `desktop.ini` files inside `.git/refs/` | delete them, re-fetch |
| 2 | "phantom modified" files with empty diffs; merges blocked | the client churns stat data; a bogus cached size can wedge the state | re-hash (a heal alias or hook), `core.checkStat minimal` |
| 3 | every command fails, `mmap failed` | Files On-Demand evicted `.git/` contents to the cloud | start OneDrive, pin the folder, read the placeholders back; not corruption |
| 4 | `<name>-DESKTOP-PJS73RO.<ext>` files | two machines edited the same file; the loser is renamed | prove each is identical to an ancestor commit, then delete |

## Procedure

**Hazard 1 (desktop.ini in refs).**
1. `find .git/refs -name desktop.ini -type f -delete`, re-fetch, and verify with `git show-ref | grep -v desktop`. A heal alias does not help here.
2. A failed fetch does not announce staleness: `origin/main` keeps its last good value. Treat any fetch that printed `fatal:` or `error:` as no information, and confirm the real remote head with `gh api repos/<owner>/<repo>/commits/main --jq '.sha[0:7]'` before trusting "up to date". The refs regrow.

**Hazard 2 (phantom modified).**
1. Re-hash flagged files and clear the ones byte-identical to the index (a `git heal` alias, for example `perl tools/git-heal.pl`); real edits are only reported.
2. Per machine, set `git config core.hooksPath tools/githooks`, the heal alias and `git config core.checkStat minimal`, and verify with `git config core.hooksPath` (empty means the hooks are not running and nothing will say so).
3. Never `git stash` in a synced repo: the sync races it. Copy to a scratch directory instead.

**Hazard 3 (mmap failed).**
1. Count evicted files under `.git/`: `powershell -c "(Get-ChildItem '.git' -Recurse -File -Force | Where-Object { $_.Attributes -band 0x400000 }).Count"` (from Git Bash put a backslash before each `$_` so the shell leaves it alone, or run it from PowerShell; `0x400000` is RECALL_ON_DATA_ACCESS; also check `0x1000`, Offline). A non-zero count is the whole story.
2. Make sure OneDrive is running; if it is not, every read fails with "The cloud file provider is not running", which looks like disk corruption.
3. Pin the repo so it cannot recur: `attrib -U +P "<repo path>\*" /s /d` (OneDrive honours the Windows pin; Google Drive's mount does not). Pinning does not hydrate what is already evicted.
4. Read every placeholder back (`ReadAllBytes` over files with the recall attribute) and repeat until the count is 0; the first pass can fail while OneDrive warms up.
5. Confirm with `git fsck && git status`. Nothing needs re-cloning.

**Hazard 4 (conflict copies).**
1. Find them with `find`, not `git status`: a `.gitignore` that refuses `*-DESKTOP-*` hides them from `??` sweeps. Also search inside `.git/` (`find .git -name '*-DESKTOP-*'`), where copies of `index`, `FETCH_HEAD`, reflogs and even a branch ref accumulate.
2. For each copy compare with the original from the remote tip: `git show origin/main:<path> | cmp -s - <copy>` (normalise CRLF); a mismatch usually means the remote moved on, so compare against the branch it came from.
3. Delete only copies proven identical to an ancestor revision; never commit one. A stale live `.git/index` (staged changes that are really an undo of the last commit) is fixed by backing up the copies, `git reset` to rebuild the index, rebasing onto `origin/main`, checking each copy matches it, then deleting.
4. Prevent: ignore `*-DESKTOP-*` in `.gitignore`, and keep virtual environments out of the sync (they hold absolute paths to one machine's home folder).

## Pitfalls

- Reaching for the heal alias when the problem is hazard 1 or 3.
- Treating `mmap failed` as corruption and re-cloning.
- Reading `0 0` from `rev-list` after a failed fetch.
- A doc claiming "all defences in place" while the config is unset: check `git config`, do not assume.
- Google Drive adds a bogus 16384-byte size on checkout that breaks the stat cache and ignores the Windows pin; treat old Drive copies as archives.
- Local git config and hooks live in `.git/`, which is shared by both machines, so a setting applied on one applies on the other.

## Verification

- [ ] `git fsck` is clean and `git status` is stable after the fix
- [ ] `find . .git -name '*-DESKTOP-*'` returns nothing, or every hit is classified
- [ ] The remote head was confirmed through `gh api`, not through a possibly stale local ref
- [ ] The repo is pinned (`attrib` shows no `U`) and OneDrive is running
