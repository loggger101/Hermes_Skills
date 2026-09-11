# Behavioral Skill Testing (RED-GREEN for Discipline Skills)

Source: distilled from obra/superpowers v6.3.0 (`skills/writing-skills/` + `docs/superpowers/specs/2026-06-10-positive-instruction-redesign-design.md`, MIT). Complements this skill's structural tests (frontmatter, related_skills resolution): those prove the file is well-formed; these methods prove the *prose changes behavior*.

**Central thesis:** writing a discipline-enforcing skill IS TDD applied to process documentation. "If you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing." The Iron Law applies to EDITS too: write or change guidance before testing it? Delete and start over — no exceptions for "just adding a section".

## When behavioral tests apply (scope gate)

Test skills that: enforce discipline; have compliance costs (time, effort, rework); could be rationalized away ("just this once"); contradict immediate goals. DON'T test: pure reference skills, or ones with no rules to violate — agents have no incentive to bypass them there. Structural tests are sufficient for those.

## RED-GREEN-REFACTOR for a skill

| TDD phase | Skill testing |
|---|---|
| RED (baseline) | Run pressure scenario WITHOUT the skill; watch the agent fail |
| Verify RED | Capture the exact rationalizations verbatim ("Agent was wrong" tells you nothing — record word-for-word choices and which pressures triggered violations) |
| GREEN | Write minimal guidance addressing ONLY those observed failures (no hypothetical content); re-run same scenarios WITH it |
| REFACTOR | New rationalization found -> explicit counter per loophole; re-verify until bulletproof |

### Pressure scenario design

- **Combine 3+ pressures** — agents resist single pressure, break under multiple. Types: Time (deadline/deploy window), Sunk cost ("waste" to delete work), Authority (senior says skip it), Economic ($/min at stake), Exhaustion (end of day), Social (looking dogmatic), Pragmatic ("pragmatic vs dogmatic").
- **Force a decision:** concrete A/B/C options with real constraints and costs; make the agent ACT ("what do you DO?"), not answer hypothetically. Preamble: "This is a real scenario. You must choose and act."
- Quality ladder: bad = academic recitation ("what does the skill say?"); good = single pressure with specifics; great = 3+ combined pressures + forced choice + "be honest about what you'd actually do".

### Meta-test triage (after an observed violation)

Ask: "You read the guidance and chose X anyway. How could it have been written differently to make Y clearly the only acceptable answer?" Three answers, three fixes:
1. "It WAS clear — I ignored it" -> not a documentation problem; strengthen the foundational principle ("violating the letter is violating the spirit").
2. "It should have said X" -> documentation gap; add their suggestion verbatim.
3. "I didn't see section Y" -> organization problem; make key points prominent / move them earlier.

### Bulletproofing toolkit (for discipline skills)

- **Close every loophole explicitly** — don't just state the rule; forbid the specific workarounds ("don't keep it as 'reference'", "delete means delete").
- **"Spirit vs letter" killer line:** "Violating the letter of the rules is violating the spirit of the rules." cuts an entire rationalization class.
- **Rationalization table** built from baseline testing: every observed excuse gets a `| Excuse | Reality |` row; each new hole also earns a Red Flags entry and (for this repo) a description update naming the violation symptom ("Use when ... tempted to test after").
- Success signs: correct choice under max pressure, agent cites the skill's sections as justification. Failure signs: new rationalizations appear, "hybrid approaches", arguing for permission while defending the violation.

## Instruction form is a TESTABLE variable (measured evidence)

Micro-tests on dispatch/composition guidance (5+ reps per phrasing, programmatic scoring, no-guidance control included):

| Case | Prohibition ("don't restate") | Positive recipe ("your output should contain: 1..5") |
|---|---|---|
| Composition under competing incentive | **4.4 unwanted items — WORSE than no guidance (3.6)** | **3.0, zero variance** (adopted) |
| + nuance clause appended to recipe | — | 3.8, noisy ("nuance dilutes recipes") |
| Discrete directive with NO competing incentive ("don't ask X to do Y") | 0/5 violations — works fine | equal but longer -> shorter wins |

**Doctrine (classify before choosing form):**
1. **Tripwires work** — phrase-level self-checks on concrete tokens ("if what you're writing contains 'do not flag'... stop").
2. **Recognition tables work** — Red Flags/rationalization tables read at DECISION time, not composition time.
3. **Discrete-directive prohibitions work** when the model has no competing incentive for the forbidden act.
4. **Composition prohibitions backfire** under a competing incentive (restating specs feels like helpful curation). Only positive recipes move these; nuance clauses make winning recipes worse, not better.
5. **Ties go to shorter phrasing** — skills are re-read hundreds of times per session (~500x measured for one harness); prose length is a real runtime cost.

Also: before rewriting any instruction list, map every cross-reference that depends on its exact form — the same tokens can serve two mechanisms at once (composition-time priming vs review-time detection inventory). And record tested-and-DECLINED options with their numbers so nobody re-proposes them without new evidence.

## Micro-test protocol (cheap wording validation before full runs)

1. One fresh-context sample per call: system prompt = the guidance variant in realistic surrounding context; user message = a task that tempts the specific failure (e.g., deliberately under-specified input for placeholder-tenting).
2. **Always include a no-guidance control.** If the control doesn't exhibit the failure, there is nothing to fix — stop, don't author the guidance.
3. **5+ reps per variant** ("single samples lie").
4. Manually read every flagged match — template echoes and quoted counter-examples masquerade as hits; automated counts overstate both directions.
5. **Variance is a metric:** when guidance binds, reps converge on the same shape; five different interpretations = wording isn't binding — tighten form before adding words.

Full pressure scenarios remain the final gate for discipline skills; micro-tests validate WORDING (cost: seconds per iteration vs minutes/hours for full runs).

## Persuasion principles that measurably work on LLMs

Cialdini-style framing applied to skill design (evidence base: Meincke et al. 2025, N=28,000 conversations — persuasion techniques more than doubled compliance, 33% -> 72%, p<.001):

- **Authority** ("YOU MUST", "No exceptions") — for discipline skills; LLMs are parahuman: authority language precedes compliance in training data.
- **Commitment** — require announcements ("I'm using [skill]"), force A/B/C choices, todos per checklist item.
- **Social proof** ("X without Y = failure. Every time.") and **scarcity** (time-bound "before proceeding") sparingly.
- **Unity** for collaborative skills; **Liking: do NOT use for compliance — it creates sycophancy.** Reciprocity rarely needed.
- Combinations by skill type: discipline -> Authority + Commitment + Social Proof (avoid Liking/Reciprocity); technique/guidance -> moderate Authority + Unity; reference -> clarity only, no persuasion at all.
- Bright-line rules reduce rationalization; implementation intentions ("When X, do Y") beat general advice ("generally do Y"). Ethical test: would the technique serve the user's genuine interests if they fully understood it?

## STOP gate (deployment)

Never batch-deploy untested skills — "deploying untested skills = deploying untested code." For each skill: RED baseline captured -> GREEN guidance addresses observed failures only, form matches failure type, wording micro-tested vs control -> REFACTOR counters in place and re-verified -> then commit. This repo's verify-all gates + structural tests still run on top; behavioral evidence is the layer they cannot see.
