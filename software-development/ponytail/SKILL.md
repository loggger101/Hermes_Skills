---
name: ponytail
description: "Laziest working solution: reuse, stdlib, native first."
version: 1.0.0
author: Hermes Agent (ported from DietrichGebert/ponytail, MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [minimalism, yagni, over-engineering, code-review, dependencies, simplicity]
    related_skills: [simplify-code, python-craft, brainstorming, mattpocock-codebase-design, requesting-code-review]
---

<!-- source: DietrichGebert/ponytail skills/ponytail* (MIT), read 2026-10-05; the debt-scan grep was run live -->

# Ponytail: the lazy senior dev

## What This Skill Does

Pushes any coding task toward the smallest solution that actually works, by climbing a fixed ladder before writing
code, and provides three review modes that hunt for over-engineering (a diff, a whole repo, and a ledger of deliberate
shortcuts). Lazy means efficient, never careless: it shortens the solution, not the reading.

## When to Use

- Writing, adding, refactoring or fixing code, and choosing libraries or dependencies, when the agent tends to over-build
- The user says "be lazy", "simplest solution", "yagni", "do less", or complains about bloat, boilerplate or needless dependencies
- Reviewing a diff or repo specifically for over-engineering (not for bugs; use a normal review for those)
- Not for prose, translation or other non-coding work

## The ladder (stop at the first rung that holds)

1. **Does this need to exist?** A speculative need is skipped, with one line saying so (YAGNI).
2. **Already in this codebase?** An existing helper, type or pattern is reused. Re-implementing what lives a few files over is the commonest slop.
3. **Stdlib does it?** Use it.
4. **Native platform feature?** `<input type="date">` over a picker library, CSS over JS, a DB constraint over app code.
5. **Already-installed dependency?** Use it. Never add a dependency for what a few lines do.
6. **Can it be one line?** Then one line.
7. **Only then:** the minimum code that works.

The ladder runs *after* understanding: read the task and the code it touches, trace the real flow, then climb. Two rungs work: take the higher.

**Bug fix means root cause.** A report names a symptom. Before editing, grep every caller of the function you will touch. One guard in the shared function is a smaller diff than a guard in each caller, and patching only the path the ticket names leaves the sibling callers broken.

## Rules

- No unrequested abstractions: no interface with one implementation, no factory for one product, no config for a value that never changes. No scaffolding "for later".
- Deletion over addition; boring over clever; fewest files; the shortest diff wins, but only once the problem is understood (the smallest change in the wrong place is a second bug).
- Complex request: ship the lazy version and question it in the same reply ("Did X; Y covers it. Need full X? Say so."). Do not stall on something you can default.
- Two stdlib options of equal size: take the one correct on edge cases.
- Mark a deliberate corner-cut with a known ceiling (global lock, O(n^2) scan, naive heuristic) using a comment `ponytail: <ceiling>, <upgrade trigger>`.
- Output: code first, then at most three short lines: `[code] -> skipped: X, add when Y.` Explanation the user asked for is not debt; unrequested defence of a simplification is.
- Non-trivial logic (a branch, a loop, a parser, a money or security path) leaves **one** runnable check behind: an `assert`-based `__main__` self-check or one small `test_*.py`. No frameworks or per-function suites unless asked.

Intensity: **lite** builds what was asked and names the lazier alternative in one line; **full** (default) enforces the ladder; **ultra** is a YAGNI extremist that challenges the requirement itself ("no cache until a profiler says so; when it does, `@lru_cache`").

## When NOT to be lazy

Never simplify away: input validation at trust boundaries, error handling that prevents data loss, security measures, accessibility basics, or anything explicitly requested. If the user insists on the full version, build it without re-arguing.
Never skip comprehension to ship a small diff: that is the dangerous kind of laziness, a confident wrong fix.
Physical systems need calibration knobs a minimal model cannot see (a real clock drifts, a sensor reads off); leave the knob.

## Review modes (list findings, apply nothing)

One numbered line per finding so the user can say "fix 2 and 5":
`<N>. <file>:L<line>: <tag> <what>. <replacement>.`

| Tag | Meaning |
|---|---|
| `delete:` | dead code, unused flexibility, speculative feature; replacement is nothing |
| `stdlib:` | hand-rolled thing the standard library ships; name the function |
| `native:` | dependency or code doing what the platform does; name the feature |
| `reuse:` | an equivalent helper already in this repo; name the path |
| `yagni:` | abstraction with one implementation, config nobody sets, layer with one caller |
| `shrink:` | same logic, fewer lines; show the shorter form |

- **Diff review:** scope is complexity only. Bugs, security and performance go to a normal review pass. End with `net: -N lines possible.`, or `Lean already. Ship.` A single smoke test or self-check is the minimum, never flag it for deletion.
- **Repo audit:** same tags over the whole tree, ranked biggest cut first. Hunt: deps the stdlib/platform ships, single-implementation interfaces, one-product factories, delegate-only wrappers, one-export files, dead flags and config, hand-rolled stdlib, duplicated helpers. **Before any `delete:`, grep the whole tree for the symbol**, including tests, fixtures and string or dynamic references. End with `net: -N lines, -M deps possible.`
- **Debt ledger:** collect the `ponytail:` markers so a deferral cannot become permanent:

  ```bash
  grep -rnE --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build '(#|//|/[*]) ?ponytail:' .
  ```

  One row per hit: `<file>:<line>, <what was simplified>. ceiling: <limit>. upgrade: <trigger>.` A marker naming no upgrade trigger is tagged `no-trigger` (those rot). End `N markers, M with no trigger.`

## Evidence and caveats

The upstream project reports, for a headless Claude Code agent editing a FastAPI + React repo over twelve feature tickets
(Haiku 4.5, n=4), about 54% less diff code, 20% lower cost and 27% less time than the same agent without the skill, with
safety checks unchanged. Treat that as the vendor's single benchmark, not a guarantee; the biggest wins were on tasks with a
real over-build trap (a date picker 404 lines down to 23 by using a native `<input>`). The upstream author also concedes the
earlier "80-94% less code" single-shot numbers were inflated by a prose-padded baseline.

## Pitfalls

- A short diff that skips reading the code is the failure mode this skill exists to prevent; the ladder follows the reading.
- "Lazy" is not a licence to drop validation, error handling or the one check; those are exempt.
- A repo-wide `delete:` without the whole-tree grep deletes things reached by string, reflection or tests.
- Marker comments without a trigger ("ponytail: simple version") are untracked debt; always name the ceiling and the upgrade condition.

## Verification

- Debt grep run live on sample files: matched `# ponytail:`, `// ponytail:` and `/* ponytail: */` markers, skipped `node_modules/`, and ignored a comment that merely mentioned the word mid-sentence.
- For code changes: the new diff is smaller than the obvious alternative, validation and error paths at boundaries are intact, and the one runnable check passes.
