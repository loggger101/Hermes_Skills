---
description: "Gate-design machinery worth stealing from hallmark's sloplint: four refusal tiers that say whether you may disagree, class = who checks it (static/render/judged) so tools and eyes never duplicate work, grades reported separately to keep '0 FAIL' honest, a waiver protocol whose guard is re-derived by the machine with reason-quality rejection rules, stable retired gate IDs, pre-emit self-critique with an anti-theatre clause - plus this file's own live measurements of sloplint on Node 22"
source_repo: Nutlope/hallmark v2.0.0 (MIT) at main, 2026-11-04 - skills/hallmark/references/gates.md + scripts/sloplint.mjs
tested_version: "LIVE-RUN on Node v22 (Windows): `node sloplint.mjs` against the repo's own fixtures/eyebrow-fail, eyebrow-pass, waiver, slopped.html. Static tier is zero-dependency; render tier did NOT run here (see boundary below). The 39 KB gates.md was read for §1-§4 and the gate tables"
verified_date: "2026-11-04"
---

# Tiered gates, guarded waivers, graded verdicts (hallmark / sloplint)

A design-linter, but its **control architecture** is what belongs in this catalog — it solves problems our own 29-gate
suite has: how to let an agent disagree with a rule without silently ignoring it, and how to keep "green" from meaning
less than it appears. Everything under "Measured" below was executed here; everything else is quoted/condensed source.

## Four tiers — the tier states whether you may disagree

| Tier | Meaning | Waivable? |
| --- | --- | --- |
| **Floor** | correctness, access, honesty, explicit bans: *"no admired page breaks it on purpose"*, or a **house rule** so reliably machine-made that the tool is stricter than the field | never |
| **Reflex** | "a default a language model falls into" — a build with a real reason may waive one **on the record** | yes, guarded |
| **Finish** (F-checks) | craft detail invisible at arm's length | reported and answered, **never blocking** |
| **Ledger** | bookkeeping about repetition | reports at `NOTE`, never counts toward the verdict |

Two details do all the work. First, Floor is defined by *whether a good practitioner would ever do it deliberately*, not
by severity vibes — which is exactly how our own gates should be classified (a missing XML-well-formedness check is Floor;
"this prose could be tighter" is Finish). Second, **the house-rule subset is declared explicitly and closed**: *"54 (the
eyebrow), 58 (the screen budget), 63 (template punctuation) and 67 (the tracked-caps label), and no others."* An agent
cannot quietly promote its own aesthetic preference to non-negotiable.

## Class says *who* checks it — so eyes never redo a tool's job

`M` static (CSS/markup, **Tailwind utility strings in components included**), `M/R` static half + render tier, `R` render
only, `R/J` render-or-judge, `J` judged by the model. And the operating rule: *"When sloplint has run, walk only the J and
R/J gates and the judged halves of M/R gates."* Our suite already separates tool-checked from human-reviewed implicitly;
naming it per-gate is what lets a reviewer stop early with justification instead of reading everything twice.

## Grades are counted separately so green cannot be inflated

`FAIL` (Floor, nothing ships) · `REFLEX` (unanswered reflex: fix or waive) · `WAIVED` · `WARN` (suspected; confirm/dismiss →
`DISMISSED`) · `ANSWERED` (Finish finding with recorded reason) · `NOTE`. Stated rationale worth keeping verbatim:

> "`FAIL` and `REFLEX` report separately, so '0 FAIL' stays a true statement about the Floor."

**Measured** — summary line shape and exit codes on Node 22:
- fail fixture → `sloplint: 10 FAIL, 1 REFLEX, 2 WARN across 1 file(s).`, **exit 1**; findings print as `FAIL 54 :66 eyebrow "01 · The tour" before <h2> | fix: Cut it; the heading already says this`
- clean fixture (one `ANSWERED`) → `sloplint: 0 FAIL, 0 WARN, 1 ANSWERED across 1 file(s).`, **exit 0**

## The waiver protocol: guard evidence re-derived by the machine

Waivers live in the artifact, below the critique line, as three fields — gate id, **guard evidence**, reason:

```css
/* Hallmark · waive 47b · one frame, a real terminal capture inside · the terminal is the product being sold */
```

