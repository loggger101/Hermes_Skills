# Checker verdict states and model-checking gotchas (verified from backnotprop/pstack `skills/statechart` @ main, 2026-11-11)

Source: `backnotprop/pstack` → `skills/statechart/` — a tool that writes a **TLA+ spec of a stateful
system** (product flow, protocol, service), runs it through TLC, and renders the result as a Mermaid
statechart with shortest bug-paths marked. Upstream license MIT (Copyright (c) 2026 Lauren Tan);
attribution retained per that license. Read from source this pass: `SKILL.md` (9.1 KB),
`scripts/test/plain-tlc.test.ts`, and the test layout in the repo tree.

**Runnability here, stated honestly:** TLC needs Java; this Windows box has node v22 but **no java, no
mise, no docker**, so an end-to-end model-check run was NOT executed here — everything below is from
reading their shipped source/tests, not local measurement. Their `scripts/run.ts` bootstraps Java+TLC
via mise on first run (network required).

## 1. The transferable idea: a checker verdict is three-valued, never two

Their test helper is literally named `agrees(...)` and returns `{status, breaks: Map<rule,count>, holds: [], unchecked: []}` —
every rule lands in exactly one of **holds / breaks / NOT CHECKED**, and "not checked" is a first-class
answer the report prints under *"Rules not checked"* with the standing note that *a rule that is not
checked can hold or break*.

The killer test case (`plain-tlc.test.ts`, "a rule that breaks before another rule fails to evaluate
breaks in either order"): two invariants where one state both violates a rule **and** makes another
rule fail to evaluate (e.g. `x' = 1 \div 0` or `Assert(FALSE, ...)` reached first). The harness asserts
the verdict is identical **in either invariant order**, and that the evaluation-failed rules come back
as `unchecked`, not as holds. That is the failure mode our own gates share:

- A pytest/shell gate that *errors* (collection error, missing dep, timeout) must never be tallied as a
  pass — same for a validator whose regex simply didn't match anything to check. Their vocabulary gives
  us the discipline: report `unchecked` explicitly with "can hold or break", so downstream readers can't
  read silence as green. Our verify-all gates print only passes/failures; when a gate *skips* (optional
  dep absent, like their `{ skip }` on TLC-dependent tests), say which claims that skip leaves unproven.
- Order-independence is the test to write for any multi-rule checker: if rule A's violation can mask or
  change rule B's verdict by evaluation order alone, the harness output is not trustworthy — pin it with
  a permutation test like theirs.

## 2. Rule peeling: enumerate all violations when the engine stops at the first

TLC halts on the first violated invariant. Their driver instead: run TLC on the config as written; for
each rule found breaking, **remove that rule and re-run**, until nothing breaks — so one session yields
every violation, not a whack-a-mole per invocation. After the first break each run is capped at 100,000
distinct states "so that a large model does not run without end", and hitting the cap downgrades rules
to *not checked* (with the caveat that the cap module reorders variables, so for temporal properties TLC
may find a different counterexample than an unbounded run).

Generalizes to any first-error engine we wrap: if stopping early is the tool's nature (linters with
`--max-errors 1`, type checkers bailing, CI steps that abort), peel-and-rerun converts one signal into a
complete inventory — and record the state cap so completeness claims stay honest.

## 3. TLC gotchas worth keeping even without running it

- **Deadlock vs terminal state:** in TLA+ a state with no outgoing step breaks `NoDeadlock` *even when it
  is a correct end state*. Fix pattern: add an action true only in end states that changes nothing —
  `Done == phase \in {"paid","failed"} /\ UNCHANGED vars` — labeled in the view. If an invariant already
  occupies the name, use `CHECK_DEADLOCK` instead of relying on the default.
- **Exploration past bugs:** TLC keeps exploring after a violation (so charts show post-bug states), and
  therefore *an unbounded model can run forever* once anything breaks — keep CONSTANTS small or add a
  `CONSTRAINT`. Constraint/`ACTION_CONSTRAINT` states still get their rules checked but are not explored
  further, so **a deadlock in such a state does not show**.
- **VIEW / SYMMETRY:** equivalent-state collapsing means an arrow may point at the canonical representative
  rather than the actually-reached state; the report says so — don't read chart arrows as literal traces.
- **`Next` as explicit disjunction** of named actions, else every step is just `Next` and bug paths lose
  their story (naming is for the human reader of the path).
- **Never weaken a rule to make it hold** — if the model has no variable expressing a rule, add the
  variable. Their one-line version of "the test must not be edited into submission".

## 4. Rendering judgment rules that transfer to any diagram-for-a-reader task

Aim ≤ ~20 arrows; coarsen by returning fewer labels from `state()` (merge values that behave alike), but:
**keep every state on a bug path**, never merge two states that break *different* rules, hide steps of an
arrow all-or-none (partial hiding silently narrows the arrow's condition), keep at least one outgoing
arrow for any model-exit state, and **say in the handoff which steps the chart hides**. Labels are written
in the reader's vocabulary ("you press play", "the roster read fails") — code/action names stay out.

## 5. Test-shape inventory of their skill (what a serious TS skill ships)

`cli.test.ts` 50 KB · `chart.test.ts` 40 KB · `differential.test.ts` 18 KB · `labels.ts` 20 KB ·
`corpus.test.ts` + a golden corpus (`test/corpus/*/sany.out`, incl. the classic **DieHard** deadlock
example, `TwoPhase*`, `Login*`) · `config-fuzz.test.ts` · `pipeline.test.ts` · `messages.test.ts`.
Differential testing = two implementations of one contract checked against shared inputs; golden corpus =
pinned outputs per model so parser regressions surface as diffs. Our nearest neighbors: Hypothesis PBT in
`property-based-testing`, mutation-tested gates in `mutation-test-audit-gate.md`; neither covers the
golden-corpus or differential shape — this closes that gap on the reference layer.
