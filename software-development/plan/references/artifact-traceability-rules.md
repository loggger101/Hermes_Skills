---
description: "Traceability rules for turning source material into a reviewable plan, from plannotator/effective-html's html-plan skill (medium-agnostic, applies to markdown plans too): no invented timelines or status badges, decisions separated from assumptions and open questions, sequence shown only where real, plus the before-delivery verification list - no commitment disappeared, stages in intended order, ownership legible"
source_repo: plannotator/effective-html at main, 2026-11-04 - skills/html-plan (MIT)
tested_version: "SOURCE-READ. The SKILL.md was read in full locally; its examples were not executed and no plan was produced with it"
verified_date: "2026-11-04"
---

# Artifact traceability rules (effective-html's html-plan)

The `plan` skill here writes a markdown plan to `.hermes/plans/`. What it does **not** state is how to avoid quietly
transforming the owner's material while restructuring it. These four lines from `html-plan` close that gap, and they hold for
markdown exactly as for HTML — the medium is incidental:

> "Turn source material into a plan people can inspect and act on. **Preserve the user's scope, ordering, commitments, and
> terminology unless they ask for broader synthesis.**"

## Do not invent structure that implies facts

- *"Do not add a timeline, progress percentage, status badge, or dashboard summary unless the source supports it."* A date
  column or a "60%" reads as fact to every later reader; if nothing established it, adding it is fabrication with extra steps.
- *"Improve grammar and structure without inflating an implementation plan into a strategy document."* The upgrade everyone
  reaches for (make it look more important) is the defect here.
- *"Show sequence and dependency only where they are real."* Ordering in a list already asserts precedence — so reordering
  someone's items is a claim, not cosmetics.
- *"Use tables for exact mappings, comparisons, or repeated fields… Keep long prose readable instead of forcing every paragraph
  into a card."* Structure serves lookup; decorative structure costs meaning.

## Separate the three epistemic categories

> "Separate accepted decisions from assumptions and open questions."

A plan that blends them is the reason plans get re-litigated: nobody can tell what was agreed. Use distinct headings (Decided /
Assumed / Open) rather than one undifferentiated body, and keep *"source commitments recognizable"* — a reader comparing against
the original should be able to trace each commitment back to where it came from.

## Verify before returning the plan

The source's own acceptance list, portable verbatim to any plan artifact:

1. **No commitment disappeared** (diff against the source; restructured plans lose items silently).
2. Stages remain in the intended order.
3. Ownership and dependencies are legible.
4. Long content does not overflow / stays readable at narrow width (HTML) — for markdown: tables don't exceed the reader's window, nested lists stay shallow.

Then: *"Return the absolute path and **note any structural interpretation you introduced**."* That last clause is the cheap
honesty move worth adopting everywhere — name the places where you imposed structure the source did not state (a grouping you chose,
an ordering you inferred), so the reader audits exactly those.

## Related in this catalog

`creative/sketch/references/fidelity-contract-effective-html.md` covers the same repo's wireframe/prototype contracts; both files
share one premise worth keeping as a house rule: **the artifact exists to make a decision testable, not to look complete.**
