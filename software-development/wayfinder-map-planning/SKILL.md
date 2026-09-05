---
name: wayfinder-map-planning
description: "Plan multi-session work as a map of decision tickets."
version: v0.9.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, multi-session, tickets]
    related_skills: [grilling-interview, mattpocock-to-tickets]
---


<!-- source: mattpocock/skills (engineering/wayfinder), ported 2026-09-05, adapted to gh CLI / local markdown trackers -->
## When to Use

- An effort too big for one agent session
- "Chart the map" / "work through the map"

## What This Skill Does

- **GitHub repo**: map = an issue labelled `wayfinder:map`; tickets = child issues (linked via "Development" section or body links); blocking = native GitHub dependencies where available, else a `Blocked by:` line in the ticket body; claim = assign to yourself (`gh issue edit N --add-assignee <you>`


# Wayfinder Map Planning

A loose idea has arrived, too big for one session and wrapped in fog: the way from here to the **destination** isn't visible yet. Wayfinding is about finding that way, not charging at the destination. Chart it as a **shared map**, then work its **decision tickets** (questions whose resolution is a decision, not slices of build) one at a time until the route is clear.

The destination varies per effort — naming it is the first act: it shapes every ticket. It might be a spec to hand off, a decision to lock before planning starts, or an in-place change like a data-structure migration. The map is domain-agnostic.

## Plan, don't do
Wayfinder is **planning** by default: each ticket resolves a decision; the map is done when nothing remains to decide before someone goes and does the thing. The pull to just execute work is usually the signal you've reached the edge of the map — hand off instead. An effort can override this in its Notes, carrying execution into the map itself.

## Refer by name
Every map and ticket has a **name** (its title). In everything the human reads, refer by that name, never a bare id/number/slug. A wall of `#42 #43 #44` is illegible; names read at a glance. The id rides *inside* the link wrapped in the name.

## Tracker choice
- **GitHub repo**: map = an issue labelled `wayfinder:map`; tickets = child issues (linked via "Development" section or body links); blocking = native GitHub dependencies where available, else a `Blocked by:` line in the ticket body; claim = assign to yourself (`gh issue edit N --add-assignee <you>`).
- **No tracker / local project**: map file `.wayfinder/map.md` + one file per ticket under `.wayfinder/tickets/`; blocking via frontmatter `blocked_by: [ids]`; claim via frontmatter `claimed_by`.

## The Map body (index, not store)
```markdown
## Destination
<what reaching the end looks like — 1-2 lines; every session orients to it first>

## Notes
<domain; skills each session should consult; standing preferences for this effort>

## Decisions so far
<!-- one line per closed ticket: gist + link. Detail lives in the ticket, never restated here -->
- [<closed ticket title>](link): <one-line gist of the answer>

## Not yet specified
<!-- fog of war: in-scope decisions you can't ticket yet; graduates as frontier advances -->

## Out of scope
<!-- work ruled beyond the destination; closed, never graduates -->
```

### Tickets
Each ticket's body is one **Question**, sized to fit a single agent session. Carry a type label — `research`, `prototype`, `grilling`, or `task`:
- **Research** (agent-alone): surface a fact from docs/APIs/knowledge bases that a decision waits on → use the research skill/subagent; capture findings as an asset linked from the ticket, not pasted in.
- **Prototype** (with human): raise discussion fidelity with a cheap concrete artifact to react to → prototype skill. Use when "how should it look/behave" is the key question.
- **Grilling** (with human): conversation — the default case → grilling-interview + domain-modeling skills. A HITL ticket only resolves through live exchange; never answer its own questions.
- **Task**: manual work that must happen *before a decision* can be made (sign up for a service, provision access, move data so its shape is visible). The one type that does rather than decides; it earns its place by unblocking a decision. Record what was done + resulting facts (URLs, row counts) later tickets depend on.

A session **claims** a ticket first, before any work (assignee = claim), so concurrent sessions skip it. A ticket is **unblocked** when everything blocking it is closed; the **frontier** = open, unblocked, unclaimed children — the edge of the known.

## Fog of war
The map is deliberately incomplete: don't chart what you can't yet see. Resolving a ticket clears fog ahead of it, graduating whatever's now specifiable into fresh tickets one at a time. **Fog or ticket?** The test is whether you can state the question *precisely now*, not whether you can answer it now. Sharp-but-blocked → ticket; unstateable → Not yet specified (coarser than a ticket; one patch may graduate into several, or none).

Out of scope: work beyond the destination — its own section, never graduates, returns only if the destination is redrawn as a fresh effort. If an existing ticket turns out to sit past the destination, close it and leave one line in Out of scope (gist + why), linking the closed ticket; keep Decisions so far for the route actually walked.

## Invocation
**Never resolve more than one ticket per session** (exception: research tickets).

### Chart the map (user brings a loose idea)
1. **Name the destination.** Grill to pin down what this map is finding its way to — it fixes scope, so settle first.
2. **Map the frontier.** Grill again, breadth-first across the whole space rather than deep on one thread. If no fog surfaces (journey fits one session), you don't need a map — stop and say so.
3. **Create the map**: Destination + Notes filled, Decisions-so-far empty, fog sketched into Not yet specified.
4. **Create tickets** you can specify now; wire blocking edges in a second pass (ids must exist first). Everything unstateable stays in the fog.
5. **Fire research subagents** for each `research` ticket, in parallel; capture findings as linked assets with a context pointer from the ticket.
6. Stop: charting is one session's work; it hand-resolves nothing.

### Work through the map (user brings a map)
1. Load the map (low-res view, not every ticket body).
2. Choose the ticket — user-named or first frontier in order. **Claim it before any work.**
3. Resolve it: zoom into related/closed tickets on demand; consult whatever skills Notes names; when in doubt, grill + domain-model.
4. Record resolution: answer as a comment (or file section), close the ticket, append one line to Decisions so far.
5. Add newly-surfaced tickets (create-then-wire); graduate fog the answer made specifiable, clearing each graduated patch from Not yet specified; rule out-of-scope anything past the destination; update or delete invalidated tickets.

Expect concurrent sessions editing unblocked tickets in parallel — re-read tracker state before writing.
