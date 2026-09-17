---
name: application-threat-model
description: "STRIDE app threat modeling with per-control security tests."
version: 1.0.0
author: rlaope (https://github.com/rlaope/oh-my-hermes), ported by Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [threat-modeling, stride, trust-boundary, attack-scenarios, security-design-review, abuse-cases]
    category: security
    homepage: https://github.com/rlaope/oh-my-hermes
    related_skills: [mattpocock-security-review, security-audit, system-design-scaling]

---

# Application Threat Model (port)

Upstream source: rlaope/oh-my-hermes `agent-skills/omh-application-threat-model` @ main (2026-09-17), MIT.
Ported verbatim except frontmatter, the two sections below, and one sibling-skill reference replaced by an
inline note (the upstream's `security-safety-review` — agent-runtime threat mapping — has no counterpart in this brain).

## What This Skill Does

Models the security of an application or deployed system the user operates: registers what is worth
taking (assets with a data class and exactly one loss), finds where trust changes hands (boundaries,
each answered by four questions), derives attack scenarios per boundary using all six STRIDE prompts,
resolves every scenario to one decision from a closed vocabulary (mitigate / transfer / accept /
eliminate) with an owner, marks each control `deployed`/`planned`/`unverified` (default unverified —
an architecture diagram describing a control is not the control), and names per-control security tests
whose observable fails when the control is removed. Closes with residual risk: accepted scenarios,
unverified controls, and every scenario whose test does not exist yet.

## When to Use

"Build a threat model for X", "STRIDE analysis", "how would an attacker reach Y", security design or
architecture review of a system you operate. Do NOT use it for: finding defects in a diff or file (use
`mattpocock-security-review`), auditing your own codebase's vulnerabilities end-to-end (`security-audit`),
or the agent's own prompt/tool/credential surface (no counterpart skill here — that is out of scope; say so).
The subject is always the modeled system, never the reviewing agent.

## The method in one pass

1. **Assets** — an asset is something an attacker wants, not every table in the schema. Each row carries a data class and exactly one loss from four fixed words: disclosure, corruption, unavailability, fraud. If none fits, the row is context, not an asset.
2. **Trust boundaries** — any place the answer to "who is asserting this, and who checked?" changes. Ask all four per boundary (see [references/threat-model-method.md](references/threat-model-method.md)).
3. **Scenarios** — run all six STRIDE prompts against every boundary; one prompt → one scenario or a recorded reason the category does not reach that boundary. Every scenario carries entry point, path, precondition, impact. A scenario whose precondition nothing can satisfy is dropped with that sentence written down — never carried as a maybe.
4. **Control decisions** — one per scenario from {mitigate, transfer, accept, eliminate}, each with a named owner. A scenario with two decisions has not been decided.
5. **Per-control tests** — the test names the observable that fails when the control is removed; a test that passes with the control deleted tests nothing.

Never write exploit code, a payload, or a runnable attack script: the precondition and the detection
signal are the useful half; the weapon is not. If asked for exploit code, give the precondition and the
detection signal instead, then hand remediation to an executor.

## Completion checklist (quality bar)

- Every component, data store, and external dependency of the real system named before one threat — a model of a system nobody described is a checklist.
- Every asset carries a data class and one named loss; every boundary names what crosses it and what authenticates the crossing.
- All six STRIDE prompts run per boundary from [references/threat-model-method.md](references/threat-model-method.md); unreachable scenarios dropped with their reason, not carried as maybes.
- Every scenario resolves to mitigate/transfer/accept/eliminate with an owner; every mitigating control carries a security test and the observable that fails without it.
- Controls read deployed/planned/unverified — none inferred from architecture description. Residual risk listed; the model is explicitly not offered as a scan, penetration test, or compliance attestation (say which of those three the user still needs).

## Recovery notes (when inputs are missing)

- Architecture not described → ask for the component map and data flows before modeling; never substitute a generic checklist for the real system.
- A scenario has no boundary and no asset → drop it with the reason rather than carrying an unreachable threat.
- The request turns out to be about the agent's own prompts/tools/credentials → stop: that is not this workflow's subject (out of scope in this brain).

## Required inputs / expected outputs

Inputs: components + call graph + deployment; data flows and classes per store/queue/message; known trust boundaries (auth points, network edges, tenant separation, third parties); deployed controls with owners; scope exclusions and threat actors in scope.
Outputs: asset register; trust-boundary table; scenario list (entry point/path/precondition/impact); one decision + owner per scenario; per-control test shapes; residual-risk statement.
