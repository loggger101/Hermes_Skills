---
description: "Reviewing a large diff without cutting corners: deterministic file list, rule grouping, per-file checklist, coverage accounting, position verification, noise filtering"
source_repo: alibaba/open-code-review (Apache-2.0)
tested_version: README, skills/open-code-review*/SKILL.md and .opencodereview/rule.json read via GitHub API @ main; `ocr` CLI not installed or run
verified_date: "2026-10-05"
---

# Large-changeset review protocol

General-purpose agents reviewing a big diff fail in three predictable ways. Open Code Review (OCR,
Alibaba's production reviewer) names them and fixes each with a hard, non-LLM step. The same steps
work by hand with plain `git`, no `ocr` needed.

| Failure | Symptom | Fix |
|---|---|---|
| Incomplete coverage | agent reviews the first files, quietly skips the rest | build the file list mechanically, then account for every entry |
| Position drift | comment cites line 140, the code is on line 212 | verify each line range against the diff before reporting |
| Unstable quality | verdicts change with small prompt edits | match review rules to files by path, not by memory |

## 1. Build the file list with git, not by eye

```bash
git diff --name-status <merge_base>..<head>        # range
git show --name-status --format= <commit>          # one commit
git status --porcelain                             # workspace (staged, unstaged, untracked)
```

Range mode: diff against the **merge base** (`git merge-base main feature`), not the tip of main,
or unrelated upstream changes appear as yours. Untracked files have no diff; read them whole.

Exclude by rule, and record why: lockfiles, generated code, vendored dirs, minified bundles, binaries,
snapshots. An exclusion with no stated reason is a skipped file.

**Checklist identity is `(path, status)`, not `path`.** A workspace can report one path twice
(a staged deletion followed by an untracked recreation); keying on path alone loses one of them.

## 2. Bundle related files, group by rule

- Review files that must agree as one unit: paired locale files (`messages_en.properties` + `messages_zh.properties`), a schema and its migration, an interface and its implementations, a source file and its test.
- On a very large change, give each bundle to its own sub-agent with isolated context (divide and conquer). Context isolation, not a bigger prompt, is what stays stable at 100+ files.
- Resolve the rules that apply to each file by path glob first, then hand the agent only those rules. Files that share a rule share one rule block; repeating the same checklist per file wastes the attention you are trying to focus.

A per-path rule is a plain-language checklist attached to a path. OCR keeps them in
`.opencodereview/rule.json` (`{"path": ..., "rule": ..., "merge_system_rule": true}`); the model
example is a rule on a provider-registry file requiring: field order, inline literals not one-use
constants, doc tables updated in every locale in the same PR, and a named regression test per new
entry. The pattern to copy is **rules that name the sibling files and tests that must change together**,
since "forgot the docs / forgot the test" is the review finding a diff cannot show by itself.

## 3. Review each file, then close the checklist

For every `(path, status)` entry: get its diff, read its rule group, pull extra context only when the
diff is not enough (full file, callers, tests), then mark it `reviewed` or `skipped` with a concrete
reason. Do not stop at the first high-severity finding. For large changes, work in bounded batches
grouped by shared rules and diff size.

## 4. Coverage accounting (required in the report)

Before reporting, reconcile the checklist against the preview list. State:

```
total_files: 38   reviewed_files: 31   skipped_files: 7   coverage_rate: 81.6%
skipped: package-lock.json (lockfile), dist/app.min.js (generated), ... one reason each
```

A review that cannot print this table has not shown it covered the change. If coverage is under 100%
for a reason other than a declared exclusion, say so at the top of the report, not in a footnote.

## 5. Position verification

Report `path`, `start_line`, `end_line` in the **new** file. Before keeping a comment, confirm the
cited lines contain the code the comment is about (read them, or `git blame -L`). If it cannot be
located, report it with line range unknown rather than a guessed number; a mispositioned comment is
worse than an unplaced one because the author goes hunting in the wrong place.

Comment fields worth carrying: `path`, `content`, `start_line`, `end_line`,
`category` (bug, security, performance, maintainability, test, style, documentation, other),
`severity` (critical, high, medium, low). Optional: a suggested replacement and the original snippet.

## 6. Filter and classify

- Critical/High (bugs, security, data loss): always report.
- Medium (performance, error-handling gaps, maintainability): report with context.
- Low (style nits): report only when clearly valuable; discard likely false positives silently.
- Give the reviewer the **business context** (what the change is for, from the PR body or commit messages). OCR's CLI takes it as `--background`; by hand, put one paragraph at the top of the prompt. Review quality rises because the agent can tell intended behavior from a bug.

## 7. Fixing

"Review" is not "review and fix". Without an explicit fix request, ask before editing. When fixing:
apply high/critical fixes that are safe and well-defined, describe fixes that need a human, skip low
items unless trivial, and verify with the user before committing.

## Using the real CLI (optional)

`npm install -g @alibaba-group/open-code-review` gives `ocr`. Useful commands, taken from its docs
(not run here):

```bash
ocr review --from main --to feature --format json --output result.json   # range; --output avoids truncated stdout
ocr review --preview                                                      # which files, no LLM call
ocr scan --path internal/agent                                            # whole-file review, no diff
ocr delegate preview --format json && ocr delegate rule <paths...>        # LLM-free: you do the review, OCR does file selection + rules
```

Its published benchmark claim (AACR-Bench: 200 PRs, 10 languages, 1,505 annotated issues) is that the
hybrid design beats a general agent on precision and F1 with about 1/9 of the tokens, at lower recall.
That is the vendor's number; treat it as direction, not proof.
