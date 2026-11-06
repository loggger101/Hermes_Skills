# oh-my-hermes (rlaope/oh-my-hermes) catalog-level review — sampled 2026-11-05, closes row 79's "~100 not individually reviewed"

Enumeration: **158 SKILL.md files** (more than the ~100 banked), plus `docs/ADDING-A-SKILL.md` authoring
guide. Strategy declared honestly as sampling, not full review: read whole - skill-health, instinct-ledger;
rule-level greps + core sections - rules-distill, adversarial-consensus; names clustered against our own
catalog for the rest. Verdict: a Hermes-native meta-catalog with real governance depth (not prompt bulk);
**keep upstream**, several rules worth adopting by statement below. Name-clash families (`omh-failure-signal-audit`,
`omh-codebase-onboarding`, `omh-context-budget-review`, `omh-live-incident-response`, threat-model, systematic-review...)
mirror skills this repo already holds - cross-harness projections of the same genres, no port needed. The
`ulw-*` (9) and `jev-*` families are their orchestration/workflow suites; untouched beyond name-level triage.

## Rules worth adopting (each stated where it lands for us)

- **Usage counts are never a health signal.** A rarely-used skill is not an unhealthy one, and no health
  card may recommend removing/archiving/retiring on low usage - drift signals instead: managed copy changed
  in place, unfixed authoring findings, update waiting on its hub. (Our `skill-library-audits` should read this
  as a standing prohibition against usage-based pruning.)
- **Empty ledger is unknown, not clean.** Hermes' curator ledger (`skills/.curator_ledger.jsonl`, or
  `hermes curator ledger --skill <name>`) can be disabled via config; an empty result means *unobserved*, and
  the default shows only the 20 newest entries. Absence-of-record claims must state those conditions - same
  family as our exclusions-before-negatives rule, applied to skill provenance.
- **Advisory-silence semantics:** `skill_manage` lint_warnings are advisory, never proof a skill works; and
  only *some* writes return them (`edit` never does) - so a write without warnings is NOT a clean lint. Directly
  applicable here: treat missing tool feedback as unknown, not pass.
- **Candidate stores vs live stores.** Learning pipeline separation: instincts are atomic (one trigger/action/
  scope + confidence + evidence refs), promotion happens ONLY through reviewed store routes (`memory_candidate`,
  `skill_update_candidate`), never by the tracker writing host memory or skills itself; project-vs-global scopes
  kept separate; exports carry redaction and trust-gap review. Formalizes exactly how this repo banks lessons
  (ledger/references first, skill/memory writes only on promotion).
- **No double-counting of native writes:** an instinct matching a curator-ledger entry that no store route
  accounts for is reported as `unreviewed_native_write` - and never counted as repeated evidence for itself.
- **Zero objections = roster defect.** In adversarial review, "agreement reached by perspectives that read each
  other is not review - it is convergence"; a round producing no objections means an angle was missing: name the
  missing perspective, add or replace before claiming consensus. (Lands on `multi-agent-deliberation` and any
  grill/review flow.)
## Process lesson banked this round (byte-level markdown editing on CRLF files)

Insert AFTER the full line terminator (`split at j+1` where `j = find("\n")`), never AT `j`: inserting at `j` orphans
the preceding CR and yields lone-CR + bare-LF pairs. This bug was introduced three rounds running (r298, twice in r300)
despite being banked as a lesson - the scan-after-edit step caught all three, but the fix is to change the splice point,
not to rely on catching it. After ANY byte insertion assert BOTH `lone-CR == 0` and `bare-LF == 0` (the file's declared
convention), not just lone-CR - r300 showed a bare LF can hide in the stamped line itself. Ledger row-stamping pattern
that finally worked: locate row start marker, find first LF after it, insert at j+1 with CRLF-prefixed text; verify by
row-index containment (start < pos < next-row-start) when rows are long and visually ambiguous - a stamp landing on the
"wrong" looking fragment may be right if that IS the target row's tail.

- **Mechanical vs judgement classification before wording** any distilled rule candidate: machine-findable-from-
  text alone vs requiring human judgement - routes review effort correctly; distill principles from large ecosystems,
  never wholesale copy (converges with our intake doctrine).
- **Voice ownership across harnesses:** the host persona owns reply language/tone/speech-level; an imported skill
  pack shapes structure and content only, and its internal record terms stay in records/tool-calls, never in the
  sentence the user reads. Cross-references `cross-harness-skill-porting`.
