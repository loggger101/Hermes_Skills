# CI Ratchets & Release Pipeline (verified from reconurge/flowsint @ 1820569)

Source: `.github/workflows/{lint,tests,release,images}.yml` + root `Makefile`. Flowsint's repo has a
large pre-existing type/lint backlog (~2200 mypy errors, ~300 eslint findings workspace-wide). Their
answer is the **ratchet pattern**: never gate on the whole backlog (CI would be red from day one and
get ignored), but gate only what each PR *semantically* changes — so new code is held to full strictness
and the backlog shrinks as files get touched.

## 1. Change-scoped typecheck with SEMANTIC-change detection (the standout)

Naive `git diff --name-only BASE...HEAD` has a hole: a repo-wide formatter adoption diffs *every* file,
so whichever PR runs it first would suddenly be gated on the entire backlog. Their Makefile target fixes
this — a file only counts as "changed" if re-running ruff on the **BASE_REF version** does not reproduce
today's content byte-for-byte:

```make
typecheck:
	@ruff_bin=$$(uv run which ruff); \
	changed=$$(git diff --name-only --diff-filter=ACMR $(BASE_REF)...HEAD -- '*.py'); \
	meaningful=""; \
	for f in $$changed; do \
		if git cat-file -e $(BASE_REF):$$f 2>/dev/null; then \
			old_reformatted=$$(git show $(BASE_REF):$$f | "$$ruff_bin" format --stdin-filename "$$f" - \
			                 | "$$ruff_bin" check --fix --stdin-filename "$$f" -); \
			if [ "$$old_reformatted" = "$$(cat "$$f")" ]; then continue; fi;   # pure reformat -> skip
		fi; \
		meaningful="$$meaningful $$f"; \
	done; \
	...run mypy per-package only on meaningful files...
```

Documented pitfalls from their comments (both real, both hit):
- Resolve the ruff binary **once** (`uv run which ruff`) and call it directly. Invoking `uv run ruff`
  per file (up to ~2x per changed file) was flaky — occasionally produced a spurious empty result that
  made a purely reformatted file look "meaningful".
- Frontend equivalent: eslint runs only on files touched vs base (`git diff --name-only ... | xargs yarn eslint`);
  `tsc --noEmit` still runs full-project because TS can't type-check one file in isolation — reported with
  `continue-on-error: true` so drift is *visible* without blocking, "flip to blocking once the backlog's paid down".

## 2. Tiered gate policy (their actual matrix)

| check | scope | blocking? | why |
|---|---|---|---|
| ruff format+check, prettier, eslint-errors | whole repo | YES | "100% clean today — any regression is new debt" |
| mypy / tsc full project | whole repo | NO (reported) | backlog too big; visibility first |
| eslint on changed files | per-PR diff | YES | ratchet: strict where it matters now |
| pytest (all 4 packages via `make test`) | PR + main | YES | behavior gates stay fully blocking |

Rule of thumb extracted: **format/lint = zero-tolerance repo-wide; typecheck = ratcheted per-PR; tests = always full.**

## 3. Release pipeline — the GH_PAT anti-loop trick (release.yml)

`workflow_dispatch` with `bump: choice[patch,minor,major,custom]`:
1. checkout **with a PAT** (`token: ${{ secrets.GH_PAT }}`) — not GITHUB_TOKEN. Why (their comment):
   pushes made with the default GitHub token do NOT trigger other workflows (GitHub anti-loop policy),
   so a plain checkout token here would *silently skip* the tag-triggered image build. A PAT push behaves
   like a human `git push --follow-tags`.
2. `yarn release -- --release-as <type>` — standard-version bumps ALL version files, rewrites CHANGELOG.md from conventional commits, commits + tags atomically (their custom updaters: `pyproject-updater.js` for every workspace pyproject.toml via regex on `^version = "..."$`, plus a standalone `sync-versions.js <X.Y.Z>` that keeps root + 4 uv-workspace members + package.json in lockstep — they're path deps of one shipped project, not independently published packages).
3. `git push origin main --follow-tags` -> tag triggers images.yml exactly like a manual release would.

Commitlint config: conventional types only (feat/fix/docs/style/refactor/perf/test/build/ci/chore/revert), kebab-case scopes — the changelog is machine-generated from these, so discipline here = free changelog.

## 4. Image build pipeline (images.yml) — tag-triggered, security-instrumented

- `on: push tags v*`; concurrency group per ref; both images dual-pushed to Docker Hub + GHCR
  (`docker/metadata-action` with semver major.minor + latest).
- Multi-arch `linux/amd64,linux/arm64` via QEMU+buildx; GHA layer cache (`cache-from/to: type=gha`).
- **Per image**: `provenance: true`, `sbom: true` on build-push-action (SLSA attestation + SBOM for free).
- Then Trivy scan of the *pushed* GHCR tag (`severity: CRITICAL,HIGH`) -> SARIF uploaded to GitHub Security via codeql-action upload-sarif, gated with `if: always() && steps.trivy.outcome == 'success'` (scan artifacts survive even if a later step fails).
- Final `security-summary` job writes a markdown table of per-image results into `$GITHUB_STEP_SUMMARY`.

## 5. Test-env note worth stealing

Their pytest CI passes dummy env values for secrets the core package reads at import time:
"flowsint_core hard-requires these at import (provided by .env locally). Dummy values — no service is reached during tests: connections (redis.from_url, create_engine) are lazy." Pattern = modules must be *importable* with placeholder config and only fail on actual use.
