# Loop Engineering (scheduled autonomous jobs)

Source: coreyhaines31/marketingskills `skills/marketing-loops/` v1.2.0 (MIT, mined 2026-09-15). That skill is marketing-specific; this reference distills the **harness-independent loop-engineering patterns** that apply to any scheduled autonomous job — including Hermes cron jobs. Complements SKILL.md's no-interaction guardrails: those keep a run from *stalling*; these keep a recurring job from being *a liability*.

## The nine-part anatomy of a loop

Every durable scheduled job should be spec-able in all nine parts. A loop missing its **self-check**, **state/idempotency**, or **stop/bail-out** "isn't a system, it's a way to do the wrong thing on a schedule."

| Part | What it defines |
|------|-----------------|
| **Check cadence** | How often the job *looks* (weekly / daily / on-trigger). Match it to signal speed. |
| **Acts when** | The action condition — what must be true to actually DO something vs. just check and skip. Most runs of a good loop are "checked, nothing to do." |
| **Purpose** | The ONE outcome this job exists to move. |
| **Skills/tools used** | Which capabilities each iteration orchestrates. |
| **Loop body** | The ordered steps run each iteration (usually: pull data → diff vs last run → identify crossings of the action condition → draft/stage response). |
| **Self-check** | Verification done *before* acting — is the signal real, or noise / seasonality / a tracking bug? Is the sample big enough to be significant? |
| **State / idempotency** | What it remembers between runs: last-run marker, dedupe key, cooldown window, "already handled" set. Non-negotiable for anything scheduled. |
| **Stop / bail-out** | When it skips, halts, escalates to a human, or disables itself — plus what it does on error. Every loop needs one, including heartbeats (their stop is "manual disable + error-halt," never "n/a"). |
| **Output** | Where results go: file, PR, staged draft, notification, report. |

The **check-cadence / acts-when split matters**: a job might *check* daily but only *act* when an entity crosses a threshold it hasn't been contacted about inside its cooldown window. Conflating the two produces jobs that either miss the window or spam.

## The cadence rule

Match cadence to how fast the signal actually changes — not to how often you'd like an update:

| Signal | Realistic cadence | Why |
|--------|-------------------|-----|
| Rankings, backlinks, domain authority | Weekly | Move slowly; daily checks are noise |
| Ad creative fatigue, CPA drift | Every 2–3 days | Platform feedback loops are days, not hours |
| Funnel / activation metrics | Weekly | Needs enough volume to be significant |
| Churn / at-risk signals | Daily or on-trigger | Early-intervention window is short |
| Content/copy decay | Monthly | Erosion is gradual |
| Competitor changes | Weekly | Infrequent but material when they happen |
| Mentions / social listening | Daily | Engagement windows close fast |

Over-frequency is the most common failure mode: it generates busywork, burns budget/tokens, and trains the human to ignore the output.

## The two-tier action model (guardrails)

Classify every action a scheduled job can take:

- **Tier 1 — autonomous-safe:** read data, analyze, diff, score, *draft*, *stage* work for review.
- **Tier 2 — gated** (human checkpoint by default): spend money, shift budget, send messages, publish anything public, delete/suppress records, change live account settings.

A Tier-2 action may run unattended only if the user has **explicitly authorized it AND** it is bounded by caps + an allowlist:
- **Hard caps:** a daily/weekly ceiling the job can never exceed; halt and alert when approached.
- **Per-run change limit:** cap how much can move in one run (e.g. ≤20%), so one bad read can't reallocate everything.
- **Allowlist:** only named targets are eligible for autonomous changes; everything else is staged.
- **Directional guardrail:** judge changes on the outcome metric (revenue/quality), not a proxy — never optimize a proxy into an outcome loss.

Compliance mapping: CAN-SPAM/CASL for outbound email/SMS (honor unsubscribes immediately, scrub suppression every send); GDPR/CCPA for anything touching personal data; FTC disclosure rules for testimonials/incentives; platform ToS + rate limits for scraping-based loops. **When a job can't confirm consent or ToS-compatibility, its stop condition is "don't act" — stage for a human.**

**PII handling:** never log raw PII in loop state or run logs — use internal IDs/hashes. Pull the minimum personal data needed; don't hoard it in state.

