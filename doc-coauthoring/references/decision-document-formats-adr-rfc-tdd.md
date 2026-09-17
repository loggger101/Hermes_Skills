# Decision Document Formats: ADR vs RFC vs TDD (verified from tech-leads-club/agent-skills @ 0ab82f6)

Source: `(creation)/create-adr` v1, `create-rfc`, `create-technical-design-doc`. License CC-BY-4.0; attribution: Tech Leads Club / Felipe Rodrigues. Mined 2026-09-17 as the exhaustion sweep of this repo. Companion to `note-taking/living-docs-governance` (which owns WHERE these live and who maintains them) — this ref owns WHAT each format is for and how to choose among them.

## The routing rule (the part that prevents doc-type confusion)

| | ADR | RFC | TDD |
|---|-----|-----|-----|
| Purpose | **Record** a decision already made | **Propose + decide** — gather stakeholder alignment BEFORE committing | **Design + plan implementation** after direction is decided |
| Audience | Team/future readers (why did we do this?) | Broad stakeholders, leadership | Engineering team |
| Focus | What was chosen and why, given the context | Should we do X? Which option? | How do we build X? |
| Timing | After the decision | Before committing to a direction | After direction is decided |

Use RFC when **the decision itself** needs alignment. Use TDD when the decision is made and you need the implementation approach. Write the ADR once the RFC/TDD path has settled — an ADR for a still-open question is fiction, and an RFC after commitment is approval theatre (see `dispatching-parallel-agents/references/discovery-interview-and-critique-protocols.md` on that failure mode).

## MADR as the default ADR shape [VERIFIED]

Their default template is MADR (Markdown Any Decision Records) with these mandatory sections, in order:
1. **Context and Problem Statement** — what situation forces a decision; the problem framed without presupposing an answer.
2. **Decision Drivers** — the constraints/requirements that bound acceptable outcomes (separate from preferences).
3. **Considered Options** — every option seriously weighed, each with its own pros/cons subsection (✅ marker on the chosen one).
4. **Decision Outcome** — choice + rationale tied to drivers; then split consequences: Positive / Negative (negative consequences are mandatory content, not optional honesty).

Numbering discipline: ADR numbers are assigned from a sequential index in `docs/adr/` and never reused or renumbered — superseded records stay with their number plus a "Superseded by #N" header line. Language adaptation rule they enforce: generate the document in the SAME language as the user's request, keeping technical terms (API, rollback, stakeholder) and product names untranslated — relevant for any non-English team consuming these docs.

## TDD section budget [VERIFIED]

Their 51KB create-technical-design-doc skill is notable mainly for its MANDATORY-vs-OPTIONAL section split: mandatory = overview/problem statement/architecture/implementation plan/testing strategy; optional (include only when applicable) = performance, security, migration, rollout. The anti-pattern they name explicitly: a TDD that pads every optional section with "N/A" — ceremony wearing an apology. Same proportionality rule as tlc-discover ("a step with no input costs a line").

## Cross-links
- `note-taking/living-docs-governance/SKILL.md` — ADR index placement, one-canonical-owner-per-fact discipline (the governance side).
- `software-development/mattpocock-spec-driven-development/references/spec-driven-patterns-tlc.md` §6b — one-way doors: which decisions even DESERVE a decision document.
