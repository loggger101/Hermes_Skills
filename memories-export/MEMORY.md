SKILL.md description field has a hard 59-char limit (60-char budget minus trailing period); skill index truncates >57 chars to '...' destroying routing signal. Count string length before saving.
§
Hermes SKILL.md files require '---' as first line (YAML frontmatter); skills created without leading '---' fail with 'must start with YAML frontmatter' error.
§
mattpocock-* skills are user-owned (not curator-managed); to edit them in background, need 'hermes curator adopt <skill-name>' first. Cannot patch user-owned skills autonomously.
§
When consolidating overlapping third-party skills into Hermes skills: keep one canonical skill (absorbs related content), delete others with absorbed_into flag, update all related_skills cross-refs to point to the survivor. Pattern: mattpocock-security-review absorbed both mattpocock-static-analysis (CodeQL/Semgrep) and the OWASP checklist from openai's security-best-practices.