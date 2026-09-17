# Repository-Grounded Threat Modeling (verified from tech-leads-club/agent-skills @ 0ab82f6)

Source: `(security)/security-threat-model` v1.0.0 (author github.com/openai/skills). Mined 2026-09-17 as the exhaustion sweep of this repo. Complements this skill's OWASP checklist + SAST flow: that one finds KNOWN vulnerability classes in code; threat modeling enumerates what an attacker CAN do given THIS system's boundaries, before or instead of a line-by-line review.

## The 8-step workflow (the load-bearing parts)

1. **Scope and extract the system model from the repo** — components, data stores, external integrations, entrypoints; explicitly SEPARATE runtime behavior from CI/build/dev tooling and tests/examples (modeling dev-only code as production attack surface is how threat models inflate); "do not claim components, flows, or controls without evidence" — every architectural claim anchored to a file.
2. **Derive boundaries, assets, entry points** — trust boundaries are CONCRETE EDGES between components with protocol/auth/encryption/validation/rate-limiting noted per edge; assets = data, credentials, models, config, compute, audit logs; entrypoints include the unglamorous ones: parsers/decoders, job triggers, admin tooling, **logging/error sinks** (log injection is an attack surface).
3. **Calibrate attacker capabilities — and state NON-capabilities.** Explicitly listing what the attacker CANNOT do prevents inflated severity ("unauthenticated but rate-limited" ≠ "unlimited"). This step is where most generic checklists fail: they assume worst-case capability by default.
4. **Enumerate threats as ABUSE PATHS, not vulnerability names** — each threat = a path from an entrypoint through boundaries to an asset (exfiltration / privilege escalation / integrity compromise / DoS), tied to the specific assets it impacts; "keep the number of threats small but high quality."
5. **Prioritize with explicit likelihood × impact reasoning**, adjusted for EXISTING controls, and state which assumptions most influence the ranking. Their illustrative tiers: High = pre-auth RCE, auth bypass, cross-tenant access, sensitive exfiltration, key/token theft, model/config integrity compromise, sandbox escape; Medium = targeted DoS of critical components, partial exposure, rate-limit bypass with measurable impact, **log/metrics poisoning that affects detection**; Low = low-sensitivity leaks.
6. **Validate assumptions WITH the user before finalizing** — 1–3 targeted questions (service owner/environment, scale/users, deployment model, authn/authz, internet exposure, data sensitivity, multi-tenancy); PAUSE and wait; if the user declines to answer, state which assumptions remain open AND how each influences priority. A threat model built on unvalidated context is a checklist with extra steps.
7. **Mitigations tied to concrete locations** — distinguish EXISTING mitigations (with evidence) from RECOMMENDED ones; each recommendation names component/boundary/entrypoint + control type, and prefers implementation hints ("enforce schema at gateway for upload payloads") over generic advice ("validate inputs"); recommendations resting on unresolved assumptions are marked conditional.
8. **Quality gate before writing the report**: every discovered entrypoint covered · every trust boundary represented in threats · runtime-vs-CI separation confirmed · user clarifications (or explicit non-responses) reflected · assumptions and open questions explicit. Output: `<repo-or-dir-name>-threat-model.md`.

## Reusable one-liners
- "Do not claim components, flows, or controls without evidence."
- Non-capabilities are content: listing what the attacker can't do is a severity control, not padding.
- Logging/error sinks are entrypoints (log injection / detection poisoning).
- A threat that isn't an abuse path through THIS system's boundaries belongs in a checklist, not this document.
