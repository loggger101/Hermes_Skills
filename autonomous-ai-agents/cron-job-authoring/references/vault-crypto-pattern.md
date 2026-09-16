# Per-User Encrypted Secret Vault (verified from reconurge/flowsint @ 1820569)

Source: `flowsint-core/src/flowsint_core/core/vault.py` (155 lines — the whole pattern fits there).
Flowsint stores third-party API keys for its OSINT enrichers. The design is a clean, copyable
reference implementation of "user-supplied secrets at rest" with envelope encryption:

## Crypto construction (all from source)

- **Master key**: env var `MASTER_VAULT_KEY_<version>` — base64-encoded 32 bytes; optional literal
  prefix `base64:` in the value. Versioned by design (`V1` today): rotating the master key means a
  new version + re-key, not breaking old rows (rows carry their own `key_version`).
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
- For non-SQL stores, keep `key_version` on each row — master-key rotation becomes an additive migration.
