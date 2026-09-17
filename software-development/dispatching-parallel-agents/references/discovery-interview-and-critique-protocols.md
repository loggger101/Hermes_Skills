# Discovery Interview & Critique Protocols (verified from tech-leads-club/agent-skills @ 0ab82f6)

Source: `(development)/tlc-discover` v0.8.0 and `(decision-making)/the-fool` v2.0.0. License CC-BY-4.0; attribution: Tech Leads Club / Jeffallan (the-fool). Mined 2026-09-17 as the exhaustion sweep of this repo. Pairs with `multi-agent-deliberation-jury.md` — discover shapes the question, jury decides it, fool attacks either.

## tlc-discover: interviewing an unshaped idea (the anti-convergence rules)

Pipeline position: SITUATION → PROBLEM → VERDICT → DECIDE. The stated failure mode is not inventing a fact but **converging early** — proposing a solution on turn two, hearing "sure", and manufacturing a decision with all the authority of one and none of the examination. Seven critical rules:

1. **No technology is *proposed* before the verdict.** Not a library, provider, or pattern. If the problem section argues for one, the framing is already a solution. (Bans proposing, never knowing — what the project already runs/committed/half-written is a constraint.)
2. **The verdict is a stop wherever the decision is open** — present it and wait. Where situation established somebody already committed, it's a line on the record instead of a gate: "manufacturing a gate whose answer you know is approval theatre that teaches everyone to click through the one that mattered."
3. **Never present an option you would not ship.** Two shapes considered every time; the second earns a full section only when live — otherwise ONE sentence naming what would have to be true for it to win (the disqualifying property, which the next stage needs anyway).
4. **Name the number that would change the decision before going and getting it.** Data with no question attached is noise that costs context; a missing number is usually a finding about instrumentation, not about the problem — ask, never read size out of silence.
5. **A decision without a concrete value is not decided** (a shape, bound, status, field). Everything downstream refuses vague input; catching it here is where it's cheap.
6. **High impact + low clarity does not get decided here.** It becomes an RFC or spike — forcing it produces the most expensive artifact there is: a decision that reads settled and is not. (This is exactly our `brainstorming` skill's triage rule, stated with teeth.)
7. **Solve for this context, not the reference architecture** — smallest shape answering the problem as measured; anything heavier must be bought with a condition true now or credibly close. Options that exist only to widen the reader's view get one line each and are marked as exactly that.

Interview mechanics: ask what is answerable NOW (a question whose prerequisite is still open yields a guess you'll treat as a finding); done = nothing answerable left, not all sections visited; **every question carries your recommended answer + reason in a line** ("agreeing then costs a word and disagreeing costs a sentence"); facts you look up, decisions you ask (spending attention on a readable fact is how a session earns the reputation of being a form); one question when answers depend on each other, two otherwise — "ten at a time is a form dump, and people answer form dumps by agreeing"; questions that can't be answered by talking (how it should feel) get ROUTED to a spike or designer — routing is a result, not a failed extraction. Proportionality: "a step with no input costs a line, and a section with no content does not appear at all — certainly not as a heading with 'N/A' under it."

## the-fool: structured critique protocol (challenge-only sibling of the-jury)

Five modes mapped to named methods: Socratic assumption inventory / Hegelian dialectic + steelman / pre-mortem (Gary Klein) + second-order consequence chains / red-team adversary personas + attack vectors / falsificationism evidence audit with A–D grading. The workflow's load-bearing steps:

- **Step 1 — Steelmann FIRST and confirm it.** Restate the position as STRONGER than stated, then ask "is this a fair restatement?" before any challenge. Challenging a strawman is how critique earns contempt; never fabricate a thesis when unclear (ask).
- **Cognitive-bias scan woven in, not sectioned** — bias findings are folded into the challenges themselves ("do not present them as a separate section" — a standalone bias list reads as accusation theater).
- **Step 4 — Engage before synthesizing.** Present only the 3–5 strongest challenges (quality over quantity; each specific and concrete, never vague "what ifs"), then explicitly require the user to respond to EACH before synthesis. Premature synthesis is where critique silently becomes agreement.
- **Output = a strengthened position**, not a verdict: acknowledge what was successfully defended, incorporate valid objections, name remaining risks. The fool only challenges — it never decides (that's the-jury) and never builds (that's tlc-implement).

## Reusable one-liners worth keeping verbatim

- "People answer form dumps by agreeing."
- "A decision that reads settled and is not" = the most expensive artifact.
- "Manufacturing a gate whose answer you know is approval theatre."
- "Self-check reproduces the author's own blind spot" (also tlc-spec-lean — see spec-driven-patterns-tlc.md).
