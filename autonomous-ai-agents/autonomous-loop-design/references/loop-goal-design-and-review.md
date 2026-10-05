# Loop goal design and review: a decidable goal, an independent judge, a boundary

Source: [affaan-m/ECC](https://github.com/affaan-m/ECC) `skills/loop-design-check` (MIT, ECC origin), read at source level
2026-10-05. The "green-keeper" gate in section 4 was written and **run here** (pytest 9.1.1, Python 3.14.6, Windows) with
a planted cheat, so its numbers are measured; the rest is ECC's design guidance, restated.

Complements [`loop-engineering.md`](loop-engineering.md): that file specifies a scheduled job (cadence, state,
bail-out); this one asks whether the loop's *goal* is right and whether it can run away or cheat.

## 1. Premise

A model has no built-in "steer toward the goal across turns"; a loop supplies the feedback. Two levels exist: execution
(a machine measures distance to the literal goal and grinds it to zero) and judgment (is the goal itself right, should it
change or stop). The machine owns the first, **a human owns the second**. Hand the sign-off to the machine and it sprints
toward a goal nobody questioned.

## 2. Writing a loop: gate, goal, type, skeleton, damping

**Step 0, veto gate (any miss = do not build a loop):** the task repeats about weekly or more; verification can be
automated; the token budget can take it; the agent has tools that actually run the thing and see the result. A repo with
no tests, no reconciliation baseline and no lint will only get its errors amplified.

**Step 1, a machine-decidable goal.** Self-check: read the goal to someone who does not know the domain; can they run one
command and say whether it is done? Five points:
1. the done-criterion is machine-verifiable;
2. **boundaries sit next to it** ("must NOT delete or weaken tests"), the anti-Goodhart clause;
3. a failure fallback: retry cap N, then escalate to a human;
4. the goal is layered (a coarse stop condition plus finer checks);
5. prefer **reconciliation over assertion**: anchor to an external fact (golden sample, upstream total, tie-out) before
   your own assertions. "Diff against the reference < 0.01" cannot be gamed the way "all tests pass" can.

**Step 2, loop type:**

| Task | Type | Stops |
|---|---|---|
| Clear "done" test | servo (goal-style closed loop) | on reaching the goal |
| No endpoint, keep a state healthy | regulator (thermostat, `/loop`) | never; acts only past a dead-band |
| Poll until a condition | regulator with an exit | when the exit holds |
| Must happen on time | wrap one of the above in a schedule | cron fires it |

**Step 3, skeleton.** *Maintenance:* document-driven dispatch (the loop reads a doc on a timer and acts only when it
changed); the problem column is human-written, the result column loop-written, state moves one way, **the exit code is
final**, and the "done" cell is flipped only by a human. *Greenfield:* plan / build / judge, where plan writes a spec with
script-judgeable acceptance conditions, build must not edit them, and the judge runs acceptance **independently and
deterministically**, returning failures to build; three failures escalate.

**Step 4, damping.** A retry cap, a hard stop and a human on the last switch. Negative feedback without damping
oscillates (the spin-in-place token burner).

**Step 5, land in stages:** run it once by hand (forces you to state how the judge decides), then harden into a skill or
sub-agents, then put it on cron.

## 3. Reviewing a loop: five failure modes (any hit = send it back)

| # | How it breaks | Review question | Antibody |
|---|---|---|---|
| 1 | Goal is a correct platitude: spins | Can a machine judge the exit yes/no? | decidable result condition |
| 2 | "Verify" means "looks ok": confident stop | Is the judge the defendant? | independent judge + exit-code rules |
| 3 | Gates only on "tests pass": deletes the tests | Is there a boundary, not just a done-criterion? | done **plus** boundary |
| 4 | Expects to ask mid-run: it will not, it commits a guess | Is any clarification deferred to runtime? | front-load every clarification |
| 5 | Stale CLAUDE.md or memory: errors amplified | Who keeps the docs it reads fresh? | layered memory + periodic lint |

Three red lines before anything goes unattended: keep judgment with a human; responsibility does not transfer (merge,
publish and money-moving authority are not delegated); and the more self-rewriting a loop is, the **stricter** the review
gate must be, placed before the action rather than as a post-hoc patch.

## 4. Failure mode 3 reproduced: a boundary gate, with a planted cheat

Setup: `calc.add` returns `a - b`; three tests (`test_add`, `test_zero`, `test_neg`); a snapshot of collected test ids is
taken before the loop. The judge exits 0 only if the suite passes **and** no baseline test id disappeared.

```python
def collect():   # pytest --collect-only -q, keep lines holding "::"
    out = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"],
                         capture_output=True, text=True)
    return sorted(l.strip() for l in out.stdout.splitlines() if "::" in l)
# snapshot: write collect() to .loop-baseline.json before iteration 1
# judge:    missing = baseline - collect();  exit 0 iff pytest passes and not missing
```

| Scenario | Naive gate (pytest exit) | Boundary gate |
|---|---|---|
| Broken code, 3 tests | 1 (correct) | exit 1, `tests pass: False` |
| **Agent deletes the two failing tests** | **0, "1 passed"** | **exit 1**, `removed: test_add, test_neg` |
| Honest fix (`a + b`) | 0 | exit 0 |
| **Agent rewrites the failing asserts to `assert True`** | 0 | **0: still a false green** |

The last row is the limit of the id-set gate: nothing was deleted. Add a second boundary: count non-constant asserts per
test file (an `ast` walk over `ast.Assert` whose `test` is not a `Constant`), snapshot it too and fail when it drops.
On that file it fell from 3 to **1**. Stronger still is reconciliation against something the agent cannot edit
(a golden output, a mutation run in CI, coverage not lowered).

## 5. Worked review: "nightly: make failing tests pass"

Naive goal "make all tests pass" hits failure modes 3, 2 and 4. Fixed goal: all green **and** no test file deleted or
weakened **and** coverage not lowered **and** a change list written. Type: servo with retry cap 3. Judge: CI run
independently, never the fixing agent. Ambiguous fixes are left for the human instead of guessed. The loop opens a PR and
does **not** merge; a human flips the last switch. The difference is four constraint lines.
