# Evidence-First PR Judge Protocol (verified from tech-leads-club/agent-skills @ 0ab82f6)

Source: `packages/skills-catalog/skills/(quality)/the-judge` v1.4.0 + `references/review-standards.md`,
`scripts/{scan_bypasses,review_gate,post_review}.py`. License CC-BY-4.0; attribution: Tech Leads Club / Felipe Rodrigues.
Mined 2026-09-16. A senior-engineer PR review with a high conviction bar: **few comments, every one backed by evidence,
posted as ONE consolidated GitHub review.** "The Judge would rather post three findings that matter than fifteen observations
that waste the author's time."

## The eight non-negotiables (override everything else)

1. **Evidence or silence.** Internal claim ⇒ verified `file:line` citation confirmed by reading the file. External claim
   (library/API/framework behavior, version, deprecation, vulnerability, best practice) ⇒ a URL from an official source
   FETCHED DURING THIS REVIEW. "Training data is a rumor; the changelog is a source." A finding without evidence is not posted. Period.
2. **Never assert external behavior from memory** — search current official docs/changelogs/advisories first; inconclusive ⇒ downgrade to a question or kill it.
3. **Noise budget**: max 5 nit comments inline; overflow becomes a count in the summary. Prefer few high-conviction comments when structural issues exist.
4. **Never comment on what the repo's own tooling catches** — run linters/typecheck/focused tests FIRST (Step 1); anything they flag is out of review scope. If the repo has no such tooling, note it and move on; do not install anything.
5. **Every comment passes a deterministic noise gate before posting** (`review_gate.py` exit 0) — no manual overrides. The gate bans AI-slop phrasing ("obviously", "simply", "delve", "seamless", "leverage", "tapestry"…), banned openers ("let me…", "first,…" — state the problem instead), em/en-dashes and exclamation marks in review text, `not just X but Y` constructions, per-severity length caps (blocker/should-fix ≤900 chars & 10 lines; nit ≤400), and requires internal findings to carry a `file:line`.
6. Language is the user's choice; English default. Verdict tokens/code identifiers stay verbatim in any language.
7. **Spend tokens where judgment lives**: read only the diff, touched files, and direct callers/callees when tracing — never ingest the whole repo. "Detection a regex can do runs in `scan_bypasses.py`, not in prose." A finding that is deterministic by nature goes into the lint-rule flywheel so the next review costs less than this one (deterministic checks graduate out of LLM judgment).
8. **The first review IS the whole review**: everything visible in round 1 is raised in round 1, batched; holding a finding for later is forbidden ("trickled comments are how reviews become infinite ping-pong"). Re-reviews verify resolution via a findings ledger (ID table) — they do not open new fronts.

## Severity → verdict mapping

| Severity | Definition | Effect |
|---|---|---|
| 🔴 blocker | changes whether the PR should merge: data loss, exploitable security, incorrect money, broken auth, irreversible migration, PII in logs | REQUEST_CHANGES |
| 🟠 should-fix | real defect, not a merge risk | COMMENT |
| 🟡 nit | minor; capped at 5 inline | none (overflow counted) |
| 🟣 pre-existing | bug the PR did NOT introduce — summary only, never inline | none |

Any 🔴 ⇒ REQUEST_CHANGES; zero 🔴 and zero 🟠 ⇒ APPROVE; else COMMENT. **Own-PR fallback**: GitHub returns 422 on
APPROVE/REQUEST_CHANGES of your own PR — detect author==authenticated user, post as COMMENT with a footer stating the intended verdict. "Do not fight this; it is API behavior."

## Workflow (condensed)

**Step 0 context + classification.** `gh pr view/diff`; classify every changed file **core vs mechanical**
(generated code, lockfiles, snapshots, vendored deps — skipped and listed). Detect MOVED CODE: 3+ consecutive lines deleted in one place
and added identically elsewhere is a move, not new code — don't re-review it as new. Determine the round from your own previous reviews on this PR; >~400 changed core lines ⇒ run review passes as parallel subagents when available (never make that a requirement).

**Step 1 deterministic ladder.** Detect and run the repo's OWN checks (lint/typecheck/focused tests — look at package.json scripts, Makefile, pyproject.toml, CI config); also ingest existing security-scanner output if wired in. Record results; exclude their findings from review scope. Then `gh pr diff | python3 scan_bypasses.py` — a stdlib-only regex scanner over ADDED lines (always exits 0: "a detector cannot block the review") emitting `path:line category content` for eight categories: suppression directives (eslint-disable, @ts-ignore/nocheck, noqa, type: ignore, pylint/rubocop disable, @SuppressWarnings, nolint, biome-ignore, pragma warning), test-dodges (.only/.skip/xit/t.Skip/@pytest.mark.skip), hook-bypass (--no-verify), TLS bypasses (rejectUnauthorized:false / verify=False / InsecureSkipVerify / NODE_TLS_REJECT_UNAUTHORIZED), type bypasses (`as any`, `as unknown as`), error-swallowing (`except: pass`, empty catch blocks), unsafe HTML (dangerouslySetInnerHTML, bypassSecurityTrust*), and sleep-as-synchronization (time.sleep/Thread.sleep). **Hits are candidates for judgment, never findings**: a suppression carrying justification + issue link is acceptable; a naked one isn't.

**Step 2 research before claims.** For every external claim in the diff's context: fetch current official docs now. Inconclusive ⇒ question or kill.

**Steps 3+ review passes** (correctness, security, structural quality, AI slop) → consolidated single review with TL;DR verdict token up top, findings ledger table for future rounds, and mechanical-file list.

## Structural-quality rules from their review-standards.md ("code judo" lens)

1. **Code judo first**: is there a move that makes this dramatically simpler — fewer concepts/branches/layers? Does the change improve or worsen local architecture; did a cohesive module become more coupled/stateful/harder to scan; is logic in the right file and layer; do repeated conditionals signal a missing model/helper.
2. **File size**: pushing a file from <1000 lines to >1000 is a PRESUMPTIVE BLOCKER on quality grounds — extract helpers/modules first; waive only with a compelling structural reason and the file still clearly organized.
3. **Spaghetti growth**: new ad-hoc conditionals / scattered special cases / one-off branches inserted into unrelated flows are DESIGN problems, not style nits — push behind a dedicated abstraction/state machine/policy object instead of tangling an existing path.
4. **Boring over magic**: flag generic mechanisms hiding simple data-shape assumptions, thin wrappers, identity abstractions, pass-through helpers adding indirection without clarity; brittle or magical behavior is a quality problem even when it works.
5. **Types & boundaries**: question unnecessary optionality/`unknown`/`any` and cast-heavy code where a clearer boundary could exist; "a silent fallback papering over an unclear invariant is a signal the boundary should be explicit."
6. **Canonical layer & reuse**: feature logic leaking into shared paths, implementation details leaking through APIs, bespoke helpers duplicating an existing canonical utility all normalize architectural drift — push code to the module that already owns the concept.
7. **Orchestration & atomicity**: independent work serialized for no reason and related updates that can leave state half-applied are design smells when the cleaner structure is obvious; don't micro-optimize, do flag avoidable orchestration complexity.

## Ported script in this skill

`scripts/scan_bypasses.py` — verbatim port of their scanner (stdlib-only, stdin diff → `path:line category content`,
always exit 0). Run it on any PR/branch diff before LLM review to zero-token-detect bypass markers; treat hits as candidates.
