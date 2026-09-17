# Multi-Agent Deliberation: the Jury Protocol (verified from tech-leads-club/agent-skills @ 0ab82f6)

Source: `packages/skills-catalog/skills/(decision-making)/the-jury` — SKILL.md v1.0.0 +
`references/{juror-archetypes,deliberation-craft}.md` + `scripts/tally.py`. License CC-BY-4.0;
attribution: Tech Leads Club (Felipe Rodrigues). Ported 2026-09-16 for this brain's
`delegate_task` multi-agent decisions — the deciding sibling of a critique-only pass (their
`the-fool`: challenges, never commits).

Use when one perspective is not enough: build-vs-buy, architecture choices, vendor selection,
research design. Do NOT use for simple factual lookups or to only critique without deciding.

## The five research findings the protocol encodes (2025–26 multi-agent literature)

1. **Deliberation is not free upside.** Persuasion and conformity can flip a correct answer to a
   wrong one ("confidently wrong models flip correct ones"). Independent opinions come first; any
   later change of mind must be earned by a specific new argument, never social pressure.
2. **Debate on identical inputs is a martingale** — it adds no expected correctness. Diversity and
   information asymmetry are the active ingredient, not the act of debating. Give jurors different
   lenses/personas/primary concerns so their reasoning decorrelates.
3. **Homogeneous panels rarely beat a simple baseline.** Persona (and model) heterogeneity is what
   buys accuracy; even imperfect dissent from a mandatory devil's advocate reduces groupthink — it
   is the cheapest defense there is.
4. **Agents anchor hard on their first opinion**, and the group's final answer stays inside the
   envelope of the initial spread (Friedkin-Johnsen-style dynamics). The blind first round is the
   single most important gate; protect it.
5. **Correlated errors cap real panel independence** — nine same-model judges can behave like two,
   and standard aggregation cannot close that Condorcet gap. Consensus is not proof: calibrate
   confidence to real diversity and always name the assumption that would break the verdict.

## Panel design (Phase 1)

- **Size**: default 3; use 5 for high-stakes/contested questions. Odd sizes avoid ties. Hard cap 5 —
  beyond it, jurors mostly add correlated noise and cost, not independence.
- **Mandatory roles on every panel**: one PROPONENT (strongest case FOR the leading option), one
  DEVIL'S ADVOCATE (strongest case against / for best alternative — non-negotiable), one INTEGRATOR
  (owns the rubric, refuses premature consensus). A panel of 5 adds two domain personas.
- **Orthogonality**: pick personas whose blind spots differ; if two would write nearly the same
  Round-1 block, replace one. Narrow practitioner personas score slightly worse individually but
  their errors are less correlated — larger net gain after aggregation. Different underlying models
  per juror decorrelate more than same-model panels (a same-model panel favors its own reasoning style).
- **Lens assignment** — each juror wields exactly ONE critical method: assumption-surfacing
  (Socratic premise inventory, tagged established/assumed), pre-mortem (2–3 concrete failure
  narratives with consequence chains), red-team (attack vectors + trigger conditions), evidence-audit
  (falsification; grade every key claim A/B/C/D and name the weakest link), second-order consequences
  (what this makes true in 6–18 months, incentives created, doors closed).
- **Break identical inputs** three cheap ways: distinct primary concern per juror; distinct lens;
  optional evidence emphasis (point different jurors at separable evidence streams — never starve a
  juror of facts, only change the emphasis).

## The protocol (run in order; never skip blindness)

1. **Frame**: decision frame (concrete options A/B/C), rubric (2–4 criteria for THIS question:
   correctness, reversibility, cost, time-to-value, blast radius…), shared evidence (read the code/
   docs now and include the relevant parts). Show all three before spawning anyone. One clarifying
   question max; otherwise state your interpretation in one line and move on.
2. **Blind Round 1 — spawn ALL jurors at once** (one turn, parallel `delegate_task` calls here). Each
   gets frame + rubric + evidence + its role/persona/lens only. No juror sees any other's output.
   Each returns: POSITION ("it depends" is not a position), 2–4 concrete ARGUMENTS from its lens,
   EVIDENCE_GRADE A (direct data/proof/reproducible) / B (solid reasoning or indirect reliable data) /
   C (plausible but thin) / D (anecdotal or assumed), ASSUMPTIONS, CONFIDENCE 0–100. No subagent
   runtime? Simulate sequentially in one context — but generate EVERY Round-1 position before any is
   revealed to anyone else; blindness is non-negotiable even then.
3. **Anonymized deliberation (Round 2)**: strip all persona/identity labels, relabel Position 1..N
   (identity leakage drives same-backbone favoritism and sycophancy). Each juror must: steelman the
   strongest opposing position BEFORE rebutting; state exactly what would change its mind; hold or
   revise — a flip MUST cite the specific new argument/evidence that caused it. **Adaptive stop**: if
   positions are stable after Round 2, STOP (extra rounds amplify conformity); one extra round only on
   a large genuine shift with the panel still split. Never exceed 2 deliberation rounds.
4. **Foreman tally — deterministic** (`scripts/tally.py`, stdlib-only, ported): confidence-weighted
   score per option from FINAL votes; flip audit (unjustified flips >50%, or every flip toward the
   earliest-stated majority ⇒ bandwagon); on SUSPECT fall back to the INDEPENDENT Round-1 aggregate
   at LOW confidence — independent aggregation frequently beats degraded deliberation, so this is a
   feature not a failure; near-tie (top options within ~10%) broken by higher evidence grade + better
   survival against the devil's advocate per rubric — never coin-flip, never abstain; homogeneity cap:
   low real diversity drops confidence one level. Evidence-grade caps: winner resting on C/D cannot be
   HIGH no matter how the vote lands.
5. **Verdict (mandatory shape)**: `VERDICT:` one actionable line · `Confidence:` HIGH/MEDIUM/LOW/PIVOT
   · up to 5 ranked reasons grounded in rubric+evidence · preserved strongest dissent ("none" only if
   genuinely unanimous) · riskiest assumption (the single thing that, false, breaks the verdict) ·
   one concrete test of it · one next action startable in minutes. PIVOT = the question itself is
   mis-framed — still give the least-bad action under current framing AND state the reframe; never use
   PIVOT to avoid deciding. Output only the block, no transcript, no preamble.

## Applying it with this brain's `delegate_task`

- Dispatch all jurors in ONE turn (parallel); each child gets its own role/persona/lens so prompts are
  not identical — that is what makes the panel worth more than one agent.
- The foreman (parent) writes frame/rubric/evidence; children return only the structured block above,
  which keeps parent context small and tally input clean.
- Run `python scripts/tally.py --input jury.json` for Phase 4 — it never abstains and prints caps;
  PIVOT and merit-based tie-breaks are flagged by the script but remain the foreman's call.
