# Harness Audit Protocol: Dual-Judge + Planted Traps (verified from tech-leads-club/agent-skills @ 0ab82f6)

Source: `packages/skills-catalog/skills/(development)/harness-eval` v1.8.3 — SKILL.md +
`references/PROTOCOL.md`. License CC-BY-4.0; attribution: Tech Leads Club. Mined 2026-09-16. A stack-agnostic way to
audit a repo's AGENT HARNESS (AGENTS.md, rules files, skills, skill references) across three tracks — and the planted-trap
calibration pattern is directly reusable for any LLM-judged gate in this brain (cf. our mutation-test-doc-gate.py).

## The three tracks (judgment ≠ remediation; report-only by default)

| Track | Question | Certainty | Cost | Method |
|---|---|---|---|---|
| **A — Correctness** | Do cited paths/commands exist? | Highest — script only, no LLM. Prefers false negatives over false BROKEN | ~0 model tokens (always runs) | deterministic inventory + existence checks |
| **B — Redundancy** | Would an agent rediscover this cheaply WITHOUT the harness text? | Medium — dual LLM judges + plants; disagree ⇒ Hold | High: 2 judges × every atomic claim | blind-judge agreement |
| **C — Usefulness** | Does deleting this surface change behavior vs theory/demo/overlap? | Lowest / MODEL-SENSITIVE — dual judges + plants + fan-in gate | Highest: 2 judges × whole surfaces | blind-judge agreement |

Ship (B) ≠ Slim (C): rediscoverable ≠ useless; useful ≠ non-redundant. Never equate the tracks. Budget is user-approved
UP FRONT via a certainty/token table before Track A runs — "do not spawn B/C judges until opted in."

## Surface tiers & scope rules

T0 always-on rules (AGENTS.md, CLAUDE.md, .cursorrules, *.mdc) · T1 skills (SKILL.md presence-based under
.agents/.cursor/.claude skill trees) · T2 one-hop cited harness files after doc-scope policy. Out of scope: README*
(never as surface or rediscovery evidence), app source (evidence only), user-global rules, recursive project-doc crawls,
and **ADRs/RFCs/decision-record trees — never scored as harness surfaces** (a skill folder NAMED `adr` that teaches how to write ADRs still counts; the decision-record corpus does not). Other cited docs are opt-in with a default-omit questionnaire.

## Track A precision rules (the Python pitfall is real)

Case-sensitive existence checks; command cites must exist in discovered manifest scripts when presented as runnable;
placeholders (`SPEC_FOLDER`, `{x}`, `[feature]`) never BROKEN; skip fenced code blocks for path cites; missing `app/`/`lib/`/
`test/` cites are BROKEN only with mandate language (load/open/must/required) in the same paragraph. **The bug they document:
never normalize paths with `str.lstrip('./')`** — lstrip strips a CHARACTER SET, so it turns `.agents/skills/x.md` into
`agents/skills/x.md` and every leading-dot cite false-positives as missing (their T2 inventory once came back empty for this exact reason). Strip only a literal `"./"` prefix.

## The planted-trap calibration pattern (steal this)

LLM judges are uncalibrated; their answer: mix known-labeled items INTO the judge's deck, unlabeled, and gate on agreement
with the labels BEFORE trusting any real verdicts.

- Track B plants: manifest echo ×2 + generic fluff ×2 ⇒ expected REDUNDANT family; fixed secrets-policy + local-vs-CI env caveat ⇒ KEEP family (KEEP plants must NOT be verbatim copies of real claims in the deck). Trap gate: miss ≤1 plant family ⇒ PASS, else discard the whole Ship band.
- Track C plants: generic clean-code theory surface + product-fluff surface ⇒ SLIM; cross-module boundary/public-API policy surface ⇒ KEEP-CORE. Same ≤1-miss gate for the Slim band.
- The trap key stays private (`trap-key.json`) — Judge2 is BLIND (must not read Judge1's scores or the key); Ship requires dual REDUNDANT + blind-judge rediscovery-cost ≤1 + trap PASS; disagreement ⇒ Hold, never a coin flip.

## Track C mechanics worth keeping

- **Rediscovery question**: "If this surface were deleted and the agent could still list the repo and open 1–2 canonical examples — would behavior change?" Section tags: BEHAVIOR-CHANGING / REPO-DEMONSTRATED (already taught by example files) / THEORY / OVERLAP (same rule in another surface, must cite path) / ROUTING-ONLY.
- **Fan-in gate (deterministic, at merge)**: before a dual-Slim surface enters the Slim band, scan the FULL harness corpus — if any other surface HARD-LOADS the path (load/read/open mandate, "source of truth"), it moves to Hold (`slim-fanin-blocked`); mere index mentions don't block. When applying cuts, never stub/delete a fan-in-blocked path without updating its consumers in the same change; and never replace a fenced teaching snippet with `See app/…` — that swaps source-of-truth for a code-tree pointer (the cut must leave remaining behavior-changing text self-contained).
- **Model sensitivity**: usefulness judgments depend on what the judge model treats as "general knowledge" vs repo-specific. Record judge model ids in both score files; prefer same non-fast model within a run; before large Slim deletes, re-run with a SECOND model family and treat cross-model disagreement as Hold — "the intersection of Slim bands is the safe delete set."
- **Mixed apply is mechanical**: for dual-MIXED surfaces the merge script emits `11-mixed-apply.md` copying each judge's Keep-core→KEEP / Slim→CUT; apply agents follow that file ONLY (no re-judging, no redesigning); empty cells ⇒ skip as Hold.

## Applying to this brain

Our audit gates are structural (frontmatter/links/counts) — the trap pattern is how you'd add a JUDGMENT gate: e.g., before
trusting an LLM review of skill descriptions or redundancy findings, run it against a deck seeded with labeled plants and require
the ≤1-miss agreement. Same philosophy as `tools/mutation-test-doc-gate.py` (self-test the gate) but for probabilistic judges instead of deterministic ones.
