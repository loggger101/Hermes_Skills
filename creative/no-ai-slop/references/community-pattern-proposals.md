# no-ai-slop: community pattern proposals & measured behavior (mined 2026-09-15)

Source: https://github.com/petergyang/no-ai-slop — `main` @ `000650b` (= v1.0.6, the version this skill ports verbatim). Everything below comes from **open/unmerged** PRs and issues as of 2026-09-15: it is NOT in the ported SKILL.md (which stays a clean upstream snapshot), but these are ready-to-apply refinements. If any PR merges upstream, re-port that hunk into SKILL.md instead of keeping this doc as the source of truth for it.

## 1. Fact-binding rule for technical drafts (PR #24 — highest-value item)

The skill optimizes for compression; **compression is where factual links break**. Failure mode: two adjacent paragraphs, each correct and about a different subject, get merged during tightening — a measurement belonging to subject A now explains subject B. Nothing misspelled, no number changed, the claim is fabricated, and it survives re-readings (happened on a real technical email; an outside reviewer caught it). The existing rules don't prevent this: "keep the user's meaning" guards against *adding* claims, not *rebinding* them.

Rules when the draft contains numbers, units, named entities, attributions, or causal claims:
- **Never merge, split, or reorder across a subject boundary** (any point where the thing described changes: material, dataset, tool, version, run, person) without re-checking each fact against the original.
- **Numbers, units, entity names, and attributions are frozen byte-identical.** Rounding a figure, dropping a unit, or replacing a specific name with a general one is a content change, not style.
- **Verify subject-fact binding as a separate pass**, reading edited draft against the original — not from memory of it. For every claim carrying a number/name: still attached to the same subject?
- **Do not remove hedges that carry technical meaning.** "Within this model", "at one bar", "computed rather than measured" look like throat-clearing but are load-bearing. Cut hedges expressing reluctance; keep hedges stating basis, condition, or method limits.
- **Don't let the synonym-cycling ban flatten two different quantities into one word** — if the draft uses two terms because they denote two things, keep both.
- **If tightening would require knowing whether something is true, stop and ask.** Joining two facts is a technical judgment, not prose editing.
- In "What changed", list separately every touched sentence containing a number/unit/name/attribution — so the writer re-verifies exactly those and nothing else (without the list they'd have to re-verify everything, which means they won't).

