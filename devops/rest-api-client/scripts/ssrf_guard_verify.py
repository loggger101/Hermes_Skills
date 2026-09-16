#!/usr/bin/env python3
"""Live-verification harness for the Flowsint outbound-HTTP hardening patterns.

Re-implements (verbatim-in-spirit) the guard + retry policy from reconurge/flowsint
@ 1820569: templates/loader/yaml_loader.py and core/template_enricher.py, then asserts
every documented behavior against concrete cases. Stdlib only — run with `py` or `python`.

Exit code = number of failed checks (0 = all pass).
"""
from __future__ import annotations

import ipaddress
import re
from urllib.parse import quote, urlparse

FAILS: list[str] = []
COUNT = 0


def check(name: str, cond: bool) -> None:
    global COUNT
    COUNT += 1
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")
    if not cond:
        FAILS.append(name)


# ---------------------------------------------------------------- guard (yaml_loader.py)
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

BLOCKED_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
    "metadata.google",
    "169.254.169.254",
}


class SSRFError(Exception):
    pass


def is_ip_blocked(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False  # not a literal IP — hostname path handles it
    return any(ip in net for net in BLOCKED_IP_RANGES)


def validate_url_safe(url: str) -> None:
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        raise SSRFError(f"Invalid URL: no hostname found in '{url}'")
    if hostname.lower() in BLOCKED_HOSTNAMES:
        raise SSRFError(f"Blocked hostname: {hostname}")
    if is_ip_blocked(hostname):
        raise SSRFError(f"Blocked IP address: {hostname}")
    if parsed.scheme not in ("http", "https"):
        raise SSRFError(f"Blocked URL scheme: {parsed.scheme}")


def blocked(url: str) -> bool:
    try:
        validate_url_safe(url)
        return False
    except SSRFError:
        return True


print("== 1. Blocked IP ranges (all from their BLOCKED_IP_RANGES list)")
for url, why in [
    ("http://127.0.0.1/x", "loopback"),
    ("http://10.0.0.5/x", "private A"),
    ("http://172.16.9.9/x", "private B (lower edge)"),
    ("http://172.31.255.1/x", "private B (upper edge of /12)"),
    ("http://192.168.0.1/x", "private C"),
    ("http://169.254.169.254/latest/meta-data/", "cloud metadata endpoint"),
    ("http://0.0.0.0:8080/x", "current network"),
    ("http://224.0.0.1/x", "multicast"),
    ("http://240.0.0.1/x", "reserved"),
    ("http://100.64.0.1/x", "CGNAT (lower edge of /10)"),
    ("http://198.18.0.7/x", "benchmark testing"),
    ("https://[::1]:8443/x", "IPv6 loopback (bracketed)"),
    ("http://[fd12:3456::1]/x", "IPv6 ULA fc00::/7 (bracketed)"),
    ("http://[fe80::1]/x", "IPv6 link-local fe80::/10 (bracketed)"),
]:
    check(f"blocks {why}: {url}", blocked(url))

print("== 2. Allowed destinations")
for url in [
    "https://api.github.com/users/octocat",
    "http://ip-api.com/json/8.8.8.8",
    "https://example.com:443/path?q=1",
]:
    check(f"allows {url}", not blocked(url))

print("== 3. Scheme allowlist (only http/https)")
for url in [
    "file:///etc/passwd",
    "gopher://127.0.0.1:6379/_INFO",
    "ftp://example.com/x",
]:
    check(f"blocks scheme: {url}", blocked(url))

print("== 4. Blocked-hostname set (literal, no DNS)")
for url in [
    "http://localhost:5001/admin",
    "https://LOCALHOST/upper-case-normalized",
    "http://metadata.google.internal/computeMetadata/v1/",
]:
    check(f"blocks hostname: {url}", blocked(url))

print("== 5. VERIFIED LIMITATIONS (documented, not failures of this harness)")
# The guard checks literal-IP hosts + a small hostname set; it does NOT resolve
# domain names to IPs before checking. A user-supplied domain whose A record points
# at 169.254.169.254 or an RFC1918 address passes validate_url_safe() as written.
check(
    "limitation: DNS-resolvable internal target is NOT caught by the literal check",
    not blocked("http://attacker-controlled.example/x"),  # hostname unknown to guard -> allowed
)
# Second limitation, found while verifying on this host (2026-09-15): unbracketed IPv6
# literals are mis-parsed by urllib.parse — the first colon is read as a port separator,
# so hostname comes back as 'fd12' / 'fe80', which matches no blocked range and slips through.
check(
    "limitation: UNBRACKETED IPv6 literal bypasses the guard (urlparse mis-parses it)",
    not blocked("http://fd12:3456::1/x") and urlparse("http://fd12:3456::1/x").hostname == "fd12",
)

# ---------------------------------------------------------------- rendering / injection (YamlLoader)
TEMPLATE_RE = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_.]*)\s*\}\}")


