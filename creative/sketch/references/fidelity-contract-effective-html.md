---
description: "Fidelity contracts for HTML review artifacts, from plannotator/effective-html: the authority ordering to settle before coding, what counts as a genuinely different direction (product decisions, not colours), intentional-unfinishedness vs sloppiness, the states list an interactive artifact must model, the interaction-completeness/accessibility checklist, and anti-house-style specifics"
source_repo: plannotator/effective-html at main, 2026-11-04 - skills/html-wireframe + skills/html-prototype (MIT)
tested_version: "SOURCE-READ. The two SKILL.md files were read in full locally; no artifact was built with them and the repo's own site examples were not rendered"
verified_date: "2026-11-04"
---

# Fidelity contracts for HTML artifacts (effective-html)

Our `sketch` skill says *make 2–3 throwaway variants*; this file supplies the discipline that decides **what a variant
is, how rough is right, and what "done enough to review" means**. Both source skills are direct-invocation specialists
("do not activate independently from a general request") — a useful convention when adding narrow modes to an existing skill.

## Settle authority before coding (both modes use the same shape)

> 1. The user's explicit instructions and accepted decisions.
> 2. The product's existing structure and terminology / established design language.
> 3. The user, task, and content being modeled.
> 4. Your own layout/design judgment.

Stating this explicitly is worth copying: most "the mockup ignored what I said" failures are the artifact resolving an
unwritten priority in favour of (4). Also settle before coding: the job, the bounded scenario, which states exist, where
the real product would take over.

## What counts as a different direction

> "Vary product decisions such as navigation model; grouping and order; primary-action placement; content density;
> overview versus step-by-step flow; desktop-to-mobile reflow. **Do not call color changes or minor card
> rearrangements separate directions.** Give each direction a short descriptive name and one sentence about its tradeoff."

Plus: keep the directions in **one HTML file** with a small keyboard-operable selector so reviewers compare without
opening files; preserve the same core content and task across them; if the user already chose a structure, build that
direction only. This is the sharpest available answer to "variants as theatre".

## Low fidelity ≠ lorem ipsum; unfinishedness ≠ sloppy

> "Use real labels and representative content. **Low fidelity is not permission to use anonymous boxes or lorem ipsum
> where wording affects the layout.**"
> "The wireframe may still be well composed. Intentional unfinishedness is different from careless spacing, illegible
> type, or broken responsive behavior."

Roughness budget: restrained grayscale, system type, plain borders, limited radius/spacing; no brand colour, gradients,
shadows, illustrations; media as labelled placeholders unless the asset changes a structural decision. Enough order to
judge hierarchy, not enough polish to invite a brand review. Annotations only where they expose an assumption, open
question, or behaviour that cannot be shown directly. Controls with no review purpose get removed or labelled out of scope.

## Mockup vs prototype: two modes, one skill

Mockup = polished, responsive, mostly static (open question is visual hierarchy/typography/colour/fit). Prototype = a
working flow (open question is navigation/input/state change/feedback/recovery/transition). Explicitly: *"Do not create a
separate `html-mockup` skill. Do not add behavior merely to make a mockup seem more complete."* If both are requested, keep
the same content and structure so fidelity changes stay comparable — that is what makes the pair cheap to diff.

Anti-house-style rule worth pinning above any generator's default taste:

> "Do not default to a gradient, a dark dashboard, interchangeable cards, or decorative metrics. A prototype for a field
> tool, an editorial workflow, and a financial approval should not feel like the same product."

## Model states before building

List them first; include only those the scenario can actually reach: loading, empty, error, success, disabled, mobile, plus
domain states from the brief. Heuristics: an async-looking action normally shows loading **and** success **and** failure or
recovery; a collection should consider its empty state; a gated action must show *why* it is disabled. And the counterweight
that keeps this from becoming checklist theatre: *"Do not force irrelevant states into the main flow just to satisfy a
checklist. Make omitted states explicit in the handoff."*

## Interaction completeness (the part usually skipped)

Native elements where they give the right semantics; whole modeled flow keyboard-operable; focus visible and deliberately
placed after meaningful transitions; dialogs get an accessible name, contain focus, close on `Escape`, restore focus to the
trigger; form errors associated with their controls and important status changes announced; **no essential behaviour hidden
behind hover**; respect `prefers-reduced-motion` while preserving state feedback; usable touch targets; no accidental
page-level horizontal overflow. In mockup mode keep semantic structure *and* visible focus styles even unwired, and make the
static review boundary clear.

## Honesty about scope instead of fake completion

> "Remove dead buttons. If an action belongs to the real system, **explain the boundary instead of pretending it completed.**"

The same rule governs our own deliverables: a demo that fakes a backend step is worse than one labelled out of scope.
Related from `html-plan`: *"Do not add a timeline, progress percentage, status badge, or dashboard summary unless the source
supports it"* — see `../../../../software-development/plan/references/artifact-traceability-rules.md`.

## Adjacent: the one-pager frame (`skills/one-pager`, 870 bytes)

> "Make a one-pager: one HTML page that shares an idea with teammates early, or recaps work for them, with big pictures and
> little words… The reader is new to the subject and has a minute… Show them with big pictures and little words **without
> withholding key details**… Explain things as if the viewer is new here, but don't use weird metaphors."

Two useful constraints compressed into four lines: audience-has-a-minute (drives hierarchy) and *don't withhold details to look
clean* (the failure mode of most exec-summary artifacts), plus an explicit ban on metaphor-as-substitute-for-explanation.
