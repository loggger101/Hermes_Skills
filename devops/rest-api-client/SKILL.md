---
name: rest-api-client
description: "Call REST APIs: auth, pagination, rate limits, errors."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [REST, API, HTTP, curl, integration]
    related_skills: [ssh-remote]
---

# REST API Client

Call REST APIs with auth, pagination, rate-limit awareness, and structured error handling. Encodes the workflow for integrating with arbitrary HTTP APIs.

## When to Use

- "Call this API endpoint"
- "Pull all pages of results from this API"
- "Post data to this service"
- "Debug why the API call is failing"
- "Find the right auth header / token setup"

Don't use for: GraphQL endpoints (different query shape); SOAP/XML-RPC; browser-based OAuth flows (stop and ask); APIs that require a SDK when a clean REST fallback exists.

## Prerequisites

- **`curl`** on PATH (universal) or **`httpie`**/`wget` as alternatives
- **API documentation or endpoint knowledge**: base URL, auth method, required headers, request shape, response shape
- **Credentials** sorted before the first call:
  - API key (header or query param)
  - Bearer token (OAuth2, personal access token)
  - Basic auth (user/pass)
  - None (public endpoints)
- **Rate limit awareness**: does the API document rate limits? Are there pagination tokens/links?

## How to Run

All API calls go through `terminal` with `curl`. Use `-s` (silent) for clean output, `-w` for status code, `-o` to write response to file, and `--write-out` for diagnostics.

```bash
# GET, simple
curl -s https://api.example.com/v1/items

# GET with auth header
curl -s -H "Authorization: Bearer $TOKEN" https://api.example.com/v1/items

# GET with API key query param
curl -s "https://api.example.com/v1/items?api_key=$KEY"

# GET with custom headers
curl -s -H "Accept: application/json" -H "X-API-Version: 2024-01" https://api.example.com/v1/items

# POST JSON
curl -s -X POST https://api.example.com/v1/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Alice", "email": "alice@example.com"}'

# POST from a file
curl -s -X POST https://api.example.com/v1/batch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @payload.json

# With response code + time diagnostics
curl -s -o response.json -w "http_code=%{http_code} time=%{time_total}s\n" \
  https://api.example.com/v1/items

# Save response to file
curl -s -o items.json https://api.example.com/v1/items

# Follow redirects
curl -s -L https://api.example.com/v1/items

# Verbose (debug failed calls)
curl -s -v https://api.example.com/v1/items
```

Pagination patterns:

```bash
# Page-based (page/per_page)
curl -s "https://api.example.com/v1/items?page=1&per_page=100"

# Cursor-based (next_token / next_url)
curl -s "https://api.example.com/v1/items?cursor=abc123"

# Link-header based (RFC 5988)
curl -s -I https://api.example.com/v1/items   # inspect Link header
```

## Procedure

### 1. Read the API contract
Before calling, know:
- Base URL + version path
- Auth method (bearer, API key, basic, none)
- Required headers (Content-Type, Accept, API version, etc.)
- Request shape for the endpoint
- Response shape and where the data lives in the JSON
- Pagination style (page, cursor, link-header, offset/limit)
- Rate limits (requests per minute/hour, burst)

### 2. Test connectivity + auth with a minimal call
```bash
curl -s -w "\nhttp_code=%{http_code}\n" https://api.example.com/v1/items
```
- `http_code=200` → good to go
- `http_code=401` → auth wrong (token expired, wrong header, wrong key)
- `http_code=403` → auth ok but not allowed
- `http_code=429` → rate limited — slow down, check Retry-After header
- `http_code=404` → endpoint wrong or resource missing
- `http_code=400/422` → request shape wrong

### 3. Handle auth
- **Bearer token**: `-H "Authorization: Bearer $TOKEN"` — stored in env, not hardcoded
- **API key header**: `-H "X-API-Key: $KEY"` (varies by API)
- **API key query param**: `?api_key=$KEY` (less secure — URL may leak in logs)
- **Basic auth**: `-u user:pass` (curl base64-encodes automatically)
- **OAuth2 client credentials**: fetch a token first with a separate call, then use it
- **Expired token**: re-fetch or refresh; don't retry the same call blindly

### 4. Paginate to get all results
Pick the pattern from the API:

**Page-based:**
```bash
page=1
while true; do
  resp=$(curl -s "https://api.example.com/v1/items?page=$page&per_page=100")
  [ -z "$resp" ] && break
  echo "$resp"
  # detect last page: empty array, or page count in response
  page=$((page + 1))
done
```

