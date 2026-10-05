---
name: conference-review-criteria
description: "How ML conference reviewers score papers; rebuttals."
version: 1.0.0
author: Hermes Agent (promoted from research-paper-writing references, 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [peer-review, neurips, icml, iclr, acl, aaai, colm, rebuttal, reviewer-simulation]
    related_skills: [research-paper-writing, scholar-evaluation, human-evaluation-design, ai-research-integrity]
---

# Conference review criteria

## What This Skill Does

Lists how reviewers at NeurIPS, ICML, ICLR, ACL, AAAI and COLM evaluate papers, so an author can pre-empt concerns and a reviewer can write a strong review. It covers the four universal dimensions, each venue's scoring and instructions, the structure of a good review, the common concerns with how to pre-empt each, rebuttal practice with a template, and a pre-submission reviewer simulation. Dates and scales are snapshots; check the venue's current call.

## When to Use

- Preparing a submission and wanting to anticipate reviewer objections
- Writing a rebuttal, or deciding which criticism to accept and which to contest
- Reviewing a paper and structuring the review
- Not for scoring a paper against a general research rubric (`scholar-evaluation`) or for the writing pipeline itself (`research-paper-writing`)

## Quick Reference

| Dimension | What reviewers ask |
|---|---|
| Quality | are claims supported, proofs correct, experiments controlled, baselines fair |
| Clarity | can the work be understood and reproduced |
| Significance | does it matter to the community |
| Originality | what is new relative to prior work |

Strong review shape: summary, 3-5 strengths, 3-5 weaknesses with suggestions, 2-4 questions, minor issues, then a recommendation with reasons. Dennett's rules open it: restate the position fairly, list agreements, list what you learned, then critique.

Common concerns to pre-empt: weak baselines (use current state of the art), missing ablations, no error bars, untuned hyperparameters, unsupported claims, incremental novelty (state what is new, compare explicitly to the closest paper).

## Procedure

1. Read the target venue's section for scoring scale, required sections (for ACL, limitations and ethics) and unique points.
2. Check the draft against the four dimensions and the common-concerns tables.
3. Run the pre-submission reviewer simulation, ideally with a real published review from the venue as a calibration example.
4. For a rebuttal: answer each reviewer separately, concede valid points, push back with evidence only where warranted, summarise changes, and keep it short.
5. For a review: follow the structure above and justify the score.

## Pitfalls

- Long, defensive rebuttals.
- Treating one venue's scale as another's.
- Leaving the limitations section until the end at venues that require it.
- Using the dates in the guide (a NeurIPS 2025 timeline) for the current year.

## Verification

- [ ] The draft was checked against the venue's own section
- [ ] Every common concern has either a pre-empting sentence or a stated reason it does not apply
- [ ] Rebuttal answers each reviewer point and states what changed

## References

- `references/reviewer-guidelines.md` - universal dimensions, per-venue guidelines, strong-review structure, common concerns, rebuttal practice and template, reviewer simulation
