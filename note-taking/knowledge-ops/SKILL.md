---
name: knowledge-ops
description: "KB ops: ingest, dedupe, sync, retrieve across stores."
version: v0.1.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [knowledge-management, second-brain, ingestion, sync, retrieval, deduplication]
    related_skills: [llm-wiki, obsidian, session-librarian]
---

<!-- source: affaan-m/ECC (MIT), ported 2026-09-09 -->
# Knowledge Operations

Manage a multi-layered knowledge system for ingesting, organizing, syncing, and retrieving knowledge across multiple stores.

## What This Skill Does

Defines a layered architecture for durable knowledge — active execution truth, quick-access memory files, structured semantic search, curated document repos, external data stores, local archive folders — plus the ingestion workflow (classify → deduplicate → store → index), sync operations between layers, and a quality gate that runs before any knowledge operation is considered complete.

## When to Use

- User wants to save information to their knowledge base
- Ingesting documents, conversations, or data into structured storage
- Syncing knowledge across systems (local files, memory tools, vector stores, Git repos)
- Deduplicating or organizing existing knowledge
- User says "save this to KB", "sync knowledge", "what do I know about X", "ingest this", "update the knowledge base"
- Any knowledge management task beyond simple memory recall

## Knowledge Architecture

Prefer the live workspace model:
- code work lives in the real cloned repos
- active execution context lives in GitHub, Linear, and repo-local working-context files
- broader human-facing notes can live in a non-repo context/archive folder
- durable cross-machine memory belongs in the knowledge base, not in a shadow repo workspace

### Layer 1: Active execution truth
- **Sources:** GitHub issues, PRs, discussions, release notes; Linear issues/projects/docs
- **Use for:** the current operational state of the work
- **Rule:** if something affects an active engineering plan, roadmap, rollout, or release, prefer putting it here first

### Layer 2: Quick-access memory files (e.g. Hermes `memories/`)
- **Path:** profile-level MEMORY.md / USER.md style stores
- **Format:** Markdown with compact high-signal entries
- **Types:** user preferences, feedback, project context, reference
- **Use for:** quick-access context that persists across conversations and is injected at session start

### Layer 3: Structured knowledge graph (MCP memory or equivalent)
- **Access:** MCP memory tools (`create_entities`, `create_relations`, `add_observations`, `search_nodes`) where available; otherwise a grep-indexable flat index file
- **Use for:** semantic search across all stored memories, relationship mapping
- Cross-session persistence with queryable graph structure

### Layer 4: Knowledge base repo / durable document store
- **Use for:** curated durable notes, session exports, synthesized research, operator memory, long-form docs
- **Rule:** this is the preferred durable store for cross-machine context when the content is not repo-owned code (this Hermes_Skills repo itself plays this role)

### Layer 5: External data store (Supabase, PostgreSQL, etc.)
- **Use for:** structured data, large document storage, full-text search
- Good for documents too large for memory files, or data needing SQL queries

### Layer 6: Local context/archive folder
- **Use for:** human-facing notes, archived gameplans, local media organization, temporary non-code docs
- Writable for information storage, but not a shadow code workspace
- **Do not use for:** active code changes or repo truth that should live upstream

## Ingestion Workflow

When new knowledge needs to be captured:

### 1. Classify
What type of knowledge is it?
- Business decision → memory file (project type) + semantic store
- Active roadmap / release / implementation state → GitHub first
- Personal preference → user-profile memory entry
- Reference info → reference-type memory entry + semantic store
- Large document → external data store + summary in memory
- Conversation/session → knowledge base repo + short summary in memory

### 2. Deduplicate
Check if this knowledge already exists:
- Search memory files for existing entries
- Query the semantic store with relevant terms (or grep SKILLS-INDEX / REFERENCES-INDEX)
- Check whether the information already exists in GitHub before creating another local note
- Do not create duplicates — update existing entries instead

### 3. Store
Write to appropriate layer(s):
- Always update quick-access memory for cross-session recall
- Use the semantic store for searchability and relationship mapping when available
- Update GitHub first when the information changes live project truth
- Commit to the knowledge base repo for durable long-form additions

### 4. Index
Update any relevant indexes or summary files (e.g. flat grep indices, category DESCRIPTIONs).

## Sync Operations

### Conversation sync
Periodically sync conversation history into the knowledge base:
- Sources: agent session exports from this and other harnesses
- Destination: knowledge base repo
- Generate a session index for quick browsing; commit and push

### Workspace state sync
Mirror important workspace configuration and scripts to the knowledge base:
- Generate directory maps
- Redact sensitive config before committing (API keys, tokens — never preserve credentials)
- Track changes over time
- Do not treat the knowledge base or archive folder as the live code workspace

### GitHub / Linear sync
When information affects active execution:
- update the relevant GitHub issue, PR, discussion, release notes, or roadmap thread
- attach supporting docs to Linear when the work needs durable planning context
- only mirror a local note afterwards if it still adds value

### Cross-source knowledge sync
Pull knowledge from multiple sources into one place:
- conversation exports (Hermes session_search, ChatGPT/Grok/Claude exports)
- browser bookmarks
- GitHub activity events
- Write a status summary, commit and push

## Memory Patterns

```text
# Short-term: current session context — in-session task tracking (todo list)
# Medium-term: quick-access memory files for cross-session recall
# Long-term: active execution truth in GitHub/Linear; durable synthesized context in the KB repo
# Semantic layer: structured entities + relations where an MCP memory server exists,
#   otherwise a flat grep-index file fulfills retrieval
```

## Best Practices

- Keep memory entries concise. Archive old data rather than letting files grow unbounded.
- Use frontmatter (YAML) for metadata on all knowledge files.
- Deduplicate before storing — search first, then create or update.
- Prefer one canonical home per fact set; avoid parallel copies of the same plan across local notes, repo files, and tracker docs.
- Redact sensitive information (API keys, passwords) before committing to Git — never preserve credentials in any layer.
- Use consistent naming conventions for knowledge files (lowercase-kebab-case).
- Tag entries with topics/categories for easier retrieval.

## Quality Gate

Before completing any knowledge operation:
- no duplicate entries created
- sensitive data redacted from any Git-tracked files
- indexes and summaries updated
- appropriate storage layer chosen for the data type
- cross-references added where relevant