**Cursor-based:**
```bash
cursor=""
while [ -n "$cursor" ] || [ -z "$cursor" ]; do
  if [ -n "$cursor" ]; then
    resp=$(curl -s "https://api.example.com/v1/items?cursor=$cursor")
  else
    resp=$(curl -s "https://api.example.com/v1/items")
  fi
  echo "$resp"
  cursor=$(echo "$resp" | jq -r '.next_cursor // empty')
  [ -z "$cursor" ] && break
done
```

**Link-header based:** parse the `Link` header for the `rel="next"` URL and follow it.

For robust pagination, prefer `execute_code` (Python + `requests` or `urllib`) when the loop has logic beyond a simple shell loop. Python handles JSON parsing, retries, and rate-limit backoff more cleanly.

### 5. Handle errors
- Check HTTP status before trusting the body
- 4xx = you did something wrong (auth, shape, permissions) — fix the call
- 5xx = server-side — retry with backoff, but don't retry forever
- 429 = rate limited — respect `Retry-After` header, back off
- Network errors (connection refused, DNS, timeout) — check the URL, the network, then retry a bounded number of times

### 6. Parse and use the response
- Pretty-print to inspect: `curl -s ... | jq .`
- Extract a field: `curl -s ... | jq -r '.data[].name'`
- Save raw: `curl -s -o items.json ...`
- For complex workflows: `execute_code` with Python `requests` or `urllib`

## Quick Reference

| Task | Command |
|------|---------|
| GET (raw) | `curl -s https://api.example.com/v1/items` |
| GET + status code | `curl -s -w "\n%{http_code}\n" URL` |
| GET with Bearer | `curl -s -H "Authorization: Bearer $TOKEN" URL` |
| GET with API key header | `curl -s -H "X-API-Key: $KEY" URL` |
| GET with API key query | `curl -s "URL?api_key=$KEY"` |
| GET with Basic auth | `curl -s -u user:pass URL` |
| POST JSON | `curl -s -X POST URL -H "Content-Type: application/json" -d '{"k":"v"}'` |
| POST from file | `curl -s -X POST URL -d @payload.json` |
| Pretty-print JSON | `curl -s URL | jq .` |
| Extract field | `curl -s URL | jq -r '.data.name'` |
| Save response to file | `curl -s -o out.json URL` |
| Follow redirects | `curl -s -L URL` |
| Verbose (debug) | `curl -s -v URL` |
| Conditional header | `curl -s -H "If-None-Match: $etag" URL` |

## Pitfalls

- **Hardcoding credentials.** Never write API keys or tokens into the command literally. Use environment variables (`$TOKEN`, `$KEY`) sourced from the user's env or `~/.hermes/.env`. Don't log them.
- **Skipping the HTTP status code.** A 200 with an error body is possible, but a non-200 with a "successful-looking" body is more common — always check the code first.
- **Assuming pagination is page-based.** Many modern APIs use cursors or link headers. Check the API docs or the first response for hints (`next_cursor`, `Link` header, `total_pages`).
- **Rate limits.** Hitting an API in a tight loop without backoff triggers 429s. Add delays between calls, respect `Retry-After`, and batch where the API allows.
- Parse JSON with `jq` — don't try to parse JSON with `search_files`-style text extraction.
- For text extraction from JSON, use `jq` or `execute_code` with Python.
- **HTTPS/certificate issues.** Corporate MITM proxies, self-signed certs, or expired CA bundles cause `SSL certificate problem` errors. Don't blindly add `-k` (insecure) — flag it for the user instead.
- **Large responses.** Don't dump multi-MB responses into context. Save to file with `-o` and read only what you need (or parse in `execute_code`).
- **POST body encoding.** `-d` sends `application/x-www-form-urlencoded` by default. For JSON, set `-H "Content-Type: application/json"` and use `-d '{"key":"value"}'` (or `-d @file.json`).

## Verification

- Minimal call returns the expected HTTP status
- Auth works (200 on an authenticated endpoint, 401 on a wrong token)
- Pagination loop returns all expected pages/items
- Parsed fields match the API response
- Errors produce the expected status and are handled (not silently ignored)
- No credentials appear in command output or logs

## Related

For APIs that require browser-based OAuth flow (e.g., "click here to authorize"), stop and ask the user — this skill covers token-based auth only. For GraphQL, use the GraphQL endpoint with a JSON `query` payload but expect a different response shape. For long-running integrations with rate limits and state, consider `cronjob` for scheduled polling. For local services, combine with `skill_view(name='docker-containers')` or `skill_view(name='ssh-remote')` if the API is on another host.
