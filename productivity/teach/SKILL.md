---
name: teach
description: "Teach a topic across sessions via mission and lessons."
version: 1.0.0
author: "Matt Pocock (mattpocock/skills, MIT) + Hermes Agent"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [teaching, learning, multi-session, mission, lessons, zone-of-proximal-development]
    related_skills: [claude-design]
---

# Teach

## What This Skill Does

Runs a **stateful, multi-session teaching workspace** in the current directory. The user's learning state lives on disk as files — `MISSION.md` (why they're learning), `RESOURCES.md` (trusted sources + communities), numbered `learning-records/0NNN-slug.md` (teaching-equivalent ADRs that calculate their zone of proximal development), self-contained HTML lessons in `lessons/`, reusable components in `assets/`, and a scratchpad `NOTES.md`. Each session: read the state, teach one tightly-scoped thing tied to the mission at just-enough difficulty, capture what was learned as a record.

## When to Use

- The user says "teach me X" / "I want to learn X over time" — anything they intend to study across multiple sessions (a language, an instrument, a domain).
- NOT for one-shot explanations or quick lookups — those are normal conversation. This skill is the multi-session contract: state on disk, mission-grounded lessons, retrieval-practice design.

## Teaching Workspace Layout

Treat the current directory as the workspace. State files (formats in `references/`):

| File | Purpose |
|---|---|
| [MISSION.md](./references/MISSION-FORMAT.md) | The *reason* for learning; grounds every teaching decision. One mission per workspace — two unrelated topics = two workspaces. Push back on vagueness ("get fitter" → "run a half marathon by October"). |
| [RESOURCES.md](./references/RESOURCES-FORMAT.md) | High-trust knowledge sources + wisdom communities, each annotated with *use for*. Never teach from parametric guesses before this is populated. |
| `learning-records/0NNN-slug.md` ([format](./references/LEARNING-RECORD-FORMAT.md)) | Non-obvious lessons / established prior knowledge; can be one paragraph. Used to compute the zone of proximal development next session. Support `superseded by LR-NNNN`. |
| [GLOSSARY.md](./references/GLOSSARY-FORMAT.md) (optional) | Canonical terminology, added only once the user demonstrably understands a term. Adhere to it in every lesson. |
| `lessons/0NNN-slug.html` | One self-contained HTML file per lesson — beautiful (think Tufte), short enough for working memory, one tangible win, linked primary source, links to other lessons/references via anchors. Open the file for the user when possible. |
| `assets/*` | Reusable components (shared stylesheet first). Read before authoring; reuse is the default — never inline what a future lesson would duplicate. |
| NOTES.md | User preferences on how they want to be taught. |

## Philosophy: knowledge, skills, wisdom

- **Knowledge** from high-trust resources (RESOURCES.md); lessons are littered with citations. For acquisition, difficulty is the *enemy* — it eats working memory.
- **Skills** through interactive practice with the tightest possible feedback loop (quizzes, in-browser tasks, real-world step lists). Here difficulty is the *tool*: retrieval practice, spacing, interleaving build storage strength, not fluency illusions. Quiz answers should be equal-length so formatting gives no clue.
- **Wisdom** from communities: when a question needs it, attempt an answer but delegate to a high-reputation community (forum/subreddit/class/local group). Respect the user if they decline joining one.

## Session Protocol

1. Read MISSION.md, learning records, NOTES.md. No mission yet → interview the user on *why* before teaching anything; confirm with them before changing an existing mission (and record the change as a learning record).
2. Pick the lesson: what the user named if they named something; otherwise the most relevant thing inside their zone of proximal development per the records.
3. Teach knowledge first, then practice via feedback loop. Keep it completable quickly — one tangible win tied to the mission.
4. Write/update a learning record for anything non-obvious learned or established. Update GLOSSARY only when understanding is demonstrated.
5. End by pointing at the next step (next lesson theme or community exercise).

## Assets & Lessons Craft

Lessons are built from `assets/` components; a shared stylesheet is the first component every workspace earns so lessons look like one consistent course. Each lesson recommends exactly one primary source to read/watch and reminds the user they can ask follow-up questions — the agent is their teacher for anything unclear.
