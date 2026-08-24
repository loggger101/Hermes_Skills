# Persistent Memory (MEMORY.md)

This is the agent-discovered persistent memory from the Hermes profile at:
`C:\Users\Loggg\AppData\Local\hermes\memories\MEMORY.md`

## Contents

```
SKILL.md description field has a hard 59-char limit (60-char budget minus trailing period); skill index truncates >57 chars to '...' destroying routing signal. Count string length before saving.

Hermes SKILL.md files require '---' as first line (YAML frontmatter); skills created without leading '---' fail with 'must start with YAML frontmatter' error.

mattpocock-* skills are user-owned (not curator-managed); to edit them in background, need 'hermes curator adopt <skill-name>' first. Cannot patch user-owned skills autonomously.

When consolidating overlapping third-party skills into Hermes skills: keep one canonical skill (absorbs related content), delete others with absorbed_into flag, update all related_skills cross-refs to point to the survivor. Pattern: mattpocock-security-review absorbed both mattpocock-static-analysis (CodeQL/Semgrep) and the OWASP checklist from openai's security-best-practices.
```

## Key Learnings

1. **Description hard limit:** 60 characters max (59 + trailing period). The skill index truncates at 57 characters + "...", so the trigger/capability must be self-contained in that window.

2. **YAML frontmatter:** Must start with `---` as the very first bytes (no leading blank line, no BOM). Missing this causes a "must start with YAML frontmatter" error.

3. **mattpocock-* ownership:** These skills are user-owned, not curator-managed. Editing them in background requires `hermes curator adopt <skill-name>` first.

4. **Skill consolidation pattern:** When merging overlapping skills, keep one canonical skill (absorbs related content), delete others with the `absorbed_into` flag, and update all `related_skills` cross-references to point to the survivor. Example: `mattpocock-security-review` absorbed both `mattpocock-static-analysis` and the OWASP checklist from `openai's security-best-practices`.
