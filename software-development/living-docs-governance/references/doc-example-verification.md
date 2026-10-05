---
description: "Verify technical docs by executing their code examples: 5-phase fact-check, example-to-test conversion rules, and a runnable Node example checker (scripts/check_doc_examples.py) proven on planted defects"
source_repo: leonardomso/33-js-concepts (.claude/skills: fact-check, test-writer, write-concept) (MIT)
tested_version: skills read via GitHub API; scripts/check_doc_examples.py written for this repo and run with Node 22.23 on a good and a planted-defect document
verified_date: "2026-10-05"
---

# Executable documentation: fact-check by running the examples

The 33-js-concepts project keeps its teaching pages honest with two agent skills: **fact-check** (verify claims) and **test-writer** (turn every code example into an
automated test that cites the doc line). The method generalises to any technical doc whose examples claim an output.

## Five-phase fact check (from the project's `fact-check` skill)

1. **Code examples**: run every block and compare printed output with its `// result` comments; "wrong" examples (marked as such) must actually misbehave, "correct" ones must work. Watch the classic misstatements: `typeof null` is `"object"`; `push` returns the new length; promise microtasks run before timers; `[] == false` is `true` while `![]` is `false`; arrow functions have no own `this`.
2. **Reference alignment**: every API claim matches the authoritative reference (MDN/spec): signature, return type, deprecation status, compatibility tables. Links must return 200 and say what the text says.
3. **External resources**: links alive, not paywalled or retitled, and the resource supports the claim it is cited for.
4. **Claims**: separate universal behaviour from browser-, version- or runtime-specific behaviour; flag pre-modern patterns taught as current; state misconceptions as misconceptions.
5. **Coverage**: look for a test per major example; list examples with no test.

Protects against: wrong behaviour claims, outdated patterns, examples that do not produce the stated output, broken links, browser-specific behaviour presented as universal, inaccurate API descriptions.

## Example-to-test conversion (from `test-writer`)

| Example kind | Action |
|---|---|
| Has `console.log` with output comments or returns a value | write a test with `expect` |
| DOM / `window` / events | separate DOM test file under jsdom |
| Intentional error | `expect(() => ...).toThrow()` |
| ASCII diagram, pseudo-code, incomplete snippet | skip, and say why |
| Browser-only API | skip or mock |
| Timing | fake timers (`vi.useFakeTimers()`), test the logic not the clock |

Conventions worth copying: tests named `should ...` and matching the doc's heading structure; a comment citing the doc lines each test came from (`From {concept}.mdx lines XX-YY`);
tests mirrored under a directory tree that matches the docs' categories.

## A runnable checker: `scripts/check_doc_examples.py`

Stdlib Python, needs `node`. For every ` ```js ` / ` ```javascript ` block, it runs the code with `console.log` captured (values formatted with `util.inspect`) and compares, in order, with the trailing
`// expected` comments:

```bash
python scripts/check_doc_examples.py docs/*.md            # exit 0 = all examples match, 1 = mismatch or crash
python scripts/check_doc_examples.py --verbose page.md    # also list passing blocks
```

Rules: only `console.log(...) // expected` lines are checked; whitespace-insensitive; `'x'` equals `"x"`; a block whose first line is `// no-run` is skipped (browser-only/pseudo-code); a block whose first line is `// throws` may crash.
The output handler also fires on a crash, so a block that prints and then throws still reports what it printed.

**Proven on a planted-defect document** (the check must fail when the doc is wrong). Good document (`typeof null // "object"`, a `map` result, `0.1 + 0.2 === 0.3 // false`, a `// no-run` block, a `// throws` block): `2 block(s) checked, 0 failing`, exit 0.
Defective document: `typeof null // "null"` reported `comment says '"null"' but printed 'object'`; `[1,2,3].push(4) // [ 1, 2, 3, 4 ]` reported `printed '4'`; `[] == false // false` reported `printed 'true'`;
a block that referenced an undefined variable and one that dereferenced `undefined` were each reported as `block crashed`; `3 block(s) checked, 3 failing`, exit 1.

Limits: JavaScript only; it compares `console.log` output, not return values or DOM behaviour; async output ordering is checked only if the doc prints in a deterministic order. Extend with Vitest for anything richer.

## Use in this repo

Run it over docs that carry JS examples whenever they change (`living-docs-governance` treats docs as governed artefacts); for Python docs, the same idea is `python -m doctest` or the `scripts/*_verify.py` harness pattern used by several skills.
