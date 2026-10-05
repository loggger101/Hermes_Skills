---
name: secret-vault-pattern
description: "Per-user encrypted secret vault: HKDF + AES-GCM, tested."
version: 1.0.0
author: Hermes Agent (promoted from cron-job-authoring references; reconurge/flowsint vault.py, crypto run live 2026-10-05)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [secrets, vault, encryption, aes-gcm, hkdf, multi-tenant, key-rotation, api-keys, at-rest]
    related_skills: [security-audit, rest-api-client, cron-job-authoring, application-threat-model, failure-signal-audit]
---

# Per-user encrypted secret vault

## What This Skill Does

Gives a small, copyable design for storing user-supplied secrets (third-party API keys) at rest with envelope encryption, taken from a 155-line implementation in reconurge/flowsint and **executed** with its database imports stubbed. It records what the construction guarantees, what it does not (key rotation is not implemented), the input handling traps, and the deferred-resolution pattern that lets tools load without a vault.

## When to Use

- A pipeline or app must store per-user or per-profile secrets and environment variables are not enough
- Reviewing a secret store for tenant isolation and rotation
- Letting tools declare a secret by name and have it bound automatically
- Not for deciding what to scan in a codebase (`security-audit`), outbound HTTP hardening (`rest-api-client`), or cron credential handling (`cron-job-authoring`, `references/credential-strategy.md`)

## The construction

- **Master key**: env var `MASTER_VAULT_KEY_<version>`, base64 of 32 bytes (an optional literal `base64:` prefix is accepted). Generate it with `openssl rand -base64 32`; a 64-character hex string fails because it decodes as 48 bytes.
- **Per-secret data key**: HKDF-SHA256 over the master key with a random 16-byte salt and `info = str(owner_id)`.
- **Cipher**: AES-256-GCM with a random 12-byte IV per secret, and AAD = `str(owner_id)`. The HKDF info and the AAD each bind the owner independently (two layers).
- **Stored per secret**: id, name, iv, salt, ciphertext plus tag, key_version, owner_id, created_at. No plaintext touches the database.
- **Lookup**: accept a UUID or a name, always scoped by `WHERE owner_id = ...` so isolation survives refactors; a parameter named `WHOXY_API_KEY` auto-binds to a vault entry of that name.
- **Deferred resolution**: parameters arrive as references; secret fields are optional at construction and required-ness is enforced only after vault resolution, so tools can still be listed and inspected without a vault.

## Procedure

1. Create the master key per version in the environment; never in the database or the repository.
2. Derive a per-secret key with a fresh salt, encrypt with a fresh IV, bind both HKDF info and AAD to the owner, store salt, iv, ciphertext and `key_version`.
3. On decrypt, **read the row's `key_version`** and pick that master key (the source stores it but ignores it, so rotation is not supported there); then rotation is an additive migration.
4. Scope every query by owner, not only the encrypt path.
5. Resolve secrets once at initialisation and read the resolved value afterwards; raise an actionable error naming the missing key when a required secret is absent.
6. Test the negative cases: wrong owner, altered ciphertext, salt or IV, missing master key.

## Measured behaviour (Python 3.14, `cryptography`, Windows)

| Check | Result |
|---|---|
| Round trip, same owner (also empty and non-ASCII text) | works |
| Another owner decrypts | `InvalidTag` |
| Ciphertext, salt or IV altered | `InvalidTag` each |
| Row read after switching `version` to V2 | `InvalidTag`: stored `key_version` is ignored |
| Missing master key / 31-byte key | `ValueError` naming the problem |
| `owner_id` falsy | `ValueError: owner_id is required` |
| `owner_id` a plain string | accepted; type is not enforced |

## Pitfalls

- Assuming rotation works because rows carry a `key_version`: it does nothing unless decryption reads it.
- Hex master keys (`openssl rand -hex 32`) fail; use base64.
- Partial upserts: serialising a model with defaults on update nulls unset fields; write only fields that were actually provided (`exclude_unset`).
- Not run: the SQLAlchemy models, migrations, the enricher `resolve_params` path and the repo's own tests.

## Verification

- [ ] Cross-owner decryption and tampered ciphertext fail authentication
- [ ] Decryption uses the row's `key_version` and a rotation test passes
- [ ] Every query is owner-scoped
- [ ] The master key is only in the environment and never logged

## References

- `references/vault-crypto-pattern.md` - the full construction from `vault.py`, lookup semantics, deferred-resolution pattern, porting notes for Hermes, the live run table, and the adjacent partial-write clobber fix