Companion eval block (PR #24): 6 checks, answered only when technical content is present; **a fail here outranks every other check on the page**. This maps directly onto this repo's own audit protocol (never build findings from stale snapshots — verify against live source); it is the writing-side version of that rule.

## 2. Signs you over-edited (PR #21)

The skill's differentiator is removing slop without flattening voice, but nothing concrete to check against made "would the writer recognize their own voice?" default to yes. Nine tells — any one means flattened; **the fix is to restore the original line, not write a better version of it**:
- Every paragraph came out about the same length.
- An unusual word became the common synonym, with no rule behind the swap.
- A joke is gone, or explained.
- A hedge became an assertion (draft now claims more than the writer knows).
- A three-sentence aside became a clause.
- Much shorter and nothing factual was cut — only character.
- You changed a line you cannot name a pattern for. *(Also added as eval check: "Can you name a pattern from this skill for every line you changed?")*
- Reorganized without saying why in What changed.
- Read aloud, it no longer sounds like the person who wrote it.

Plus an over-confidence guard (eval): *the edited draft must be no more confident than the original anywhere.*

## 3. New patterns from PR #21 (four + two lists)

- **Manufactured enthusiasm.** "Great question", "Absolutely", "Amazing", "Fantastic", "Perfect", stacked exclamation points. Praise the reader did not ask for reads as filler; one real-energy `!` is fine, a second in the same paragraph is not.
- **Hedging stacks.** "It might be possible that" + "in some cases it could potentially" + "generally speaking". One qualifier is honesty and stays; three stacked on one claim is slop. *Thin to one hedge rather than removing all of them, or the edit ends up more confident than the writer.* ("It might be possible that some users could potentially prefer this" → "some users may prefer this.")
- **Assistant sign-offs.** "I hope this helps", "Let me know if you have any questions", "Feel free to reach out", "Happy to help", "Does that make sense?" — survive when a draft is pasted out of a chat window. Delete; the draft ends at its last real sentence.
- **List ceremony.** "First, Second, Third, Finally" on an already-numbered list; every bullet forced into identical grammatical shape. Cut ordinals, vary length unless parallel carries meaning — but keep a genuine sequence as a list (a five-step procedure should not be flattened into prose to prove a point).
- **Redundant modifiers** (new cut-list): very unique, completely finished, absolutely essential, extremely important, actual fact, end result, future plans, past history, added bonus, close proximity. Cut the modifier, keep the noun.
- **Jargon replacement map** — delete-and-leave-a-hole is its own failure: leverage/utilize → use, facilitate → help, streamline → simplify, empower → let, elevate/supercharge → improve, robust → solid or reliable.
- Worked pair for conditional adverbs (the "keep when they carry emphasis/uncertainty" rule): *"Just two people showed up"* keeps **just**; *"I just wanted to check in"* does not.

## 4. Terms-of-art split of the ban list (PR #51)

The absolute ban list holds nine words that also name real things — a draft about any of them loses the correct word and the model reaches for a worse synonym: harness → test/wiring harness; realm → Kerberos/HTTP auth realm; beacon → BLE beacon, 802.11 beacon frame; robust → robust regression / standard errors; leverage → financial leverage ratio; streamline → streamline flow (aerodynamics); elevate → elevated privileges, "elevate the limb"; foster → foster parent/care; facilitate → a facilitator facilitates a session. Since the skill installs into coding agents via `npx skills`, technical drafts are a large share of where it runs — exactly where this misfires.

Fix shape (uses the file's own conditional mechanism, no new one): 17 words stay absolute ("none is the right word in ordinary prose"); the nine move to **"banned in the AI sense, kept as terms of art"** — cut when reaching for weight the sentence hasn't earned; keep when naming the actual thing; *do not reach for a worse synonym to avoid the list*. Generalizable lesson: **an absolute ban list is unsafe in any skill that will edit technical text** — every word on it must survive the "is this also a term of art?" test, or use conditional phrasing.

## 5. Definition by negation (PR #48) + verdict sentences (PR #39)

- Binary contrasts currently catch "It's not X, it's Y" in *prose*; formatting-slop catches heading *form*. Neither covers a label that **defines by negation**: "The trend, not the pair" for a section comparing a six-month series against one month-pair — read cold it says nothing because "the pair" only resolves from the paragraph above. Extension: applies to headings, bullet labels, table captions, slide titles. **Cold-read test:** cover the surrounding text and read the label alone; if it doesn't say what the section contains, rewrite ("The trend, not the pair" → "Six-month trend.").
- **Verdict sentences** (PR #39): blunt "That is…" / "This is…" after the facts — sounds like a model announcing its conclusion. Cut and let the facts end it.

## 6. Internal contradiction found in upstream's own rules (PR #38)

Editing principles say *keep* fragments when clear and characteristic of the writer; Patterns to cut says dramatic fragmentation → "use complete sentences". An agent reading the patterns list literally deletes exactly what the principles protect — opposite instructions from one file, no precedence stated. Proposed fix: narrow the fragment rule to **stacked** fragments used for rhythm/drama (repeated shapes are already covered by Robotic rhythm), and state once at the top of Patterns that **principles take precedence where they conflict**. Generalizable skill-authoring lesson: when a rule set mixes conditional principles with absolute pattern bans, declare which wins explicitly — otherwise the model follows whichever list it read last.

## 7. Measured behavior (issue #45 — same-model replay benchmark)

Independent maintainer of ZeroSlop ran no-ai-slop in a controlled replay: 18 drafts, GPT-5.4 high reasoning, batches of three, each tool with pinned instructions; originals scored 76.3 on the writing metric (lower = better). Results for no-ai-slop:

| Metric | Value |
|---|---|
| Mean writing score | **28.4** (originals 76.3) |
| Important details kept | **17/18** — one draft lost something the fact check considered important |
| Average length change | **-13.7%** |

Ranked second of four tools replayed. The 17/18 is exactly the failure class PR #24's fact-binding rule targets (compression silently rebinding a detail), and -13.7% quantifies typical compression — expect roughly that much shortening, which makes "restore the original line" over-edit fixes matter more than they sound.

## 8. Language-specific pattern files (PR #50 Korean, PR #17 Chinese)

Anti-slop lists do NOT transfer across languages — each language has its own AI tells, and both open PRs add per-language reference files instead of bloating the main skill:
- **Korean** (`references/korean.md`, PR #50): 번역투 (translated-English stiffness), 이중 피동 (double passive), 명사화 (unnecessary nominalization), 사물존칭 (honorifics applied to objects — a tell no English list has), 빈 수식어 (empty modifiers). The build script gains an `if references.is_dir(): copytree(...)` so the file ships in the package.
- **Chinese** (PR #17): empty officialese ("高度重视", "持续推进", "取得积极成效"), framework padding without content ("以X为引领、以Y为抓手..."), four-character phrase stacks, public-account hook templates ("很多人不知道的是...").

Generalizable lesson for any multilingual skill: keep the universal rules in SKILL.md and put language-specific pattern lists in `references/<lang>.md` with a one-line trigger in the main file — the universal patterns (binary contrasts, colon reveals) hold cross-lingually, but word-level bans and honorific/grammar tells are per-language.

## 9. Ecosystem notes

- Japanese adaptation: [53able/no-ai-slop-ja](https://github.com/53able/no-ai-slop-ja) — redesigned around Japanese grammar/honorifics, credits upstream (issue #46). ZeroSlop ([manavmishra/ZeroSlop](https://github.com/manavmishra/ZeroSlop)) cites no-ai-slop as prior work.
- Claude Code plugin support is PR #52 (open at mine time): `marketplace.json` + `plugin.json`, install via `/plugin marketplace add petergyang/no-ai-slop`. Works WITHOUT an explicit skills array because their layout is exactly what CC's native one-level discovery handles (`skills/<name>/SKILL.md`); this repo needs the explicit array for its `<category>/<skill>/` two-level paths — corroborates the round-18 finding in cross-harness-skill-porting.md. Namespaced invocation caveat: plugin-installed skills invoke as `/no-ai-slop:no-ai-slop`, not bare `/no-ai-slop`.
