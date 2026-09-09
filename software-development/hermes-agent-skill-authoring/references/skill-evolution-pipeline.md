---
description: "DSPy+GEPA skill-evolution pipeline (NousResearch/hermes-agent-self-evolution) — verified CLI, requirements, when NOT to use"
source_repos: NousResearch/hermes-agent-self-evolution (MIT; GEPA = ICLR 2026 Oral), read at source level 2026-09-09
verified_date: "2026-09-09"
---

# Skill Evolution Pipeline (DSPy + GEPA)

`NousResearch/hermes-agent-self-evolution` is a standalone optimization pipeline that evolves the TEXT of Hermes skills, tool descriptions, and prompt sections — no GPU training. It wraps skill text as a DSPy module, generates an eval dataset, runs **GEPA** (Genetic-Pareto Prompt Evolution; ICLR 2026 Oral) which reads execution traces to understand *why* candidates fail, then gates survivors through constraint checks before opening a PR against the hermes-agent repo.

## Verified CLI (from `evolution/skills/evolve_skill.py`, read at source level)

```bash
git clone https://github.com/NousResearch/hermes-agent-self-evolution.git
cd hermes-agent-self-evolution && pip install -e ".[dev]"

python -m evolution.skills.evolve_skill \
  --skill <name>                    # required: skill name to evolve
  [--iterations N]                  # default 10 GEPA iterations
  [--eval-source synthetic|golden|sessiondb]   # default synthetic; sessiondb = real Claude Code/Copilot/Hermes history
  [--dataset-path <JSONL>]          # pre-built eval dataset instead of generating one
  [--optimizer-model openai/gpt-4.1]      # GEPA reflection model (LiteLLM-style name)
  [--eval-model openai/gpt-4.1-mini]     # evaluation model
  [--hermes-repo <path>]            # hermes-agent repo to diff/PR against
  [--run-tests]                     # full pytest suite as constraint gate
  [--dry-run]                       # validate setup, no optimization
```

The tool reports the measured improvement and explicitly refuses to celebrate a non-improvement ("Try: more iterations, better eval dataset, or different optimizer model") — treat its output numbers as the acceptance signal.

## Requirements / cost

- Everything runs via LLM API calls (mutate → evaluate → select). Typical run ≈ 50–500+ calls; upstream quotes ~$2–10 per optimization on hosted models.
- Model names are LiteLLM-style (`openai/gpt-4.1`), so any OpenAI-compatible endpoint works — including a local LM Studio server (`http://127.0.0.1:42069/v1`) if you point the model name at it (e.g. `openai/qwen3.8-27b@q4_k_xl` with base_url override). Quality of GEPA reflections on a local 27B is unverified; assume hosted-class models for real runs, local only as a cheap smoke test.
- Three engines exist in the repo: **DSPy+GEPA** (MIT — skills/prompts/tool descriptions), **MIPROv2** (MIT fallback optimizer), **Darwinian Evolver** (AGPL v3, external CLI only — code files). Only invoke the AGPL one via subprocess; never import it.

## When to use / NOT use

- USE: a skill that is measurably underperforming on tasks you can score (exact match, test pass/fail, rubric), and you have or can generate ~3+ eval examples. GEPA works with as few as 3 examples but more is better.
- DON'T: skills whose "quality" has no scorer — write the evaluator first; that's the hard part per upstream. Don't run it to fix a factual error in a skill (just edit the fact). Don't treat an evolved variant as automatically safe — review the diff, re-run this repo's `verify-all.py` gates, and keep the constraint gate (`--run-tests`) on.
- Tiering from the project plan: skill files = highest value/lowest risk; tool descriptions next (tool selection is a classification problem); system-prompt sections last (prompt-cache breakage risk — optimize offline only).

## Relationship to this brain's audit stack

Evolution proposes text changes; it does NOT replace `tools/verify-all.py` (frontmatter/description-length/link/count gates) or the per-skill test suites discovered by `run-skill-tests.py`. A healthy workflow: evolve with `--run-tests`, then run verify-all, then commit through the normal hermes-cronbot flow. The `.usage.json` per-skill metrics in a live profile are a natural source for picking which skills to evolve (low success / high cost).
