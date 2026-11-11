# The Agent Skills Standard (upstream) vs Hermes Skill Gates

Source: [agentskills.io/specification](https://agentskills.io/specification), fetched 2026-11-11, and the spec pointer in
[anthropics/skills](https://github.com/anthropics/skills) (`spec/agent-skills-spec.md`, which is now only a stub: "The spec
is now located at agentskills.io/specification"). The `anthropics/skills` repo (Apache-2.0, 192k stars at census) ships the
reference implementations plus a template whose whole content is `name` + `description` frontmatter - nothing else is required.

Verified in-repo the same day: **all 254 skill directory names in this catalog already satisfy the upstream name rule**
(lowercase `a-z0-9`, single hyphens, no leading/trailing/consecutive hyphen, max 64 chars; zero violations). Two skills live as a
category dir holding `SKILL.md` directly (`doc-coauthoring/`, `huggingface-trackio/`) - still conformant, since the standard only
requires that the skill directory contain `SKILL.md`.

## Upstream constraints (the whole required surface)

| Field | Required | Constraint |
|---|---|---|
| `name` | yes | 1-64 chars, unicode lowercase `a-z`/`0-9`/`-`, no leading/trailing/consecutive hyphen, **must equal the directory name** |
| `description` | yes | 1-1024 chars, non-empty; must say *what* it does **and** *when* to use it, with keywords that trigger recall |
| `license` | no | License name or a bundled license file; keep short |
| `compatibility` | no | Max 500 chars: intended product, system packages, network access |
| `metadata` | no | Map of **string keys to string values** only |
| `allowed-tools` | no | Space-separated pre-approved tool list (experimental) |

Body has no format restrictions; recommended sections are steps, input/output examples, edge cases. Directories beyond
`SKILL.md` are optional conventions: `scripts/` (executable code), `references/` (docs read as needed), `assets/` (files used in
output - templates, icons, fonts). File references must be **relative from the skill root**.

## Progressive disclosure budgets (the reason structure matters)

1. **Metadata** (~100 tokens): `name` + `description` loaded at startup for *every* installed skill.
2. **Instructions** (< 5000 tokens recommended, SKILL.md < 500 lines): the body, loaded once activation is decided.
3. **Resources**: files under `scripts/`, `references/`, `assets/` - read only when required; scripts may execute without ever being
   loaded into context.

For reference files longer than ~300 lines, include a table of contents. Multi-domain skills should split by variant
(`references/aws.md | gcp.md | azure.md`) so the agent reads exactly one.

## Where Hermes gates are stricter (and what an export must do)

| Concern | Upstream standard | This repo's audit gate | Export consequence |
|---|---|---|---|
| `description` length | up to 1024 chars | **<= 59 chars**, double-quoted YAML string | A Hermes catalog cannot carry upstream-style trigger prose; the "when to use" text has to live in the body or a sibling field, so exported skills lose triggering fidelity unless descriptions are rebuilt |
| `version` / `author` / `platforms` | not defined (may sit under `metadata`) | required top-level fields (`metadata.hermes` also required) | Exporters must move them into `metadata:` and stringify |
| `metadata` values | **strings only** | lists are idiomatic here (`tags`, `related_skills`) | List-valued keys violate the standard's string→string map: join to a delimited string, or drop, on export |
| `name` == directory | required | enforced by this repo too (audit rejects duplicates) | Compatible both ways |
| Body section headers | unrestricted | `## What This Skill Does` / `## When to Use` + capitalization standard | Upstream skills imported here need header normalization; the reverse is harmless |

Practical rule when porting **out**: keep `name`, rewrite `description` into upstream prose (what + when + keywords, see
`references/eval-driven-skill-development.md` for measuring it), stringify every metadata value, and move scripts/references/assets
under those exact directory names - they are the only paths upstream loaders look at.

Practical rule when porting **in**: treat `compatibility:` as a hint to be verified (probe the named package/CLI here) rather than
truth, and remember that an upstream skill with no `version` still needs one before it can land in this catalog.

## Related upstream facts worth keeping

- Anthropic's document skills (`docx`, `pdf`, `pptx`, `xlsx`) are published Apache-2.0 inside the same repo as production
  reference implementations; Hermes ships its own MIT equivalents under `productivity/` and `mlops`-adjacent skills, so treat them
  as **parallel implementations**, not upstream/downstream - do not overwrite ours with theirs, but they remain a good source for
  procedures (form-filling, OOXML editing) our versions lack.
- The repo is installable as a Claude Code plugin marketplace (`/plugin marketplace add anthropics/skills`, then
  `document-skills` or `example-skills`) and mirrors the same skills in Claude.ai and via API - one corpus, three surfaces. Our own
  equivalent of that pattern (one catalog, several harnesses) is held by `references/multi-harness-distribution.md`.
