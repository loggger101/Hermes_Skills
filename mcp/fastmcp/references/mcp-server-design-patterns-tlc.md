# MCP Server Design Patterns (verified from tech-leads-club/agent-skills @ 0ab82f6)

Source: `packages/mcp/src/*` (~614 lines of server code, FastMCP-based) + SECURITY.md §"MCP Server Security". MIT license.
Mined 2026-09-16. This is a production MCP server that serves an on-demand skill catalog over stdio — the reference design for
**progressive disclosure with integrity**, and several patterns apply to any MCP server we build (see `fastmcp` SKILL.md).

## Progressive-disclosure tool ladder (each step pays only what it needs)

| Tool | Step | Returns |
|---|---|---|
| `search_skills` | 1 — find by intent | ranked matches + short usage hint (fuzzy; never the whole catalog unprompted) |
| `list_skills` | browse, EXPLICIT user ask only | whole catalog grouped by category |
| `read_skill` | 2 — load instructions | SKILL.md body + list of bundled files (frontmatter stripped to save tokens) |
| `fetch_skill_files` | 3a — files meant to be READ | text of references/ files, validated against the registry's `files[]` before any network call |
| `prepare_skill_files` | 3b — files meant to be RUN | checksum-verified files written to a local cache dir + file:// links; contents never enter context |

The read-vs-run split is the key idea: **instructions and reference docs go through context; executable scripts land on disk**
with `$SKILL_DIR` exported, so running them costs zero tokens. The server keeps tool modules thin (registration only) with all logic in pure, directly unit-tested `tools/core/` functions — "anything that costs the agent tokens or touches the filesystem needs a reason recorded in code next to it."

## Integrity: pin, hash, verify-before-write

1. **CDN ref pinned once per process** (`cdn.ts`): prefers an env override (dev/local), else resolves `latest` from the npm registry ONCE and pins that exact version — "avoid mutable @latest URLs for skill content (supply-chain / cache poisoning)." The resolved ref is cached with a promise to dedupe concurrent calls, reset on failure.
2. **Aggregate content hash** (`integrity.ts`): SHA-256 over sorted `filePath + bytes` of the WHOLE file set — same algorithm as the registry generator's (cross-package invariant documented in both places). After downloading all files with `Promise.allSettled`, a mismatch throws: "The CDN content may have been tampered with or is out of sync with the registry." Verify the ENTIRE skill set before writing ANY of it to disk.
3. **Revision-keyed staging** (`staging.ts`): staged dir = `<root>/<skill>/<contentHash[:N]>`. Consequences: writes are ADDITIVE (a new revision lands beside the old — that's what lets the tool honestly declare `destructiveHint: false`, whose documented meaning is "additive, not destructive"); identical bytes already on disk ⇒ left untouched (`idempotentHint: true` holds); superseded revisions pruned only after a grace period ("a script from the previous revision may still be running") and best-effort (prune failure must never fail staging).
4. **Remote code lands owner-only, no execute bit** — `writeFile(..., { mode: 0o600 })`: "running it takes a deliberate act by the caller (invoking an interpreter), never an accidental one." Every destination is re-checked against the revision dir AFTER path resolution (second gate on top of registry-path validation).
5. **Honest tool annotations**: `readOnlyHint`/`destructiveHint`/`idempotentHint` are properties of THIS implementation, verified in code comments — not assurances about intent. The one write-tool also supports `dry_run` returning a preview BEFORE any network fetch or filesystem write ("a write tool should be previewable without the client having to support elicitation").
6. **Stdout reserved for JSON-RPC** — all logging exclusively to stderr (protocol corruption otherwise). Warmup: registry fetched + indexes built at startup, server won't start if CDN unavailable; background refresh on a TTL interval with `.unref()` so it never blocks shutdown; refresh failures log and keep serving the last good index.

## Narrow threat surface by design (SECURITY.md)

Read-only against the registry · no auth needed because stdio-local (no network-exposed endpoint) · path validation makes arbitrary-URL fetch impossible (`fetch_skill_files` checks every requested path against `files[]`) · no local filesystem access except the explicit staging tool · stdout reserved for JSON-RPC. The whole server is ~600 lines — small enough to audit in one sitting, which IS the security property.

## Registry generator patterns (skills-catalog/src/utils.ts + generate-registry.ts)

- **VERIFIED DEFECT they fixed** (worth knowing before writing frontmatter parsers): a single-line regex on `description:` captures only the INDICATOR CHARACTER of YAML block scalars (`description: >` / `|`) — their registry once published literal `">"` as every affected skill's description across CLI + marketplace. Their fix is a hand-rolled stdlib parser that detects `/^[>|][+-]?\d*$/`, collects indented continuation lines, and folds vs joins correctly (folded: blank line ⇒ newline; else space). **Check any regex frontmatter extractor for this** — ours (`tools/gen-skills-index.py` line 50) uses the same single-line-regex shape; it is safe today only because our ≤59-char description gate makes block scalars impossible, and a future long-description skill would silently publish `>` until then.
- **Auto-repair at generate time**: if frontmatter `name` isn't slug-shaped (`/^[a-z][a-z0-9-]*$/`) the generator rewrites SKILL.md in place (logged) — registry integrity over contributor convenience, with a visible ✏️ message.
- Registry is committed + published to npm + served via jsDelivr; `deprecated.yaml` carries name/message/alternatives so consumers get deprecation notices instead of dead skills.
