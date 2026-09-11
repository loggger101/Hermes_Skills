# Defense in Depth (Make the Bug Structurally Impossible)

Use after you've found a root cause involving invalid data and added validation in ONE place — that single check can be bypassed by different code paths, refactoring, or mocks.

Source: adapted from obra/superpowers v6.3.0 (`skills/systematic-debugging/defense-in-depth.md`, MIT). Examples re-expressed for Python.

**Core principle:** Validate at EVERY layer data passes through. Make the bug structurally impossible.

```
Single validation:  "We fixed the bug"
Multiple layers:    "We made the bug impossible"
```

## The Four Layers

1. **Entry Point Validation** — reject obviously invalid input at the API boundary (empty/whitespace, existence, type). Throw a specific error per case so failures are diagnosable.
2. **Business Logic Validation** — ensure data makes sense for THIS operation (`initialize_workspace(project_dir)` raises if project_dir is empty; a workspace can't exist without one).
3. **Environment Guards** — prevent dangerous operations in specific contexts: under `pytest` (or any test mode), refuse to touch the real filesystem outside temp dirs, refuse network writes, etc. Compare resolved absolute paths against an allowed prefix before acting.
4. **Debug Instrumentation** — capture context for forensics at each layer boundary (`logger.debug("about to git init", directory=..., cwd=os.getcwd())`) so that when a future bug slips past layers 1-3, the logs show where it entered.

## Applying the Pattern (4 steps)

1. **Trace the data flow** — where does the bad value originate? Where is it used?
2. **Map all checkpoints** — every point the data passes through on its way to the dangerous operation.
3. **Add validation at each layer** — entry, business logic, environment guard, instrumentation.
4. **Test each layer independently** — try to bypass layer 1 and verify layer 2 catches it; disable one layer at a time in tests.

## Why Multiple Layers (the evidence)

From the session that produced this technique: all four layers were necessary during testing — different code paths bypassed entry validation, mocks bypassed business-logic checks, platform edge cases needed environment guards, and debug logging identified structural misuse when other layers had gaps. **Don't stop at one validation point.** A single check is a fix; layered checks are an invariant.
