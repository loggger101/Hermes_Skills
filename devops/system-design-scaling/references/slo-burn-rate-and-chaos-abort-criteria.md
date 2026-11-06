# SLO error-budget & chaos abort-criteria math (from alirezarezvani/claude-skills slo-architect + chaos-engineering; measured-consistent 2026-11-05)

Upstream verdict: **keep upstream, adopt the math and governance rules** - their three stdlib tools
(`slo_designer.py`, `error_budget_calculator.py`, `slo_review.py`) live in that catalog (`engineering/skills/`),
not vendored here. Every number below was recomputed on this box and matches; upstream source is Google SRE
Workbook ch.5 canon, MIT-licensed skill wrapper.

## Burn-rate arithmetic (dimensionless multipliers - the commonly botched part)

```
allowed_downtime(window) = (1 - target) x window_minutes      # 99.9% / 30d: 0.001 x 43200 = 43.2 min
burn_rate   = observed_bad_fraction / allowed_bad_fraction    # NOT an error-rate percentage
threshold(budget_fraction f, alert_window w) = f x SLO_window_hours / w
```

For a 99.9% / 30-day SLO (720 h window): fast page `0.02 x 720/1 = 14.4`; slow page `0.05 x 720/6 = 6.0`;
ticket `0.10 x 720/72 = 1.0`. A multiplier of 14.4 means bad-events at `14.4 x 0.001 = 1.44%` - the unit trap:
multipliers are relative to budget, never percentages directly. **Thresholds scale with the reporting window**:
the same policy on a 28-day SLO is `672 h`: 13.44 / 5.6 / ~0.933 (verified). Multi-window pairing = long + short
window at the same multiplier, page only when BOTH breach - single-window alerts are either noise (5-min) or
post-hoc (30-day), one of the four cardinal mistakes upstream enumerates with these others: target above what
the system sustains, CPU/memory as SLI (system green while users suffer), and no written budget-burn policy.

**Target selection from data:** `target = floor(p50(last 30d SLI) x 100) / 100` - never a target the service
has not demonstrably held; window 28 days (4 calendar weeks) recommended for weekly seasonality.

## SLO bug catalog (`slo_review.py` check list, reusable as review questions)

target >= 99.99% without massive-eng justification | target <= 99.0% signals wrong SLI | window < 7d
(statistical noise dominates) or > 90d (feedback too slow) | vague/missing SLI definition ("everything OK") |
no documented action when budget burns | CPU/memory as user-experience proxy. Also: keep SLAs out of the SLO
doc, and SLO strictly tighter than any contractual SLA (beat contract before customers notice).

## Chaos engineering: abort criteria are the fifth principle

Netflix's four (hypothesis around steady state; vary real-world failures; run in production - staging never
reproduces prod failure modes; automate to continuous - "one-off chaos is a press release") plus upstream's
fifth: **a chaos experiment with no abort criteria defined up front is an outage by another name.** Blast-radius
estimate before injecting: `exposed_users = traffic_share x user_population` over the planned duration (their
calculator consumes slo-architect's error-budget output on stdin - inter-tool contract worth copying: budget in,
abort thresholds out). Abort trigger wired to burn-rate breach of the protected SLO closes the loop; feature-flag
kill-switch is the abort mechanism (see `devops/feature-flag-lifecycle`).

## Same-catalog triage 2026-11-05 (row 73 remainder)

Mined here: slo-architect, chaos-engineering. Skipped with reason after full read or structure+tool-surface
review: observability-designer (three-pillars prose + alert-noise tooling we would not vendor; nothing beyond
its SLO scaffold which defers to slo-architect itself), runbook-generator (skeleton generator, generic sections),
secrets-vault-manager (standard HashiCorp/cloud patterns; our `security/secret-vault-pattern` holds the crypto
patterns already), env-secrets-manager (.env audit prose + scanner script we keep upstream), database-designer
(schema/index/migration generator prose over standard normalization doctrine). dependency-auditor skipped too,
worth noting for its honesty genre: it labels its ~16-CVE pattern set "a smoke layer, not a replacement for live
advisories" and pairs with `npm audit`/`pip-audit` - capability claims stated at their real ceiling.
