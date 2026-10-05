---
name: skill-intake-and-release
description: "Vet, import, evolve and release third-party skills."
version: 1.0.0
author: Hermes Agent (promoted from hermes-agent-skill-authoring references, 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, supply-chain, registry, installer, versioning, release, dspy, gepa, skill-seekers]
    related_skills: [hermes-agent-skill-authoring, skill-library-audits, security-audit, secret-vault-pattern, github-pr-workflow, ci-gate-design]
---

# Skill intake and release

## What This Skill Does

Covers the life of a skill that comes from somewhere else, and the repo that ships skills: how to harden an installer or registry, how to turn a generator's draft or a vendor's skills into repo-format skills, when automated text evolution helps and what its scorer really measures, and how a multi-skill repo versions, regenerates and releases itself.

## When to Use

- Installing, syncing or mirroring skills from a registry, a vendor package or another repo
- Writing or reviewing an installer, lockfile or MCP server that serves skill content
- Turning Skill Seekers output or a vendor's `skills/` directory into skills for this repo
- Deciding whether to run DSPy+GEPA skill evolution, and reading its results
- Setting up repo versioning, a changelog that drives releases, generated README blocks with drift checks, or per-skill evals
- Not for writing one skill by hand (`hermes-agent-skill-authoring`) or auditing a library's consistency (`skill-library-audits`)

## Which reference

| Need | Reference | Key facts |
|---|---|---|
| Harden a registry or installer | `references/skill-registry-security.md` | four threats (payloads, credential theft, update supply chain, prompt injection); five installer layers: sanitize, path-contain, symlink-guard, hash-pinned lockfile with atomic writes, append-only audit log; scan cache keyed by content hash; allowlist entries with reason, owner and expiry; an MCP server that validates every path against the manifest |
| Draft skills from a codebase or docs | `references/skill-seekers-generated-drafts.md` | Skill Seekers 3.10.0 ran offline in 3 s: its API reference and dependency graph were good, its `SKILL.md` was boilerplate that lost the README's own overview; keep the references, rewrite the skill by hand |
| Import a vendor's skills | `references/vendor-shipped-skills-preline.md` | discover-then-fetch with opaque IDs, scoped list calls, deterministic placement rules, a single script entry point; a `name:` that differs from its directory fails this repo's audit |
| Evolve skill text | `references/skill-evolution-pipeline.md` | GEPA optimises keyword overlap with the rubric (rubric copied verbatim scored 1.00, a correct answer in other words 0.35); the constraint gate passes unclosed frontmatter and a 90% shrink; its 15 000-character cap would reject 19% of this repo's skills |
| Version and release a skill repo | `references/skill-repo-release-engineering.md` | two version layers (repo and per-skill); a `VERSIONS.md` channel for installed copies; marker-block regeneration with a `--check` mode; an idempotent release cut from the changelog block; validation scoped to changed skills; `evals/evals.json` per skill; renames leave stale folders |

## Procedure

1. Record provenance and licence before importing anything: source URL, commit, licence, and whether the text may be redistributed.
2. Read every script and hook in the incoming skill; a skill directory is loaded into model context, so treat install like writing to a privileged location.
3. Import as a draft: rewrite `SKILL.md` to this repo's frontmatter, trigger-style description and sections; keep generated references only after skimming them for errors.
4. Run the library audit (`python tools/audit-skills.py`) and the repo gates (`python tools/verify-all.py`); fix name and directory mismatches by renaming one side.
5. For an installer you write, apply all five layers on every operation and log each install, update and removal.
6. Only run skill evolution when a scorer exists that measures the behaviour; replace the keyword-overlap metric, review the diff, and re-run the repo gates on the output.
7. When shipping a release, bump the repo version in the same PR as the change, regenerate marker blocks, and let the changelog block be the release notes.

## Pitfalls

- Importing a generated draft as-is: boilerplate descriptions, absolute local paths and empty fields pass nothing useful to the agent.
- Treating "improvement" printed by an evolution run as evidence; with five holdout examples and a word-overlap score it is noise.
- One-time allowlist overrides without an expiry; they become permanent.
- Checking a path prefix without a trailing separator, so `/allowed/dir` matches `/allowed/directory`.
- Renaming skills in a restructure and leaving the old folders behind.

## Verification

- [ ] Source, commit and licence recorded for every imported skill
- [ ] No imported script executes unreviewed code
- [ ] Imported skills pass `audit-skills.py` and `verify-all.py`
- [ ] Any evolved text was scored by a metric that reads behaviour, then diffed
- [ ] Repo version, per-skill versions and changelog agree in the release PR

## References

- `references/skill-registry-security.md` - registry and installer supply-chain patterns from tech-leads-club/agent-skills (installer layers, scan cache, allowlists, MCP path validation, CI, governance)
- `references/skill-seekers-generated-drafts.md` - Skill Seekers 3.10.0 as a draft generator and how to finish its output
- `references/vendor-shipped-skills-preline.md` - skills shipped inside a UI library, patterns to copy and where they clash with our conventions
- `references/skill-evolution-pipeline.md` - DSPy+GEPA pipeline: CLI, cost, when not to use it, what its metric, gate and session importer really do
- `references/skill-repo-release-engineering.md` - versioning layers, update channel, generated blocks, release automation, evals, migration lessons (from coreyhaines31/marketingskills)
