# User Profile (USER.md)

> **Historical snapshot, not current state.** This is a point-in-time copy taken when the profile
> was first mirrored into this repo (2026-08-24). The live files it was copied from have moved on
> considerably since. For what the agent actually reads and writes today, use
> [`../memories/`](../memories/) — those are kept byte-identical to the live store by the weekly
> sync. This file is kept because it preserves early entries that the live memory later condensed
> into one-line references.


This is the user profile from the Hermes profile at:
`C:\Users\Owner\AppData\Local\hermes\memories\USER.md`

## Contents

```
User prefers LaTeX resumes over Word docs; wants them to closely match their original formatting style (not be over-engineered).

Runs AspireCURES (github.com/loggger101/aspirecures) — a patient-matching nonprofit website for rare brain diseases. Operates a weekly automated research pipeline that pulls from Europe PMC + PubMed + ClinicalTrials.gov + ISRCTN, curates with a Claude gatekeeper, and renders into 9 disease pages. Prefers a two-agent split: cronjob = preparer (collects/gates/emits JSON report), separate commit agent = executor (merges, renders, validates, commits). Explicitly corrected the ANTHROPIC_API_KEY misunderstanding — the agent IS the model, no API key needed. Runs tasks locally, values full reasoning capability even in autonomous mode (no user interaction ≠ non-reasoning). Wants prompt bodies to be self-contained and embed exact guardrails from the repo's own documentation.
```

## Key Facts

1. **Resume preference:** LaTeX over Word docs. Wants close match to original formatting style — not over-engineered.

2. **AspireCURES:** Runs a patient-matching nonprofit for rare brain diseases at `github.com/loggger101/aspirecures`. Operates a weekly automated research pipeline:
   - Sources: Europe PMC, PubMed, ClinicalTrials.gov, ISRCTN
   - Curation: Claude gatekeeper
   - Output: 9 disease pages
   - Architecture: Two-agent split:
     - **Preparer (cronjob):** Collects, gates, emits JSON report
     - **Executor (commit agent):** Merges, renders, validates, commits
   - Key correction: The agent IS the model — no ANTHROPIC_API_KEY needed
   - Values: Full reasoning capability even in autonomous mode (no user interaction ≠ non-reasoning)
   - Prompt preference: Self-contained bodies that embed exact guardrails from the repo's own documentation
