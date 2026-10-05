# Per-User Encrypted Secret Vault (reconurge/flowsint @ 1820569; crypto run 2026-10-05)

Source: `flowsint-core/src/flowsint_core/core/vault.py` (155 lines — the whole pattern fits there).
Flowsint stores third-party API keys for its OSINT enrichers. The design is a clean, copyable
reference implementation of "user-supplied secrets at rest" with envelope encryption:

## Crypto construction (all from source)

- **Master key**: env var `MASTER_VAULT_KEY_<version>` — base64-encoded 32 bytes; optional literal
  prefix `base64:` in the value. Versioned by schema (`V1` today). **Caveat (run 2026-10-05, see the
  section at the end):** rows store a `key_version`, but `Vault.version` is hard-coded to `"V1"` and
  `get_secret` never passes the row's version to decryption, so rotation is NOT supported by this code;
  it would need a re-key of every row.
- **Per-secret data key**: HKDF-SHA256(master_key, salt=random 16 B, info=str(owner_id)) -> AES-256.
  The `info` context binds the derived key to a specific user — the same master key + different
  owner derives different keys even with identical salts.
- **Cipher**: AES-256-GCM (authenticated encryption) via `cryptography.hazmat.primitives.ciphers.aead.AESGCM`.
  IV = random 12 bytes per secret.
- **AAD** (additional authenticated data): `str(owner_id).encode()` — decryption by the wrong user
  fails authentication, not just yields garbage. This is what makes a stolen row useless to another
  tenant even if they know the master key's derivation path for their own ID… precisely: it binds
  ciphertext integrity to owner identity; cross-user reads raise `InvalidTag`.

Stored per secret (SQLAlchemy `Key` model): `id (uuid)`, `name`, `iv`, `salt`, `ciphertext`
(ciphertext+tag), `key_version`, `owner_id`, `created_at`. No plaintext ever touches the DB.

## Lookup semantics worth copying

- `get_secret(vault_ref)` accepts **either a UUID or a name**: tries `uuid.UUID(ref)`, on ValueError
  falls back to name lookup — always scoped by `WHERE owner_id = self.owner_id` (tenant isolation is
  in every query, not just the encrypt path).
- Caller side (`Enricher.resolve_params`): for a param of type `vaultSecret`, first try the value the
  user passed as an explicit vault ID; else look up by the *param name* itself (e.g. declaring a
  param named `WHOXY_API_KEY` auto-binds to a vault entry with that name); if still nothing and
  `required: true` -> raise with an actionable message naming the missing key ("go to Vault settings
  and create a 'X' key").

## Deferred-resolution pattern (the subtle part)

Params arrive at construction as *references*, not values. The base class builds a strict Pydantic
model (`create_model(..., extra="forbid")`) where **vaultSecret fields are always optional** — the
required-ness is enforced only AFTER vault resolution in `async_init()`. Why: an enricher must be
instantiable (and listable/metadata-inspectable) without a vault; failing at construction would break
discovery. Sequence: construct -> `resolve_params()` (vault lookup by ID then name, else default) ->
strict validate resolved dict -> store in `self.params`. Inside code you then call
`self.get_secret("NAME")` which just reads the already-resolved param — no vault access at scan time.

## Porting notes for Hermes cron/agent contexts

- The same shape works for any per-user or per-profile secret store: versioned master key from env,
  HKDF with `info=tenant_id`, AES-GCM, AAD = tenant id, per-row salt+iv+version.
- Keep the *name-as-ID* dual lookup — it's what makes "declare a param named MY_API_KEY" ergonomic;
  users create one vault entry and every tool that names it picks it up.
- Enforce ownership in the query (not just after fetch) so tenant isolation survives refactors.
- For non-SQL stores, keep `key_version` on each row **and read it on decrypt** (flowsint stores it but does not use it) — then master-key rotation becomes an additive migration.

## Run 2026-10-05: `vault.py` executed with its DB imports stubbed

`vault.py` (155 lines, unchanged in substance since 2026-06-04; later commits are formatting) was loaded with stub
`dotenv`/`sqlalchemy`/`models` modules and its `_encrypt_key` / `_decrypt_key` / `_get_master_key` called with the real
`cryptography` package (Python 3.14, Windows). Results:

| Check | Result |
|---|---|
| Round trip, same owner | works (also empty string and non-ASCII text) |
| Another owner decrypts the row | `InvalidTag` |
| Ciphertext, salt or IV altered | `InvalidTag` each |
| Correct derived key but another owner's AAD | `InvalidTag`: **AAD and the HKDF `info` each bind the owner independently** (two layers; the earlier "precisely..." sentence on AAD conflated them) |
| Row encrypted under V1 read after setting `version = "V2"` with a V2 master key present | `InvalidTag`: the stored `key_version` is ignored; `get_secret` builds `{salt, iv, ciphertext}` only. **Rotation is not implemented.** To rotate, pass `row.key_version` into the master-key lookup and keep all versions' keys available |
| `MASTER_VAULT_KEY_V1` missing | `ValueError: Missing master key V1` |
| 31-byte base64 key | `ValueError: Master key must be 32 bytes (256 bits)` |
| `base64:` prefix | accepted |
| 64-character **hex** string (e.g. from `openssl rand -hex 32`) | `ValueError: ... 32 bytes`: it is decoded as base64 into 48 bytes. Generate the key with `openssl rand -base64 32` |
| Not valid base64 | `binascii.Error` (a `ValueError` subclass) |
| `owner_id` falsy | `ValueError: owner_id is required to use the vault.` |
| `owner_id` a plain string such as `"alice"` | accepted: it is stringified into HKDF info and AAD, so the type is not enforced |

Other minor observations from reading: `_derive_user_data_key(master_key, salt)` ignores its `master_key` argument and re-reads
the environment; a commit on 2026-06-04 fixed "vault owner_id type matching".
Not run: the SQLAlchemy models, Alembic migrations, the enricher `resolve_params` path, and the repo's own test suite.

## Adjacent pattern from the same repo (2026-09-20, source-read)

Commit "stop node upsert from nulling unset FlowsintType fields" (PR #228, with a repro test) fixed a **partial-write
clobber**: upserting a Pydantic model into the graph wrote every field, so fields the caller never set overwrote stored values
with null. The fix is to serialise with `exclude_unset` semantics (write only fields that were actually provided). The same trap
applies to any `PATCH`/upsert built from a model with defaults.