**Always-escalate list (never fully autonomous):** crisis/negative brand mentions and legally-sensitive issues; high-value or strategic accounts; anomalies in revenue or spend (flag immediately, don't self-correct); anything that deletes data or contacts a large audience at once.

**Kill switch:** every scheduled job needs a manual off switch — disable the schedule/cron, or a global flag the body checks. A loop you can't stop quickly is a liability. Document it where the loops are scheduled.

## State & idempotency patterns

Persist state in a file per job (the source uses `.agents/loops/<name>.json` + an append-only `<name>.log`; on Hermes, anywhere durable and outside git churn — `cron/`-adjacent or a dedicated dir). Never keep state only in memory; a job that forgets on restart repeats itself.

```json
{
  "job": "<name>",
  "last_run": "2026-09-15T09:00:00Z",
  "cursor": "2026-09-14T23:59:59Z",   // watermark — only process items newer than this
  "handled": ["id_1042"],              // dedupe keys already acted on
  "cooldowns": { "id_1042": "2026-09-29T00:00:00Z" },  // entity -> next-eligible timestamp
  "in_flight": ["item_x"],             // open items (running tests/interventions) — don't start conflicting ones
  "counters": { "id_1042_attempts": 2 } // attempt counts that drive stop conditions
}
```

The four patterns: **watermark** (process only past `cursor`; advance it at the end of a *successful* run — safe to re-run); **dedupe set** (check key against `handled` before acting, add after); **cooldown map** (per-entity suppression windows so nobody is re-contacted inside them); **in-flight guard** (no overlapping actions). Keep state small and prune expired entries.

### Run logging = the vanity-loop detector

Append one line per run whether or not it acted:
```
2026-09-15T09:00Z  checked=312  acted=2   note="2 newly at-risk, staged"
2026-09-16T09:00Z  checked=298  acted=0   note="no action"
```
It answers two questions: **Is it a vanity loop?** — every run `acted=0` for weeks and nobody misses it → delete it. Or does it act *every* run? — that's chasing noise; the self-check is broken. "A job that emails a dashboard nobody reads is worse than nothing."

## When NOT to loop

- **Strategy or creative direction is the real work.** Loops maintain and optimize; they don't set positioning or make judgment calls each run.
- **The action publishes or spends without review** — auto-*drafting* is fine, auto-*publishing*/auto-*shifting budget* needs a checkpoint unless explicitly authorized with caps + allowlist.
- **The signal is too sparse to be significant.** A weekly conversion-rate loop on 40 visitors/week measures noise (this is the self-check's job: sample-size gate).
- **It's a vanity loop** — nobody acts on the output → delete it.

## Orchestration & rollout (multiple loops)

Four layers; data flows down, learnings flow back up:

```
SENSING     (detect what changed; trust the numbers first) — tracking-QA + periodic full-board review
   ▼
DIAGNOSTIC  (per-signal watchers figure out what to do about it)
   ▼
ACTION      (staged drafts / nudges / moves — mostly human-checkpointed)
   ▼
LEARNING    (capture what worked → feeds back into SENSING & DIAGNOSTIC)
```

Connective tissue: the periodic full-board review is the **router** (reads top-line metrics, dispatches each notable mover to the loop that owns it); tracking-QA + anomaly detection are the **foundation** — if measurement is broken, every downstream loop acts on lies; a shared backlog/sink collects hypotheses so individual loops don't each run their own experiments.

**Duplicate ownership rule:** when two jobs could act on the same signal, one *owns* the action and the other only flags (an at-risk account belongs to the churn job, not the upsell job — never upsell an account that's churning).

Rollout order: foundation first (trust the data + see the board) → plug leaks / protect existing value → fix conversion of what you already get → grow acquisition → optimize monetization → compounding/advocacy. Rules: **one at a time** (prove it earns its keep before adding the next); cap the total to "loops whose output I can review"; re-audit quarterly (recalibrate thresholds, kill dead loops).

## Mapping onto Hermes cron jobs

| Loop concept | Hermes equivalent |
|---|---|
| Loop body | The cron prompt (phased instructions) — write it so most ticks end in a silent skip |
| Check cadence / acts-when | Cron schedule + the threshold block in `.hermes/cron/active/*.json` (thresholds ARE the "acts when" condition; see SKILL.md's threshold-key pitfall) |
| Self-check | A prompt phase that validates signal significance *before* any Tier-2 action — sample size, stale-data check ("if events look stale, report 'stale,' don't fabricate movement") |
| State / idempotency | Durable state file + append-only run log per job (watermark/dedupe/cooldown patterns above) |
| Stop / bail-out | Blocked/Flagged-for-review section in the output contract; error path = report, never self-correct anomalies |
| Two-tier model | The no-interaction guardrail block already forbids Tier-2 *interactive* actions; extend it to name which staged outputs are drafts vs. what would require explicit authorization + caps |
| Kill switch | `hermes cron` disable / gateway stop — document the job's off-switch in its config comment |
| Vanity-loop detector | The run log: after a few cycles, if every delivery is "nothing changed" and nobody reads it, or every tick acts, retire/fix it |

## Anti-patterns (from the source)

- Looping without a stop condition → runaway spend or infinite churn.
- Same cadence for everything → most runs happen too often and get ignored.
- No self-check → the job acts on noise, seasonality, or a tracking bug.
- No human checkpoint on spend/publish actions.
- Building ten loops at once → start with one, prove it earns its keep, then add the next.

## Banned vocabulary (user-facing output)

Avoid: "set it and forget it," "fully autonomous marketing/ops," "AI does everything," "10x on autopilot." Loops are disciplined systems with checkpoints — describe them honestly in reports to the user.
