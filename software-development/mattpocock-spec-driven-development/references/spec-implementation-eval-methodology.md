# Spec-Implementation Evaluation Methodology (verified from tech-leads-club/agent-skills @ 0ab82f6)

Source: `packages/skills-catalog/skills/(development)/spec-driven-eval` v1.0.0 (author Waldemar Neto, CC-BY-4.0).
Mined 2026-09-16. Use when grading how completely an implementation fulfills a PRD/spec — benchmarking multiple
implementations of the same PRD, or auditing "was this feature 100% implemented?" (incl. test coverage vs acceptance
criteria). The design goal is **reproducibility**: same PRD + same commit ⇒ same final grade across runs and evaluators.

## Two subjects, two questions — keep verdicts separate

1. **Framework fidelity** — did it honor the PRD and stay in bounds (respect: implementation side + scope S), and
   surface implicit requirements without noise (elicitation E)?
2. **Harness completeness** — does the test suite prove every sanctioned requirement is actually built (T + gates G)?

The linkage that makes "all implemented" well-defined: the harness is held accountable for the full SANCTIONED SET =
`PRD acceptance criteria ∪ valid E-additions`. A valid extracted requirement with no test is a *harness* miss, not a
framework miss — extraction defines the verification target.

## Why binary checks (the core design choice)

Graded/Likert scales ("is this a 3 or a 4?") are the dominant source of evaluator-to-evaluator disagreement; atomic
binary MET/UNMET checks raise inter-evaluator agreement to roughly human level, and partial credit is DERIVED from the
fraction met — never judged on a sliding scale.

**Five core rules:** (1) Evidence-or-zero: every MET cites `file:line`; no located evidence ⇒ UNMET; never award credit
from assumptions or from the PRD restating intent. (2) Search-before-zero: before any UNMET, record the search actually
performed — "UNMET means *searched and genuinely absent*, not *did not look*"; a check with no shown search is *not yet
scored*. (3) Read the path end-to-end INCLUDING THE DATA SHAPE: for an emitted/persisted artifact inspect the constructed
payload object itself, not just the call site — `emit(...)` being reached does not prove the named field is in it; a test
that exercises but doesn't assert a behavior does NOT meet its verification check. (4) Judge ≠ author when benchmarking:
LLM judges over-reward their own output (self-preference bias); if same model, flag it and treat borderline checks as UNMET.
(5) Evaluator is READ-ONLY over the subject — never fix a red gate to make it green; record ✗, apply Adjusted Final, list
the fix in the report. Modifying the subject mid-evaluation contaminates the benchmark AND invalidates the diff surface.

## Reproducibility rules (all mandatory)

1. **Freeze the AC list AND its checklist** — the single biggest drift source; both `I`, `T` and denominators depend on
   them. Persist to `_ac-baseline.md`; every implementation of that PRD scores against the identical baseline. One AC = one
   testable assertion; one check = one atomic observable yes/no proposition (no collapsing, no splitting). The baseline is
   deliberately NOT timestamped — it's a shared contract artifact; only report filenames get UTC timestamps (so parallel
   evaluators of the same story never overwrite each other).
2. Priority comes from the PRD's explicit P0/P1/P2 labels, never inferred silently (unlabeled ⇒ `ASSUMED`, listed under Assumptions).
3. Round once at the end; carry full precision through arithmetic; round only reported values to 2 decimals.
4. **Compute, don't calculate**: the roll-up MUST be executed as a script taking per-AC fractions + priority weights as
   input, with its output pasted into the report — "a hand-summed denominator is a known failure mode that silently shifts
   the grade band." Σw derived inside the script from the same weight table shown in the report.
