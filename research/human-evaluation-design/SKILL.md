---
name: human-evaluation-design
description: "Design, run and report human evaluations for ML papers."
version: 1.0.0
author: Hermes Agent (promoted from research-paper-writing references, 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [human-evaluation, annotation, inter-annotator-agreement, crowdsourcing, irb, nlp, ml-papers]
    related_skills: [research-paper-writing, experiment-design, ai-research-integrity, scholar-evaluation]
---

# Human evaluation design

## What This Skill Does

Walks through a human evaluation of model outputs from "do I need one" to the reporting paragraph a reviewer will look for: study design, annotation guidelines with a pilot, recruitment, quality control, agreement metrics, statistical tests for the ratings, and IRB and ethics. The full guide is in `references/human-evaluation.md`.

## When to Use

- A paper reports generated text, summaries, safety judgements, preferences or agent task completion, and automated metrics are not enough
- Reviewers criticised a human evaluation as weak, or agreement is low
- Writing the annotator, agreement and protocol paragraphs of a methods section
- Not for classification accuracy or loss comparisons (automated metrics are the right tool), A/B tests on live traffic (`experiment-design`), or the paper pipeline as a whole (`research-paper-writing`)

## Quick Reference

| Question | Answer from the guide |
|---|---|
| Needed? | yes for fluency, summaries, nuanced safety, system preference, task completion; usually no for classification accuracy; no for perplexity |
| Annotators | at least 3 per item, or no agreement metric is possible |
| Pilot | 3-5 annotators, 20-30 items, discuss disagreements, revise guidelines; second pilot if kappa is below 0.40 |
| Quality control | 10-15% attention checks, annotator qualification, monitoring during collection |
| Agreement | Krippendorff's alpha as default; Cohen's kappa for 2 raters; Fleiss for 3+ on categorical items; ICC for continuous ratings; always report a chance-corrected metric plus raw percent agreement |
| Reading alpha | above 0.80 excellent, 0.67-0.80 good, 0.40-0.67 borderline (discuss), below 0.40 revise and redo |
| Reporting | annotator count and platform, qualifications, pay rate, agreement, rating protocol, randomisation and blinding |

## Procedure

1. Decide whether a human evaluation is needed using the table in the guide; if only an automated metric applies, stop.
2. Write the annotation guideline (definitions, scale, worked examples, edge cases, common mistakes) and run the pilot.
3. Recruit, then screen with a qualification task; embed attention checks and randomise item and system order.
4. Collect while monitoring quality; drop and replace failing annotators by a rule fixed beforehand.
5. Compute agreement, then analyse: a sign test on pairwise preferences (ties excluded), a Wilcoxon signed-rank test with an effect size for paired Likert ratings, and a Holm correction when testing several systems.
6. Report with the mandatory paragraphs and an appendix holding the guideline, interface screenshots and raw counts.
7. Check the IRB and ethics list before collecting, not after.

## Pitfalls

- One or two annotators, so no agreement can be computed.
- Skipping the pilot and discovering the guideline is ambiguous after the budget is spent.
- Reporting averages only, which hides disagreement.
- Not randomising presentation order, so position bias favours one system.
- Treating high agreement as correctness; validate against expert judgements.
- Not reporting compensation, which reviewers flag as an ethics concern.

## Verification

- [ ] At least 3 annotators per item and a pilot was run
- [ ] Attention checks and qualification rules were set before collection
- [ ] A chance-corrected agreement metric and raw agreement are both reported
- [ ] Presentation order was randomised and the study was blinded where possible
- [ ] Pay rate, platform and ethics approval status appear in the paper

## References

- `references/human-evaluation.md` - the full guide: study design, annotation guidelines, platforms, quality control, agreement metrics and code, statistics, reporting, IRB and ethics, pitfalls
