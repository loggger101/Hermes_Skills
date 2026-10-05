---
name: hermes-integrations
description: "Hermes MCP servers, webhooks, Portal auth, Hindsight."
version: 1.0.0
author: Hermes Agent (promoted from hermes-agent references, 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, mcp, webhooks, gateway, nous-portal, oauth, memory, hindsight, integrations]
    related_skills: [hermes-agent, hermes-extensions, fastmcp, mcporter, secret-vault-pattern, pinggy-tunnel]
---

# Hermes integrations

## What This Skill Does

Four ways Hermes talks to things outside itself: the **native MCP client** (external MCP servers become first-class tools), **webhook subscriptions** (outside services trigger agent runs), **Nous Portal auth** for third-party apps, and the **Hindsight memory provider**. Each reference holds the config keys, CLI calls, security behaviour and the order in which to check when it fails. Core CLI, config and troubleshooting stay in `hermes-agent`.

## When to Use

- Adding, debugging or securing an MCP server in `~/.hermes/config.yaml` (`mcp_servers`)
- Letting GitHub, GitLab, Stripe, CI or sensors start an agent run by POSTing to a URL
- Someone asks whether another app (Karakeep, OpenWebUI, LibreChat, n8n) can use their Nous Portal subscription
- Installing or fixing the Hindsight memory provider, or "memory is not recalling"
- Not for building an MCP server (`fastmcp`), ad-hoc MCP calls from a shell (`mcporter`), Hermes themes and plugins (`hermes-extensions`), or general Hermes setup (`hermes-agent`)

## Which reference

| Need | Reference | Key facts |
|---|---|---|
| MCP servers | `references/native-mcp.md` | servers sit under `mcp_servers` in `config.yaml`; tools register as `mcp_<server>_*` at startup; stdio servers get only a safe baseline environment (`PATH`, `HOME`, `USER`, `LANG`, `TERM`, `XDG_*`), secrets only through the server's `env` key; credential-like text is stripped from error messages; a saved `platform_toolsets` list can hide MCP servers; sampling lets servers request LLM calls |
| Webhooks | `references/webhooks.md` | enable the webhook platform first (`hermes gateway setup` or `platforms.webhook` in config, default port 8644); `hermes webhook subscribe/list/test`; per-subscription HMAC-SHA256 secret checked on every POST; subscriptions hot-reload from `~/.hermes/webhook_subscriptions.json`; filters and templates narrow noisy event streams |
| Portal auth for other apps | `references/portal-auth-for-third-party-apps.md` | three layers to walk in order: is it a Hermes plugin (already authenticated through Hermes's provider) or a separate app; what Portal exposes to external apps; whether a bridge is possible; apps expect a static base URL plus bearer token, so a pitched OAuth flow would not reach them |
| Hindsight memory | `references/hindsight-memory-provider.md` | modes `cloud`, `local_embedded`, `local_external`; retain is asynchronous, so test recall on the next turn, not the same turn; check `memory_mode`, bank id and hooks in a fixed order; Memory Defense is off by default and redacts only future writes; use separate banks and tags per user |

## Procedure

1. Name the integration and open its reference; read the Security section before the Quick Start.
2. MCP: add the server block, pass only the secrets it needs through `env`, restart Hermes, confirm the `mcp_<server>_*` tools appear, and check the platform's toolset allowlist if they do not.
3. Webhooks: confirm `hermes webhook list` works, subscribe with a prompt template and an `--events` filter, give the service the returned URL and secret, then run `hermes webhook test <name>`.
4. Portal question: answer Layer 1 first (plugin or separate app) before proposing any auth change.
5. Hindsight: run `hermes memory status`, then the numbered recall checks in order, with a two-turn controlled test.
6. For a local webhook receiver, reach it through a tunnel (`pinggy-tunnel`) and keep the HMAC secret out of chat and logs.

## Pitfalls

- Passing the whole shell environment to an untrusted MCP server; only the `env` key should carry secrets.
- Skipping the signature check in a webhook receiver, or treating a URL as a secret.
- Offering OAuth into Portal for a plugin that already runs inside Hermes.
- Judging Hindsight on a same-turn recall test, or pointing a credential-handling agent at a shared bank without Memory Defense.
- Trusting versions and flags written here: they were checked on Hermes v0.21.5 and the vendor docs dated in each reference.

## Verification

- [ ] MCP tools for the server appear after restart and a call succeeds
- [ ] A test webhook produces one agent run and delivers to the configured target
- [ ] Signature mismatch is rejected (try a wrong secret)
- [ ] Hindsight recall works on the turn after a stated fact
- [ ] No secret appears in config committed to git or in a chat message

## References

- `references/native-mcp.md` - native MCP client: config, transports, security, troubleshooting, examples, sampling
- `references/webhooks.md` - webhook subscriptions: setup, commands, templates, filters, patterns, security, troubleshooting
- `references/portal-auth-for-third-party-apps.md` - three-layer answer to "can app X use my Portal subscription"
- `references/hindsight-memory-provider.md` - Hindsight install, modes, config, recall checks, retain rules, Memory Defense
