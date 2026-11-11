---
description: "Routing-quality and conformance harness ported from addyosmani/agent-skills, with this corpus's 2026-11-11 measurements"
source_repo: addyosmani/agent-skills (MIT) - scripts/run-evals.js + scripts/lib/skill-lint.js at main, read 2026-11-11
tested_version: "Rules ported by reading the upstream JS; the ranking math was reproduced here and its behaviour measured on this corpus. Upstream's own runner (node, needs `claude` CLI) was NOT executed - Tier-3 behavioural evals are described from source only."
verified_date: "2026-11-11"
---

# Routing-quality harness (descriptions decide activation)

A skill library can pass every consistency gate and still route badly: indexes match disk, links
resolve, lanes exist - and the agent still picks the wrong skill, because what a host actually reads
to choose is the one-line `description` injected into its prompt. Upstream's harness measures that
layer; this repo had no equivalent (`tools/audit-skills.py` checks frontmatter/link/secrets shape,
`tools/check-router-coverage.py` checks that router *lanes name* in-scope skills - neither scores how
separable two descriptions are). Ported as `tools/analyze-skill-routing.py`, read-only.

## What upstream measures (run-evals.js)

**Tier 2 - deterministic, CI-safe, zero dependencies.** A per-skill case file (`evals/cases/<skill>.json`)
carries trigger prompts; each **positive** prompt must rank its skill in `top_k` (default 3) when scored
against *all* skill descriptions, and each **negative** prompt must NOT rank it #1. Minimums per case
file: 3 positive, 2 negative, >=1 behavioural eval - a file below that is an error even if every test
passes, so coverage cannot be quietly skipped. A **rank-1 ratchet** (`--min-rank1 <pct>`) fails the run
when routing quality drops below the checked-in baseline: percentages are compared to a committed
number, never to prose memory of one.

**Routing collisions.** Every pair of skills is scored by cosine similarity of TF-IDF vectors and flagged
at **>=0.5 (warn) / >=0.75 (error)**. The corpus doc per skill is `name tokens x2 + description tokens` -
the doubled name is distinguishing signal, not decoration (measured below: identical prose with different
names scores ~0.67, so 0.75 really does mean "near-duplicate" rather than "same topic").

**Tier 3 - opt-in, spends tokens, never in CI.** Each behavioural eval runs headless `claude` inside a
throwaway workspace: `git init`, commit the fixture as a baseline, `git apply` the patch, then grade the
full `stream-json` trace with a grader (tolerant parse, outcome persisted). Executor tools are an explicit
allowlist (`Read,Glob,Grep,Edit,Write,Bash,WebFetch,WebSearch`) with `--permission-mode acceptEdits`, so
the agent *performs* the skill instead of narrating it. Two guards worth stealing: the skill-name argument
is validated against path traversal (no `..`, no absolute paths - otherwise `--behavioral ../../x` escapes),
and prompts go in on stdin rather than interpolated into shell arguments, because a graded artifact can
carry injected instructions.

## Lint rules upstream enforces that this repo's auditor did not

From `scripts/lib/skill-lint.js`. Four of these were genuinely absent here:

- **Top-level frontmatter allowlist.** Only `name, description, license, compatibility, metadata,
  allowed-tools` may sit at the top level; vendor/runtime fields belong under `metadata`. Hosts do not
  promise to ignore unknown keys, so a published skill carrying them can fail packaging on a strict client.
- **Positive trigger clause.** The description must say *when* to use the skill: `use when` /
  `use before|after|during`. Negated clauses ("Do not use when X") describe exclusions and do not count -
  and **every** negation is stripped before re-testing. Upstream's own comment records why that needs a
  separate `/g` copy of the pattern: a global JS regex carries `lastIndex` across `.test()` calls, so
  reusing one instance silently under-strips and lets two-negation descriptions pass on the leftovers.
- **`name:` must equal the directory name**, directories and supporting `.md` filenames lowercase-hyphen-separated.
- **Declared-but-empty support subdirectory** is a defect (a `references/` with nothing in it means content
  was lost or never written), and exemptions are validator-owned: if a SKILL.md tries to declare its own
  exemption (`type: meta`, `exempt: sections`) while not on the allowlist, that fails loud - an author must
  not be able to switch off their own gate.
- **500-line body budget** (warning, not error): a SKILL.md loads in full the moment it activates, so its
  length is paid for on every activation. Upstream keeps it a warning because trimming is editorial; failing
  CI would block unrelated work on an over-budget skill.

## Measured state of this corpus - 2026-11-11

`tools/analyze-skill-routing.py`, run against both trees (reports kept at
`%LOCALAPPDATA%\hermes\audits\skills-plugins\routing-{repo,live}-2026-11-11.json`):

| Check | repo clone (`Hermes_Skills`) | live tree (`~\.hermes\skills`) |
|---|---|---|
| skills scanned | 255 | 218 |
| C1 `name:` != directory | **0** | **0** |
| C2 non-kebab dir / supporting `.md` | 7 (informational) | 7 |
| C3 no positive trigger clause | **254/255 (~100%)** | 216/218 |
| C4 non-spec top-level keys | `version`, `author`, `platforms` on all 255; then `prerequisites` x19, `dependencies` x9, `category` x3, `triggers` x3, `required_commands` x2 + 8 singletons (17 distinct) | same shape |
| C5 empty support subdir | 1 (`cli-tool-craft/references`) | - |
| C6 over 500-line budget | **21** (top: research-paper-writing 1238, design-taste-frontend 960, windows-desktop-e2e 899, sql-for-data 828) | 22 (research-paper-writing 1630) |
| routing pairs >=0.5 / >=0.75 | **10 / 0** | 12 / 0 |

