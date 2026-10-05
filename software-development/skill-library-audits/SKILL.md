---
name: skill-library-audits
description: "Audit a skill library: frontmatter, links, headers."
version: 1.0.0
author: Hermes Agent (promoted from hermes-agent-skill-authoring references, 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, audit, frontmatter, related-skills, lint, harness, calibration]
    related_skills: [hermes-agent-skill-authoring, skill-intake-and-release, living-docs-governance, ci-gate-design, multi-agent-deliberation]
---

# Skill library audits

## What This Skill Does

Checks a whole directory of `SKILL.md` files for consistency, instead of reading them one by one: YAML frontmatter, `related_skills` links, section headers, name-to-directory matches, and whether a skill's own checks (or an LLM judge) can be trusted. It holds the patterns behind this repo's `tools/audit-skills.py` so they can be rebuilt in another skill repo, plus a calibration method for LLM-judged gates.

## When to Use

- Building or extending an audit script for a repo of skills, and wiring it to CI or a cron job
- A sweep found broken `related_skills`, duplicate names, malformed YAML or inconsistent `## When to use` headers
- Standardising headers or frontmatter across dozens of skills in one pass
- Auditing an agent harness (AGENTS.md, rules, skills) for stale paths, redundancy or dead weight with LLM judges
- Not for writing a single new skill (`hermes-agent-skill-authoring`), vetting third-party skills (`skill-intake-and-release`), or auditing prose claims in docs (`living-docs-governance`)

## Which reference

| Need | Reference | Key facts |
|---|---|---|
| Build the audit script | `references/audit-script-pattern.md` | discover every `SKILL.md`, parse frontmatter with a regex plus `yaml.safe_load`, run a battery of checks, print JSON, exit 0 or 1 on threshold breaches; recognise alternative header spellings; validate cross-references; cron integration |
| Frontmatter checks | `references/frontmatter-audit-pattern.md` | YAML must parse; required fields; description length and final period; closing `---`; `name:` equal to the directory name; the full-library script that found broken refs and name/path mismatches |
| Fix `related_skills` | `references/related-skills-audit.md` | six breakage patterns: core-tool names listed as skills, shortened names, skills that do not exist, stale refs after a reorganisation, missing links, malformed YAML; duplicate `name:` across directories |
| Header cleanup | `references/section-header-standardization.md` | standard section order, capitalisation rules, detection greps, a bulk-fix script, headers that are acceptable and false positives to ignore |
| Trust an LLM-judged gate | `references/harness-audit-dual-judge-traps.md` | three tracks (script-checked correctness, redundancy, usefulness); two blind judges plus planted traps; disagreement means Hold, not a coin flip |

## Procedure

1. Run the repo's existing gate first (`python tools/audit-skills.py`, `python tools/verify-all.py` here); build a new script only for a check it does not make.
2. Write each new check as a function returning issue lines, with a threshold and an exit code, and print findings as `file: rule: message`.
3. Prove every check on a planted defect (a skill with a broken link, a long description, a mismatched name) before trusting a clean run.
4. For `related_skills`, resolve every entry against the set of real `name:` values; fix by removing core-tool names, correcting shortened names, or writing the missing skill.
5. For header or frontmatter rewrites, run the detection grep, apply the bulk fix to a copy, diff, then commit; skip headers listed as acceptable.
6. For an LLM-judged audit, mix known-labelled items into the judge's deck, gate on agreement with the labels, and keep script-checkable correctness separate from judgement.
7. Record the thresholds the repo uses (this repo's description limit is 59 characters) in the script, not in prose.

## Pitfalls

- Trusting the older docs' "60 characters"; the live script is authoritative.
- A frontmatter regex that matches a `---` rule inside the body, or a leading blank line or BOM that hides the frontmatter.
- Fixing a broken `related_skills` entry by deleting it when the link was the only thing connecting the skill to the graph.
- Bulk-rewriting headers and also changing code blocks or quoted examples.
- Treating a judge pair's agreement as proof; without planted traps both can agree on a wrong answer.

## Verification

- [ ] Each new check fails on a planted defect and passes on a clean tree
- [ ] The script exits non-zero on findings and zero otherwise
- [ ] Every `related_skills` entry resolves and no two skills share a `name:`
- [ ] Bulk edits were diffed before commit

## References

- `references/audit-script-pattern.md` - repo-health audit script shape, header recognition, thresholds, cross-reference validation, cron delivery
- `references/frontmatter-audit-pattern.md` - the frontmatter validation rules and the full-library audit script
- `references/related-skills-audit.md` - broken-link patterns and the audit commands that find them
- `references/section-header-standardization.md` - standard headers, capitalisation, detection and bulk fix
- `references/harness-audit-dual-judge-traps.md` - three-track harness audit with blind judges and planted traps (from tech-leads-club/agent-skills)
