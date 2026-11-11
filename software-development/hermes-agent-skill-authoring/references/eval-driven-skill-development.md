# Eval-Driven Skill Development (measured loop, from `anthropics/skills` skill-creator)

Source: [anthropics/skills](https://github.com/anthropics/skills) `skills/skill-creator/SKILL.md` (485 lines, Apache-2.0), read
in full 2026-11-11. This is the upstream *quantitative* counterpart to this skill's structural gates and to
`references/behavioral-skill-testing.md`: that file tests whether a discipline skill changes behaviour under pressure; **this** one
measures whether a skill actually improves outcomes against a baseline, and whether its description triggers at all.

Applicability on this box: the upstream optimizer loop shells out to `claude -p`. Measured 2026-11-11: **`claude` is not on PATH
here**, so run descriptions-of-record by hand (or via an available harness) rather than assuming the automated loop works. The rest
of the loop needs only subagents plus a filesystem, which Hermes has (`delegate_task`).

## Core loop

1. Capture intent (what should the skill enable; when must it trigger; expected output format; are outputs objectively verifiable -
   if yes, test cases are worth building; writing-style/art skills usually aren't).
2. Draft the SKILL.md. All "when to use" prose belongs in `description`, not the body.
3. Write 2-3 realistic test prompts (the kind a real user types) and save them as `evals/evals.json` **before** writing assertions.
4. Run every prompt twice - with-skill and baseline - then grade, review with the human, rewrite, repeat; expand the test set later.

## A/B arms: spawn both in one turn

- Spawn the with-skill arm and the baseline arm for each case **in the same turn**. Serialising them (all treatments first, baselines
  after) is the documented mistake - they drift apart in environment state.
- Baseline depends on what you're doing: creating a skill → no skill at all; improving an existing skill → snapshot it first
  (`cp -r <skill> <workspace>/skill-snapshot/`) and point the baseline arm at the **snapshot**, otherwise your own edits leak into
  the control.
- Workspace layout (sibling of the skill dir): `<skill>-workspace/iteration-N/<eval-name>/{with_skill,old_skill|without_skill}/outputs/`.
  Name eval directories descriptively ("form-field-roundtrip"), not `eval-0`; create dirs as you go.

## Timing data is capture-or-lose

Token counts and wall time arrive on the subagent completion notification and are **not persisted anywhere else**. Write each one to
`timing.json` (`{"total_tokens": …, "duration_ms": …}`) *as the notification lands*; a batched pass afterwards has nothing to read.
In Hermes terms: pull usage from the child result immediately after `delegate_task` returns rather than reconstructing it later - and
if your harness exposes no usage numbers at all, record that honestly instead of inventing them (see this repo's convention on dated
provenance fields).

## Grading contract

- Per-run `grading.json` must use the field names **`text`, `passed`, `evidence`** - not `name`/`met`/`details`. Viewer/aggregation
  tooling keys off exactly these, so a plausible synonym silently produces empty columns.
- Prefer a script over eyeballing for anything programmatically checkable; scripts get reused across iterations.
- Aggregate per configuration: pass rate, time, tokens - mean ± stddev and the delta vs baseline. Put each treatment before its control.

## Analyst pass (what aggregate stats hide)

After aggregating, look for: assertions that **always pass regardless of skill** (non-discriminating - they inflate scores and teach
nothing), evals with **high variance** (likely flaky; fix the case or the assertion before believing either arm), and time/token
trades where a treatment wins accuracy by burning 3x tokens.

## Triggering: descriptions are the mechanism, and models under-trigger

- Skills are offered to the model as name + description; that text decides invocation. Upstream's countermeasure for under-triggering
  is deliberately "pushy" prose: enumerate mention-forms ("whenever the user mentions dashboards, internal metrics, or wants to
  display any company data, even if they don't ask for a 'dashboard'").
- Measured behaviour worth knowing: models **skip skills for tasks they can do directly**. "read this PDF" may never trigger a PDF
  skill no matter how well its description matches - so trigger evals built from trivial one-step prompts prove nothing. Make eval
  queries substantive (multi-step, concrete: file paths, column names, company context, casual phrasing, even typos).
- Trigger eval set: ~20 realistic queries, roughly half should-trigger and half not. The valuable negatives are **near-misses** -
  same keywords, different need ("adjacent domain", or right task but a better tool) - never obviously-unrelated filler, which tests
  nothing.
- Optimizer loop (needs a scriptable CLI): split the set 60% train / 40% held-out test, run each query ~3 times to get a stable
  trigger rate, propose description edits from failures, re-score both splits for up to ~5 iterations, and pick `best_description`
  by **test** score - selecting on train score overfits the eval set.

## Writing rules that survive measurement (upstream's editorial stance)

- Imperative voice; explain *why* instead of stacking all-caps MUSTs - rigid prohibition blocks are treated as a yellow flag, and this
  matches the measured result in `references/behavioral-skill-testing.md` where a positive recipe beat a prohibition (3.0 with zero
  variance vs 4.4 unwanted items, worse than no guidance at all).
- Look for **repeated work across runs**: if every test-case agent independently wrote its own `create_docx.py`, that is the signal to
  bundle the script once in `scripts/` and tell the skill to use it - otherwise every invocation reinvents it.
- Generalise from feedback rather than patching the specific example: a skill tuned to three hand-picked prompts is useless at scale;
  when something is stubborn, try a different metaphor or workflow instead of adding another constraint.

## Hermes adaptations (what changes here)

- Arms = `delegate_task` children with the same prompt and context strings except the skill path; children inherit tools rather than
  running in an isolated sandbox, so state leakage between arms is possible - run them against separate scratch dirs and never let one
  arm write where the other reads.
- This repo's `tools/verify-all.py` gates are **structural** (frontmatter, links, counts, citations). They cannot tell you a skill
  helps; the loop above is what supplies that evidence, so a "skill added, verify-all green" commit means *shaped correctly*, not
  *effective*.
- For skills in this catalog whose value is procedural and cheap to exercise (scripts, commands), prefer running the real procedure as
  the eval - which is how most rows of `docs/starred-repos-ledger.md` were mined - and reserve full A/B benchmarking for skills where
  judgement does the work: writing style, review strictness, plan quality.
