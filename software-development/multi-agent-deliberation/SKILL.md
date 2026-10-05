---
name: multi-agent-deliberation
description: "Jury, interview and critique protocols for decisions."
version: 1.0.0
author: Hermes Agent (promoted from dispatching-parallel-agents; tech-leads-club/agent-skills the-jury, tlc-discover, the-fool; CC-BY-4.0, attribution Tech Leads Club / Felipe Rodrigues)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [multi-agent, decision-making, jury, deliberation, critique, pre-mortem, discovery, delegate-task]
    related_skills: [dispatching-parallel-agents, grilling-interview, brainstorming, decision-questionnaire, one-three-one-rule, mental-models]
---

# Multi-agent deliberation

## What This Skill Does

Gives three protocols for decisions where one perspective is not enough: the **jury** (a blind panel of differently-lensed agents that votes, with a deterministic tally), a **discovery interview** that stops an unshaped idea from converging early on a solution, and a **critique** protocol (a challenge-only sibling of the jury that strengthens a position without deciding). `dispatching-parallel-agents` stays the skill for splitting independent work across agents; this one is for deciding, interviewing and challenging.

## When to Use

- Build vs buy, architecture choices, vendor selection or research design where reasonable people would split
- An idea is still shaped like a solution ("sure, let's do X") and the problem is not established
- A plan or position needs a steelman, pre-mortem or red-team before commitment
- Not for factual lookups, for pure critique that must also decide (use the jury), or for splitting independent bug fixes (`dispatching-parallel-agents`)

## The jury in brief

Research behind the design: deliberation is not free upside (persuasion can flip a correct answer), debate on identical inputs adds no expected correctness (diversity does), agents anchor on their first opinion (the blind first round is the key gate), and same-model panels have correlated errors, so consensus is not proof.

1. **Panel**: default 3, 5 for high stakes, never more than 5. Mandatory roles: proponent, devil's advocate, integrator (owns the rubric); a panel of 5 adds two domain personas. Give each juror one critical lens (assumption-surfacing, pre-mortem, red team, evidence audit, second-order consequences) and a distinct primary concern.
2. **Frame**: concrete options, a 2 to 4 criterion rubric, and shared evidence; show all three before spawning anyone.
3. **Blind round 1**: spawn all jurors at once (parallel `delegate_task`); each returns POSITION, 2 to 4 arguments, EVIDENCE_GRADE A to D, ASSUMPTIONS and CONFIDENCE 0 to 100. No juror sees another's output; with no subagents, generate every position before revealing any.
4. **Anonymised round 2**: strip identity labels, steelman the opposing position first, state what would change your mind; a flip must cite the specific new argument. Stop if positions are stable; never exceed 2 rounds.
5. **Tally with `scripts/tally_jury.py`** (stdlib): confidence-weighted score, flip audit (unjustified flips or a bandwagon fall back to the independent round 1 aggregate at LOW confidence), evidence-grade cap (a winner resting on C or D cannot be HIGH), homogeneity cap; near-ties are broken on evidence and survival against the devil's advocate, never by coin flip. `--example` prints a sample input.
6. **Verdict shape**: one actionable line, confidence (HIGH, MEDIUM, LOW or PIVOT), up to 5 ranked reasons, the strongest dissent, the riskiest assumption with a concrete test, and one next action. PIVOT means the question is mis-framed; still give the least-bad action.

## Discovery interview (do not converge early)

No technology is proposed before the verdict; the verdict is a stop wherever the decision is open; never present an option you would not ship; name the number that would change the decision before fetching data; a decision without a concrete value is not decided; high impact plus low clarity becomes an RFC or spike, not a decision; solve for this context, not a reference architecture. Ask only what is answerable now, and give every question your recommended answer and reason. Done means nothing answerable is left.

## Critique (challenge only)

Steelman first and have the user confirm it, then present only the 3 to 5 strongest concrete challenges (Socratic, dialectic, pre-mortem, red team or falsification), fold bias findings into the challenges rather than a separate list, require the user to respond to each before synthesis, and end with a strengthened position, not a verdict.

## Pitfalls

- Letting jurors see each other's round 1, or labelling personas in round 2 (identity leakage drives sycophancy).
- More than 2 rounds: extra rounds amplify conformity.
- A homogeneous panel presented as independent; nine same-model judges can behave like two.
- Using PIVOT to avoid deciding.
- Manufacturing a gate whose answer you already know ("approval theatre").

## Verification

- [ ] Round 1 was blind and all jurors were spawned in one turn
- [ ] Jurors hold distinct lenses and the panel has a devil's advocate
- [ ] The tally output was used, not overridden by feel, and its caps are stated
- [ ] The verdict names the riskiest assumption and a concrete test

## References

- `references/multi-agent-deliberation-jury.md` - the five research findings, panel design, the five-phase protocol, verdict shape, and how to apply it with `delegate_task`
- `references/discovery-interview-and-critique-protocols.md` - the seven anti-convergence interview rules and the structured critique protocol, plus reusable one-liners
- `scripts/tally_jury.py` - deterministic verdict aggregation (ported with attribution, CC-BY-4.0)