Rules from source: *"sloplint re-derives the guard; a build that cannot state its guard usually finds it does not hold."*
One waiver per gate named by clause (`47b`, not `47`). A waiver naming a Floor is rejected and **the gate fires**. Reason
quality is checked mechanically: under 24 characters, boilerplate, or reused word-for-word on another waiver ⇒ rejected.
Finish findings get `answered <check> · <reason>`; suspected findings get `dismissed <id> · <evidence>`.

**Measured** — the rejection paths really fire (`fixtures/waiver`):
```
WAIVER 40 :1 waiver on 40 REJECTED (Floor is never waivable) | fix: Fix the gate, or satisfy the guard and say why in the page's own words
WAIVER 40 :1 answer on 40 REJECTED (only Finish findings are answered; Reflex is wai…
WAIVED 1 :42 display font "inter" (--font-display)
NOTE waive :1 4 reflex gates waived (7b, 22, 25, 1): that is a house style, not a set… | fix: Lock it into a design.md so later pages inherit it instead of re-arguing it
sloplint: 0 FAIL, 1 WARN, 5 WAIVED, 2 REJECTED, 1 ANSWERED, 1 NOTE across 1 file(s).   # exit 0
```

**Gotcha measured:** two waivers were *rejected* and the run still exited **0**, because no Floor gate independently failed.
Read the summary line (or `--json`), never `$?` alone — "exit 0" means "no FAIL", not "everything you wrote was valid". Same
class of trap as a green CI job whose optional matrix leg was skipped.

**The promotion rule**, which is the part to copy into our own governance: *"the same gate waived on three consecutive builds
is a house style, not an exception"* → lock it into config (`design.md`) so later work inherits instead of re-arguing. Our
suite has the raw material for exactly this — 54 scripts sit in "the untested ledger with reasons"; recurring *accepted*
exceptions there are candidates for becoming real gates or documented defaults, and nothing currently detects that drift.

## Stable IDs: retired numbers stay retired

> "**Retired numbers stay retired:** 5, 13, 14, 21, 31, 35, 36, 43, 45, 51, 52, 57, 60 and 61 are never reused, so an older
> stamp still reads."

Annotations outlive the rule set, so IDs are append-only. Applies to any waiver/exception/suppression scheme — including our
`retired-skills.txt`, which serves the same purpose for skill names.

## Pre-emit self-critique with an anti-theatre clause

Score the *planned* work 1–5 on six axes before building; anything under 3 triggers revision first: Philosophy (does it have
an argument a reader could disagree with), Hierarchy (survives the squint test), Execution, Specificity (*"could belong to no
other product"*), Restraint (*"lost something you liked"*), Variety (*"shares almost nothing with the last three runs"*). Then
stamp the score **and name the weakest axis plus the fix taken**; *"straight 5s name what was cut to earn them. Never invent a
weakness to fill the field."* That last sentence is the general antidote to self-review theatre — worth adopting wherever we ask
an agent to grade itself, including our own reviewer-subagent prompts.

## Dependency boundary (measured here)

Static tier: **zero dependencies**, Node 18+, reads `.html`/`.css` plus `.jsx .tsx .vue .svelte .astro` (parses Tailwind class
strings and `cn`/`clsx`/`cva` calls), skipping `node_modules dist build coverage` and dot-folders. Render tier needs
**puppeteer-core + a Chrome binary**: with neither installed, `--render` prints
`render tier not run: no puppeteer-core found locally, globally or via HALLMARK_PUPPETEER` **and still exits 0**. Resolution
order for the library is local cwd → skill dir → `$HALLMARK_PUPPETEER` → `npm root -g`; Chrome comes from `$CHROME_PATH` or a
bundled path. So on this box: static lint usable today, render/judged gates need an install — and verify skipped tiers by their
message, not the exit code.

## Related in this catalog

Concrete CSS/access tells and honesty floors worth adopting regardless of tooling:
`../../../../creative/design-taste-frontend/references/hallmark-css-floors.md`. The redesign record (`--before` captures what a
target page *says and does*, `--kept` checks the rebuild against that record) maps onto
`creative/redesign-existing-projects`; gate 84's "run the real product and capture it instead of drawing a mock" is the same rule
our `dogfood` skill argues for.
