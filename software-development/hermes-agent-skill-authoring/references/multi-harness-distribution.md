---
description: "Shipping one guidance document across Claude Code, Cursor and Hermes surfaces - the file shapes observed in multica-ai/andrej-karpathy-skills (single-file CLAUDE.md, .cursor/rules/*.mdc with its two frontmatter keys, skills/<name>/SKILL.md, plugin.json + marketplace.json), the /plugin marketplace install flow, a provenance trap where the repo moved org but its own install URLs still name the old owner - plus a map of Karpathy's four coding principles onto skills this catalog already holds"
source_repo: multica-ai/andrej-karpathy-skills at main, 2026-11-04 (tree + README + .cursor/rules/karpathy-guidelines.mdc read via `gh api`)
tested_version: "SOURCE-READ. Files and tree were fetched from the live repo; no plugin was installed into Claude Code or Cursor here"
verified_date: "2026-11-04"
---

# Distributing one guidance doc across harnesses

## The four surfaces, as actually committed

`git ls-tree -r main` on that repo shows the same content shipped four ways:

| Path | Surface | Notes (observed) |
| --- | --- | --- |
| `CLAUDE.md` | Claude Code project instructions | single file; README documents both `curl -o CLAUDE.md <raw>` for a new project and an **append** form (`echo "" >> CLAUDE.md && curl <raw> >> CLAUDE.md`) for existing ones |
| `.cursor/rules/karpathy-guidelines.mdc` | Cursor project rule | frontmatter is just two keys: `description:` (a long "use when…" sentence) and **`alwaysApply: true`**; body repeats the same markdown |
| `skills/karpathy-guidelines/SKILL.md` | agent-skill layout | our shape; one dir, one SKILL.md |
| `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` | Claude Code plugin marketplace | install is two steps: `/plugin marketplace add <owner>/<repo>` then `/plugin install <name>@<marketplace>` — after which it applies **across all projects**, unlike the per-project CLAUDE.md route |

Two decisions worth copying when we publish our own guidance outside Hermes: scope (per-project file vs global plugin) is
the main axis, and keeping one body of text means the Cursor rule needs only a wrapper with `alwaysApply`, not a rewrite. Our
repo already generates `.claude-plugin/plugin.json` from the skill tree (`tools/gen-claude-plugin.py`); this repo shows the
companion `marketplace.json` that makes it installable by name, and the `.mdc` wrapper as the Cursor equivalent of our SKILL.md.

## Provenance trap (measured)

The starred path is **multica-ai**/andrej-karpathy-skills and `gh api repos/multica-ai/...` resolves fine — but the README's own
install commands and raw URLs still name **forrestchang**/andrej-karpathy-skills (`/plugin marketplace add forrestchang/…`,
`raw.githubusercontent.com/forrestchang/…`). So a copy-paste of upstream install instructions can point at an org that is no longer
canonical. Check the owner in the URL before curl-ing guidance into a project, and when recording a star's provenance record where
the content *lives*, not what its docs say.

## Karpathy's four principles — already covered here (do not re-port)

Derived from Karpathy's post on LLM coding pitfalls ("The models make wrong assumptions on your behalf and just run along with them
without checking… don't manage their confusion, don't seek clarifications, don't surface inconsistencies, don't present tradeoffs").
Each principle ships with a one-line test — the useful part:

| Principle | Their test | Already held by |
| --- | --- | --- |
| Think Before Coding (state assumptions, present interpretations, push back, stop when confused) | ask rather than guess | `grill-me`, `mattpocock-ask-if-underspecified`, our own runtime `<act_dont_ask>`/`<missing_context>` rules |
| Simplicity First (no speculative abstraction/configurability/error handling for impossible cases) | *"Would a senior engineer say this is overcomplicated? If yes, simplify."* | `ponytail`, pstack's Laziness Protocol (`verification-culture/references/pstack-principle-steering.md`) |
| Surgical Changes (don't improve adjacent code; remove only orphans **your** change created; mention unrelated dead code, don't delete) | *"Every changed line should trace directly to the user's request."* | `mattpocock-code-review`, `receiving-code-review`; note the asymmetry it states cleanly — clean up your own mess, never pre-existing dead code unprompted |
| Goal-Driven Execution (rewrite imperatives as verifiable goals: "Fix the bug" → "write a test that reproduces it, then make it pass"; plan as `[step] → verify: [check]`) | *"Strong success criteria let the LLM loop independently. Weak criteria ('make it work') require constant clarification."* | `test-driven-development`, `verification-before-completion`, `executing-plans` |

The genuinely transferable residue is small but real: the **imperative→verifiable rewrite table** and the
`step → verify: check` plan line are better-shaped than our equivalent in places, and the tradeoff disclaimer at the top of their
rule file — *"These guidelines bias toward caution over speed. For trivial tasks, use judgment."* — is a sentence worth having in any
behavioural skill we author, because it is what keeps caution rules from being applied to a one-line edit.
