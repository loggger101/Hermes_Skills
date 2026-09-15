# Skill-Repo Release Engineering (versioning, update channel, generated blocks)

Source: coreyhaines31/marketingskills @ 5b2c000 (MIT; mined 2026-09-15). A 50-skill repo with a mature release system worth borrowing for any multi-skill repository — including this one. Distilled from `AGENTS.md` versioning rules, `VERSIONS.md`, `.github/workflows/{release,sync-skills,validate-skill}.yml`, `.github/scripts/sync-skills.js`, `scripts/sync-partners.mjs`, and the per-skill `evals/evals.json` harness.

## Two-layer versioning (repo release vs per-skill)

Two independent x.y.z numbers with different bump rules:

**Repo release version** — one number shared by `.claude-plugin/plugin.json` → `version`, marketplace metadata, and the `VERSIONS.md` changelog headings:
- **x** = repo-wide changes (restructures, spec changes, breaking)
- **y** = new skill(s) added
- **z** = updates to existing skills — *including substantial ones*. A new reference file in an existing skill is a z bump, never y.

**Per-skill version** — `metadata.version` inside each SKILL.md frontmatter, mirrored in the VERSIONS.md table. Bump on ANY shipped change to that skill (minor = new capability or description triggers; patch = fixes/clarifications). Why per-skill matters: **the update check compares VERSIONS.md against users' local skill metadata — an unbumped change is invisible to installed users.**

Discipline rules observed in their history:
- Bump the repo release version **in the same PR** that ships the change (they shipped 2.7.0/2.8.0 without touching plugin.json and needed a catch-up commit later).
- The per-skill table row (`| skill | version | last updated |`) is what agents diff — keep it machine-parseable.

## VERSIONS.md as an agent self-update channel

The repo ships `VERSIONS.md` (version table + newest-first changelog) and instructs consuming agents, in AGENTS.md:
1. **Once per session**, on first skill use: fetch the raw `VERSIONS.md`, compare versions against local copies.
2. **Prompt only if meaningful**: ≥2 skills have updates, OR any single skill has a major bump (1.x → 2.x). Never nag for one patch note.
3. Non-blocking notification at end of response ("Skills update available: X marketing skills have updates…").
4. On "update skills": `git pull` in the clone dir + confirm what changed.

