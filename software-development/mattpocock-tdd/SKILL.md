---
name: mattpocock-tdd
description: "TDD red-green-refactor at pre-agreed seams."
version: 1.1.0
author: Adapted from mattpocock/skills
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [tdd, red-green-refactor, testing, vertical-slices, seams]
    related_skills: [test-driven-development, systematic-debugging, mattpocock-diagnosing-bugs, mattpocock-code-review]

---

## When to Use

Use when the user wants to build features or fix bugs test-first, mentions \"red-green-refactor\", wants to write tests before implementation, or wants integration tests at the right seams.

## What This Skill Does

Implements **test-driven development** with the red → green → refactor loop. Every test is written at a pre-agreed **seam** — the public boundary of a module — so that refactoring internal implementation never breaks the test suite.

This skill is the "mattpocock" flavor; for the general-purpose TDD methodology, load `skill_view(name='test-driven-development')`.

## Seams: Where Tests Go

A **seam** is the public boundary you test at. Test only at pre-agreed seams.

### Types of Seams

| Seam Type | What It Tests | Example |
|-----------|--------------|---------|
| **Public API** | HTTP endpoints, CLI commands, library exports | `curl /api/v1/papers`, `myparser --input file.json` |
| **Function boundary** | Public functions, class methods | `parse_arxiv_response(xml)` |
| **Integration boundary** | Component to external system | Database writes, API calls |
| **CLI boundary** | Command-line interface | `python scripts/search_arxiv.py --id 2402.03300` |

### Choosing Seams

For each module:
1. Ask: what would change most often without affecting callers? That's your seam.
2. Ask: what external system does this module talk to? Mock/stub it.
3. Ask: what's the smallest test that validates real behavior?

```python
# Example: testing a data-source parser at its seam
# DON'T test internal helper functions
# DO test the public parse() function with real XML input
```

## The Loop: Red → Green → Refactor

### Red: Write a Failing Test
Write exactly one test that captures the next piece of behavior. Assert on the **symptom**, not the implementation:

```python
def test_parser_handles_missing_abstract():
    # Given: XML entry without <summary>
    xml = '<entry><title>Test</title></entry>'
    # When:
    result = parse_arxiv_entry(xml)
    # Then: parser doesn't crash, returns None for abstract
    assert result['abstract'] is None
```

**Pitfall**: Don't write a test that passes trivially — it must fail first.

### Green: Write the Minimum Code
Write just enough code to make the test pass. Don't over-engineer:

```python
def parse_arxiv_entry(xml):
    # First version: just handle the missing abstract case
    title = extract_tag(xml, 'title')
    abstract = extract_tag(xml, 'summary')  # returns None if missing
    return {'title': title, 'abstract': abstract}
```

**Pitfall**: Don't write extra features "while you're in there."

### Refactor: Improve Without Changing Behavior
Clean up the code. The test suite is your safety net:

```python
def parse_arxiv_entry(xml):
    # After refactor: still passes the same test
    title = _safe_extract(xml, 'title')
    abstract = _safe_extract(xml, 'summary')
    return Entry(title=title, abstract=abstract)
```

Run tests after refactoring to confirm green still passes.

## Vertical Slicing

**Don't** write all tests first (horizontal slicing). Instead, use **vertical slices**: one behavior, tested and implemented end to end.

1. Write a test for feature A
2. Implement feature A
3. Run the test — green
4. Write a test for feature B
5. Implement feature B
6. Run the tests — both green

This gives you working software at every step and catches integration issues early.

## Anti-patterns

| Anti-pattern | What Happens | How to Avoid |
|---|---|---|
| **Implementation-coupled** | Tests break when you refactor but behavior hasn't changed | Test through seams, not internals |
| **Tautological** | The assertion recomputes the expected value the same way the code does | Hardcode expected values, or use independent logic |
| **Horizontal slicing** | Write all tests first, then all implementation | Use vertical slices — test + implement per feature |
| **Over-mocking** | Every test mocks everything; you're testing mocks, not behavior | Mock only external systems; let internal code run |
| **Test interdependence** | Tests break when run in isolation | Each test sets up its own state |
| **Brittle assertions** | `assert result == {'a': 1, 'b': 2}` breaks if a key is added | Assert on the fields you care about |

## When to Skip Unit Tests

- **One-lin scripts** — test via integration or manual verification
- **Configuration files** — type-check or validate syntax instead
- **Glue code** — test the components it glues, not the glue itself
- **Trivial getters/setters** — if they can't have bugs, don't test them

## Tooling by Language

| Language | Framework | Run Command | Assertion Style |
|----------|-----------|-------------|-----------------|
| Python | pytest | `pytest tests/` | `assert result == expected` |
| JavaScript | Jest | `npx jest` | `expect(result).toBe(expected)` |
| Go | builtin | `go test ./...` | `if result != expected { t.Fatal() }` |
| Bash | bats | `bats tests/` | `[ "$result" = "expected" ]` |

## AspireCURES Context

For the research pipeline, use TDD when adding new data-source parsers, gating logic, or disease-page rendering. Each data source should have tests at the parser seam. Vertical slices work well for adding a new disease page feature end-to-end: write a test for the fetch → gate → render pipeline for one disease, implement it, then expand to the next.

For the cronjob preparer agent: write tests for the JSON report shape before implementing the gating logic. For the executor agent: test the disease-page validation checks before running them on production renders.
