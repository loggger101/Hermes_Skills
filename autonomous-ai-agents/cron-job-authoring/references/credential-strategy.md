# Credential Strategy for Cron Jobs

Decision tree for what to do when a cron job hits a step that needs credentials it doesn't have.

## The three options (priority order)

### 1. Skip and record (preferred for verification steps)

The step is a check — link rot against an auth-gated endpoint, a live API call, a token-bearing request. The job can't do it without the credential.

**Action:** Skip the step. Mark it as unverified in the report with the reason "credential not available — manual verification needed." Continue with everything else.

**Example (skill audit):**
> CR5 cross-check (huggingface-trackio): Could not verify the HuggingFace CLI commands against current docs — no HF_TOKEN in environment. Marked unverified. Structure, trigger, and steps all PASS.

**Example (link rot):**
> Skill 'arxiv' references https://arxiv.org/help/search — could not fetch (no network credential available in this environment). Marked unverified. All other CR8 checks for this skill were testable locally and PASS.

### 2. Use what's available (scope to existing credentials)

The environment has SOME credentials but not all. Scope the work to what the available credentials allow.

**Action:** Do everything the available credentials permit. Note explicitly what's out of scope.

**Example:**
> Environment has a read-only GitHub token. I verified repo listing and PR metadata endpoints. Write-endpoint checks (create PR, add label) are out of scope — no write token available. Marked those CR8 checks as "credential not available — read-only token only."

### 3. Hard blocker → record and continue

The step is foundational — the job can't meaningfully proceed without it. But stopping the whole job is worse than recording the gap and doing non-dependent work.

**Action:** Record the blocker with the reason. Continue with any work that doesn't depend on it. Don't stop the job.

**Example:**
> Blocked: job requires a database connection string to audit migration skills. No DB_URL in environment. Recording as blocker. All non-DB skills in the audit are still evaluated and reported.

## What NOT to do

- **Don't search the web for how to obtain the credential.** That's the agent doing work the user didn't authorize, and it may lead to consent screens or token-generation flows the user hasn't approved.
- **Don't attempt an OAuth flow.** Even if the agent knows the OAuth provider, an interactive login requires a human.
- **Don't prompt the user.** The user isn't there.
- **Don't stop the whole job for one missing credential.** Record and continue unless literally nothing else is possible.
- **Don't silently skip without marking.** A skipped check that isn't flagged looks like the job completed fully. Always mark unverified items explicitly.

## How to mark unverified items in a report

Use a consistent phrase so the user can scan for them:

- "credential not available — manual verification needed"
- "credential not available — read-only token only, write-endpoint checks out of scope"
- "credential not available — no network access in this environment"

Avoid vague phrasing like "could not verify" without the reason — the user needs to know it's a credential gap, not a bug in the skill or the job.

## Relationship to guardrails

The credential strategy is the constructive half of the no-interaction guardrail. The guardrail says "don't prompt." The credential strategy says "when you can't prompt and you can't proceed, here's what to do instead." Both belong in the prompt.