Readings that matter:

- **C3 is the headline.** Essentially every description in this brain states *what* it does and not *when*
  to use it - while Hermes' own authoring guidance asks for `Use when <trigger>. <behavior>.`. The corpus
  diverges from its platform's stated convention almost universally. Deliberate policy, recorded here: **do
  not mass-rewrite 254 files.** Terse noun phrases are a real trade-off (the index is injected every turn;
  trigger clauses cost characters against the 59-char limit this repo enforces). Adopt on touch - when a
  skill is edited anyway, spend some of its budget on a `Use when ...` clause - and hold new skills to it.
- **C4 says our portability surface is exactly three keys.** `version`, `author`, `platforms` sit top-level
  on all 255 (spec-illegal); everything Hermes-specific (`tags`, `related_skills`) is already correctly nested
  under `metadata.hermes`. So exporting to a strict Agent Skills client needs those three moved or stripped -
  one mechanical transform, not a rewrite. See cross-harness-skill-porting for export consequences.
- **C6: 21 skills exceed upstream's activation-cost budget.** The remedy is the split this repo already uses:
  move depth into `references/*.md` and keep SKILL.md to the decision path. Top offenders are named above;
  they were measured, not guessed (research-paper-writing at 1238 lines costs ~4x its budget on every activation).
- **C5: one empty `references/` dir** - git cannot track an empty directory so nothing was lost from the clone,
  but it flags a skill whose reference content never landed. Worth checking when that skill is next touched.

### The ten flagged pairs (repo tree, faithful weighting)

```
0.749  github/github-issue-to-pr        <-> github/github-issues
0.583  creative/design-taste-frontend   <-> frontend-design/frontend-design
0.552  autonomous-ai-agents/cron-config-authoring <-> autonomous-ai-agents/cron-job-authoring
0.535  research/llm-wiki                <-> software-development/code-wiki
0.525  productivity/nano-pdf            <-> productivity/pdf
0.525  creative/hyperframes-video       <-> creative/remotion-video
0.523  creative/architecture-diagram    <-> creative/diagram-design
0.514  creative/ascii-art               <-> creative/ascii-video
0.514  creative/system-atlas            <-> software-development/repo-atlas
0.503  creative/static-site-seo         <-> web-development/static-site-patterns
```

`github-issue-to-pr <-> github-issues` at **0.749 sits one thousandth under upstream's error bar** - the two
are nearly indistinguishable by description alone, and only `github-issue-to-pr` pointed at its counterpart.
Fixed this round: `github-issues` now names it in `related_skills` and carries a "Not for driving one issue
through to a merged PR" line under *When to Use*.

The rest are topic neighbours rather than duplicates; several already disambiguate each other (hyperframes-video
and remotion-video name one another). Treat a flag as a prompt to check the pair, not an automatic defect: for
each, either sharpen one description so the boundary is legible from the index alone, or accept it and record
why here.

## Limits of this method (measured, not assumed)

- Ranking uses **name + description only**; tags, body text and reference filenames never enter the score.
  A skill with a terse description but precise body content looks confusable to this tool and routes fine in practice.
- Scores are corpus-relative: IDF is `log(1 + N/(1+df))`, so thresholds do not transfer between corpora of
  different size. Upstream calibrated 0.5/0.75 on their catalog; on ours (N=255) the same numbers sit in a
  distribution whose top pair is 0.749 and whose tail begins around 0.50 - treat >=0.5 here as "look at this pair",
  not "this pair is broken".
- Fixture measurements on throwaway trees, to calibrate intuition: two skills sharing one description sentence but
  different names -> **0.598** (warn only); identical descriptions, differing names -> **0.671**; same trigger clause
  with one word changed -> **0.830** (crosses error). Unrelated skill in the same tree stayed unpaired at warn=0.05.
- The doubled-name weighting is load-bearing: an earlier port of mine weighted name tokens once, which
  reported only **3** pairs on this corpus and put `github-issue-to-pr <-> github-issues` at **0.570** -
  comfortably inside the warn band instead of one step from error (faithful weighting: **0.749**), while
  inflating `hyperframes-video <-> remotion-video` to 0.648. Wrong term frequency hid the riskiest pair and
  invented a milder one. Faithful reproduction of upstream's `buildCorpus()` is what produced the ten-pair list above.

## Using the tool here

```bash
python tools/analyze-skill-routing.py                       # this repo, human summary; exit 0 clean
python tools/analyze-skill-routing.py --json report.json    # machine-readable findings
python tools/analyze-skill-routing.py --probe "render my composition to mp4"   # who wins this prompt?
python tools/analyze-skill-routing.py <other-tree> --warn .6 --budget 700      # audit a third-party library
```

Exit codes: `0` no hard finding, `1` C1 mismatch or any pair >= error threshold, `2` bad root. It writes nothing -
deliberately not wired into `verify-all.py`, because its informational checks (C3/C4/C6) describe conventions this
repo holds differently and a gate that fires on 254 skills is noise, not signal.
