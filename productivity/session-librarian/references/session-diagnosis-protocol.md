---
description: "Diagnose a bad agent session from its transcript on disk: intake, context-safe reading, seven analyst dimensions, cited report; Claude Code JSONL token double-count verified"
source_repo: obra/superpowers (MIT), skills/diagnosing-superpowers
tested_version: Claude Code transcript JSONL on Windows (3,419-line, 8.2 MB real session); scripts/transcript_stats.py was run on it. The protocol itself is source-read from upstream
verified_date: "2026-10-05"
---

# Diagnosing a bad session from its transcript

Use when the user asks why a session went wrong: repeated work, a plan that was ignored, "it took too long", "why was it
so expensive", a skill that never fired. `session-librarian` finds and tidies sessions; this is the next step, reading one
and reporting what happened with evidence.

## The rule everything else hangs on

**Every finding cites `path:line`, and every number comes from the transcript or a command you ran.** A finding with no
citation is dropped. A token price, a duration or a count recalled from memory is invented.

You report; you do not diagnose the tool that was in use. "The skill is badly written" is a conclusion the maintainer draws
from your evidence, not something the report asserts. If the user presses for a fix, point at the evidence and stop.

## Procedure

1. **Intake before analysis.** Ask one question at a time until you can write a problem statement: which session(s), the
   turn range if known, what was expected, what happened, and the observable that matters (wall-clock, tokens, a repeated
   action, one specific step). "It took too long" is a complaint, not a statement. If the user is away, write the questions
   and stop; a statement you reconstructed for them is not an answer. A request already scoped to one event is itself the
   statement.
2. **Locate.** Resolve the session to an absolute path. Confirm a past session by quoting its first prompt and timestamp,
   not by recency, and list the candidates you rejected. List subagent transcripts too. Keep a case file in the scratchpad
   holding: the paths, the field meanings you observed, rejected candidates, and anything unresolved. Later readers use it
   instead of repeating discovery.
3. **Triage.** Read the region around the reported problem yourself first. Then, if the transcript is long, give one
   analyst subagent one dimension each (below), the case file path, and a return format of
   `finding / evidence path:line "quote ≤200 chars" / turns / confidence` plus a `Checked:` line. Pass absolute paths: a
   subagent's "current session" is its own. Discard any finding with no `path:line`.
4. **Report** in a fixed order: verdict, problem statement, findings by dimension with citations, coverage (what you did
   and did not read), open questions.
5. **Optional, only on request:** search existing issues, draft one, or build a scrubbed bundle. Show the exact text and
   get approval before anything is posted. A bundle is the user's session data repackaged, so never build one unprompted
   and tell the user scrubbing can miss things.

## Context safety (read this before opening any transcript)

One JSONL record can exceed a megabyte; printing one whole can overflow your own context. Measured on a real 3,419-line
Claude Code session: 8.2 MB total, and line 25 alone was 191,254 characters.

- Measure first: `wc -lc F` and a long-line check (`awk '{ if (length($0) > 100000) print NR, length($0) }' F`).
- Count and locate before reading: record types, line numbers of matches, never `cat` or content `grep`.
- Extract small fields from specific lines and cut them (`cut -c1-500`). Anything over 500 characters means tighten the slice.
- Read-only: never modify, move or delete a session file.
- `jq` is not installed on every machine (absent here: `jq: command not found`, which a `2>/dev/null` hides, leaving an
  empty result that looks like "no records"). Use
  [`scripts/transcript_stats.py`](../scripts/transcript_stats.py), which streams the file and bounds every printed field.

## Claude Code transcript facts (observed, not assumed)

Do not infer one harness's format from another's; establish record meanings from the file in front of you. For Claude Code
JSONL under `~/.claude/projects/<project>/<session-id>.jsonl`:

- Record `type` values seen: `assistant`, `user`, `attachment`, `system`, `queue-operation`, `file-history-*`, `last-prompt`,
  `custom-title`, `agent-name`, `cost-state`. Only some are conversation turns; `user` records also carry tool results,
  so a `user` record is not necessarily a human prompt. Hook output and system reminders arrive as attachments or
  injected text.
- **One API message is written as several `assistant` records, one per content block** (thinking, text, each tool_use),
  and every one of them carries the same `message.id` and the same `usage` object. In the measured session: 1,179
  assistant records, 512 distinct message ids, and in all 424 multi-record ids `output_tokens` was identical across
  records. Summing usage over records inflated output tokens 2.4x (1,111,773 against 454,169 counted once per id) and cache
  reads 2.3x (619 M against 264 M). **Count usage once per `message.id`.**
- Cache reads dominate: 264 M cache-read tokens against 1,024 plain input tokens in that session. A "tokens used" total
  that adds the counters together mostly measures the context being re-read each turn, so report the counters
  separately.
- A tool call is a `tool_use` block (`name`, `input`); its result is a `tool_result` block in a later `user` record with
  the same `tool_use_id`. Match them by id, not by adjacency.
- Subagent transcripts are separate files; in a subagent, "user" is the parent agent, not the human.

## The seven analyst dimensions

All seven always run; the complaint decides what you read first and what leads the verdict.

| Dimension | What it checks |
|---|---|
| Skill timeline | which skills loaded, when, and whether the one the user expected ever fired |
| Plan adherence | steps in the plan against steps done; read the compaction lines first, plans get lost there |
| Repeated work | tool calls grouped by `(tool, key)` over a threshold; a re-read after an edit is not a finding, a re-read after a compaction is attributed to the compaction |
| Stumbles | errors, retries, reverted edits, approaches abandoned |
| Quality evidence | whether claimed results were verified in the transcript (a test run, a diff read) |
| Request conflicts | human instructions that contradict each other or a later action |
| Cost and time | tokens and wall-clock per turn and per subagent, gaps over ten minutes, ten largest tool results, compactions |

Repeated-work thresholds that upstream uses: reads and searches 3, edits 2, shell commands 2 (exempt status checks and test
runs such as `git status`, `ls`, test runners), subagent dispatches 2 with the same description.

| Complaint | Read first, lead with |
|---|---|
| "It took too long" | cost-and-time, stumbles |
| "Why this extra work?" | repeated-work, plan-adherence |
| "Why so expensive?" | cost-and-time |
| "It ignored the plan" | plan-adherence, compaction lines first |
| "Skill X never fired" | skill-timeline |

## Running the stats script

```bash
python productivity/session-librarian/scripts/transcript_stats.py SESSION.jsonl --repeat 3
```

It prints file size and lines over 100,000 characters, record-type counts, token totals both ways (once per message id,
and the naive sum, so the inflation is visible), the five largest tool results by line, gaps over ten minutes, and
repeated tool calls. On the measured session it flagged a 191 KB line, 2 idle gaps (13 min and 1 h 24 min), and an Edit to
one file repeated 4 times. It never prints a record whole.

## Limits

- The stats script covers cost, gaps, size and repeats. Skill timeline, plan adherence and quality evidence need a reader
  (you or a subagent) following the case file; the script does not attempt them.
- "Last record per `message.id` wins" is used for usage; in the measured session the copies were identical, so which one
  wins did not matter there. Check again on a transcript from a different Claude Code version.
- Timestamps are taken from each record's `timestamp`; a gap between two records says time passed, not why (idle, waiting for the
  user, or a long tool). Say which only when the records show it.
- The analyst prompts, scrub/audit prompts and report templates upstream (`obra/superpowers` `skills/diagnosing-superpowers/`)
  were read, not run, and are summarised above rather than copied.
