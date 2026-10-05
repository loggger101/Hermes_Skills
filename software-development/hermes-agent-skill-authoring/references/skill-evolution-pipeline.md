---
description: "DSPy+GEPA skill-evolution pipeline (hermes-agent-self-evolution): CLI, cost, when NOT to use, and what its metric, constraint gate and session importer really do (run)"
source_repos: NousResearch/hermes-agent-self-evolution (MIT; GEPA = ICLR 2026 Oral), CLI read at source level 2026-09-09; metric, constraints and importer run 2026-10-05
verified_date: "2026-10-05"
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

The tool reports a measured "improvement" and refuses to celebrate a non-improvement ("Try: more iterations, better eval dataset, or different optimizer model"). **Do not treat that number as the acceptance signal**: the metric behind it is a keyword-overlap heuristic, not the LLM judge (see "What the metric and the gates actually do" below). Read the diff and re-score with a real scorer.

## Requirements / cost

- Everything runs via LLM API calls (mutate → evaluate → select). Typical run ≈ 50–500+ calls; upstream quotes ~$2–10 per optimization on hosted models.
- Model names are LiteLLM-style (`openai/gpt-4.1`), so any OpenAI-compatible endpoint works — including a local LM Studio server (`http://127.0.0.1:42069/v1`) if you point the model name at it (e.g. `openai/qwen3.8-27b@q4_k_xl` with base_url override). Quality of GEPA reflections on a local 27B is unverified; assume hosted-class models for real runs, local only as a cheap smoke test.
- Three engines exist in the repo: **DSPy+GEPA** (MIT — skills/prompts/tool descriptions), **MIPROv2** (MIT fallback optimizer), **Darwinian Evolver** (AGPL v3, external CLI only — code files). Only invoke the AGPL one via subprocess; never import it.

## When to use / NOT use

- USE: a skill that is measurably underperforming on tasks you can score (exact match, test pass/fail, rubric), and you have or can generate ~3+ eval examples. GEPA works with as few as 3 examples but more is better.
- DON'T: skills whose "quality" has no scorer — write the evaluator first; that's the hard part per upstream. Don't run it to fix a factual error in a skill (just edit the fact). Don't treat an evolved variant as automatically safe — review the diff, re-run this repo's `verify-all.py` gates, and keep the constraint gate (`--run-tests`) on.
- Tiering from the project plan: skill files = highest value/lowest risk; tool descriptions next (tool selection is a classification problem); system-prompt sections last (prompt-cache breakage risk — optimize offline only).

## What the metric and the gates actually do (run 2026-10-05)

Re-checked at repo HEAD (last commit 2026-06-17, `fix(config): honor explicit --hermes-repo`). `evolution.core.constraints`,
`config` and the metric were imported and run with a stub `dspy` (no model calls, no `dspy` install); the importer's secret
filter and encoding were run on Python 3.14 / Windows with `rich` installed.

### The optimised metric is keyword overlap

`evolve_skill.py` passes `skill_fitness_metric` to GEPA (lines ~157 and ~170) **and** uses it for the holdout comparison
that prints "improvement" (~lines 217-226). `LLMJudge` is imported but not used in that loop. The metric returns 0 for empty
output, else `0.3 + 0.7 x overlap`, where overlap is the share of the rubric's distinct words that appear in the output. Results:

| Output for rubric "Lists each bug with file and line, ranks severity, and does not comment on style" | Score |
|---|---|
| A correct review in other words (null deref in api.py:42 critical ...) | **0.35** |
| The rubric text copied verbatim | **1.00** |
| The rubric's words shuffled into nonsense | **0.90** |
| A wrong answer that happens to say "file" and "line" | 0.40 |
| Empty | 0.00 |

So evolution rewards skill text that makes the agent echo the expected-behaviour wording. With the default dataset (20
examples, 50/25/25 split) the holdout has **5 examples**, so a small "improvement" is within noise. The `LLMJudge`
composite (0.5 correctness + 0.3 procedure + 0.2 conciseness minus a length penalty that ramps from 0 at 90% of the size cap to
0.3) is the better scorer; wire it in or supply your own metric before trusting a run.

### The constraint gate is shallow (all defaults: skill 15 000 chars, tool description 500, parameter 200, growth +20%)

| Candidate | Verdict |
|---|---|
| Well-formed skill | pass |
| Frontmatter never closed | **pass** |
| `name:` / `description:` appearing only in the body (frontmatter has neither) | **pass** (the test is a substring search of the first 500 characters) |
| Valid frontmatter whose `description:` comes after 500 characters of earlier keys | **fail** (false rejection) |
| 200-character description (this repo's audit gate allows 59) | **pass** |
| Invalid YAML (tab, unbalanced quote) | **pass** |
| Frontmatter with an empty body | pass |
| +19.9% vs +20.1% growth | pass / fail |
| Shrinks 90% (content deleted) | **pass**: only growth is limited, not shrinkage |
| Tool description 501 characters; whitespace-only | fail; fail |

Size cap versus this repo: of 205 `SKILL.md` files, **39 (19%) exceed 15 000 characters** (median 8 714, largest 78 267), so
the default cap rejects every large skill before it can be evolved. Run `verify-all.py` after any evolved output, as above;
the gate does not replace it.

### Session importer (`--eval-source sessiondb`)

Reads `~/.claude/history.jsonl` (user prompts only), Copilot session events and Hermes session JSON, filters with a secret
regex, then sends candidates to an LLM for relevance scoring. Findings:

- **Of 26 planted genuine secret-shaped strings the regex caught 11 and missed 15.** Caught: `sk-ant-`, `sk-proj-`, `ghp_`, `AKIA...`,
  `xoxb-`, `Bearer <20+ chars>`, `-----BEGIN PRIVATE KEY-----` and RSA, the names `AWS_SECRET_ACCESS_KEY` / `DATABASE_URL`,
  `password=`. **Missed:** `github_pat_...`, `ghs_`, `gho_`, an unlabeled AWS secret value, `AIza...` Google keys, `hf_...`,
  `xoxp-`, Stripe `sk_live_`, `Authorization: token <value>`, OpenSSH and EC private-key headers, `postgres://user:pass@host`,
  `"api_key": "..."`, `passwd:`, JWTs. It also flagged both prose controls ("The secret: keep tests fast", "see sk-learn-pipeline-helper-utility-for-x").
- **`open(path)` without an encoding**: with the Windows default (cp1252) a prompt "résumé ... 日本語" was imported as
  `rÃ©sumÃ© ... æ—¥æœ¬èªž` with no error; `PYTHONUTF8=1` fixed it. Set it before any run on Windows.
- Use `--dry-run`, read the dataset JSONL, scrub it yourself, and never point `sessiondb` at history that contains credentials
  you would not paste into the judge model.

Not run: GEPA itself, dataset generation with a model, PR creation, the test suite (`pytest tests/`).

## Relationship to this brain's audit stack

Evolution proposes text changes; it does NOT replace `tools/verify-all.py` (frontmatter/description-length/link/count gates) or the per-skill test suites discovered by `run-skill-tests.py`. A healthy workflow: evolve with `--run-tests`, then run verify-all, then commit through the normal hermes-cronbot flow. The `.usage.json` per-skill metrics in a live profile are a natural source for picking which skills to evolve (low success / high cost).
