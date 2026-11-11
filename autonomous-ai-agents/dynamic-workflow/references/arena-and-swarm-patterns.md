# Arena & swarm: pstack's multi-agent orchestration contracts (verified from backnotprop/pstack @ main, 2026-11-11)

Source: `backnotprop/pstack` → `skills/arena/SKILL.md` and `skills/swarm/SKILL.md`, read in full from
shipped source (MIT, Lauren Tan). These are the two multi-agent skills in pstack; our corpus held only a
passing "swarm" mention — the mechanics below were unmined until now. Nothing executed here (they drive a
host's subagent tool); this is contract/pattern knowledge read from text that is unusually precise about
failure handling, which is what makes it portable.

## Arena — N candidates, cross-family judge, pick base, GRAFT the losers

Phases: Frame → Fan out → Cross-judge → Pick → Graft → Verify (todolist per phase before launching). The
mechanics that are genuinely new relative to our fan-out patterns (`dynamic-workflow`,
`dispatching-parallel-agents`):

1. **Rubric asymmetry.** At frame time derive 3–6 concrete gradeable criteria — and give them ONLY to the
   picker/judge: "Candidates only see the task." Grading against a rubric the generators optimized toward
   is grading their gaming, not their work. (Our review flows show judges rubrics; hiding them from makers
   is the missing half.)
2. **Cross-family judge.** The single readonly judge must never run on the parent's model family ("a Claude
   parent gets grok-…fast; any other parent gets claude-opus first"), with an explicit degradation ladder
   when a slug is rejected (same-model nearest level/speed → next pool entry → skip judge and say so). The
   bias theory is stated by construction, not hoped for.
3. **Pick rule.** Read every candidate end to end; score criterion-by-criterion "not on holistic feel"; base
   = what a future maintainer can extend most easily WITHOUT breaking invariants; ties break toward cleaner
   boundary / smaller API.
4. **Graft, don't merge.** Walk each loser once for the one-or-two things worth porting ("usually one or two
   per candidate, not most of it"), folded by hand so the result stays coherent under ONE mental model —
   mechanical pasting is called out. Two diagnostics worth stealing: candidates converging on one shape =
   strong agreement (ship consensus, no graft); wild divergence = **the frame was underspecified — reframe
   and re-run rather than averaging the divergence**. Divergence is a signal about your prompt, not a menu.
5. **Synthesis note as required output**: names base+why, judge verdict or explicit skip, each graft with
   source candidate, what was rejected and why, dropouts, verification result — an audit trail for a
   generated artifact, same spirit as our handoff docs but for parallel generation.

## Swarm — coverage/race fan-out whose results are CHECKABLE before aggregation

Phases: Frame → Fan out → Aggregate → Report. The load-bearing contracts:

1. **Race semantics declared BEFORE spawning**: partition slices, race identical briefs, or mix — and a
   race must name `first pass`, `rank all`, or `best-of` up front. Choosing the selection rule after seeing
   results is how parallel work becomes post-hoc cherry-picking.
2. **Measurement briefs carry their own verification**: when workers measure or verify commits, "each brief
   names the exact SHAs" and a measurement brief also names the method (sample count, what one sample is,
   order) — and the worker must record both in its result. Aggregation then DROPS any result that doesn't
   record the SHAs/method its brief named, respawns once; after a second miss it becomes an explicit **gap**,
   and "a gap does not count as a pass". Three-valued worker verdicts (result / gap / dropout) — the same
   holds/breaks/not-checked discipline r311 recorded for TLC rules, applied to fan-out aggregation. Silence
   is never green.
3. **Worker report protocol**: `PASS` / `ISSUES` / `BLOCKED` with evidence; a worker that can prove a defect
   lists EVERY issue it can prove, not only the first (kills one-find-then-stop behavior).
4. **Dropout handling defined at every phase** ("proceed with N-1 and note it") — partial results stay usable
   without pretending full coverage.
5. **Harness-mapping table as degradation ladder**: Cursor `Task` params (`subagent_type: generalPurpose`,
   `environment: cloud|local`, `cloud_base_branch`) map to Claude Code `Agent`, OpenCode `task`, Codex
   `spawn_agent`; parameters you don't have get DROPPED, brief and model kept; no subagent tool at all → run
   the workers yourself serially. Write orchestration against capabilities with named fallbacks, not one host's API.

## When to reach for which (their triggers, adopted)

Arena: "one attempt at a non-trivial artifact would lock in the wrong shape" — design/plan/prose where shape
matters and generation is cheap. Swarm: parallel COVERAGE or racing/measurement with verifiable done-ness.
Both open a per-phase todolist before launching anything, both require saying so when a phase degrades (judge
skipped, worker dropped, seat rejected) — the say-so rule is what keeps degraded runs honest.
