# User Profile (USER.md)

This is the user profile from the Hermes profile at:
`C:\Users\Loggg\AppData\Local\hermes\memories\USER.md`

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
