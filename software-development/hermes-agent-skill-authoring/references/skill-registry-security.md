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
   (we already compute hashes during parity diffs — persist them).
2. **No script-behavior audit.** Our `audit-skills.py` validates frontmatter/links/counts; it never inspects
   what a skill's scripts do at runtime (network calls, env access). Their CI static-analysis gate is the
   missing layer for our 145+ tracked scripts. Minimum viable: grep-level denylist (subprocess + socket /
   requests to non-allowlisted hosts) as an audit warning class.
3. **No expiry on manual security overrides.** The parallel-cli 'dangerous' scan verdict is a standing,
   unreviewed exception — the exact anti-pattern their `expiresAt` field exists to kill.

## Licensing note [VERIFIED]

Code = MIT; skill content (SKILL.md files) = CC-BY-4.0 unless individual files say otherwise (dual-license
note in LICENSE). Attribution required if porting any of their 92 skills — none were ported this round
(overlap with existing brain coverage: architecture/DDD cluster, cloud-deploy vendors, figma/playwright);
only the registry-security patterns above are recorded.
