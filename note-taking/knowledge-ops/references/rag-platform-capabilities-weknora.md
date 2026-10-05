---
description: "Capability checklist for a document RAG/knowledge platform, taken from Tencent WeKnora's README (hybrid search, citations, KB edit/rollback, sync connectors, agent memory, RBAC, MCP) plus how to evaluate one; README-sourced, not run"
source_repo: Tencent/WeKnora (v0.8.2, 2026-09-24; licence file is Tencent's custom MIT-style text, GitHub reports NOASSERTION)
tested_version: README and release metadata read via GitHub API; the Docker/Kubernetes stack was NOT deployed, so every capability below is a claim from the project's README
verified_date: "2026-10-05"
---

# What a production knowledge/RAG platform has to cover (WeKnora as the reference list)

WeKnora is Tencent's open-source "knowledge management framework for Q&A, tasks and wikis" (Go back end, v0.8.2). Its README is a useful **requirements checklist** for anyone building or choosing a document-knowledge system,
even though nothing here was run. Three modes share the same knowledge bases: **RAG** to look things up, an **agent** for multi-step tasks, and a **wiki** to organise knowledge.

## Capability checklist (from the README)

| Area | What the platform claims |
|---|---|
| Retrieval | hybrid search, multimodal parsing, **citations so answers can be checked** |
| Ingestion | 10+ formats (PDF, Word, images, Excel, XMind; Office files parsed); folder uploads **keep their directory tree** |
| Sources | auto-sync from Feishu wiki/Drive, Confluence, GitLab, Notion, Yuque, DingTalk Docs, RSS, Tencent IMA |
| Curation | retrieval chunks can be **edited, diffed and rolled back**; cross-session long-term memory for confirmed user facts and preferences |
| Agent | multi-step reasoning with tools; skills from ClawHub/SkillHub/Git/ZIP in session-persistent sandboxes (Docker, E2B, Cube); browser skill via an extension |
| Interfaces | IM channels (WeCom, Feishu, Slack, Telegram), an embeddable web widget, a **built-in MCP server** for Cursor/Claude, scoped API keys with a principal model |
| Models | 27 built-in vendors with a generated catalogue (OpenAI, DeepSeek, Qwen, Zhipu, Hunyuan, Gemini, MiniMax, NVIDIA, LiteLLM, Ollama); LLM, vector DB and storage backends swappable |
| Operations | multi-workspace RBAC (four roles, per-resource ownership, per-workspace audit log), several storage instances per workspace, a task-queue dashboard with worker-pool governance, Langfuse tracing of agent steps and tokens |
| Deployment | Docker or Kubernetes, local or private cloud so data stays in your environment |

## Using the list to evaluate or design a system

1. **Can every answer be traced?** Require source citations down to the chunk and document version; test with questions whose answer is in exactly one known paragraph.
2. **Can you fix a bad chunk?** Edit/diff/rollback of indexed chunks is the difference between a demo and an operable KB.
3. **Is ingestion faithful?** Check tables, scanned pages, spreadsheets and nested folders on your own documents, not the vendor's sample.
4. **Freshness:** connectors that re-sync, with deletions propagated; stale chunks are the commonest silent failure.
5. **Access control and audit:** per-workspace roles and logs matter as soon as two teams share a KB; check that retrieval filters by the caller's permissions, not only the UI.
6. **Observability:** trace queries to retrieved chunks, prompts and token cost (Langfuse-style), and keep a regression set of question/expected-source pairs.
7. **Exit options:** swappable models and stores, and an export of chunks and embeddings metadata, so you are not locked in.
8. **Agent access:** if tools can act, run them in an isolated sandbox with scoped credentials (see `application-threat-model`).

## For this repo

For a personal or small-team knowledge base, the existing `llm-wiki` (interlinked markdown), `qmd` (local markdown search) and `obsidian` skills cover the lightweight route without a server; a platform like WeKnora is the heavier route
when you need multi-user permissions, connectors and an agent UI. If you evaluate it: deploy with Docker Compose in a throwaway environment, ingest your own documents, and score the checklist above before adopting.
Licence: the repository's `LICENSE` is Tencent's custom text (MIT-style notice plus third-party notices); GitHub lists it as NOASSERTION, so read it before redistribution.
