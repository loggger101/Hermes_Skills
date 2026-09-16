# SSRF Guard & Outbound-HTTP Hardening (verified from reconurge/flowsint @ 1820569, v1.2.12)

Source: `flowsint-core/src/flowsint_core/templates/loader/yaml_loader.py` + `template_enricher.py`
+ `templates/types.py`. Flowsint is an OSINT graph tool whose *user-supplied* YAML templates and
n8n webhook URLs issue outbound HTTP — so it treats every rendered URL as hostile input. The whole
pattern below is portable to any service where a user (or LLM) can influence the destination of an
outbound request: webhooks, "add your API" integrations, template engines, agent tool calls.

## 1. SSRF guard — validate AFTER rendering, before every request

The check runs on the *rendered* URL inside `_process_single_input` (after `{{var}}` substitution),
not at config time — a placeholder can render to an internal address:

```python
url = YamlLoader.render_template(req.url, values)   # user data substituted in
try:
    validate_url_safe(url)                          # raises SSRFError -> request never happens
except SSRFError as e:
    Logger.info(...); raise TemplateEnricherError(f"Blocked URL: {e}")
```

`validate_url_safe` (273-line file, ~40 lines of logic):

1. `urlparse(url)`; no hostname -> block (`Invalid URL`).
2. Hostname in a **blocked-hostname set** -> block. Their set is small and specific:
   `localhost`, `localhost.localdomain`, `metadata.google.internal`, `metadata.google`,
   `169.254.169.254` (AWS/GCP/Azure metadata endpoint).
3. Hostname parses as an IP in a **blocked-range list** -> block:

```python
BLOCKED_IP_RANGES = [
    ipaddress.ip_network("127.0.0.0/8"),      # loopback
    ipaddress.ip_network("10.0.0.0/8"),       # private A
    ipaddress.ip_network("172.16.0.0/12"),    # private B
    ipaddress.ip_network("192.168.0.0/16"),   # private C
    ipaddress.ip_network("169.254.0.0/16"),   # link-local (cloud metadata)
    ipaddress.ip_network("0.0.0.0/8"),        # current network
    ipaddress.ip_network("224.0.0.0/4"),      # multicast
    ipaddress.ip_network("240.0.0.0/4"),      # reserved
    ipaddress.ip_network("100.64.0.0/10"),    # carrier-grade NAT
    ipaddress.ip_network("198.18.0.0/15"),    # benchmark testing
    ipaddress.ip_network("::1/128"),          # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 private (ULA)
    ipaddress.ip_network("fe80::/10"),        # IPv6 link-local
]
```

4. **Scheme allowlist**: only `http`/`https` — blocks `file://`, `gopher://`, etc. in one line.

**Two verified limitations (measured on this host 2026-09-15 while building the harness):**
- No DNS resolution: a user-supplied *domain* whose A record points at an internal address passes —
  only literal IP hosts and the small hostname set are checked. If destinations can be domains, add a
  resolve-and-recheck step (or pin to known-good endpoints).
- **Unbracketed IPv6 literals bypass it**: `urlparse("http://fd12:3456::1/x").hostname` returns `"fd12"`
  (first colon read as port separator), which matches no blocked range. Bracketed forms (`[fd12:3456::1]`)
  are caught correctly. If IPv6 literals must be supported, normalize/bracket before validating — or reject
  hostnames containing `:` outright in the URL slot.

See `scripts/ssrf_guard_verify.py` (this skill) for a runnable harness covering all ranges, schemes,
hostnames, both limitations, sanitization, dot-notation extraction, and the retry decision table.

## 2. Injection hardening at the substitution layer, not the transport layer

- Template vars: regex `\{\{\s*([a-zA-Z_][a-zA-Z0-9_.]*)\s*\}\}`; a missing variable raises
  `TemplateRenderError` (fail loud — never substitute empty).
- **URL components are percent-encoded at render time**: `quote(str(value), safe="-_.~")`.
  Headers/body use the same renderer with `sanitize=False` (header values must not be mangled,
  and they can't alter URL structure). So encoding is a *per-slot policy*, applied where it matters.
- Method allowlist: only `GET`/`POST` accepted in templates (`Literal["GET","POST"]`).

## 3. Retry policy (measured defaults — portable numbers)

From `TemplateRetryConfig` + `_make_request_with_retry`:

| knob | default | bounds | note |
|---|---|---|---|
| max_retries | 3 | 0–10 | attempts = retries+1 |
| backoff_factor | 0.5 s | 0.1–10.0 | wait = factor × 2^attempt (exponential) |
| retry_on_status | [429, 500, 502, 503, 504] | — | the canonical "transient" set |

Decision logic worth copying verbatim:
- Status in `retry_on_status` -> back off and retry.
- Other **4xx**: re-raise immediately (client errors don't fix themselves) *unless* that code is
  explicitly in `retry_on_status`.
- TimeoutException -> same exponential backoff, then raise after the last attempt.
- Every retry is logged with attempt number and wait time — silent retries are invisible to users.

## 4. Secrets never touch templates or logs

- Template declares `{name, required, description}` per secret; at runtime `{{secrets.NAME}}`
  resolves from an encrypted vault (see cron-job-authoring/references/vault-crypto-pattern.md).
- Required-but-missing secret raises before any request is made.
- The raw response (status/headers/body) is kept on the enricher (`get_raw_response()`) for
  debugging, but secrets are resolved into a private dict — never written to logs.

## 5. Verified inconsistency in their own codebase (the lesson)

`TemplateEnricher` runs `validate_url_safe()` on every rendered URL — but the **n8n connector**
(`flowsint_enrichers/n8n/connector.py`) posts straight to a user-supplied `webhook_url` param with
no SSRF check at all. Same repo, same threat model (user-controlled destination), one path guarded,
one not. When auditing: grep for every site that issues an outbound request and confirm each one
passes the guard — "the framework has protection" is not evidence any given call uses it.

## 6. Deployment-side companion defenses (from their PR history)

- **PR #178** — nginx `map $http_host` allowlist defaulting to deny: defends against DNS rebinding,
  where a victim's browser treats the attacker-controlled domain as same-origin and skips CORS, so
  only a *server-side* Host check stops it. Default allowlist = localhost/127.0.0.1/[::1] (any port);
  LAN/public deploys must add their own hostname/IP. Pitfall documented in the diff: nginx
  `add_header` inheritance is **replace-all, not merge** — a location block that sets any header
  silently drops every server-level security header unless re-declared there.
- **PR #213** (`fix/flow-object-level-authz`) — object-level authorization (IDOR) on Flow
  update/delete/read: checking "user is authenticated" was not enough; each endpoint must verify the
  resource belongs to the acting user. Their `check_investigation_permission(user_id, investigation_id, actions)`
  pattern = role matrix (OWNER all / EDITOR read+create+update / VIEWER read) resolved per-resource from a join table.

## Porting checklist for your own services

1. One shared `validate_url_safe()`; call it on the *rendered* URL at every request site.
2. Blocked ranges: loopback, RFC1918, link-local (metadata!), 0/8, multicast, reserved, CGNAT + IPv6 equivalents.
3. Scheme allowlist http/https only.
4. Percent-encode user values when they land in URL slots; leave header/body slots unencoded but logged carefully.
5. Retry: exponential backoff on {429, 5xx} only; fail fast on other 4xx; log every retry.
6. Secrets via vault/params resolved at init — never hardcoded, never in logs.
7. AuthN is not authZ: per-resource ownership check (IDOR) on every mutating endpoint.
