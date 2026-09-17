---
name: failure-signal-audit
description: "Find swallowed errors, bad fallbacks, gaps, false green."
version: 1.0.0
author: rlaope (https://github.com/rlaope/oh-my-hermes), ported by Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [silent-failure, swallowed-error, empty-catch, dangerous-fallback, false-green, error-propagation, debug-hygiene]
    category: software-development
    homepage: https://github.com/rlaope/oh-my-hermes
    related_skills: [verification-culture, systematic-debugging, mattpocock-security-review]

---

# Failure Signal Audit (port)

Upstream source: rlaope/oh-my-hermes `agent-skills/omh-failure-signal-audit` @ main (2026-09-17), MIT.
Ported verbatim except frontmatter and the two sections below; upstream's OMH-specific artifact ids are
kept as vocabulary but this brain has no machine consumers for them — treat them as named finding types, not files to emit.

## What This Skill Does

Audits code, frontend/browser behavior, agent traces, or runtime reports for failures that were
swallowed, downgraded, hidden by fallbacks, or reported green without enough evidence. Four separate
finding types, never blended: **silent failure** (empty catch / ignored exception / log-only handling),
**dangerous fallback** (default value or degraded mode that masks the error instead of surfacing it),
**propagation gap** (lost stack, ignored async rejection, missing context across a boundary), and
**false-green status** (a PASS/green claim with no observed check behind it). Each finding names its
location or evidence ref, severity, user/operator impact, and the smallest safe remediation route.

## When to Use

"Find swallowed errors", "why did this pass CI when X broke", "audit for dangerous fallbacks / false
green". Do NOT use it as a substitute for `systematic-debugging` (one live bug with a repro) or for an
incident that is open right now (`incident-response`). This workflow produces findings and remediation
handoffs — it does not itself patch, run CI, close incidents, or claim reliability.

## The audit discipline (quality bar)

- Name the user-facing objective, required context, next action, and stop condition before hunting. Separate prepared guidance from observed platform/runtime/file/delivery evidence at every step.
- Hold **masked-failure** and **intended-fallback** as competing hypotheses for each suspect site — with observed evidence for and against each — until one reading is discriminated. A catch block that swallows can be a deliberate degraded mode; the audit must say which, from evidence.
- Order probes cheapest-discriminating-first: read the handler and its callers → logs and traces → only then demand expensive reruns or instrumentation.
- When a check went green without an observed fix, bisect from the last run that surfaced the failure to the first that swallowed it before naming the masking change.
- Attribute a masked failure to a specific handler or fallback **only with revert-verify evidence** (the signal observed reappearing when it is removed), otherwise mark causation unproven.
- Route remediation only against a reproduced failing signal; a handoff without a reproduced failure first is a guess.

## Completion checklist

- Audit scope, source surfaces, and evidence types are named up front.
- Swallowed errors, dangerous fallbacks, propagation gaps, and false-green claims reported as separate finding types — each with location/evidence ref, severity, impact, smallest safe remediation route.
- Fallback risk matrix separates: safe fallback / user-visible degraded mode (intended) / masked failure / destructive fallback.
- No remediation, runtime repair, verification, CI, merge, or future-reliability claim is made without observed follow-up evidence.

## Safety rules

- This audit is not remediation, code modification, runtime repair, incident closure, verification, review sign-off, CI, merge-readiness, or proof that hidden failures no longer exist.
- Do not claim connector/gateway/runtime/file/memory/host-automation evidence from prepared guidance; report actual tool results or `not_observed` / `not_available`.

## Recovery notes (when inputs are missing)

- No code/trace/runtime evidence supplied → prepare the audit plan and request the smallest source surface to inspect.
- User wants live SLO/incident review of a running outage → that is incident command, not this workflow; hand off (`incident-response`).
- Rendered browser proof needed before PASS on frontend findings → capture it first (screenshot/DOM evidence), then re-judge against the observed state.
