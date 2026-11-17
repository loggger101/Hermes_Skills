---
title: "Harness loader constraints: what actually reaches the model"
description: "Per-harness SKILL.md loading rules (roots, listing truncation, drop-vs-degrade conditions, size budgets) measured by NVIDIA/SkillEvaluator harness profiles, plus a 2026-11-16 audit of this machine's two skill trees against them."
---

# Harness loader constraints: what actually reaches the model

A `SKILL.md` can satisfy the Agent Skills spec and still never reach the model. Each
harness has its own loader: different folders scanned, different YAML parser strictness,
different listing budgets, different silent-truncation points. This document records those
constraints as *measured* facts, their verification method, and what they imply for how this
repo's skills are written and placed.

Source: `NVIDIA/SkillEvaluator` (Apache-2.0) @ `main`, fetched 2026-11-17 — 1303 tracked paths,
`src/skillevaluator/harness/profiles/{hermes,claude-code,codex,copilot-cli,openclaw,opencode}.yaml`.
Every profile carries a `verified:` block naming version, source commit, date (2026-11-01), OS
(linux) and method. The method is the interesting part: **proxy-captured canary probes x3** —
inject an unusual string into a skill, watch what each harness actually sends upstream, repeat
three times; three profiles add source reading (`method: proxy-captured canary probes x3 + source`).
That is why their numbers are usable as facts rather than documentation folklore. One profile note
worth copying as doctrine: *"Pin the commit: the displayed version string did not match the installed code."*

## Hermes loader rules (profile `hermes.yaml`, verified against NousResearch/hermes-agent
`c419cf7c864ac0ee511dbd9f7091a8bba0b567ee`, binary reports 2026.9.24, method canary probes + source)

