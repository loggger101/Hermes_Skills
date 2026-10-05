# Automation a 66k-star contribution repo runs on itself (TheAlgorithms/Java)

Source: [TheAlgorithms/Java](https://github.com/TheAlgorithms/Java) (MIT, 66.4k stars, pushed 2026-10-04), read at source level
2026-10-05: `.github/workflows/*.yml`, `.github/workflows/scripts/check_structure.py`, `pom.xml`. **The structure check was run
live** (Python 3.14.6, Windows) against a synthetic tree with planted defects; the Java toolchain (JDK 21, Maven) is not installed
here, so the build, checkstyle, spotbugs, PMD and jacoco parts are source-read only. Useful as a template when a repo takes
many outside pull requests and a maintainer has no time to police them by hand.

## 1. Structure lint in 20 lines (run live)

`project_structure.yml` runs on every push and PR: `python3 .github/workflows/scripts/check_structure.py`. The script walks
`Path(".").rglob("*.java")` and fails (exit 1, one path per line) when a file's `parent.parents` does not contain
`src/main/java/com/thealgorithms/` or `src/test/java/com/thealgorithms/`.

| Planted case | Result |
|---|---|
| clean tree (main + test each in a `sorts/` subfolder) | exit 0 |
| `tools/Misplaced.java` | exit 1, prints `tools\Misplaced.java` |
| a file **directly** in `.../com/thealgorithms/Root.java` | exit 1: it uses `parent.parents`, so the package root itself does not count, only subdirectories do (a category folder is mandatory) |
| `src/main/java/com/other/O.java` | exit 1 |
| `.../sorts/deep/er/D.java` | exit 0 (any depth below a category) |
| `node_modules/x/Vendored.java` | **exit 1**: `rglob` has no exclusion list, so vendored or build directories fail the gate; add an ignore list before reusing it |

Path separators print with backslashes on Windows; the comparison itself works on both OSes. The same few lines adapt to "every
skill folder has a SKILL.md" or "every doc lives under docs/" in this repo's style.

## 2. Close stale PRs whose CI failed (source-read)

`close-failed-prs.yml`, daily at 03:00 UTC (`cron: '0 3 * * *'`) plus `workflow_dispatch`, `actions/github-script`, permissions
`issues: write`, `pull-requests: write`. Per open PR (oldest-updated first, 100 per page):

1. skip when `updated_at` is within 14 days;
2. list the PR's commits and keep **meaningful** ones: committed after the cutoff and **not** a merge of `main`/`master`
   (message starts `merge branch 'main'` or contains `merge remote-tracking branch 'main'`), so a bot merge does not keep a dead PR alive;
3. read check runs and workflow runs for the head SHA; `hasAnyFailure` needs a failed one, `allCompleted` needs every one
   completed/skipped (cancelled counts for workflow runs), and an absent check list does not block;
4. close **only if** there are no meaningful commits **and** a failure **and** everything finished: post an explanatory comment, then
   `pulls.update({state: 'closed'})`.

Design points worth copying: the comment says why and how to reopen; API errors on checks or runs are caught and logged rather
than aborting the sweep; a PR with no CI at all is never closed. Caveats (reading the code, not run): `checks.listForRef` is
called without pagination, so only the first page of check runs is seen on PRs with many checks; the 14-day cutoff and the
`failure`-only conclusion ignore `timed_out` and `cancelled` check runs.

## 3. Generated DIRECTORY.md via a pull request (source-read)

`update-directorymd.yml` on every push to `master`: `DenizAltunkapan/directory-tree-generator@v2` (`path: src`,
`extensions: .java`, `show-extensions: false`), commits `DIRECTORY.md` when it changed, then `peter-evans/create-pull-request@v8`
opens a PR from branch `update-directory` with a **`REPO_SCOPED_TOKEN`** secret rather than `GITHUB_TOKEN`. Reason (GitHub's rule,
not tested here): events created with the default token do not trigger other workflows, so a bot PR would sit without its CI.
The generated index goes through review like any change, so a bad generator run cannot land directly on `master`. Compare this
repo's own `gen-*-index.py` + `verify-all.py` drift gate, which fails the build instead of opening PRs.

## 4. The quality stack in the build (source-read; `pom.xml` on master)

Java `release 21`; JUnit via `junit-bom 6.1.3` with `junit-jupiter`, AssertJ, Mockito `5.24.0`, commons-lang3 `3.21.0`,
commons-collections4 `4.6.0`; plugins `maven-surefire 3.6.0`, `maven-compiler 3.16.0`, `jacoco 0.8.15` (coverage),
`maven-checkstyle 3.6.0` running Checkstyle `14.1.0` against `checkstyle.xml`, `spotbugs-maven-plugin 4.10.x` with
`spotbugs-exclude.xml`, and `maven-pmd-plugin` (default ruleset plus `pmd-custom_ruleset.xml`, with `pmd-exclude.properties` as the excluded-from-failure list). Workflows beside the build:
`clang-format-lint.yml` (formatting), `infer.yml` (Facebook Infer static analysis, `.inferconfig`), `codeql.yml`, `stale.yml`
(`actions/stale@v11.0.0`: stale after 30 days, closed 7 days later, issues and PRs labelled `dont-close` exempt, daily at 00:00 UTC),
and a devcontainer/Gitpod config for contributors. The stale bot is the slow path; section 2 is the fast path for PRs that are already red. One PR must pass formatting, three static analysers, CodeQL,
tests and structure before a human looks at it.

## Takeaways for a repo that accepts outside PRs

1. Put cheap deterministic gates (structure, format) first and make failures print the offending path.
2. Auto-close abandoned PRs only when failure, inactivity and "no real commits" all hold, and say so in the comment.
3. Let generated files arrive as PRs authored by a token that can trigger CI.
4. Give gates an exclusion list; the one script above fails on `node_modules`.
