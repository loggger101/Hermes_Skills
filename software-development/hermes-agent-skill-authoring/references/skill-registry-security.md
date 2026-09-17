---
description: "Skill registry supply-chain + installer security patterns, mined from tech-leads-club/agent-skills (MIT code / CC-BY-4.0 content)"
source_repos: tech-leads-club/agent-skills @ main 2026-09-16 (SECURITY.md, tools/validate-skills.ts, packages/cli)
verified_date: "2026-09-16"
---

# Skill Registry Security Patterns (tech-leads-club/agent-skills — round-27 mine)

A managed skill registry for coding agents ("the secure, validated skill registry") with 92 skills.
Their value to us is not the individual skills but **how they harden a whole class of supply-chain risk**
that applies directly to this brain's own install/sync pipeline (`hermes skills install`, hub lock.json,
`sync-hermes-skills.py`). Threat framing (their SECURITY.md): agent-skill attacks come in four flavors —
malicious payloads (obfuscated code/binaries), credential theft (silent env-var exfiltration), supply-chain
(malicious updates to existing installs), and prompt injection (hidden instructions). Snyk's 2026 report
they cite: **13.4% of marketplace skills contain critical issues** — the baseline risk this design answers.

## The four-threat → guarantee mapping [SRC]

| Threat | Their structural answer | Note for our brain |
|---|---|---|
| Malicious payloads | 100% open source, no binaries; every line auditable | We already refuse binary-only skills at port time — same principle |
| Credential theft | CI static analysis blocks suspicious network calls / secret access before publish | Our `audit-skills.py` checks frontmatter/links but NOT script behavior — see gap list below |
| Supply chain (updates) | Immutable integrity: lockfile + per-skill SHA-256 content hash; code never changes without explicit upgrade | hub lock.json records install metadata but no content hash — the one pattern worth stealing |
| Prompt injection | Human curation / manual review of every prompt for safety boundaries | We do this ad hoc at port time; their version is a standing gate with named reviewers in allowlist entries |

## Installer defense-in-depth (packages/cli) [SRC]

Five independent layers, each operation passes through **all** — no single bypass suffices:

