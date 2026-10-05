# PR body shape: a visual summary, before/after evidence, merge danger

Source: [mattpocock/skills](https://github.com/mattpocock/skills) `skills/engineering/pr/SKILL.md` (MIT; promoted to a
model-invoked skill in 1.3.0, commit read 2026-10-05), itself credited there to the `show-me` skill by Dex Horthy (HumanLayer).
Read at source level; nothing was run. Use it whenever you write or rewrite a pull request body, alongside
`SKILL.md`'s PR workflow and `mattpocock-code-review` for the review side.

## The template

```markdown
## Summary

<diagram, diff-sketch, or tree>

## Evidence

- **Before:** <screenshot/output/failing test run>
  **After:** <screenshot/output/passing test run>

## Merge Danger

**Door:** <one-way or two-way>

<optional: description>

**Blast Radius:** <one-word description>

<optional: potential ramifications of merge>
```

Skip preambles, keep prose brief, and use the project's domain vocabulary from `GLOSSARY.md` (formerly `CONTEXT.md`).

## Summary: the smallest view that makes the point

Pick the visual that fits the change; use one, sometimes several, rarely all.

| Change is about | Show |
|---|---|
| logic or an algorithm | pseudocode (`on(save) / if content is unchanged / return cached result ...`) |
| runtime control flow | a call tree (`submitForm / createSession / persistPrompt / launchAgent`) |
| UI structure | a component tree with the state and module boundaries that matter, file paths in parentheses |
| file responsibility or a broad refactor | a shallow file tree with a one-line comment per directory |
| component interaction or data flow | a Mermaid `sequenceDiagram` |
| what changes in an existing shape | a `diff` block matched to the topic: a component tree with `+` lines, a file tree with `+`/`-` moves, a call tree with inserted and removed calls, or control flow with added guards |
| mostly-new code, or a target shape to copy | the whole block |

Place each visual next to the short text it supports. Keep only the calls, files, props, states and boundaries needed for the current
question.

## Evidence

Concrete proof it works, as a before and after. Ranking from the source: **screenshots are S-tier** when the change is visual and
the environment allows it; **execution-based evidence is A-tier**: test results or console output, showing the exact test that now
fails-then-passes, written as pseudocode.

## Merge Danger

- **Door:** a **two-way** door can be walked back (cheap to roll back, lower risk); a **one-way** door cannot (destructive actions,
  hard-to-reverse decisions, data migrations).
- **Blast Radius:** the scope of impact, with every possibility considered: layout shift, breakage for consumers, mobile
  responsiveness, and so on. One word in the template, ramifications below it when needed.

## Using it in this repo's flow

1. Generate the Summary visual from the real diff (`git diff --stat`, the tree you actually changed), not from memory.
2. Paste the failing and passing command output for Evidence; if no test exists, say so and link the change that adds one.
3. State the door and blast radius honestly. A migration, a deleted field or a published artefact is a one-way door.
4. End with the attribution lines the session asks for. A PR body is outward-facing: confirm before posting it.
