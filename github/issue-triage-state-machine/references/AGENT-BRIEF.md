# Writing Agent Briefs

An agent brief is a structured comment posted on an issue or PR when it moves to `ready-for-agent`. It is the authoritative specification that an AFK agent will work from. The original body and discussion are context: **the brief is the contract**.

The brief states what the agent should do, which stretches to both surfaces: for an issue, building the change from nothing; for a PR, what's left to do *to the existing diff* — finish it, close gaps, address review points. Same principles either way.

## Principles

### Durability over precision
The item may sit in `ready-for-agent` for days or weeks; the codebase will change meanwhile. Write so the brief stays useful as files are renamed, moved, refactored:
- **Do** describe interfaces, types, behavioral contracts
- **Do** name specific types, function signatures, config shapes to look for or modify
- **Don't** reference file paths (they go stale)
- **Don't** reference line numbers
- **Don't** assume current implementation structure remains

### Behavioral, not procedural
Describe **what** the system should do, not **how**. The agent explores fresh and makes its own implementation decisions.
- Good: "The `SkillConfig` type should accept an optional `schedule` field of type `CronExpression`"
- Bad: "Open src/types/skill.ts and add a schedule field on line 42"

### Complete acceptance criteria
Every brief needs concrete, testable, independently verifiable criteria.
- Good: "`gh issue list --label needs-triage` returns issues that have been through initial classification"
- Bad: "Triage should work correctly"

### Explicit scope boundaries
State what is out of scope — prevents gold-plating and assumptions about adjacent features.

## Template

```markdown
## Agent Brief

**Category:** bug / enhancement
**Summary:** one-line description of what needs to happen

**Current behavior:**
What happens now (broken behavior for bugs; status quo the feature builds on).

**Desired behavior:**
What should happen after the work is complete. Specific about edge cases and error conditions.

**Key interfaces:**
- `TypeName`: what changes and why
- `functionName()` return type: current vs desired
- Config shape: new options needed

**Acceptance criteria:**
- [ ] specific, testable criterion 1
- [ ] specific, testable criterion 2

**Out of scope:**
- thing that should NOT change
- adjacent feature that seems related but is separate
```

## Examples

### Good (bug)
```markdown
## Agent Brief
**Category:** bug
**Summary:** Skill description truncation drops mid-word, producing broken output

**Current behavior:** When a skill description exceeds 1024 characters it is truncated at exactly 1024 regardless of word boundaries — descriptions end mid-word (e.g. "Use when the user wants to confi").

**Desired behavior:** Truncation breaks at the last word boundary before 1024 chars and appends "...".

**Key interfaces:**
- The `SkillMetadata` type's `description` field: no type change, but validation/processing logic must respect word boundaries
- Any function that reads SKILL.md frontmatter and extracts the description

**Acceptance criteria:**
- [ ] Descriptions under 1024 chars unchanged
- [ ] Over 1024 truncated at last word boundary before 1024
- [ ] Truncated descriptions end with "..."
- [ ] Total length including "..." ≤ 1024

**Out of scope:** changing the 1024 limit; multi-line description support
```

### Good (enhancement)
```markdown
## Agent Brief
**Category:** enhancement
**Summary:** Add `.out-of-scope/` directory for tracking rejected feature requests

**Current behavior:** Rejected features are closed with `wontfix` + comment. No persistent record of decision/reasoning; future similar requests require recalling prior discussion.

**Desired behavior:** Rejected feature requests documented in `.out-of-scope/<concept>.md` capturing decision, reasoning, and links to all requesting issues. Triage checks these files for matches early.

**Key interfaces:**
- Markdown format: `# Concept Name`, `**Decision:**`, `**Reason:**`, `**Prior requests:**` list with issue links
- Triage workflow reads all `.out-of-scope/*.md` early and matches by concept similarity

**Acceptance criteria:**
- [ ] Closing a feature as wontfix creates/updates the file
- [ ] File includes decision, reasoning, link to closed issue
- [ ] Existing match → append to "Prior requests", no duplicate file
- [ ] Triage surfaces matching prior rejections

**Out of scope:** automated matching (human confirms); reopening rejected features; bug reports (only enhancement rejections)
```

### Good (PR)
For a PR, "Current behavior" describes the state of the diff and the brief asks to finish/fix it:
```markdown
## Agent Brief
**Category:** enhancement
**Summary:** Finish the contributor's `--json` output flag for `triage list`

**Current behavior:** The PR adds `--json` serializing the issue list. Happy path works; two gaps remain — errors still print as human text, and no test coverage for the new flag.

**Desired behavior:** With `--json`, all output (incl. errors) is well-formed JSON on stdout; exit codes unchanged; default output untouched when flag absent.

**Key interfaces:**
- Error path emits `{ "error": string }` under `--json` instead of plain text
- Reuse the serializer the PR already added — don't introduce a second

**Acceptance criteria:**
- [ ] Valid JSON for success and error cases
- [ ] Exit codes match non-JSON command
- [ ] Test covers `--json` success + one error case
- [ ] Default output byte-for-byte unchanged

**Out of scope:** `--json` on other commands; changing the PR's defined success payload shape
```

### Bad (what to avoid)
```markdown
## Agent Brief
**Summary:** Fix the triage bug
**What to do:** The triage thing is broken. Look at the main file and fix it. The function around line 150 has the issue.
**Files to change:** src/triage/handler.ts (line 150), src/types.ts (line 42)
```
Bad because: no category; vague description; stale-prone paths/lines; no acceptance criteria; no scope boundaries; no current-vs-desired behavior.
