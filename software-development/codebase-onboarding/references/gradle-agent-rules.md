---
description: "Gradle 9.8 repo's own instructions for coding agents: wrapper only, never full build or clean, target subprojects, -q, language levels, Spock test rules, public-API annotations; source-read"
source_repo: gradle/gradle (Apache-2.0), AGENTS.md and .agents/*.md on main, 2026-10-05; latest release v9.8.0 (2026-09-24)
tested_version: "SOURCE-READ ONLY: no Java or Gradle is installed on this machine and no wrapper distribution was downloaded, so none of the commands below were run"
verified_date: "2026-10-05"
---

# Working in the Gradle repository as an agent

Gradle's `AGENTS.md` is 12 lines pointing at human docs (CONTRIBUTING, ErrorMessages, Javadoc style, Nullability, Testing)
and a `.agents/` folder with five topical files plus a Claude-format skill `/gradle-code-review` under `.claude/skills/`
(`add-gradle-project` is the other one). The rules below are from those files. Policy on AI contributions is separate:
see `github/github-pr-workflow/references/ai-policies-of-starred-repos.md` (no AI co-author trailers; disclose in the PR).

## Building

- Use `./gradlew` (the wrapper). **Never a system `gradle`.**
- **Never run `./gradlew build`** on the whole repo and **never a `clean` task**: the repo is huge, and the build system is
  trusted to apply changes ("if you can't reason about the results of a build, the problem is elsewhere").
- Always target specific subprojects, and pass **`-q`** to cut output noise.
- Useful tasks: `./gradlew sanityCheck` (before submitting), `compileAll` (production + tests), `:build-logic:check`,
  `:docs:docs`, `install` (needs `gradle_installPath` on the CLI or in `~/.gradle/gradle.properties`), `binDist` (zip under
  `packaging/distributions-full/build/distributions/`).
- The version being built is in `version.txt`.

### Language levels

Production code targets a JVM by the module's `gradleModule.targetRuntimes` flags: `usedInClient` -> Java 8,
`usedInWorkers` -> Java 8, `usedInDaemon` -> Java 17; when several are set the **minimum wins**. Constants live in
`platforms/core-runtime/build-process-services/.../SupportedJavaVersions.java`. Test sources always compile to Java 17.

## Testing

- Framework: Spock (Groovy). Unit tests: `./gradlew :<subproject>:test` (for example `:launcher:test`). Integration tests run a
  real Gradle build: `:<subproject>:forkingIntegTest` and `:<subproject>:configCacheIntegTest`; **a new test must also pass
  with the configuration cache on**. Another Java: `-PtestJavaVersion=21`.
- Unless the change is wide, narrow runs with `--tests`.
- Prefer integration tests that check external state (produced files); use unit tests for many-input isolated logic.
- Look at similar existing tests first; keep tests simple (repetition is fine; use Spock data tables); helpers are under
  `testing/internal-integ-testing/src/main/groovy/org/gradle/`.
- **Do not assert inside the build scripts under test**: such assertions can be silently skipped and fail with poor
  messages. Print to stdout and assert in the test, or test via build operations.
- Link a bug test to its issue with `@spock.lang.Issue`.

## API changes

- Nullability: JSpecify `@Nullable` and `@NullMarked` only (new packages are `@NullMarked`); never `javax.annotation`.
- A type is public API iff its fully-qualified name matches `PublicApi.includes` / `PublicKotlinDslApi.includes` and not the
  excludes (`build-logic-commons/basics/.../PublicApi.kt`); everything else is internal and needs no compatibility care.
- **New public API:** mark with both `@Incubating` and `@since <x.y.z>` in the **three-component** form from `version.txt`
  (`@since 9.6.0`, not `9.6`). Do not add an `accepted-public-api-changes.json` entry. If `sanityCheck` flags a new member,
  fix the annotation, never the JSON.
- **Changing or removing public API:** run `sanityCheck`, add an entry to `accepted-public-api-changes.json` only if the change
  is approved, sort with `./gradlew :architecture-test:sortAcceptedApiChanges`, re-run `sanityCheck`.

## Tooling and review

- Run git commands directly, never `git -C <path>`; prefer `git grep`.
- Commit message: blank line after the subject, subject at most 50 characters, capitalised, no final period, imperative mood,
  body wrapped at 72 characters and explaining what and why.
- With IntelliJ connected, use the IDE diagnostics tool to check compilation instead of Gradle compile tasks; keep using
  Glob/Grep for search; refer to files by relative path.
- Reviews: follow `contributing/CodeReview.md` (correctness, API contracts, edge cases, security; ignore style, formatting,
  naming). Report findings only, each as `path:Lstart-Lend` plus a short description and a severity
  (`critical`/`major`/`minor`/`suggestion`), no summary or verdict; if nothing is wrong, say so in one line. Scope is every
  commit since the fork point plus uncommitted and untracked changes.

## Not verified

Everything above is from the repo's text. Not run: any Gradle command, the wrapper download, JDK selection on Windows, the
`gradle-code-review` skill, or the sanity checks.