5. **Self-consistency ensemble k=3**: evaluate three times independently at low temperature, majority MET/UNMET per check;
   persistent disagreement on one check means its wording is ambiguous — sharpen it in the baseline (fix the operational
   definition, don't average away disagreement).

## Scoring model

- `I = # I-checks MET / # I-checks` where each AC decomposes into behaviorally-observable clauses only. Three parsing rules:
  **conjunction/payload-field** — every named field in an enumerated artifact gets its own check, verified against the actual
  constructed object; **disjunction/product-chosen** — "A or B" is either one check per independent path OR (when framed as
  product-controlled) two checks: default implemented + alternative reachable without code change (hard-coding one option fails);
  **wiring/ingress** — for async side-effects delivered via inbound events, a dedicated wiring I-check that the entry endpoint
  receives+verifies+dispatches by type to the handler; "a fully-tested handler behind a dead or mis-routed endpoint still fails."
- `T = # T-checks MET / # T-checks` at policy-fixed levels (pure logic ⇒ unit required; observable HTTP/contract/persistence ⇒
  e2e/integration required). **T-outcome** checks assert the REAL resulting state against real infra, entry-point-neutral (driving
  a handler directly vs through HTTP is equivalent — don't penalize async architectures for not being driven end-to-end);
  mock-only (`expect(save).toHaveBeenCalled()`) proves a call, not an outcome ⇒ UNMET for "results in/persisted" checks ONLY —
  the exclusion must not over-fire: when the asserted proposition IS the external call ("calls StripeClient.cancel"), a spy is correct.
  Required level is a FLOOR: an e2e test asserting a unit-required proposition satisfies it.
- `AC_score = 0.6·I + 0.4·T`; `Story_score = mean(ACs)`; `Final = Σ(w·Story)/Σw` with P0=3, P1=2, P2/out-of-scope=0 (excluded from the
  grade, reported separately as roadmap readiness). Weights fixed across a benchmark — changing them breaks comparability. Bands: ≥0.90
  spec-complete / 0.75–0.89 strong / 0.60–0.74 partial / 0.40–0.59 weak / <0.40 inadequate.

## Reported BESIDE the grade (never folded into Final — comparability)

- **Robustness R** — extra tests beyond PRD cases, weighted High=1.0/Med=0.5/Low=0.25; a high R with low T is still a low grade.
- **Scope S** — traceability: every built behavior must trace to a sanctioned source (PRD AC or valid E-addition). PRD-boundary
  violation ⇒ fail; rogue build (traces to neither) ⇒ fail; plan drift (sanctioned but not/half-built) ⇒ partial. A VALID requirement
  correctly deferred as out-of-scope is good discipline, NOT a penalty.
- **Engineering Gates G** — each gate actually-executed ✓/✗ or explicit `not-run` with ATTEMPT EVIDENCE ("probe-before-not-run": the
  command executed and its error output pasted; "infra unavailable" without a probe is fabricated evidence). The build gate is pinned
  mechanically to one canonical command exiting 0 — no evaluator discretion. Only confirmed-red triggers `Adjusted Final = Final × 0.5`
  (unadjusted stays reported); not-run grants/deducts nothing. Pre-existing unrelated toolchain failures in untouched code are documented
  non-graded notes, not ✗.
- **Test Distribution D** — every added feature test classified into exactly one tier: Necessary (P0 primary happy path) / Secondary
  (other AC-mapped: P1, edges, negative paths, authz, idempotency) / Nice-to-have (no AC; defensive/exhaustive). Report counts + % with a
  shape read — thin on Necessary but heavy on Nice-to-have = "robustness without proven core."

## Elicitation E — did the framework extract what it should have?

- **E_recall** against a FROZEN implicit-requirement category rubric (PRD-agnostic, reusable): input validation & bounds · error
  taxonomy & messaging · AuthN/AuthZ · idempotency & dedup · concurrency & races · data lifecycle & consistency · observability · limits/
  pagination/rate · external-dependency failure · state-transition integrity. `E_recall = Addressed/(Addressed+Missed)`, N/A excluded; cite
  spec.md:line per category. For head-to-head benchmarks also report POOLED recall (union of all frameworks' valid additions as the master list).
- **E_precision** via an added-requirement ledger: every spec requirement not traceable to a PRD line, adjudicated binary with one-line
  warrant — Valid-necessary / Valid-defensive / Invalid (hallucinated or contradicting); `E_precision = (valid)/(total additions)`. The valid
  set feeds the harness denominator and S-traceability.
- **E_justified** — fraction of additions carrying explicit rationale/traceability; unjustified additions are a smell even when plausible.

## Bias controls & anti-patterns (condensed)

Verbosity bias: more code/tests never raises I or T — only AC-mapped checks count, surplus goes to R/D. Anchoring: score against the frozen
baseline + calibration anchors (reference.md holds worked clearly-MET / clearly-UNMET / borderline examples; >20% judge disagreement ⇒ checklist
wording too vague). Anti-patterns worth quoting back verbatim: scoring on a "feels like 0.75" slide instead of counting binary checks; re-deriving
the AC list per implementation (breaks comparability); UNMET without showing the search or MET without file:line; searching the full codebase
before bounding with `git diff --name-only` (the DIFF SURFACE is the primary evidence scope — record it in the report); awarding credit from a
symbol-name match instead of tracing the path end-to-end; reporting a gate as passing without running it; fixing subject code to turn red green.
