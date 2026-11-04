---
description: "Agent-tool discipline distilled from morluto/rea (429k stars), whose skill pack is the most rigorous MCP contract available: capability-vs-instructions separation, summary-first analysis with retained evidence references, treating client-side truncation of a SUCCESSFUL result as incomplete rather than canonical, retry-once-only-if-safe semantics for dropped tool calls, no-repeat-without-changed-input, and observations vs inferences vs unknowns - plus verified artifact facts (PyInstaller CArchive layering, Bun --compile module graph, ESP32 0xE9 magic) and the absence-inference trap from scoped captures"
source_repo: morluto/rea at main, skill metadata version "60", 2026-11-04 - .agents/skills/reverse-engineer-anything/SKILL.md (37 KB) read in full; its references/*.md (~120 KB total: native-and-artifacts 49.7 KB, connection-and-recovery 19 KB, environments 15.5 KB, javascript-applications 15.4 KB, runtime-observation 11.9 KB, evidence-workflows 11.3 KB) characterised by structure only
tested_version: "SOURCE-READ. No REA/MCP server was installed or run here and no target was analysed - this is a contract/method extraction, not a tool verification. Deliberately NOT ported as a skill: the instructions name `open_binary`/`inspect_artifact`-style tools and engines (Ghidra, IDA, JADX, Binwalk) that do not exist in this environment"
verified_date: "2026-11-04"
---

# Tool-capability and evidence discipline (rea's MCP contract)

REA is a reverse-engineering pack, but the part worth keeping here has nothing to do with RE — it is **how an agent should behave
around tools whose availability, output size and failure modes are uncertain**. Every rule below is quoted or condensed from its
skill text; none was executed. Read this before writing any skill that depends on an MCP server or a large-output tool.

## Capability is not instructions

> "Installing this skill supplies instructions; it does not register the MCP server, install analysis engines, or add tools to an
> already-running agent."

And the corollary that catches everyone: *"a skill installed from repository main may describe capabilities absent from an older npm
release"* — so **use the connected server's actual tool list and input schemas**, never the schema your skill text assumes. Our own
skills that reference MCP tools should say this once rather than let a stale body assert tools that aren't there.

Related anti-pattern it forbids: *"Do not run diagnostics or setup before every investigation"* — if tools are present and registration
isn't known-stale, go straight at the target. Diagnosis is for an **observed** blocker, and different blockers (client approval policy vs
shell PATH vs registration vs engine availability) have *different* remedies: "avoid repeating setup for all of them". It also refuses to
install prerequisites as a repair: *"REA setup never installs or upgrades Node.js, npm, Homebrew, Java, Ghidra, IDA, JADX, Kuna, Binwalk,
or Unblob… do not install unrelated software to repair MCP registration."* Repair the layer you observed broken; never widen scope to make
an error go away.

## Retry semantics for tool calls (the part our guardrails lack)

- Connection drops: *"retry that call once only when it is safe to repeat or known not to have started. If it may already have changed the
  target, or it fails again, tell the user and ask them to restart"* — i.e. **idempotence decides retry**, exactly the benny rule in
  `autonomous-ai-agents/cron-job-authoring/references/benny-repro-automation-safety.md`, here applied to RPC instead of posts.
- *"Do not retry a startup failure that returns the same unchanged result."* Same input ⇒ same output ⇒ retrying is noise, not progress.
- Host timeout without a result: *"do not repeat the unchanged call or assume work stopped"* — there's an explicit deadline distinction in its
  recovery guide. A timeout tells you about the **transport**, not about whether the side effect happened.

## Summary-first analysis with retained references (context-budget mechanics)

Default to `detail: "summary"`, keep the full dossier as a retained record addressed by `parent_evidence_id`, then page into it
(`inspect_analysis_view`) or pass that ID where another tool accepts a reference — *"request `\"detail\": \"complete\"` only when the dossier
must travel inline."* Composition rule worth copying anywhere: **each source can independently be inline or retained**, and you must preserve
its identity, coverage, partial facts and unknowns; a paged view has *its own* evidence ID, so use the parent ID when the consumer needs the whole thing.

Two cost notes that are good general heuristics: *"A complete small inventory can cost less than extra calls and schemas"* (don't page
something tiny just because paging exists), and *"Do not repeat an identical analysis or rejected call without a changed input or resolved blocker."*

## The truncation trap — measured in our own environment

> "A client can also truncate a successful tool result **without** a REA transport error. Treat that preview as incomplete; use the retained
> parent ID for smaller views or export when the full record is needed. **Do not parse the preview as canonical JSON** or repeat the producer."

This is precisely what happens here: Hermes demotes oversized tool output ("tool-output demoted at compaction — N chars preserved in session
history"), and `web_extract` head+tail-truncates with a saved-file path. The rule that follows, and which this catalog should enforce on any
large-read workflow: **a truncated result is a pointer, not data** — re-read from the saved file or re-query narrower before summarising,
counting, parsing JSON, or quoting numbers out of it. Never let a visible prefix become the basis for "the config says X".

Related transport handling: on `resource_constraint` with `details.resource: "transport"`, page/export rather than re-run — *"The analysis remains
complete in the ledger; avoid repeating it merely to request the same oversized response."* And CLI JSON streams without a single frame, which is why
large extractions belong in a file/pipe, not one tool result (see `autonomous-ai-agents/context-budget-planning`).

## Epistemic categories for every conclusion

> "Every conclusion must distinguish **observations, inferences, and unknowns**. Cite Evidence IDs, preserve limitations and incomplete coverage,
> and **never imply that static analysis observed execution**."

The last clause is the sharpest generalisable line here: a static read of code is not evidence about runtime behaviour. Our research/verification skills
should carry it explicitly (it's the same discipline as `verification-before-completion`, phrased to stop exactly one common overclaim). Also scope
discipline for anything that executes: *"do not broaden the target or action beyond those fields."*

## Absence-inference trap from scoped captures (generalises far beyond traffic)

For a passive SPA capture, its default scope is **the page's own origin**, while *"data APIs usually live on another origin"*; you must discover API
origins from absolute URLs in loaded bundles and pass them explicitly (`allowed_origins` — note: *the list replaces the default scope*, it doesn't extend
it), then **"read `completeness.excluded` before reporting that an API is absent."**

That is a universal rule for filtered queries, log greps, search facets and index lookups alike: **absence within a bounded scope is not absence**. Before
concluding "X isn't there", check what the scope excluded. Our `search_files`/`grep` workflows should report exclusions when the negative claim matters.

## Artifact facts worth keeping (from its routing table)

- **PyInstaller**: the **CArchive is the application layer**; the bootloader is only the native prefix — so analyse the archive members, not the exe header.
  *"Runtime options are metadata, not files"*, and compact delivery still inventories and hashes members.
- **Bun `--compile`**: the stored **module graph** is the application layer; extract it and analyse the JavaScript.
- **ESP32-family images**: magic byte **`0xE9`** identifies app/bootloader images, analysable without a native provider.
- **.NET NativeAOT** PE/ELF → treat as native (decompile for pseudocode); optional metadata recovery has a documented host/layout boundary. Managed
  PE/CLI is a different route entirely (`inspect_managed_artifact`).
- **Apple resources**: plist / Interface Builder / asset-catalog work needs no `CFBundleExecutable`, and resource sessions have *no* executable digest —
  use the binary path for native code.
- HAR/SAZ/qlog decoders run in a dedicated heap: env var `REA_CAPTURE_DECODER_OLD_GENERATION_MIB` (default **192 MiB**, floor 8, max 16384) set where the
  server starts — and *"Host memory and `NODE_OPTIONS` do not raise it."* A useful precedent when tuning any decoder service: a worker-local budget is not
  raised by global heap flags.

## What was deliberately **not** ported, and why

No RE skill was created from this repo. Its instructions are inseparable from tools that don't exist in this environment (`open_binary`,
`inspect_artifact`, `trace_native_values`, …) and engines (Ghidra, IDA, JADX, Binwalk, Unblob) we have no reason to install; shipping them would create a
skill whose every step fails — the exact failure mode our catalog's honesty rules exist to prevent. If RE work ever becomes real here, re-read upstream v60+
and port with live verification of at least one end-to-end target. Ghidra itself is covered separately (see its ledger row); `mcp/mcporter` covers calling any
MCP server that *is* registered.