1. **Input sanitization.** Skill names/paths stripped of path separators (`/\`), null bytes +
   Windows-forbidden chars (`:*?"<>|`), leading/trailing dots+spaces, collapsed `..`, forced ≤255 chars,
   empty → `'unnamed-skill'`. Blocks the classics: `../../../etc/passwd`, `skill\0name`, `.hidden`.
2. **Path containment (post-sanitization belt).** Every resolved target must satisfy
   `normalize(resolve(target)).startsWith(normalize(resolve(base)) + sep)` — both sides fully resolved
   first, and the separator is appended to the base so `/allowed/dir` does not match `/allowed/directory`.
   Applied at every read/write/delete call site (install/get/remove/isInstalled), not once in a helper.
3. **Symlink guard.** `lstat()` never `stat()` (detects without following → no TOCTOU); symlink targets
   resolved and re-checked against the base dir even for chains; `ELOOP` caught + link force-removed; on
   Windows, directory junctions instead of symlinks.
4. **Lockfile integrity.** Strict schema validation on every read (invalid file migrates to clean state —
   no silent corruption); writes are backup → `.tmp` → atomic rename (kill mid-write leaves old intact);
   per-skill SHA-256 content hash for tamper detection; removal only of locklisted skills (`--force` is
   audit-logged).
5. **Append-only audit trail.** JSONL at `~/.config/agent-skills/audit.log`; entries never overwritten —
   the forensic record of every install/update/remove with success/failure counts and timestamps.

**Portable rule:** an installer that writes to a user's agent directory is writing to *prompt-injection
real estate* (anything in skills/ gets loaded into model context). Treat it like root: sanitize → contain →
verify symlinks → hash-pin → log, all five, every operation.

## Scan-cache + allowlist discipline [SRC]

- Every skill has a SHA-256 content hash; scan results cache in `.security-scan-cache.json` keyed by that
  hash — unchanged skills skip re-scanning (fast enough for every PR), changed ones rescan. Same idea as
  our doc-count gate's machine-truth pattern, applied to security scanning.
- **Allowlist entries are versioned exceptions**: `skill + code` match key, mandatory human `reason`,
  named `allowedBy` GitHub identity, `expiresAt` strongly recommended — expired entries auto-reactivate
  the finding so no exception becomes permanent. The allowlist is committed and reviewed in every PR:
  *exceptions are visible or they don't exist.* This is the exact anti-pattern our `.hub/lock.json`
  'dangerous' verdict on parallel-cli suffered from (a one-time manual override with no expiry).

## MCP server as narrow attack surface [SRC]

Their registry-reading MCP server: read-only, local stdio only (no network endpoint), **path validation
against the manifest's `files[]` array before any fetch** (arbitrary-URL-fetch is structurally impossible),
zero local filesystem access, and stdout reserved for JSON-RPC with all logs to stderr. The generalization:
an MCP server that serves content should validate *every requested path against a declared file list* —
the manifest itself becomes the allowlist, so prompt-injection-via-arbitrary-fetch dies at the API boundary.

## Structural validator (tools/validate-skills.ts) [SRC]

342-line stdlib-ish TS check suite per skill; notable checks beyond our audit gate:

- **Description trigger test**: description must contain a trigger phrase (`use when`, `trigger`,
  "user says"...) — a skill whose description never fires is dead weight in the context window. Our
  descriptions carry triggers by convention but nothing enforces it; cheap to add as an audit warning.
- **Negative-scope test**: description should state what NOT to use for (`do not use`, `not intended for`)
  — mirrors our own 'When to Use' anti-patterns, formalized as a checkable string property.
- **Body length budget**: >500 lines = warning "consider moving content to references/" (progressive
  disclosure enforced numerically). We have no such cap; hub skills occasionally run long.
- **Example + error-handling presence** in body (regex-level, deliberately weak — a smell detector not a proof).
- **Reference-linking**: every file under `references/` must be mentioned in SKILL.md or it's flagged —
  the same discoverability lesson as our round-21b linked_files fix, automated.

## Gaps this pattern exposes in our own pipeline (action list) [ANALYSIS]

1. **No content hash on hub installs.** `lock.json` records what was installed but not *what bytes*; a
   malicious upstream update is indistinguishable from a benign one until re-read. Adding per-skill SHA-256
   to the lock + verifying at sync time would close the supply-chain row of their threat table for free
   (we already compute hashes during parity diffs — persist them). *Still open.*
2. **No script-behavior audit.** Our `audit-skills.py` validates frontmatter/links/counts; it never inspects
   what a skill's scripts do at runtime (network calls, env access). Their CI static-analysis gate is the
   missing layer for our 145+ tracked scripts. **Closed in round-27b** — `audit-skills.py` now runs check 7:
   a zero-threshold hardcoded-secret scan over every skill-content `.py/.sh/SKILL.md` (AWS/GitHub/OpenAI/Slack
   token shapes, PEM blocks, non-placeholder `password=` literals; env reads excluded), wired into verify-all
   and self-tested by `tools/mutation-test-secret-gate.py`. The deeper runtime-behavior layer (network-call
   analysis) remains open — the secret scan is its minimum viable form.
3. **No expiry on manual security overrides.** The parallel-cli 'dangerous' scan verdict is a standing,
   unreviewed exception — the exact anti-pattern their `expiresAt` field exists to kill. *Still open.*

## Exhaustion status (rounds 28/28b/28c, complete 2026-09-17) [ANALYSIS]

Round 27 mined SECURITY.md + installer only; round 28 mined the REST of the repo at source level — all 92 skills'
frontmatter/bodies (every one tracked in an explicit examined/unseen ledger), `packages/mcp` (full server), `.github/workflows/release.yml`,
`tools/validate-skills.ts`, registry generator (`skills-catalog/src/{utils,generate-registry}.ts`), CONTRIBUTING.md governance. Ported with
attribution: the-jury protocol + its tally script → `software-development/dispatching-parallel-agents/references/multi-agent-deliberation-jury.md`;
the-judge's bypass scanner → `github/github-code-review/scripts/scan_bypasses.py` (live-tested). New refs across rounds 28–28c: MCP server design patterns, spec-driven patterns + eval methodology (+ tlc-spec-lean §6b), harness dual-judge trap audit, monolith-decomposition pipeline, modular-design-principles violations/split-criteria, discovery-interview-and-critique protocols, ADR/RFC/TDD formats (doc-coauthoring), repository threat modeling (security-review), bounded self-heal loop (cron-pipeline-watchdog SKILL.md), Vercel Web Interface Guidelines UI checklist (`web-development/static-site-patterns/references/web-interface-guidelines-ui-checklist.md` — the one full verbatim port this repo received, MIT). gh-fix-ci gained field-drift + job-log-fallback pitfalls. Remaining unmined surfaces are non-knowledge by nature: marketplace Next.js UI, CLI TUI components (React+Ink), Nx generator scaffolding.

**Final disposition ledger for explicitly-rejected clusters (do NOT re-mine):** gtm/ (17 skills — marketing domain outside brain scope; already integrated in round 24 via marketingskills); cloud deploy vendors (aws/cloudflare/netlify/render/vercel) = vendor CLI walkthroughs, no portable patterns beyond what ci-ratchets covers; framework dev skills (rails-dev/react-native-expert/shopify-developer/frontend-blueprint/react-composition-patterns/tactical-ddd/coding-guidelines — coding-guidelines is the Karpathy guidelines already reflected in our python-craft/mattpocock cluster); atlassian MCP wrappers (jira/confluence) = thin API maps for tools this brain doesn't use; figma pair + web-automation/playwright-skill + chrome-devtools = tool-specific operation guides, no general knowledge beyond what dogfood/adversarial-ux-test cover; excalidraw-studio/mermaid-studio/nx-* = overlap with our creative/diagram-design or Nx-vendor specifics; sentry monitoring skill = thin API map (our rest-api-client covers the pattern); web-quality-audit/perf-*/core-web-vitals/seo/web-accessibility/web-best-practices/security-best-practices/react-best-practices = standard checklists whose substance is already in static-site-patterns + website-audit cro-form-ux-checklists.md — EXCEPT Vercel's Web Interface Guidelines, which had zero coverage and was ported (28c); subagent/cursor-subagent creators → the skill-vs-subagent decision tree is generic enough to be noted here: complex multi-step task needing ISOLATED context ⇒ subagent; one-off action or procedure without isolation need ⇒ skill.

## CI pipeline patterns (.github/workflows/release.yml) [SRC]

- **Fork-PR security scanning via Merge Queue**: GitHub does not expose repo secrets to fork workflows, so their Snyk scan
  runs only on same-repo PRs — but a second job triggers on `on: merge_group` (the event fires when a PR enters the Merge
  Queue), where it DOES run with base-repo secrets; requiring that status check blocks merge for ALL PRs including forks.
  Generalization: any secret-gated CI step can be made fork-proof by re-running it in a `merge_group` job and making it a required check.
- **Change-scoped release detection**: per release group, `git diff --name-only <latest-tag-for-group>..HEAD -- <group paths>`;
  empty ⇒ skip that group entirely (no tag bump, no publish). Tag prefixes disambiguate groups (`v*`, `skills-catalog-v*`, `mcp-v*`).
- **Bot-loop prevention**: release jobs filter `github.actor != '<release-bot>[bot]'` AND commit message not starting with the bot's own prefix.
- **Snapshot publishing for PRs** (label-triggered): version `0.0.0-pr<N>.<shortsha>`, publish to npm tag `snapshot` WITH provenance, checkout of the fork branch done via a generated GitHub App token; CI-pass verified before publishing.
- Generated data committed by CI ("chore(release): update generated skills data") only when changed — same marker-block regen discipline as their VERSIONS.md (see skill-repo-release-engineering.md).

## Contribution governance: issue-first flow (CONTRIBUTING.md) [SRC]

They moved from open PRs to **issue-first** because "at volume, a machine-generated PR is not reliably distinguishable from a large
human one" — the entry point became issues where intent settles before code; members keep direct-PR rights. Credit rules: idea author's
handle in `metadata.author`, issue linked from implementing commit, release-notes credit. AI-assisted contributions are expected with two
conditions: you can defend every line, and you disclose agent involvement — "an unreviewed agent output submitted as your own work is the
thing this policy exists to filter." (Relevant if our repo ever gets automated-PR volume; see also `github/github-pr-workflow/references/agent-contribution-guardrails.md`.)

## Environment pitfall they document [SRC]

"Each tool sets NODE_ENV for you (`test` for Jest, `production` for a Next build). A `NODE_ENV=development` exported in your profile makes
`nx build marketplace` fail with confusing React errors such as `Cannot read properties of null (reading 'useContext')` during prerender. If a
build fails only on your machine, check `echo $NODE_ENV` first." — the classic shell-env-shadowing-tool-env failure; add to any Next.js static-export troubleshooting list.

## Licensing note [VERIFIED]

Code = MIT; skill content (SKILL.md files) = CC-BY-4.0 unless individual files say otherwise (dual-license
note in LICENSE). Attribution required if porting any of their 92 skills — none were ported this round
(overlap with existing brain coverage: architecture/DDD cluster, cloud-deploy vendors, figma/playwright);
only the registry-security patterns above are recorded.
