# Library Audit Methodology

A systematic approach to auditing a collection of skills (or any artifacts) for quality, consistency, and completeness.

## When to Use

Use when the "bug" is not a code bug but a quality gap across a collection of documents — e.g., all skills in a repository are thin, have inconsistent formatting, missing sections, or broken links.

## The Feedback Loop

Apply the same tight-feedback-loop discipline from `mattpocock-diagnosing-bugs`:

### 1. Build a Signal

Define a scoring rubric and score every artifact:

| Criterion | Points | Check |
|-----------|--------|-------|
| **Frontmatter** | 5 | Has `name`, `description`, `version`, `author`, `license` |
| **When to Use** | 5 | Clearly states when to use this skill |
| **What This Skill Does** | 5 | Explains the skill's purpose and scope |
| **Prerequisites** | 5 | Lists tools, commands, or setup needed |
| **Process/Steps** | 15 | Numbered, actionable, concrete steps |
| **Examples** | 5 | At least one practical example |
| **Pitfalls** | 5 | Lists common mistakes or gotchas |
| **Verification** | 10 | Checklist or criteria for confirming success |
| **Total** | **50** | Minimum passing score: 40 |

### 2. Score All Artifacts

```bash
# Score all SKILL.md files in the repo
for skill in $(find . -name "SKILL.md" -not -path ".git/*"); do
    score=$(python scripts/score_skill.py "$skill")
    echo "$score $skill"
done | sort -n
```

### 3. Tighten the Loop

- Focus on the lowest-scoring artifacts first
- Each artifact should be fixable in one pass (add missing sections)
- Keep a ledger of scores to track improvement

### 4. Fix Specifically

For each low-scoring artifact:
1. Identify the specific missing section or issue
2. Add the missing section with content specific to this skill
3. Re-score to confirm improvement

### 5. Verify

- Lowest score should improve after each pass
- No artifact should drop in score
- All artifacts should eventually reach 40+ points

## Scoring Script Template

```python
#!/usr/bin/env python3
"""Score a SKILL.md file against the audit rubric."""
import re
import sys

def score_skill(filepath):
    with open(filepath) as f:
        content = f.read()

    score = 0
    checks = [
        (r'name:', 5),                    # Frontmatter: name
        (r'description:', 5),              # Frontmatter: description
        (r'version:', 2),                 # Frontmatter: version
        (r'author:', 2),                   # Frontmatter: author
        (r'license:', 1),                  # Frontmatter: license
        (r'## When to Use', 5),           # When to Use section
        (r'## What This Skill Does', 5),  # What This Skill Does section
        (r'## Prerequisites', 5),        # Prerequisites section
        (r'## Process|## The Process|## Workflow', 10),  # Process section
        (r'```', 5),                     # Has code examples
        (r'## Pitfalls', 5),              # Pitfalls section
        (r'## Verification', 10),         # Verification section
    ]

    for pattern, points in checks:
        if re.search(pattern, content):
            score += points

    return score

if __name__ == "__main__":
    print(score_skill(sys.argv[1]))
```

## Quality Gates for Skill Audits

1. **Frontmatter consistency**: Every skill must have the same frontmatter fields
2. **Section completeness**: All skills must have the 5 standard sections
3. **Link validity**: All `skill_view()` and `references/` links must resolve
4. **Content quality**: Each section must have substantive content (not just headers)
5. **No duplicates**: No two skills with the same name or overlapping purpose

## Reporting Format

```
AUDIT REPORT: Hermes_Skills Repository
Date: YYYY-MM-DD
Total Skills: 127
Average Score: 42.3/50
Skills below threshold (40): 32

THIN SKILLS (score < 30):
  28: security/mattpocock-security-review (missing: Pitfalls, Verification, Prerequisites)
  27: github/github-issue-to-pr (missing: What This Skill Does, Prerequisites)
  ...

ACTIONS:
1. Expand thin skills (score < 30) — target: 50
2. Fill missing sections — target: all skills ≥ 40
3. Fix broken links — target: 0 broken
4. Deduplicate — target: 0 duplicates
```
