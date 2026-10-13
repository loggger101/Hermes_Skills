"""scripts/har_to_client.py on synthetic HAR files: API filtering, {id} grouping, header and
body capture, replay hints, the real scheme, decoded base64 bodies, and the no-API exit."""

import base64
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "har_to_client.py"
UA = "Mozilla/5.0 (Test)"


def entry(
    method,
    url,
    *,
    mime="application/json",
    rtype="xhr",
    body="",
    status=200,
    headers=(),
    post=None,
    encoding=None,
    query=(),
):
    content = {"mimeType": mime, "text": body}
    if encoding:
        content["encoding"] = encoding
    req = {
        "method": method,
        "url": url,
        "headers": [{"name": "User-Agent", "value": UA}, *headers],
        "queryString": [{"name": k, "value": v} for k, v in query],
    }
    if post:
        req["postData"] = {"mimeType": "application/json", "text": post}
    return {
        "_resourceType": rtype,
        "request": req,
        "response": {"status": status, "content": content},
    }


def run(tmp_path, entries, *args):
    har = tmp_path / "x.har"
    har.write_text(json.dumps({"log": {"entries": entries}}), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(har), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    return proc.returncode, proc.stdout


def test_groups_ids_and_filters_static(tmp_path):
    entries = [
        entry(
            "GET", "https://api.example.com/v1/items/123", body='{"id": 123}', query=[("page", "1")]
        ),
        entry("GET", "https://api.example.com/v1/items/456", body='{"id": 456}'),
        entry("GET", "https://cdn.example.com/app.js", mime="text/javascript", rtype="script"),
        entry("GET", "https://example.com/logo.png", mime="image/png", rtype="image"),
        entry(
            "POST",
            "https://api.example.com/v1/login",
            post='{"user": "u"}',
            headers=[{"name": "Authorization", "value": "Bearer abc"}],
        ),
    ]
    rc, out = run(tmp_path, entries)
    assert rc == 0, out
    assert "=== GET https://api.example.com/v1/items/{id}  (x2)" in out
    assert "page = 1" in out
    assert "=== POST https://api.example.com/v1/login  (x1)" in out
    assert 'request body (application/json):\n    {"user": "u"}' in out
    assert "authorization: Bearer abc" in out
    assert "app.js" not in out and "logo.png" not in out
    assert f"User-Agent (send this): {UA}" in out
    assert "Authorization/token header present" in out
    assert out.rstrip().endswith("2 distinct endpoints.")


def test_include_static_and_host_filter(tmp_path):
    entries = [
        entry("GET", "https://cdn.example.com/app.js", mime="text/javascript", rtype="script"),
        entry("GET", "https://api.other.org/q", body="{}"),
    ]
    rc, out = run(tmp_path, entries, "--include-static", "--host", "cdn.")
    assert rc == 0 and "app.js" in out and "api.other.org" not in out


def test_http_endpoint_keeps_its_scheme(tmp_path):
    """Round-257: this printed 'https://legacy.example.com/status'."""
    rc, out = run(tmp_path, [entry("GET", "http://legacy.example.com/status", body="{}")])
    assert rc == 0 and "=== GET http://legacy.example.com/status" in out


def test_same_path_on_two_schemes_is_two_endpoints(tmp_path):
    entries = [
        entry("GET", "http://h.example.com/a", body="{}"),
        entry("GET", "https://h.example.com/a", body="{}"),
    ]
    rc, out = run(tmp_path, entries)
    assert rc == 0 and "2 distinct endpoints." in out


def test_base64_body_is_decoded(tmp_path):
    """Round-257: the raw base64 string was printed as if it were the body."""
    b64 = base64.b64encode(b'{"hello": "world"}').decode()
    rc, out = run(tmp_path, [entry("GET", "https://a.example.com/x", body=b64, encoding="base64")])
    assert rc == 0 and '{"hello": "world"}' in out and b64 not in out


def test_binary_and_broken_base64_are_labelled(tmp_path):
    binary = base64.b64encode(bytes(range(200, 256))).decode()
    entries = [
        entry("GET", "https://a.example.com/bin", body=binary, encoding="base64"),
        entry("GET", "https://a.example.com/bad", body="@@not-base64@@", encoding="base64"),
    ]
    rc, out = run(tmp_path, entries)
    assert rc == 0
    assert "[binary body, 56 bytes]" in out
    assert "[undecodable base64 body] @@not-base64@@" in out


def test_body_is_truncated(tmp_path):
    body = json.dumps({"k": "v" * 2000})
    rc, out = run(
        tmp_path, [entry("GET", "https://a.example.com/big", body=body)], "--max-body", "50"
    )
    assert rc == 0 and "v" * 200 not in out


def test_no_api_traffic_exits_1(tmp_path):
    rc, out = run(
        tmp_path, [entry("GET", "https://e.example.com/s.css", mime="text/css", rtype="stylesheet")]
    )
    assert rc == 1 and "No API-looking entries found" in out