This is a cheap, no-infrastructure freshness protocol for any skill library distributed as a git repo — better than nothing, and it keeps stale installs from silently drifting. (For this brain: our sync-hermes-skills cron already does the local↔repo parity direction; the missing piece would be an equivalent check when *installing* third-party skills into `~/.claude/skills` or a project's `.agents/skills/`.)

## Marker-block regeneration with CI drift checks

Generated content inside hand-maintained files is wrapped in comment markers and owned by exactly one script:

```markdown
<!-- PARTNERS:START -->
| Partner | Category | Guide |   ← regenerated from partners.json
...
<!-- PARTNERS:END -->
```

- `node scripts/sync-partners.mjs` regenerates every marked block (README Partners section + registry table) from the canonical JSON; everything outside markers is untouched.
- **`--check` mode for CI**: recompute each block, compare to what's on disk, exit 1 if anything drifted — "run `node scripts/sync-partners.mjs --check` to verify nothing has drifted." The write path and the check path share one codebase (same rendering function), so a drift failure means exactly "someone hand-edited generated content or forgot to run the script."
- Same pattern in `.github/scripts/sync-skills.js`: scans `skills/*/SKILL.md`, regenerates the README skills table between `<!-- SKILLS:START/END -->` markers, updates marketplace.json + plugin.json skill counts — committed back by a GitHub Action (`git-auto-commit-action`) so contributors never touch generated files.

This is the same philosophy as this repo's index generators (gen-skills-index.py et al.) but adds two things worth copying: **(a)** a `--check` mode wired into CI that fails on drift, and **(b)** generation committed by bot action rather than relying on each contributor remembering to run it.

## Idempotent auto-release from markdown blocks

`.github/workflows/release.yml`:
- Triggers only when `.claude-plugin/plugin.json` or `VERSIONS.md` changes on main (version bump = release intent).
- Reads the version, checks if tag `v$VERSION` exists → **idempotent** ("safe to re-run / backfill manually").
- Extracts release notes by regex-splitting VERSIONS.md on `\n### x.y.z (date)\n` and taking that block; title = first non-empty line with markdown stripped, truncated at 100 chars.
- `gh release create v$VERSION --target <sha> --title … --notes-file …`.

Properties worth copying: the changelog IS the release notes (one source of truth — no separate RELEASE_NOTES file to drift); idempotency makes backfilling a forgotten tag trivial; path-filtered trigger means content-only PRs never create releases.

## Change-scoped validation matrix

`validate-skill.yml`:
- `detect-changes` job: `git diff --name-only BASE HEAD | grep 'SKILL.md$' | xargs -I{} dirname {} | sort -u` → JSON array of changed skill dirs (handles both PR base/head and push before/after).
- `validate` job runs **only if the list is non-empty**, with a matrix over just those skills (`fail-fast: false`) using an external validator action — so validation cost scales with change size, not repo size.

For this brain that's a direct optimization on verify-all.py for CI contexts where only 1–2 skills changed (the local pre-commit gate still runs everything; the remote job could scope to touched skills).

## Per-skill evals harness (`evals/evals.json`)

Every skill ships `evals/evals.json`: `{skill_name, evals: [{id, prompt, expected_output, assertions[], files[]}]}`. The shape:
- **prompt** — a realistic user request (casual phrasing included deliberately: "this page isn't converting. can you take a look?").
- **expected_output** — prose describing the correct behavior trajectory ("Should check for product-marketing.md first… Should provide recommendations organized as Quick Wins, High-Impact Changes, and Test Ideas").
- **assertions** — 5–10 machine-checkable bullets derived from expected_output.

This is a lightweight behavioral spec per skill: it encodes *trigger phrases that must fire* (eval id 3 above tests the casual phrasing), *required first steps*, and *output structure*. It complements this brain's structural gates (frontmatter, related_skills resolution) exactly as `behavioral-skill-testing.md` describes — but is cheap enough to ship with every skill rather than only discipline skills. When porting a third-party skill into this repo, keeping its evals file under the skill dir gives future rounds an instant regression suite: run each prompt in a fresh agent session and check assertions.

## Shared-context document pattern (`.agents/product-marketing.md`)

The `product-marketing` skill maintains ONE context doc that every other skill reads first ("check for product marketing context first" is literally the first instruction of ~40 skills). v2.1 added:
- A **`Document version:` header + newest-first dated Changelog** inside the shared doc — since every downstream skill generates against it, a paper trail of *what changed and why* (positioning/ICP shifts) makes cross-skill output traceable. On any substantive save: bump version, update Last updated, prepend one changelog line naming sections touched + reason; never rewrite past entries.
- **Auto-draft from codebase** as the default onboarding path (study README/landing pages/package.json → draft V1 → user corrects), with verbatim customer language pushed for over polished descriptions.

Generalizable: any multi-skill workflow that repeats the same foundational context benefits from one versioned shared doc + "read it first" convention, instead of re-asking per task. (Hermes equivalent already exists — memory files; this adds the *per-project* variant and its changelog discipline.)

## Partner/sponsorship governance for content repos

`tools/PARTNERS.md` is a model for keeping paid presence out of editorial recommendations in an open repo:
- **One principle**: "Sponsorship funds the work, never the recommendations." Money buys a *disclosed presence*, never bias.
- Three entry kinds: neutral tool integration (anyone can PR one) / ◆ Verified Partner (paid + vetted; same guide format as neutral PLUS disclosure header in-file, registry marker, partners.json entry) / house tool (maintainer's own — stricter disclosure than a partner).
- **Disclosure travels with the file** — skills get forked and re-indexed across ecosystems, so the disclosure must survive forking: it lives at the top of the artifact itself.
- The integrity rubric for ANY content naming a tool: options not one answer (always list real alternatives incl. free/DIY); at the point of relevance; no forced endorsement ("best"/"recommended" banned); facts over framing; disclose self-interest; **the swap test** — "if you swapped your tool for a competitor, the section should still read as fair."
- Lapse handling: 30-day flagged-unmaintained window before removal so installs never break silently; deactivation = `active:false` in the canonical JSON (keeps history).

Relevant to this brain's hub-installed skills and any future sponsorship of our own repos.

## Claude Code-only dynamic injection (`!`command``)

Claude Code executes `` !`shell command` `` embedded in SKILL.md at load time — the model sees output, not instruction. Useful: auto-inject a shared context file (`` Product context: !`cat .agents/product-marketing.md 2>/dev/null || echo "No product context…" ` ``), today's date, current git branch. **Cross-agent hazard**: other agents see the literal string as garbled instructions — keep it out of cross-harness SKILL.md files; apply only in local `.claude/skills/` overrides. (Recorded here because this brain ports skills across harnesses.)

## v1→v2 migration lesson: renames leave stale folders

Their 2.0 renamed 17 skills + consolidated two into one (`page-cro`+`form-cro` → `cro`). Installing over a v1.x install left **stale old-name folders alongside the new ones** — both live, both discoverable, ambiguous which wins. Their fix: an explicit cleanup list in the README upgrade section + fallback filename checks in every skill (skills check `.claude/product-marketing-context.md` as legacy fallback so nothing breaks if users don't migrate). Generalizable to any rename pass over a distributed library: ship the removal list with the release, and make consumers tolerant of both old and new locations during one transition window.
