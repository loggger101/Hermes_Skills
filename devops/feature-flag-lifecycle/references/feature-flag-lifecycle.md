---
description: "Feature flags as a lifecycle: flag types and lifespans, ring/linear/log/cohort rollout maths, kill-switch registry fields, stale-flag detection and the traps in alirezarezvani's three scripts"
source_repo: alirezarezvani/claude-skills (MIT) - engineering/feature-flags-architect
tested_version: "SKILL.md and the three stdlib scripts (flag_debt_scanner.py, kill_switch_audit.py, rollout_planner.py) run on Python 3.14.6 / Windows against a planted git repo; vendor/provider guidance is source-read only"
verified_date: "2026-10-05"
---

# Feature-flag lifecycle (progressive delivery)

Fits `system-design-scaling` where a design says "ship behind a flag", "canary", or "ramp to 100%". The idea worth
keeping from the source skill: a flag is a controlled lifecycle, `request -> design -> ship -> ramp -> cleanup -> archive`,
and the debt is the flags that never reach cleanup.

## Flag types decide the lifespan (source-read)

| Type | Purpose | Lifespan | Cleanup trigger |
|---|---|---|---|
| Release | hide unfinished work | days to weeks | 100% reached, then delete the branch |
| Experiment | A/B variants | weeks | winner picked |
| Operational | kill switches, circuit breakers | months to years | feature retired |
| Permission | entitlements per plan/account | permanent | plan removed |

Only Release and Experiment flags belong on a stale-flag watchlist. A permanent `if (FLAG_X)` repeated in 50 places is a
Permission flag in disguise: move it to runtime config. Target from the source skill: retire a Release flag within
60 days of reaching 100%.

## Rollout schedules (run: `rollout_planner.py`, population 100 000, start 2026-10-05)

| Strategy | Run result | Note |
|---|---|---|
| `ring`, 14 days, target 100 | 1, 5, 25, 50, 100 % on days 0, 3, 6, 9, 12 | Ends on **day 12, not 14**: interval is `duration // (stops-1)`, so a 14-day request finishes two days early |
| `ring`, target 30 | 1, 5, 25, 30 % on days 0, 4, 8, 12 | stops above the target are dropped, target appended |
| `linear`, 14 days, target 50 | 3.57 % per day, one phase per day | no canary stage; first phase exposes 3 570 of 100 000 users |
| `log`, 14 days, target 100 | **25.6 %** on day 0, then 40.6, 51.2 ... | "fast early" means a quarter of the population on the first day; only use after a ring canary |
| `cohort`, target 100 | internal 20 %, beta 40 %, free 60 %, paid 80 %, all 100 % | percentages are `target / 5` steps: "internal" is sized at **20 000 users** of the population, which no internal cohort is. Treat the cohort names as order only and size each cohort yourself |

Every phase in the generated table carries the same abort text (`error_rate > baseline + 1pp OR p99_latency > baseline * 1.2`) and
the same verify step. Replace both with metrics that fit the feature before using the table. Whatever strategy is chosen,
start at 1 % or an internal cohort, not at a tenth of the users.

## Registry fields that make a kill switch real

The auditor expects one `##`/`###` section per flag naming: owner, type, kill-switch trigger, dashboard. Add the flag entry
**before** the code, deploy at 0 %, prove the switch works in staging, then ramp. Keep the abort threshold in the entry, not
in someone's head.

## Detecting stale flags: what the upstream scripts get wrong (run)

A planted git repo (flags dated 2025-01 and 2026-10) and registries written four ways gave these results; the same
checks are summarised in `software-development/failure-signal-audit/references/regex-scanner-false-greens.md`.

| Script | Planted case | Result |
|---|---|---|
| `flag_debt_scanner.py` | flag first added by **editing** an existing file | `age_days=None`, never debt: `git log --diff-filter=A -S` only sees commits that add a *file* |
| | old flag used in 6 files | **not debt**: the rule is `uses <= --min-uses` (default 2), so the worst offender (the 50-places anti-pattern in its own docs) is exempt |
| | `--min-uses 10` | text header still prints `<=2 uses` (hard-coded) |
| | `uses` | counts files, not call sites (read from the source, not run separately) |
| `kill_switch_audit.py` | every field written `Owner: TBD`, `Kill switch: none`, `Dashboard: n/a` | **PASS** (field check is `word in section.lower()`) |
| | one prose sentence "No owner, no type, no kill switch and no dashboard" | **PASS** |
| | heading `` ## `name` ``, `- **name**`, or `## name:` | flag reported undocumented (heading regex is `^#{2,3}\s+[\w.\-:]+\s*$`, so the trailing colon becomes part of the name) |
| | one line missing (`dashboard`) | correctly WARNs, exit 1 |

Both scripts exit 1 on findings, so they work as gates only after these are fixed. Fixes that were checked:

- Date a flag with `git log --format=%cI -S<name> | tail -1` (no `--diff-filter`): gave 2025-01-02 for the edited-in flag that the
  upstream command left undated.
- Treat age and usage as separate signals: report `age > max-age` flags with `uses` shown, and list heavily used old flags first.
- Validate field **values** (non-empty, not `TBD|none|n/a|?`), not field names.
- Accept a backticked or bold heading, and strip a trailing `:`.

## Anti-patterns (source-read, still sound)

Permanent flag in many places; flag with no owner; no documented kill switch; an A/B test that runs for months;
flags for cosmetic changes that a deploy would ship. Build-versus-buy: with under about 50 flags and no targeting, a config
file or environment variable is enough; hosted providers and their pricing change often, so check them at decision time.
