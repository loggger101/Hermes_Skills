---
description: "two external skill-packs the owner starred, reviewed as intake candidates and kept upstream rather than ported: K-Dense's 177-skill Scientific Agent Skills (catalog shape, its maintenance-metadata frontmatter convention worth adopting, autoskill's screenpipe-driven skill-drafting with a stated single data source) and ppt-master (a closed intermediate-DSL whose three-state input contract and per-layer non-responsibilities are a reusable pattern for any agent-authored markup compiled into a strict target format)"
source_repo: K-Dense-AI/scientific-agent-skills at main + hugohe3/ppt-master docs, 2026-11-04
tested_version: "registry/README/sampled-SKILL.md **read from source** (two skills fetched whole and read); ppt-master reviewed from its five design documents (~256 KB). Nothing installed or executed"
verified_date: "2026-11-04"
---

# Two external skill-packs, reviewed for intake — both stay upstream

## K-Dense `scientific-agent-skills` (MIT, v2.72.0) — 177 skills

Facts read from README and tree listing: **177** skills under a flat `skills/<name>/SKILL.md` layout; MIT; ships to the open Agent Skills standard *and* as a portable **Agent Plugins** package (`plugin.json` + `skills/`) so hosts that support it load the whole collection as one plugin; CI publishes both a **security-scan** workflow badge and a **skill-tests** workflow badge (i.e. skills are tested in CI, not just written); advertised working with Cursor / Claude Code / Codex / Google Antigravity. There is also an accompanying paper — *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents* (arXiv:2609.00065) — which makes this collection a **citable precedent for the second-brain premise itself**: procedural knowledge for agents as a first-class, publishable artifact. Their desktop app (`K-Dense BYOK`) consumes these skills with 100+ scientific databases.

Domain spread is biology / chemistry / medicine / physics / engineering / Earth science / data analysis / scientific communication. Sampled names show the overlap risk plainly: `astropy`, `anndata`, `biopython`, `bids`, `arboreto`, `alphagenome`, `benchling-integration`, `bgpt-paper-search` — plus meta-skills like `autoskill`.

**Verdict: do not port wholesale.** It is bio/chem-heavy relative to this owner's astro / econ / Hermes-ops stack, and duplicating 177 domain skills would dilute the index for no gain. Its value here is (a) an **upstream lookup and duplicate-check target** — before authoring any new science skill, check whether they already have one; (b) conventions worth stealing, below.

### The convention worth adopting: maintenance metadata in frontmatter

Their `skills/astropy/SKILL.md` header carries more than name/description:

```yaml
license: BSD-3-Clause license
compatibility: Requires Python 3.11+, Astropy 8.0.1 and NumPy 2+; SciPy for cosmology,
  matching and fitting (uv for installation). Some features (object name resolution, site
  lookups, remote FITS reads, IERS updates) need network access.
metadata:
  version: "1.5"
  last-reviewed: "2026-09-30"
  skill-author: K-Dense Inc.
```

Two things make that better than a bare description. `compatibility` states **which features need the network** — exactly the fact an agent gets wrong at runtime, and the same class of trap our own references log (e.g. "no internet on this box" workarounds). And `last-reviewed: 2026-09-30` is a *staleness signal we do not currently carry*: our tree tracks verified-date inside reference bodies but nothing at skill level says when the top-level guidance was last re-read against current versions. Recorded here as an option for `hermes-agent-skill-authoring`, with the honest caveat that adding a required field to ~217 skills is a bulk change needing owner sign-off — and that a date nobody maintains can be worse than none, since it invites false trust.

### `autoskill` — their take on mining work history into skills

A meta-skill that reads **Screenpipe** history windows to detect repeated research workflows, matches them against existing skills, then stages drafts "for review". Three design details are worth keeping regardless of whether anyone uses the skill: it declares its single data source and hard failure mode up front ("no alternate data source… if the daemon isn't running, `run()` raises `ScreenpipeUnreachable` with install instructions"); detection and embedding inference run **locally** while only *redacted app/title cluster summaries* reach the LLM; and it never auto-installs a skill — drafts go to human review. That is the same governance line this repo draws at intake, arrived at independently.

## `ppt-master` — a closed-DSL pattern library (the more transferable of the two)

Its design docs are the interesting part even for anyone who never generates a slide deck.

**The intermediate language is deliberately smaller than its host format.** It compiles "project-canonical SVG", explicitly *not* browser SVG: *"SVG adapts to PPT Master; PPT Master does not expand to follow the entire SVG standard."* The contract closes allowed elements, attributes, units, metadata and target (DrawingML) mappings. Input is then classified into three states with different handling — a table worth copying for any agent-authored-markup-to-strict-target pipeline:

| State | Handling |
| --- | --- |
| **Canonical** authoring input (what prompts/templates emit) | compiles through registered mappings, no warnings |
| **Compatible** (documented historical spelling with one safe deterministic normalisation) | checker emits a *non-blocking* warning; converter normalises it and **never feeds the alias back into prompts** |
| **Invalid / unsupported** (no mapping, ambiguous meaning, risk of invalid target output) | checker errors and blocks the flow |

The governing sentence: *"Compatible reads are a controlled migration boundary, not permission to widen the authoring language."* That last clause is the trap most such projects fall into — accepting a legacy spelling on read eventually reintroduces it in generation. Keeping the *read* surface wider than the *write* surface, and enforcing that asymmetry, is directly applicable here: skill frontmatter, our docx/pptx builders, HTML widgets for `::preview`, registry CSV columns.

**Layers get an explicit non-responsibility column.** Workflow / authoring guidance / deterministic tools are separated not just by what each does but by *"explicit non-responsibility"* — conversion, validation and packaging belong to deterministic tooling; reasoning about the message belongs to the workflow; neither substitutes for the other. Naming what a layer must *not* do is stronger documentation than naming what it does, because it forecloses the plausible wrong fix rather than just describing the right one.

**Capability docs indexed by target feature, with negative space declared.** The mapping guide answers "for a PowerPoint feature, what project representation owns it and what survives export or import?" — and states plainly that **"a feature not listed here is not implicitly supported."** Enumerating non-support removes the guesswork that positive-only docs leave behind.

**Quality contract worth stealing for any AI-authored artifact:** output is an *editable draft*, human owns the final mile, and whole-slide screenshot skins are **rejected outright** as fake editability — with one narrow exception (image-to-PPTX) whose rules are spelled out: vision-capable host required, text restored natively over a text-removed base, decorative graphics rebuilt only under strict visual locks. The honest framing — "the selected model still sets the quality ceiling" — is the same no-substitution-of-judgment stance as pstack's *Name the Substitution* (`verification-culture/references/pstack-principle-steering.md`).
