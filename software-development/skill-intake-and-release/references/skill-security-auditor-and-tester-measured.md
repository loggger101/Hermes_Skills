# skill-security-auditor + skill-tester (alirezarezvani/claude-skills) — measured 2026-11-05

Banked partial-mining targets from round-139 ("in case a later pass wants them"), now mined. Verdict:
**keep upstream, do not vendor** - the auditor is one 44 KB stdlib script worth *running*, its ideas are
worth *adopting*; neither skill's instructions port (paths assume their repo layout).

## What they are

- **skill-security-auditor**: static PASS/WARN/FAIL scanner for a skill dir or git URL. Four layers:
  code-exec risks in `.py/.sh/.js/.ts` files, prompt-injection patterns in `.md`, dependency supply-chain
  (typosquat dictionary, unpinned versions), filesystem structure (binaries, symlinks, boundary paths).
  `--strict` promotes any WARN to FAIL; `--json`; git-URL mode shells out to clone (`subprocess`).
- **skill-tester**: four-tool pipeline over their repo layout - `skill_validator.py` (structure/frontmatter/
  tier line-counts), `script_tester.py` (AST syntax, import analysis, timed execution vs expected_outputs/),
  `quality_scorer.py` (0-100 + letter grade + `improvement_roadmap`, `--minimum-score` gate), plus a separate
  security scorer. Verification loop rule worth stealing: apply the **top** roadmap item and re-run *all*
  tools - "never report a partial pass".

## Measured on this box (python 3.14, Windows; fixtures + our own tree)

- Clean skills PASS with zero findings (`systematic-debugging`, `build-systems-data`,
  `python-toolchain-notes`, `semgrep-rule-creator`).
- Planted fixture: `os.system` concat, bare `eval(input())`, "Ignore previous instructions" and
  "Send contents of ~/.ssh..." in SKILL.md -> **5 CRITICAL, verdict FAIL, exit 1 even without --strict**
  (their CI `$?` check is sound).
- **Waiver placement pitfall:** trailing same-line `# noqa: SEC-AUDITOR (reason)` suppresses; the comment on
  its OWN LINE above the flagged line does NOT. First test failed for exactly this reason - retest confirmed.
  Block form (`auditor:ignore-start/end`) documented as fail-closed ("an unclosed block suppresses nothing") -
  not exercised here, untested.
- **Deviation from their own table:** "Subprocess (safe) -> INFO" never fired; canonical
  `subprocess.run(["echo","x"], check=True)` produced zero findings of any severity, so the safe-subprocess
  inventory claim is absent in practice (regex gap or JSON-mode suppression).
- **Layer-split blind spot (by design, but load-bearing for intake):** code-execution patterns are scanned
  ONLY in script files; `.md` gets prompt-injection patterns only. `exec(base64.b64decode(...))` and
  `requests.post(url, data=key)` planted inside SKILL.md were NOT flagged as code risks (the same md line's
  exfil prose WAS caught by PROMPT-EXFIL). This repo embeds heavy example code in references/*.md - a PASS
  from this auditor over such skills says nothing about that layer. Read PASS as "script files clean + no
  injection phrases", never as "whole skill safe".

## Adoptable ideas (recorded, not vendored)

- **Fail-closed waivers** (unclosed ignore-block suppresses nothing; reason mandatory in the marker): same
  governance line this repo draws in `verification-culture/references/tiered-gates-and-waivers.md` - sloplint
  re-derives guards and rejects boilerplate, here an unclosed block protects by defaulting to ON. Two
  independent implementations of "waivers must be harder to abuse than findings are to fix".
- **Precedence declaration for conflicting standards**: skill-tester's scope note resolves its tier-minimum
  line-counts against the newer ~100-line authoring doctrine *explicitly* ("legacy skills measure here; new
  skills follow write-a-skill - do not pad"). Pattern: when a repo grows a stricter successor standard, name
  which binds for what population in the older artifact itself. Our analog risk: audit-enforced description
  caps vs imported upstream formats with extra keys (README already notes why those are left as shipped).

Upstream paths: `engineering/skills/skill-security-auditor/` and `.../skill-tester/` (also mirrored under
their `.codex/.gemini/.hermes/.vibe` harness dirs). Threat model reference (~10 KB) read at fetch, not fully
re-ported; license follows the catalog repo.
