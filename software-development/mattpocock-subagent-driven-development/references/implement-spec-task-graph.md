# Implement a whole spec: tickets as a task graph on one integration branch

Source: [mattpocock/skills](https://github.com/mattpocock/skills) `skills/engineering/implement-spec/SKILL.md` (MIT; graduated in
1.3.0, user-invoked there), repo HEAD `4588b32` (2026-10-05). Source-read, **not run**. An earlier audit of this repo skipped
it as thin; the 1.3.0 version is a complete orchestration recipe and fits this skill's subagent pattern, so it is recorded here. Inputs
come from `conversation-to-spec` (the spec) and `mattpocock-to-tickets` (the tickets).

## Model

- The goal is **the whole spec implemented on one integration branch**, with each ticket resolved the way the issue tracker closes
  work. The goal is the branch, not a PR: a **draft PR opens only if the tracker closes work through PRs or the user asks**, and only
  after the first merge, because a branch with no commits ahead of `main` cannot open one.
- Tickets are **not a list of steps**. They are a **task graph** with blocking relationships, so at any moment there is a **frontier**
  of tickets whose blockers are done and that are ready to be grabbed.
- Subagents communicate sparsely through **context pointers** (the spec, ticket ids, research notes, earlier commits) instead of copied text.
  Run implementers **in the background** for concurrency.
- The issue tracker must be named by the user or the project's setup file; if none was provided, say so rather than defaulting to `gh`.

## Steps

1. Read the spec and tickets and build the graph (ticket -> blockers).
2. Optional **exploration subagent**: gathers the codebase files or external docs the tickets need and saves markdown notes in a
   directory **outside the repo** that every later subagent can read, so implementers spend their time building.
3. Create the integration branch.
4. One **implementer subagent per ready ticket**, each in **its own worktree on its own branch** (see
   `mattpocock-using-git-worktrees`). Each implementer:
   - confirms the worktree is based on the integration branch and resets onto it if not;
   - builds the ticket with the TDD skill (`mattpocock-tdd`);
   - merges the integration tip into its own branch **before reporting done**, so the integration merge is a fast-forward.
5. When an implementer finishes, a **merger subagent** merges its branch into the integration branch.
6. If the merge unblocks tickets (the frontier changed), start new implementers immediately; that keeps concurrency at its maximum.
7. When all tickets are done, run `mattpocock-code-review` on the integration branch and fix everything it raises in **one** implementer.
8. If a draft PR exists, mark it ready (write its body with `github-pr-workflow/references/pr-body-shape.md`); otherwise resolve each
   ticket per the tracker's convention and report the integration branch name.
9. Delete all implementer worktrees.

## Why this shape works (and where it can fail): my analysis, not from the source

- Merging the integration tip *into the ticket branch first* moves every conflict to the implementer, who has the context, and
  leaves the merger with trivially fast-forwardable branches.
- Worktrees give filesystem isolation; the graph gives logical isolation. Two tickets that touch the same file should be linked
  as blockers rather than run side by side.
- Failure points to plan for: an implementer that never rebases (stale base), a ticket whose blocker list is wrong (a hidden
  dependency shows up as a failing merge), and notes saved inside the repo (they pollute the diff). On this Windows machine the
  repos live in OneDrive, where worktrees and phantom-modified files cause trouble (see the global notes); create worktrees outside the synced tree.
- Related patterns: `dispatching-parallel-agents` for independent problem domains, `mattpocock-subagent-driven-development` for the
  per-task review loop, `merge-reconciler` when two agents' branches conflict.