| Rule | Behaviour | Consequence for authoring |
|---|---|---|
| Roots scanned | `~/.hermes/skills`; project `.hermes/skills` and `.agents/skills`. **Not** `~/.agents/skills` | A user-level install under `~/.agents/skills` is invisible to Hermes even though Codex reads it. These are the profile's paths, measured on **linux** — on this Windows box the user-level root is `%LOCALAPPDATA%\hermes\skills` and `~/.hermes` is empty, so resolve the root on the OS you are on before concluding a skill "is not installed" |
| Project trust | Project skills are *invisible until the repo is trusted* (`hermes skills trust`, `skills.trusted_project_dirs`) | "Installed but never triggers" is usually trust, not a bad description. Trust admits **every** project skill in that dir — treat it as running their code as your own |
| Precedence | project > `~/.hermes/skills` > `skills.create_dir` > `external_dirs` (project wins, 3/3) | A repo-local copy silently shadows a newer user-level one. Check which copy loaded before debugging content |
| Listing budget (`HM-DESC-60`) | The skill list shows only the first ~60 chars of `description` — **57 + `...`** in 0.16, a word boundary near 59 on main — and the trigger is not in them | Put the trigger ("Use when …") inside the first 57 characters. This is why this repo's audit gate caps descriptions at ≤59 chars: it is load-bearing, not cosmetic |
| `HM-NESTED` | A nested `SKILL.md` (inside another skill's dir) loads as a **second, separate** skill — hidden folders are walked too | Never ship a `references/**/SKILL.md`; rename or relocate it |
| `HM-SYMLINK-FILE` / `HM-RESOURCE-SYMLINK` | A symlinked `SKILL.md` is **not loaded**; a symlinked *folder* works. Symlinked resource files are omitted from the skill's file list (medium confidence) | Sync scripts may copy or link — verify manifests are real files, and don't lean on links for reference material |
| `HM-CASING` | `skill.md` / `Skill.md` is **never loaded** on Linux/macOS (3/3 each) | Exact casing only. A case-insensitive Windows tree can hide this until the repo lands on a Linux box |
| `HM-DUP-KEY` | Duplicate frontmatter keys: last value wins (Hermes tolerates it; Codex and OpenClaw **drop** the skill outright) | Write to the strictest harness you target, not the forgiving one |
| `HM-LINKED-LAYOUT` | Files outside `references/`, `templates/`, `assets/`, `scripts/` are left out of the skill's file list; the model finds them only if `SKILL.md` names their paths | Placement decides reachability. Either move support files into those four dirs or cite each path explicitly in the body |
| `HM-VIEW-BUDGET` | When the model loads a skill, `skill_view` returns ~the whole body **up to the 100,000-char tool-result budget** (lower on models under ~167K context). Over it: the model gets a **1,500-char preview, not the instructions**. `/name` and `-s` preload still deliver the full body | Keep `SKILL.md` under ~95,000 chars. A long body does not fail loudly — it silently delivers nothing useful. This is the single most dangerous budget here because the skill *looks* loaded |
| Ignored fields | `allowed-tools` ignored; `disable-model-invocation` ignored (model can still invoke); `agents/openai.yaml` implicit-invocation policy is Codex-only; Claude-only fields are inert but harmless | Never rely on a field for enforcement in Hermes. Use harness permission settings instead |
| Placeholders | `$ARGUMENTS` is **not** substituted — the model sees the literal text. `${CLAUDE_SKILL_DIR}` likewise: use `${HERMES_SKILL_DIR}` or paths relative to `SKILL.md` | Describe expected input in words. Large bodies are spilled and paged through in small reads |
| Naming/listing | Duplicate skill names list twice (model sees two); a near-identical description on a sibling risks wrong-skill selection; `platforms:` can hide the skill from the list on excluded systems | Unique name, description that "names what only that skill does" |

## Cross-harness limits in one table

| Harness | Roots scanned | Listing cut / budget | Drops the skill outright when |
|---|---|---|---|
| Hermes | `~/.hermes/skills`, project `.hermes/skills` + `.agents/skills` (trust-gated) | ~60 chars (`...` at 57); no published total budget | Non-canonical manifest casing; symlinked manifest. Not scanned: `~/.agents/skills` |
| Claude Code 2.1.316 | `.claude/skills`, `~/.claude/skills`. **Not** `.agents/skills` | Cut at 1,536 chars (description + `when_to_use` counted together); whole-list budget ≈1% of context window at 4 chars/token, 8,000 if unknown | Nothing found beyond one level: grouping folders are not searched (`CC-GROUPING`, depth > 0 → not loaded). `$N` price-like tokens become argument placeholders when invoked with ≥5 args (`$4.00` → `<5th arg>.00`) — reword amounts as `USD 4.00`; `\$4.00` escapes here but shows the backslash elsewhere |
| Codex CLI 0.166.0 | `.agents/skills`, `.codex/skills` (project + user), scan depth ≤6, skips hidden dirs | Cut at 1,024 codepoints (observed: 1,021 + `...`); list budget 2% of context / max 10,000 tokens | Missing or non-string description; invalid YAML (**tab indent** or duplicate keys); UTF-8 **BOM**. ≤0.141 *rejected* >1024-char descriptions rather than truncating (so a long description is a hard failure on old Codex) |
| Copilot CLI | — | 1,024 **UTF-16 units** (not codepoints): an emoji-heavy or CJK description can pass char count and still be over | Strict YAML parsing; over-limit descriptions |
| OpenClaw / OpenCode | their own roots | see profiles | invalid YAML (OpenClaw); OpenCode loads where several others do not |

Read the strictness ladder as a rule: **Codex is the harshest loader** (tabs, BOM, dup keys and a
missing description each drop the skill silently), Hermes/Claude degrade instead. If one corpus must
serve all of them, author to Codex's rules; nothing stricter than that costs anything on the others.

### Directory intersection for dual-target corpora

Hermes lists files under `references/`, `templates/`, `assets/`, `scripts/`. SkillEvaluator's schema
recognises `agents/`, `references/`, `scripts/`, `assets/`, `evals/`, `tests/`, `tools/`, `config/`
(anything else = LOW advisory; extend with `SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS`). So:

- **Safe in both:** `references/`, `scripts/`, `assets/`.
- `templates/` reaches the model in Hermes but is unrecognised (LOW) to their schema.
- `agents/`, `evals/`, `tests/`, `config/` satisfy their schema but are *not* listed by Hermes — the
  model sees those files only if `SKILL.md` cites the path.

Corroboration of this repo's own design: `tools/gen-claude-plugin.py` documents that Claude Code's
loader "does NOT walk category folders, so pointing it at the repo root finds exactly zero skills"
(verified against Claude Code 2.1.270) and works around it with an explicit `skills` array in
`.claude-plugin/plugin.json`. NVIDIA's independently-derived `CC-GROUPING` rule states the same fact
and adds that a symlink from `.agents/skills` works — two separate measurements agreeing, which raises
confidence in the existing design rather than changing it.

## Their Tier-1 gate taxonomy (ideas worth stealing for this repo's 31 gates)

Default `validate` checks: `schema`, `version`, `security`, `pii`, `license`, `code-integrity`,
`unicode`, `quality`, `lint`; `dependency` is opt-in. Notable thresholds and heuristics:

- **Schema:** names 1–64 chars, kebab-case, must start with a letter, no trailing/consecutive hyphens;
  directory name must equal frontmatter `name`; `anthropic`/`claude` reserved in names. Frontmatter
  *keys* must be strings — an unquoted `yes`/`123`/`null`/date key is HIGH (`Field 'metadata.true'`).
  `alwaysApply` and `globs` are **forbidden** skill fields (Cursor-rule leakage). Unknown fields LOW.
- **Sizes:** ≤500 lines recommended; `manifest_size` LOW >32 KiB, MEDIUM >50 KiB, HIGH >256,000 bytes —
  note these are far stricter than Hermes' ~100K-char delivery budget, and they gate on *bytes* not chars.
- **Portability findings inside schema:** `duplicate_key` HIGH, `manifest_bom` MEDIUM,
  `description_utf16_length` MEDIUM (≤1024 chars but >1024 UTF-16 units), `description_trigger` LOW
  (no "Use when …" in the first 60 chars), `manifest_symlink` / `nested_manifest` MEDIUM.
- **Quality score** = Correctness 35% + Discoverability 25% + Reliability 25% + Efficiency 15%, pass ≥70,
  computed with no LLM; token budget for a body is a *recommended* 5,000 tokens estimated as chars/4
  (explicitly not tokenizer output — tables and identifiers count worse).
- **Script lint heuristics** (advisory only): `flat_script` (no function definitions), `deep_nesting` >6,
  `magic_numbers`, `missing_shebang`, `no_input_validation` (no argparse/click/typer/explicit raise).
  Node scripts count for skill-type detection but are **not** linted — the report says how many were skipped.
- **Honest-incomplete doctrine**, matching this repo's own "a SKIP is never reported as a pass":
  `--no-llm` does not remove scanner requirements; a scanner that cannot run yields `INCOMPLETE` and a
  **nonzero exit**. Tier gating: Tier 1 always gates, Tier 2 gates unless `--no-block-on-dedup`, Tier 3
  only with `--block-on-agent-eval`.

## Running it against this corpus

```bash
pip install skillevaluator            # or: uv tool install skillevaluator
skillevaluator harness-check ./some-skill     # no LLM, no key, ~1s: loads / degraded / dropped per harness
uv run --python 3.13 skillevaluator quality-check ./some-skill -r cli -r json -o reports/first-quality
```

Caveats before trusting a green/red here: support level is **Experimental** (community, no SLA); the
project downloads third-party scanners (SkillSpector, Gitleaks; Semgrep optional) at pinned releases —
review those licences and expect network fetches; Tier 1 needs the scanners present or it exits nonzero.
Their own example skill scores 88.8/100 (B).

## Audit of this machine's two trees against these rules (measured 2026-11-16, Windows)

Ran a stdlib scan of both skill roots — the live Hermes tree at `%LOCALAPPDATA%\hermes\skills`
(`C:\Users\Owner\AppData\Local\hermes\skills`; this section first named it `~/.hermes/skills`, the
profile's linux path, which on this box is an **empty** directory) and the mirror repo's category dirs
(`profiles-export/`, `profile/`, `memories/`, `docs/`, `tools/` excluded as non-loadable):

| Check | Live tree (211 manifests) | Mirror categories (255 manifests) |
|---|---|---|
| Nested `SKILL.md` inside a skill dir (`HM-NESTED`) | 0 | 0 |
| Symlinked manifest / bad casing | 0 / 0 | 0 / 0 |
| Duplicate frontmatter keys (`HM-DUP-KEY`, Codex-fatal) | 0 | 0 |
| Exact-duplicate descriptions across tree (wrong-skill-selection risk) | 0 | 0 |
| Longest `description` | **59 chars** (none longer) | 59 chars |
| Bodies >32 KiB / >50 KiB | 9 / 3 | 8 / 2 |
| Bodies over ~90K chars (`HM-VIEW-BUDGET` risk zone) | 0 | 0 |
| Bodies >500 lines (their advisory) | 22 | 21 |

Interpretation, including where the checker is wrong for us:

- **The ≤59-char description cap is validated by measurement.** The observed maximum in both trees is
  exactly 59 — `audit-skills.py` enforces it — and Hermes' listing cut lands at ~57–60. So the gate is
  aligned with a real delivery boundary; do not "relax for readability".
- **No structural loader defects.** Casing, symlinks, nested manifests, duplicate keys: all clean in both trees.
- **Independently re-audited, and the root path corrected (2026-11-16, second session).** A separate
  stdlib scan of the 255 mirror manifests reproduced 0 findings across eight rules — oversized bodies vs
  the ~95K `skill_view` cliff, nested/symlinked manifests, casing, BOM, tab-indented frontmatter, missing
  and >59-char descriptions — so the clean verdict holds by two routes. Two corrections fell out of it:
  the live root is `%LOCALAPPDATA%\hermes\skills`, not `~/.hermes/skills` (empty here), and its manifest
  count read 212 then 213 minutes apart, so **211 is a timestamp, not a constant** — something writes
  that tree live. Note also that the Hermes tree is a *copy*, not a link: repo edits never reach it,
  while Claude Code loads the repo itself through `~/.claude/skills/hermes`, so the two can disagree
  indefinitely. Largest mirror body measures 79,491 chars (`creative/design-taste-frontend`), below the
  89,713 recorded for the live tree — another sign the copies have diverged.
- **`$ARGUMENTS` false positive — triage rule worth keeping.** The only hit in either tree is
  `autonomous-ai-agents/claude-code/SKILL.md`, where `$ARGUMENTS` appears *as documentation about* Claude Code's
  slash-command substitution, inside a fenced example. A harness checker flags it as "not substituted"; the correct
  disposition is **keep**, because the literal is instructional content, not an intended placeholder. When any
  loader-rule scanner reports a hit, first ask whether the token is *used* or *documented*.
- **Near-threshold watch item:** `creative/design-taste-frontend/SKILL.md` measures 89,713 chars in the live tree —
  roughly 90% of Hermes' ~100K-char `skill_view` budget (and lower still on models under ~167K context). It is not a
  violation today; it becomes silent instruction loss with one more expansion. Splitting it into body + references/
  before the next growth round is cheaper than debugging "the skill loaded but the agent ignored it".
- **22 bodies exceed their 500-line advisory.** Not a Hermes failure mode (Hermes delivers long bodies fine up to the
  budget), but every one of them pays load cost on every invocation. Progressive disclosure says the detail belongs in
  `references/`; treat this as a queued refactor, not a defect list.

## What this changes about how skills get written here

1. Trigger-first descriptions are a **delivery** requirement (chars 0–57), not style: after ~59 chars Hermes has already cut it.
2. A skill that "loads but does nothing" is a size bug before it is a model bug — check body char count against the ~95K safe ceiling, then whether files sit in one of the four listed dirs (`HM-LINKED-LAYOUT`).
3. Which copy loaded matters more than which file you edited: precedence is project > user > create_dir > external_dirs, and trust gates all project skills at once.
4. For multi-harness corpora, author to Codex's strictness (no tabs in frontmatter, no BOM, unique keys, description present) — it costs nothing on lenient loaders and prevents silent drops.
5. Cross-checking an independently-measured external profile against your own tree is a cheap truth layer: this pass confirmed four of our conventions and produced one false positive with a reusable triage rule.
