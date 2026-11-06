# flowsint-enricher-builder — reviewed (source-read 2026-11-05; banked from round-170 "not reviewed")

Upstream `.claude/skills/flowsint-enricher-builder/SKILL.md` (~10.5 KB, read whole). It is a codegen
skill for the flowsint OSINT graph pipeline (Pydantic types + decorator-registered enrichers writing to
Neo4j). Not portable as-is - every path and API belongs to their monorepo - but it carries several
governance patterns that generalize to this repo's own intake/authoring discipline. Verdict: reviewed,
patterns recorded below; app internals otherwise stay held by `flowsint-pipeline-patterns.md` (r170/r253)
and `security/secret-vault-pattern/references/vault-crypto-pattern.md`.

## Transferable patterns

- **Authoritative-source-paths table as step zero.** The skill opens with a literal path -> purpose map
  ("Read these first. Never assume signatures or fields - open the file.") covering type defs, registries,
  base classes, UI mapping, docs. Same doctrine this repo applies to mining: name where ground truth lives
  before any generation. Reusable shape for our own skills that touch multi-file systems: enumerate source-of-
  truth paths explicitly rather than describing them in prose.
- **Reuse / extend / create-new decision tree, surfaced BEFORE codegen.** List entities -> open closest type
  files -> decide (reuse if fields covered with `extra="allow"`; extend for 1-2 missing optional fields; new
  type only when conceptually distinct: different primary key / label semantics / graph role) -> "Never cram
  data into a wrong type" and present candidates + gaps + recommendation to the user first. Direct analog of
  skill-intake judgment (extend existing skill vs new skill), including its failure mode: adding fields/skills
  because convenient, not because conceptually right.
- **Registration by decorator + tree-walk auto-discovery; "do not edit registry.py".** New file in the right
  directory is picked up on restart (`load_all_enrichers()` walks the tree; no `__init__.py` needed). The same
  invariant our indexes enforce via generation: hand-editing a generated registry is the corruption vector;
  ours = regenerate + drift-gate, theirs = decorator side-effect. Also note their UI gotcha: a type works as
  enricher I/O but stays invisible in the picker until added to `_get_category_definitions()` - registration can
  be multi-surface, and partial registration fails silently-ish (our both-surfaces lesson again).
- **Known-smell containment.** Their documented casing inconsistency (`Ip` vs `IP`, mixed `social`) comes with
  an entropy rule: match the casing already used in that directory, do not introduce a third variant; cleanup is
  a separate flagged task. Same family as our bundled-skills-left-as-shipped convention - tolerate legacy noise,
  forbid adding to it, keep cosmetic fixes out of functional commits.
- **Batch resilience + no silent excepts**: per-item try/except in `scan()` ("one failing input must not kill
  the batch"), every `except` logs. Cross-reference: `software-development/failure-signal-audit`.
- **Codified pushback.** A literal "When the user is wrong" section: show the existing type's fields, explain
  the mismatch, propose extend-or-new - and refuse to generate the bad version; plus an explicit anti-pattern
  list ("refuse to generate these": hardcoded keys even temporarily, manual node dicts bypassing typed
  instances, `Any` types outside the named escape hatch `n8n/`). Escape-hatch naming is worth noting: their
  wildcard-typed connector is legitimate ONLY inside a declared directory - exceptions need an address.

## Vault-resolution semantics (complements vault-crypto-pattern.md)

Params schema types include `vaultSecret`; resolution order at runtime (`Enricher.resolve_params`): explicit
vault ID param -> else lookup by param name -> if `required: true` and missing, hard exception naming the key.
So secret binding is convention-first (param name doubles as vault key default), with override - matches how our
own tooling prefers named env keys over config indirection.
