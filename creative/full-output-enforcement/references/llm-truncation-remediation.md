---
description: "Why models truncate/lazily answer and how to force complete outputs — root causes, parameter tuning, prompt templates; claims verified against primary sources where possible"
source_repos: Leonxlnx/taste-skill research/laziness/* (MIT), clone @ ccbc156 mined 2026-09-10. Verification pass this date: EmotionPrompt checked vs arXiv 2307.11760, LazyBench vs arXiv 2410.11437, Gemini thinking params vs ai.google.dev docs + live API error reports
verified_date: "2026-09-10"
---

# LLM Output Truncation & Laziness — Root Causes and Remediation

Distilled from taste-skill's `research/laziness/` directory (a structured analysis of why production LLMs produce incomplete outputs). This is the *why* behind the `full-output-enforcement` skill: that one bans placeholder patterns, this one explains where they come from and what actually suppresses them.

**Verification status legend:** ✅ = checked against a primary source on 2026-09-10 · ⚠️ = plausible but not verifiable here (treat as heuristic) · ❌ = contradicted or distorted vs the cited source — corrected inline.

## Root causes

### RLHF brevity bias + stopping pressure ✅(mechanism) / ⚠️(economics numbers)
Providers have an economic incentive to minimize output length; alignment training rewards short confident summaries over exhaustive multi-step work, and autoregressive models carry a learned "stopping pressure" that recent iterations calibrate aggressively. Observable symptoms: skipped structured-output fields (long JSON/markdown sections), halting mid-task with "let me know if you want me to continue", refusing comprehensive solutions in favor of "think about it". The repo's "$0.0001/token baseline cost" figure is ⚠️ unverified — the mechanism claim stands without it.

### Training-data placeholder propagation ✅(well-established)
Models imitate abbreviated human code: `# implement auth here / pass` patterns from Stack Overflow, tutorials with "complete this yourself", forum skeleton answers, blog posts that truncate repetitive blocks ("similarly for the remaining cases"). The model assigns high probability to truncation tokens in exactly the contexts where full output is appropriate — without aggressive prompting, the tutorial-style pattern wins because it's far more common in the training distribution. This is why *banning* placeholder patterns in-prompt (as `full-output-enforcement` does) works at all: you're overriding a learned prior, not fixing a bug.

### Cognitive shortcuts / "model laziness" ✅(LazyBench, with scope correction)
⚠️→✅ **Scope correction:** the repo cites LazyBench as evidence frontier text models shortcut long tasks; the actual paper (arXiv 2410.11437, "Difficult Task Yes but Simple Task No") is about **multimodal** LLMs failing simple yes/no questions on images they can correctly describe — laziness was *more pronounced in stronger* models (GPT-4o lazy rate ~75% on yes/no). The transferable finding: capability does not mitigate shortcutting, and forcing the model to do the hard part first fixes a large share of failures. **✅ Verified from the paper:** requiring chain-of-thought / description-first ordering fixed ~40% of laziness cases — i.e., *making the task harder in a structured way is a remediation*, not just an annoyance.

### Context-window asymmetry + consumer middleware ⚠️
Huge input windows (up to 2M tokens on some models) against strictly capped output limits create preemptive compression: when the model estimates it can't finish, it summarizes instead of risking cutoff. Consumer web tiers add software-level truncation (history capping ~32K per the repo — ⚠️ unverified figure; retrieval-based recall that silently drops earlier instructions). Practical rule ✅(behavioral): direct API / CLI access to the same model routinely produces complete outputs where the consumer UI produced truncated ones. If a "model limitation" only appears in one surface, suspect middleware before architecture.

### Error-avoidance truncation ⚠️
Models also shorten output as risk mitigation: longer output = larger surface for compounding errors/hallucination. This compounds with RLHF brevity bias on long-form tasks. Implication: verification loops (below) reduce this incentive by making the model check its own claims rather than hedge them away.

❌ **Unverified in source:** the "winter break hypothesis" (ChatGPT outputs measurably shorter in December because training data contains holiday-period brevity; stating "It is May" in the system prompt increases length) — no primary study found during verification. Interesting, but treat as folklore until cited.

## Remediation ladder (parameter → prompt → architecture)

### 1. Parameter tuning
- **Temperature/top-p**: low temp (0–0.5) sharpens toward highest-confidence continuations; the repo's claim that top-p 0–0.6 + low temp "reduces entropy enabling creative refusals and unnecessary summarization" is ⚠️ a heuristic, not a measured result. For code/structured output: low temperature is standard practice ✅(conventional).
- **Gemini thinking levels** ✅ (verified against ai.google.dev/gemini-api/docs/thinking + live API error reports): Gemini 3 models use `thinking_level` (minimal/low/medium/high) instead of the legacy token-count `thinking_budget`; sending both in one request returns HTTP 400 ("thinking_budget and thinking_level are not supported together" — confirmed verbatim in a real cline/cline issue). Level support is per-model: e.g. gemini-3-pro-preview supports low+high only (no medium); flash models get minimal→high. For code generation / complex analysis use `medium` or `high`; avoid pairing extremely low temperature with high thinking level (occasional internal reasoning loops, ⚠️ repo claim).

### 2. Prompt engineering
- **Stakes/emotional framing** — ❌ corrected: the repo attributes "+45% from a $200 tip" and "34%→80% accuracy on logic tasks" to Microsoft Research. The actual EmotionPrompt paper (arXiv 2307.11760, MS Research + CAS) reports **relative** improvements of ~8% on Instruction Induction and up to **+115% on BIG-Bench**, plus a 106-participant human study showing ~10.9% average improvement in generative quality/truthfulness from emotional stimuli appended after the prompt; truthfulness on ChatGPT rose 0.75→0.87. The direction is real and reproducible (stakes language correlates with high-effort training content), but the repo's per-stimulus numbers are inflated/misattributed — use "small single-digit to double-digit relative gains, largest effects on hard reasoning benchmarks" as the honest summary.
- **Explicit syntax binding** ✅(pattern): remove discretion about length by (a) forbidding answers from training weights alone — require tool execution first; (b) requiring evidence blocks (raw data/URLs/exec results) *before* narrative, so the model reads its own retrieved evidence. This is the same discipline as my `grounded-citations` skill.
- **XML-structured prompts** ✅(conventional): separate `<context>` (passive background), `<data>/<logs>` (active material to process), `<tasks>` (numbered actions) — reduces premature truncation triggered by intent-parsing confusion.
- **Verification loops**: Chain-of-Verification (generate → generate verification questions about own claims → answer them independently → revise); reverse prompting (give a one-line objective, have the model write its own structured prompt); self-grading loop (define excellence for this task → grade output against it → iterate until met). CoV is ✅ established; the other two are ⚠️ practitioner patterns.

### 3. Architectural patterns
- **Lazy-loaded skills** ✅(this brain's own architecture): frontmatter name+description (~100 tokens) as discovery hook, full body loaded on demand. The repo claims ~35% average context reduction and a discovery-success gap between vague descriptions (~68%) and specific ones (~90%) — ⚠️ unverified numbers; the mechanism is exactly how Hermes skills work (see `hermes-agent-skill-authoring`: description truncates at 57 chars in the index, so specificity must fit that window).
- **MCP grounding** ✅: with live docs fetched into context instead of static weights, the incentive to hallucinate-or-truncate disappears — the model reasons over current authoritative data. (This is why my own brain prefers tool-grounded answers for anything version-sensitive.)
- **Chunked task execution** ✅(pattern): for outputs that would exceed generation limits: (1) request architecture/outline first; (2) each component individually with explicit completeness instructions; (3) assembly/integration last. Prevents the model from estimating total length and preemptively compressing. This is also why multi-call agent workflows beat one giant prompt for big deliverables.

## Ready-to-use enforcement templates (verbatim, MIT source)

**General purpose:**
```text
You must provide the FULL, complete, and exhaustive output for this task.
Do not summarize, abbreviate, or truncate for brevity.
You are strictly forbidden from using placeholders. Never use comments like
"// ... rest of code here", "[continue here]", or bare ellipses standing in
for omitted content. If the output is 500 lines, produce all 500 lines.
If you approach your output limit, stop at a clean breakpoint and indicate
where to resume. Do not rush to a conclusion or compress remaining sections.
```

**Code generation:**
```text
Write the complete, production-ready implementation. Every function, every
import, every edge case handler must be present in the output.
Do not use placeholder comments (// TODO, // implement here, // similar
to above). Do not describe what code should do — write the actual code.
If the implementation requires multiple files, output each file completely
with its full path as a header.
```

**Analysis and documentation:**
```text
Provide an exhaustive analysis covering every aspect requested. Each section
must contain substantive content, not summaries or references to "see above."
Do not use phrases like "as mentioned earlier" to avoid repeating necessary
context. Each section should be self-contained and complete.
Structure your output with clear headings. If the analysis requires multiple
parts, produce all parts in full.
```

**Continuation handling:**
```text
If your response approaches the output token limit:
- Do not compress remaining content to fit
- Do not skip ahead to a conclusion
- Stop at a natural breakpoint (end of a function, end of a section)
- End with: [PAUSED - X of Y sections complete. Send "continue" to resume]
On "continue", pick up exactly where you stopped. No recaps or repetition.
```

## Empirical findings worth keeping (with corrections)

| Finding | Status | Note |
|---|---|---|
| Truncation is a *behavioral* artifact, not memory/context failure — 200-turn conversations showed surprising instruction retention (Dec-2025 controlled study cited by repo) | ⚠️ single-source | Consistent with the RLHF/stopping-pressure mechanism; no primary paper located during verification |
| No model fully satisfied both length requirements and all sub-part instructions in multi-part prompts | ⚠️ same source | Matches field experience: explicit per-section completeness checks beat one global "be thorough" |
| LazyBench: laziness more pronounced in stronger models; CoT-first ordering fixed ~40% of lazy cases | ✅ arXiv 2410.11437 | Multimodal scope — see correction above |
| EmotionPrompt: relative gains up to +115% on BIG-Bench, ~8% Instruction Induction, truthfulness 0.75→0.87 (ChatGPT) | ✅ arXiv 2307.11760 | Repo's "$200 tip = +45%" is a distortion of these numbers |
| Gemini: `thinking_level` and `thinking_budget` mutually exclusive → HTTP 400; per-model level support varies (Pro often lacks medium) | ✅ Google docs + live API error verbatim | See parameter section for the exact error string |