def sanitize_url_component(value: str) -> str:
    return quote(str(value), safe="-_.~")


class TemplateRenderError(Exception):
    pass


def render_template(template: str, values: dict[str, str], sanitize: bool = True) -> str:
    def replace(match: re.Match) -> str:
        key = match.group(1)
        if key not in values:
            raise TemplateRenderError(f"Missing template variable: {key}")
        value = values[key]
        return sanitize_url_component(value) if sanitize else str(value)

    return TEMPLATE_RE.sub(replace, template)


print("== 6. Placeholder rendering + URL-component sanitization")
check(
    "substitutes {{address}}",
    render_template("http://ip-api.com/json/{{address}}", {"address": "8.8.8.8"})
    == "http://ip-api.com/json/8.8.8.8",
)
# injection attempt: value that would break out of the URL path / add a host
evil = '127.0.0.1/x?y=1#@attacker.example'
rendered = render_template("http://api.example.com/v1/{{key}}", {"key": evil})
check(
    "percent-encodes injection payload (safe=-_.~)",
    rendered == f"http://api.example.com/v1/{quote(evil, safe='-_.~')}",
)
check(
    "encoded payload cannot alter URL structure",
    urlparse(rendered).hostname == "api.example.com" and "@" not in (urlparse(rendered).path or ""),
)
try:
    render_template("http://x/{{missing}}", {})
    check("missing variable raises TemplateRenderError", False)
except TemplateRenderError:
    check("missing variable raises TemplateRenderError", True)

print("== 7. Dot-notation extraction (extract_nested_value)")


def extract_nested_value(data, path: str):
    if not path:
        return data
    current = data
    for part in path.split("."):
        if current is None:
            return None
        if isinstance(current, list):
            try:
                idx = int(part)
            except ValueError:
                return None
            if 0 <= idx < len(current):
                current = current[idx]
            else:
                return None
        elif isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


nested = {"data": {"results": [{"ip": "1.2.3.4"}, {"ip": "5.6.7.8"}]}}
check("dot path into nested list item", extract_nested_value(nested, "data.results.0.ip") == "1.2.3.4")
check("out-of-range index -> None (not exception)", extract_nested_value(nested, "data.results.9.ip") is None)
check("missing key -> None", extract_nested_value({"a": 1}, "b.c.d") is None)

# ---------------------------------------------------------------- retry policy (template_enricher.py + types.py)


class RetryConfig:
    def __init__(self):
        self.max_retries = 3          # default, bounds 0-10
        self.backoff_factor = 0.5     # default, bounds 0.1-10.0 (seconds)
        self.retry_on_status = [429, 500, 502, 503, 504]


def backoff_waits(cfg: RetryConfig):
    return [cfg.backoff_factor * (2 ** attempt) for attempt in range(cfg.max_retries)]


print("== 8. Exponential backoff schedule")
waits = backoff_waits(RetryConfig())
check(
    "default factor 0.5, retries 3 -> waits [0.5, 1.0, 2.0] s",
    waits == [0.5, 1.0, 2.0],
)


def retry_decision(status: int, cfg: RetryConfig = None):
    """Mirrors _make_request_with_retry's decision logic."""
    cfg = cfg or RetryConfig()
    if status in cfg.retry_on_status:
        return "retry"
    if 400 <= status < 500 and status not in cfg.retry_on_status:
        return "raise"   # client errors don't fix themselves (except listed ones)
    return "ok"


print("== 9. Retry decision table")
for status, expected in [
    (200, "ok"), (429, "retry"), (500, "retry"), (502, "retry"),
    (503, "retry"), (504, "retry"), (404, "raise"), (401, "raise"), (403, "raise"),
]:
    check(f"status {status} -> {expected}", retry_decision(status) == expected)

# custom config: a 4xx CAN be retried if explicitly listed
cfg = RetryConfig()
cfg.retry_on_status = [429, 500, 502, 503, 504, 418]
check("explicitly-listed 4xx (418) -> retry", retry_decision(418, cfg) == "retry")

# ---------------------------------------------------------------- summary
print()
if FAILS:
    print(f"RESULT: {len(FAILS)} FAILED / {COUNT - len(FAILS)} passed (of {COUNT})")
    raise SystemExit(len(FAILS))
print(f"RESULT: all {COUNT} checks PASSED (guard ranges, schemes, hostnames, both documented "
      f"limitations, sanitization, dot-notation extraction, backoff schedule, retry decision table)")
