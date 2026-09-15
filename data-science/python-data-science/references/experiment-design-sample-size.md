# Experiment Design & Sample Size (A/B test statistics)

Source: coreyhaines31/marketingskills `skills/ab-testing/` v2.0.0 + references (MIT; mined 2026-09-15). Domain framing is marketing, but the statistical discipline applies to any two-arm comparison — including CR-pipeline-style agent tournaments and pipeline A/B runs. Use this when designing an experiment BEFORE running it: the design decisions (metric tiers, sample size, duration) are where most experiments go wrong; the analysis afterward is mechanical by comparison.

## Design order (hypothesis first)

1. **Hypothesis** — "If we [change], then [primary metric] will improve by at least [MDE], because [mechanism]." No mechanism = no test worth running.
2. **Test one thing.** Multiple simultaneous changes make a positive result uninterpretable (you don't know which change caused it) and split traffic across too many variants.
3. **Metric tiers** — decide all three before launch:
   - **Primary metric**: the ONE number that decides the test (e.g., trial signup rate). Single, pre-registered.
   - **Secondary metrics**: supporting evidence (engagement depth, time on page) — informative, never decisive.
   - **Guardrail metrics**: things that must NOT regress (revenue per visitor, support tickets, churn). A "win" on the primary with a guardrail breach is not shippable.
4. **Sample size** (below), then **traffic allocation**, then implementation choice: client-side splitting (fast to ship, can leak/flash) vs server-side (cleaner assignment, more work).

## Sample size quick reference (α=0.05 two-sided, 80% power)

Inputs: baseline conversion rate + minimum detectable effect (MDE — the smallest lift worth detecting; set from business impact and what past tests have actually shown, not aspiration). Tables are sample **per variant** for a two-variant test:

| Baseline | Detect 5% relative lift | 10% | 20% | 50% | 100% (double) |
|---|---|---|---|---|---|
| 1% | 1,500,000 | 380,000 | 97,000 | 16,000 | 4,200 |
| 3% | 480,000 | 120,000 | 31,000 | 5,200 | 1,400 |
| 5% | 280,000 | 72,000 | 18,000 | 3,100 | 810 |
| 10% | 130,000 | 34,000 | 8,700 | 1,500 | 400 |
| 20% | 60,000 | 16,000 | 4,000 | 700 | 200 |

Reading: at a 3% baseline you need ~120k per variant to detect a *relative* 10% lift (3.0→3.3%). Low baselines + small expected effects = enormous samples — that's the number telling you "don't test this, or change something bigger."

**Duration:** `days = (sample_per_variant × n_variants) / (daily_traffic × %exposed)`. Worked: need 10k/variant at 5k visitors/day fully exposed → 4 days. But apply the floor and ceiling rules below on top of the raw number.

## Duration floors and ceilings (the part sample-size math misses)

**Minimum duration even with enough samples:**
- **≥1 full week** — captures day-of-week variation (weekday vs weekend behavior is a real confound).
- **2 business cycles for B2B** — decision patterns differ by phase.
- **Through paydays/period boundaries for e-commerce** — beginning/end of month effects.

A 4-day "significant" result that straddles only weekdays is measuring the weekday effect, not your change.

**Maximum duration: avoid >4–8 weeks.** Novelty effects wear off (early adopters drive initial behavior), external factors intervene seasonally, and opportunity cost compounds — a test running forever blocks the next one. If you can't reach sample size in 8 weeks at current traffic, the right move is usually to change something bigger or aggregate more events per user, not wait 6 months.

## Common design mistakes (each kills validity silently)

1. **Underpowered tests** — no realistic chance of detecting a real effect → you'll mostly conclude "no difference" and ship nothing ever. Fix: be honest about MDE; if the required sample is absurd, that's information about the change's likely size.
2. **"Overpowered"** (reaching significance before target sample) — this one is actually fine IF you pre-committed to a fixed horizon: honor it or you've reintroduced peeking bias. Don't stop early just because p<0.05 on day 3 of a planned 14-day test.
3. **Wrong baseline** — using site-wide average instead of the specific page/metric's rate (a pricing page at 8% is not the site's 2%). Sample size scales with the wrong number → under- or over-powered in unpredictable directions.
4. **Ignoring segments you plan to analyze** — if you'll slice results by device/geo/cohort, compute sample for your *smallest* planned segment, not total traffic. A "significant" overall result can be driven entirely by one segment while another regresses.
5. **Too many concurrent tests / variants** — each additional variant divides the already-tight traffic budget. Prioritize ruthlessly; run fewer, larger tests rather than a dozen underpowered ones.

## Sequential testing (peeking) — when and how

Checking results before reaching sample size inflates false-positive rate (each look is another chance to cross the threshold by noise). If you genuinely must peek (high-risk change where a bad variant should stop early):
- Use a method that **adjusts for multiple looks** (alpha-spending boundaries / always-valid p-values; Bayesian approaches with decision thresholds rather than point estimates — PostHog-style, Optimizely Stats Accelerator, VWO SmartStats).
- Tradeoffs: more flexibility to stop early, slightly larger required sample, more complex analysis.
- Never: run a fixed-horizon design and eyeball the p-value daily "just in case."

## Analysis discipline (after the test)

- Pre-register the decision rule at launch ("primary improves ≥X% with 95% confidence AND no guardrail regresses → ship") so post-hoc rationalization has less room.
- Report: sample sizes achieved per arm, primary metric delta + CI, secondary metrics, every guardrail, and segment breakdowns — including the boring negative ones. A results doc that only shows favorable slices is not a result, it's a highlight reel.
- Non-significant ≠ "no effect" when underpowered; state power honestly ("with n=… we could detect ≥X%").

## Mapping to this brain's workflows

- **CR-pipeline / GA experiments:** the same tiers apply — primary = win-rate or ELO delta, guardrails = no degenerate strategy collapse (diversity metrics), and "one full cycle" floors translate to whole tournament brackets rather than calendar weeks.
- **Cron-loop self-checks** (`cron-job-authoring/references/loop-engineering.md`): the sample-size gate IS the loop's self-check — a churn-watch on 40 accounts/week is measuring noise; the cadence-vs-signal table already encodes this, these tables give it numbers.
- **Website audits:** when an audit recommends "test X," attach the required sample from these tables so the recommendation includes its own feasibility verdict (a page with 500 visitors/month can't test a 10% relative lift on signup in any sane timeframe — say so).
