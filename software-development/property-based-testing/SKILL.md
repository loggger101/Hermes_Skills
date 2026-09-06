---
name: property-based-testing
description: "Hypothesis property tests: roundtrip, oracle, invariant"
version: v1.0.0
author: Hermes Agent (ported from trailofbits/skills property-based-testing)
license: CC-BY-SA-4.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hypothesis, testing, pbt, python, verification]
    related_skills: [test-driven-development, test-infra-ml]
---

<!-- source: trailofbits/skills plugins/property-based-testing (starred-repo deep-dive 2026-09-05). Upstream license CC-BY-SA 4.0 — attribution retained per that license. -->

## What This Skill Does

Property-based testing (PBT): instead of asserting one hand-picked input, assert a **rule
over the whole domain** and let the generator hunt for counterexamples. Worth it when code has
an algebraic shape — an inverse, an invariant, an oracle. Code with no such shape gets example
tests; saying so is a valid outcome (don't add the dependency just to look rigorous).

## Property Catalog

| Property | Formula | Where it applies |
|---|---|---|
| Roundtrip | `decode(encode(x)) == x` | serialization, conversion pairs |
| Inverse | `f(g(x)) == x` | encrypt/decrypt, compress/decompress |
| Oracle | `new(x) == reference(x)` | optimization, refactoring, reimplementation |
| Idempotence | `f(f(x)) == f(x)` | normalization, formatting, sorting |
| Invariant | holds before and after | any transformation, contract state |
| Easy to verify | `is_sorted(sort(x))` | complex algorithms with cheap checkers |
| Commutativity / Associativity / Identity | algebraic laws | binary/set ops, combining ops |

Strength ordering (weakest→strongest): no-crash → type-preservation → invariant → idempotence
→ roundtrip/oracle. **Assert the strongest property the code supports.** "No crash" alone rarely
justifies the dependency — if that's all you find, either a small rearrangement exposes something
stronger or this is honestly a poor PBT candidate (rule out the first before settling for the second).

## The Two Ways a Property Test Asserts Nothing

- **Tautology** — `assert add(a,b) == a + b` restates the implementation; shared bugs can't fail it.
  Exception: `f(x) == f(x)` IS a real determinism property when f isn't obviously pure (dict/set
  serializers, hashing, anything reading the clock).
- **Vacuity** — `assume()` filtering out nearly every input passes without exercising anything;
  self-contradictory `assume()` passes having run zero cases. Push constraints into the strategy so
  the generator produces valid inputs directly.

## Writing Strategies (the decisions that matter)

1. **Constraints go in the strategy, not `assume()`.** `st.integers(min_value=1)` beats
   `@given(st.integers())` + `assume(x > 0)` — filtering wastes budget and trips Hypothesis's
   exhausted-filter guard (a warning nobody reads). Reserve `assume()` for relations between two
   already-generated values.
2. **Derive dependent fields** with `st.composite`/`.flatmap`, don't generate independently + filter:
   ```python
   @st.composite
   def sized_list_and_index(draw):
       xs = draw(st.lists(st.integers(), min_size=1))
       i = draw(st.integers(min_value=0, max_value=len(xs) - 1))
       return xs, i
   ```
3. **Pin known edge cases** with `@example([])` / `@example([1])` — empty, single, all-duplicates,
   zero, negative, max-representable recur every time; they run on every invocation and document intent.
4. **Settings by context:** 10 examples for local iteration, ~200 for CI, 1000 + `deadline=None`
   nightly. Default deadline turns a slow machine into a failing test — that flake gets suites deleted.
5. **Test the error path:** `st.binary()` against a decoder; contract = "raises DecodeError or
   succeeds, never IndexError, never hangs." Catch only the documented exception.

## Interpreting Failures (most of the work)

A failure means one of three things — different responses:

| Symptom | Cause | Action |
|---|---|---|
| Violates a documented guarantee | Code bug | Report with shrunk input + quote from doc |
| Input violates a documented precondition | Over-broad strategy | Constrain the strategy (NOT a bug) |
| Property contradicts docstring/type | Wrong property | Fix the property |
| Edge case spec never addresses | Ambiguous spec | Ask maintainer — discussion, not bug report |

**Ground before trusting:** check what the code actually promises in descending authority: external
spec → type annotations → docstrings → existing tests → function name (weakest; `normalize` often
means something narrower than the word). Worked example: idempotence fails on `'\x00'`; if docs say
"any unicode" it's a real bug, if they say "ASCII printable only" it's a strategy fix.

Recurring failure patterns: lone surrogates break text roundtrips (bug iff format claims arbitrary
str); denormals break numeric invariants (`1e-320` is exactly what no human writes by hand);
hash/equality divergence violates the language contract itself — report without grounding; off-by-one
in custom iterators shows up as `list(it(xs)) == xs` dropping the last element.

Report with classification attached, including uncertain cases ("ambiguous spec, needs a maintainer
decision") — a suppressed finding can't be triaged by anyone else.

## When to Use / Not Use

**Use:** encode/decode pairs, parsers, canonicalizers, validators, numeric types, comparators/sort
order, data structures, state invariants; reviewing whether existing `@given` tests assert anything
real; a shrunk counterexample where you must tell wrong-property from genuine-bug.
**Not for:** coverage-guided binary fuzzing (libFuzzer/AFL), mutation campaigns, static analysis,
benchmarking, e2e UI tests. If the project has no PBT library yet, adding one is a dependency
decision that belongs to the user — offer once with the specific property you'd write.
