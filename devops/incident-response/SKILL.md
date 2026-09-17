---
name: incident-response
description: "Command an open incident: severity, roles, timeline."
version: 1.0.0
author: rlaope (https://github.com/rlaope/oh-my-hermes), ported by Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [incident-command, sev1, outage, reliability, postmortem-prep, on-call, operations]
    category: devops
    homepage: https://github.com/rlaope/oh-my-hermes
    related_skills: [cron-pipeline-watchdog, system-design-scaling, verification-culture]

---

# Live Incident Response (port)

Upstream source: rlaope/oh-my-hermes `agent-skills/omh-live-incident-response` @ main (2026-09-17), MIT.
Ported verbatim except frontmatter, the two sections below, and sibling-skill names that do not
exist in this brain (`reliability-review`, `support-operations`, `connector-operator`) — those are
noted inline as out-of-scope handoffs instead of dangling references.

## What This Skill Does

Commands an incident that is STILL OPEN: declares severity from observed blast radius (severity is
declared live state, not an adjective), names one commander plus operations/communications/scribe
roles, keeps an append-only typed timeline (observation / action / decision — corrections are new
entries, never edits), records mitigations as temporary or permanent with what removes them, and
verifies recovery against a named signal at its healthy value rather than inferring it from the
mitigation landing. The record this workflow writes is exactly the source document a later
postmortem reads: every timeline entry captures what was believed when, not what turned out right.

## When to Use

"Production is down / we have an outage / declare severity / who's the incident commander / verify
recovery." Do NOT use it for: a closed incident (that's postmortem + SLO/error-budget review work —
out of scope here, hand off), one customer's support case with no declared incident, or watching a
release rollout where nothing is broken yet. Pair with `cron-pipeline-watchdog` when the "incident"
is a stale cron dataset rather than live user-facing service degradation.

## Severity is declared state, not an adjective

Severity is a value somebody set at a time, from an observed fact. Record the level, the fact, the
person, and the timestamp; a change appends a new entry and never overwrites the old level.

| Level | What makes it this level | Consequence |
| --- | --- | --- |
| SEV1 | A core flow is unavailable or wrong for most users, or data is being lost or corrupted | page immediately, commander required, customer notice drafted before mitigation lands |
| SEV2 | A core flow is degraded, or one flow is unavailable for a bounded set of tenants or regions | page the owning team, commander required, customer notice prepared |
| SEV3 | A non-core flow is degraded, or a core flow has a working workaround | owning team handles in hours, commander optional, no customer notice unless asked |

Two rules the ladder cannot state for you. Severity is set from observed blast radius, never from how
alarming the alert text reads. And an unknown blast radius is declared at the higher level until
measured, then lowered by an appended entry that names the measurement.

## Roles

One person per role, and one role per person while the incident is small.

- **Commander** — owns decisions and the severity level. Does not debug. When the commander starts debugging, the incident has no commander.
- **Operations** — the only person changing production during the incident. Every change is announced to the commander before it is made and appended afterwards.
- **Communications** — owns the customer notice, the status-page text, and internal updates. Writes them; sending happens through whatever channel exists (a connector, a page tool, or a human) and is recorded as observed only when that channel returns a result.
- **Scribe** — owns the timeline. Appends what was observed, changed, and decided, with times.

A role nobody filled is recorded unfilled with the reason, never left blank. Below SEV3 the commander
may hold scribe; the commander may never hold operations.

## Timeline entries are append-only

Three types, no others:

| Type | What it records | Required fields |
| --- | --- | --- |
| `observation` | something seen: a metric, an error, a customer report | time, actor, source, the value or quote |
| `action` | something changed: a restart, a flag flip, a rollback, a scale-up | time, actor, what changed, where, whether it is temporary |
| `decision` | something chosen: a severity change, a mitigation approved, a role handed over | time, actor, the choice, the reason at the time |

A correction is a fourth entry of the matching type that names the entry id it corrects and says what
was wrong. Never edit, never delete, never reorder. The value of the timeline afterwards is that it
records what was believed when, and an edited entry destroys exactly that. Record the reason at the
time it was believed, not the reason that turned out to be right — a timeline rewritten with hindsight
teaches the review nothing.

## Mitigation is not a fix

A mitigation stops the damage; a fix removes the cause. Record every mitigation with four fields: what
changed, where, `temporary` or `permanent`, and what removes it. Mitigations that are almost always
temporary — feature flag off, traffic shifted away from a region, rate limit lowered, cache extended,
consumer paused, job disabled, rollback to an older build — almost always need the removal recorded.

An undeclared temporary mitigation becomes permanent because nobody wrote down that it was supposed to
come back. That follow-up is the one item this workflow hands to the postmortem even when the incident
is otherwise clean.

## Recovery verification

Recovery is an observation, never an inference. Before anything is called recovered, four things must
be on the record: (1) the signal, named before the mitigation was applied where possible; (2) the value
that counts as healthy, stated as a number with its unit and window; (3) the observed value, with its
time; (4) who observed it. If the signal is itself down — the dashboard, the alerting pipeline, the log
stream — the incident stays open and the record says which signal is unavailable. A recovery claim
resting on a mitigation being applied is the failure this step exists to prevent.

## Communication ledger

Every outbound message has two states and never both: `prepared` (text written, target named, nothing
sent) and `observed` (a channel returned a result, with what it returned and when). Every public
message states the next update time, and a missed update time is itself a timeline entry. What a
message may state is bounded by the timeline: no cause that has not been observed, no restoration that
has not been verified, no apology that commits to remediation nobody has decided.

## Handing over and closing

An incident that outlives one shift hands over explicitly: the incoming commander reads the timeline
back, states the current severity and the open mitigations, and the handover itself is a `decision`
entry naming both people. An implicit handover is how two people both believe the other is commanding.

Close when the recovery verification is on the record and every temporary mitigation is either removed
or carried as a named follow-up. Then hand the record to postmortem work: the error-budget consequence
and remediation tracking are review-phase work, and this timeline is their source.

## Completion checklist (quality bar)

- Severity declared from observed blast radius with the observation that set it; changes append, never replace.
- One commander named before anything else; operations/communications/scribe each name a person or read unfilled.
- Every timeline entry timestamped, attributed, and typed per [references/incident-command-method.md](references/incident-command-method.md).
- Each mitigation marked temporary/permanent with what removes it.
- Recovery verified against the named signal at its healthy value; unavailable signal = incident stays open and says so.
- Paging/status-page/customer sends read `prepared` until a channel result is observed — never assumed delivered.

## Safety rules

- Never rewrite or delete a timeline entry. A correction is a new entry naming the one it corrects, because the timeline is what the review reads afterwards.
- Do not claim a page was sent, a status page updated, or a customer notified; sends are observed only when the channel returns a result.
- Do not call the incident recovered because a mitigation landed; recovery needs the named signal at its healthy value with the observer recorded.
- Never leave a temporary mitigation unmarked — record what it changed and what removes it, or it becomes permanent by omission.
- Never print customer records, credentials, tokens, or connection strings pulled into the timeline as evidence.

## Recovery notes (when inputs are missing)

- Nobody named commander → ask for one before anything else; an incident without a commander produces opinions instead of decisions.
- No recovery signal stated → ask which signal and what value counts as healthy before calling anything recovered.
- Incident turns out to be closed → hand the postmortem off (out of scope here) and leave this record as the timeline it reads.
- A send channel fails or returns nothing → keep the entry `prepared` and name the unconfirmed channel instead of assuming delivery.
