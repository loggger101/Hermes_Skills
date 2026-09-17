# Spec-Driven Development Patterns (verified from tech-leads-club/agent-skills @ 0ab82f6)

Source: `packages/skills-catalog/skills/(development)/tlc-spec-driven` v3.3.0, `tlc-plan` v0.2.0
(+ `references/document-format.md`), `tlc-implement/references/verify.md`, `spec-lean/scripts/lessons.py`.
License CC-BY-4.0; attribution: Tech Leads Club / Felipe Rodrigues. Mined 2026-09-16. These are the
patterns worth stealing for this brain's spec-driven work (see also `mattpocock-spec-driven-development`).

## 1. Auto-sizing depth by complexity — not a fixed pipeline

The core principle: **complexity determines depth, never ceremony**. Assess scope first, apply only what it needs:

| Scope | Specify | Design | Tasks | Execute |
|---|---|---|---|---|
| Small (≤3 files) | one-liner inline | skip | skip | implement + verify inline |
| Medium (<10 tasks) | brief spec | skip — design inline | skip — implicit | implement + verify |
| Large (multi-component) | full spec + requirement IDs | architecture + components | full breakdown + deps | per-task implement + verify |
| Complex (ambiguity, new domain) | full spec + gray-area discussion | research + architecture | breakdown + phase plan | implement + interactive UAT |

Specify and Execute are always required; Design/Tasks auto-skip when the scope doesn't need them. A
"discuss gray areas" step triggers inside Specify whenever ANY implicit-requirement dimension is present:
persistence/state, external calls, auth, payments, concurrency, state transitions — a pure read endpoint or
config tweak skips it entirely. Undiscussed gray areas are written to the spec's *Assumptions & Open
Questions* (agent's chosen default + rationale) — never silently dropped; that is what lets a closure gate pass.

## 2. EARS-shaped acceptance criteria with CONCRETE values

EARS notation shapes: `When <trigger>, then <observable outcome>` · `While <state holds>, <outcome>` ·
`If <condition goes wrong>, then <outcome>` · `Always, <invariant>`. The hard rule that makes them testable:
**every criterion is an observable outcome with a concrete value.** "The columns exist" is not a criterion —
a horizontal layer-slice has nothing observable to write. Slices are outcomes someone can watch ("schema first,
then endpoints" produces pieces nobody can verify alone). On screens, every state that matters gets its own line:
empty / loading / error / unauthorised.

**Refuse rather than guess.** A gap in the source comes back as a question; "a plausible criterion nobody decided
is the expensive failure — it reads well, gets approved, and ships." When the source contradicts the code, amend
the SOURCE (quietly building the right thing leaves the document five other people read still wrong). `Decided`
carries only what is hard to reverse, in its literal shape; everything reversible is decided while building.

## 3. The nine unwritten requirements — a fixed sweep list

When turning any PRD/design doc into tasks, walk TWO fixed lists instead of inventing scope: every surface the work
exposes (screens × states, API routes × error shapes) and all NINE implicit-requirement dimensions, recording each
landing as *a criterion already in the source / existing behaviour / n/a with reason / Unresolved* — never a landing
the walk invented. The nine:

1. validation 2. failure modes 3. idempotency & retry 4. authorization 5. concurrency & ordering 6. data lifecycle
7. external-dependency failure 8. state transitions 9. observability

`Swept` is one line each, every time — "All nine, one line each" is the format rule; an n/a must say why it does not
apply. This is the same family as spec-driven-eval's E_recall rubric (10 categories there) — both exist because LLMs
systematically omit exactly these dimensions from specs and implementations.

## 4. Deterministic gates run before human review — "enforced by code, not memory"

Structural gates are scripts with non-zero exit = STOP: validate spec BEFORE confirming it (closure gate: EARS-shaped
ACs, filled assumptions, well-formed requirement IDs); validate tasks BEFORE presenting them (granularity smell, no
forward-phase dependency, every task carries `Tests` + `Gate`); check commit message on each atomic commit; and a
completion gate before declaring done — the Verifier's report must exist with verdict PASS citing file:line evidence.
A missing/FAIL/placeholder/evidence-free report fails the gate automatically. The principle generalizes to any repo
gate design: **anything you want guaranteed runs as code, because model memory drifts.**

## 5. Execution contract (per task) + independent Verifier with a discrimination sensor

- Tests derive from acceptance criteria and assert spec-defined outcomes — they never mirror the implementation.
- The gate must pass before a task is done; **the test runner decides, not self-assessment**.
- One atomic commit per task; mark the task complete in tasks.md BEFORE that commit (a crash between the two steps is
  how resume redoes finished work). Never weaken/skip/delete tests to make them pass.
- Blast radius: approving a spec authorizes local implementation and commits only — push/deploy/production DB need an
  explicit go-ahead per action.

**Verifier rules worth stealing verbatim:** the Verifier is a fresh subagent with no inherited context (an author
re-checking reapplies the thinking that produced the gap); it runs read-only, fixes nothing; and **it is dispatched by
whoever holds the whole feature, never by a builder** — "a fresh context is not independence on its own: the parent
writes the brief, so a Verifier spawned by the agent that just closed the last batch inherits that agent's *scope* even
though it inherits none of its tokens." The verdict goes to the orchestrator/user, never back to the author. FAIL →
fix tasks routed to an implementer → re-verify, bounded to 3 fix→re-verify iterations before escalating.

**Discrimination sensor**: behavior-level mutations run in a scratch state and then discarded — it confirms the tests
can actually detect regressions (a suite that passes both with and without a mutation is not discriminating). This
complements deterministic gates: the gate proves the suite runs; the sensor proves the suite means something.

**Verifier step 1 insight**: check the checklist against its binding sources FIRST, because "a checklist that is wrong
validates cleanly" — every later comparison shares both ends of the same mistaken artifact. And compare in BOTH
directions: a contradiction (check vs design) outranks a failing test; but absence is blind to comparison ("a check
nobody wrote contradicts nothing"), so enumerate what each binding source decides and confirm each has a check.

## 6. Self-improving lessons layer with deterministic bookkeeping (`lessons.py`)

LLM supplies judgment (which failure happened, phrasing, grounding); the script owns everything mechanical: IDs,
recurrence counting across distinct features, candidate→confirmed promotion (threshold 2), quarantine on repeated
failure when applied (threshold 2), pruning of stale uncorroborated candidates (45-day window). Canonical state is a
machine-owned JSON store; LESSONS.md is regenerated on every write — "bookkeeping by hand is exactly what rots a
lessons file, so it lives here, not in a prompt." Grounded signals: ac_gap / surviving_mutant / spec_precision_gap /
spec_deviation / gate_fail. Pattern for any persistent learning artifact: **judgment in the model, arithmetic in code.**
