---
name: repo-agent-instructions
description: "Write CLAUDE.md/AGENTS.md with incidents and gates."
version: 1.0.0
author: Hermes Agent (from the knowledge vault's in-repo-agent-instructions page, four of the owner's repos read 2026-10-01)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [claude-md, agents-md, repo-instructions, memory, conventions, documentation, agent-tooling]
    related_skills: [mattpocock-writing-for-agents, repo-atlas, living-docs-governance, one-authority-per-fact, codebase-onboarding]
---

# In-repo agent instructions

## What This Skill Does

Describes what a committed `CLAUDE.md` / `AGENTS.md` should contain, based on four of the owner's repos that converged on the same habits independently, and how such a file relates to per-machine memories. The in-repo file is the committed, versioned authority shared by every agent and both machines; memories reach one machine only.

## When to Use

- Creating or restructuring a repo's `CLAUDE.md` or `AGENTS.md`
- Deciding whether a rule belongs in the repo file or in a memory
- A repo with unwritten rules (frozen tags, byte-identical output contracts) that agents keep breaking
- Not for the general craft of writing for agents (`mattpocock-writing-for-agents`), auto-generated orientation docs (`repo-atlas`), or exploring an unfamiliar repo (`codebase-onboarding`)

## What good files share

1. **Every rule carries the incident that made it** ("each one exists because it broke in a past round"). A bare rule invites a later session to simplify it away; the incident is the argument against.
2. **A register of things decided or measured, so nobody reopens them** ("Decided: do not re-open", "Measured and declined", closed items that stay closed), each dated with its reason.
3. **Generated files named up front** as editing rules: what is built and never edited, and which input to edit instead.
4. **The gate to run before committing**, stated as a command, with what it proves.
5. **Numbers that rot are deleted, not corrected**: no line counts, no interpreter version; tell the reader to ask the machine.
6. **Portable split**: put the rules in `AGENTS.md`, which any agent reads, and make `CLAUDE.md` a one-line `@AGENTS.md` import.
7. **Say how to read it**: a huge file needs an opening table of which part to grep for which task; a short one can be read whole.

## Memory vs file

- The file is shared by both machines and every agent; a memory is per machine. Memory should **point at** the file, not copy it.
- When the two disagree, the file wins; when memory corrects the file, the file should then catch up and the memory be removed.
- Whether an agent may push, merge or sign commits is decided only by memories today (side-branch workflow, no live-site work, no commit attribution), so such rules hold on one machine and not the other; write them into the repo file if they should travel.

## Procedure

1. List the rules a new agent keeps breaking and attach the incident and date to each.
2. Add the decided-register, the generated-files list and the pre-commit gate.
3. Remove any count, version or length that will rot; link to the authority instead (`one-authority-per-fact`).
4. If other agents will read it, put the content in `AGENTS.md` and import it from `CLAUDE.md`.
5. Keep git rules explicit (never rebase, never stash, branch then merge) and push permissions where they will be read.
6. Review it when a memory contradicts it.

## Pitfalls

- A count copied from a memory into the file into a wiki: wrong in three places.
- Rules with no reason attached.
- A file so long it cannot be read whole with no routing table at the top.
- Putting repo-specific rules only in a machine's memory.

## Verification

- [ ] Each rule names its incident
- [ ] Decided items, generated files and the pre-commit gate are listed
- [ ] No rotting counts or versions are stated
- [ ] Repo-wide permission rules are in the file, not only in memory
