"""scripts/feed.py against a local HTTP server: RSS 2.0, Atom, RSS 1.0 and JSON Feed parsing,
discovery, --since/--limit, and the round-257 cases (guessed paths printed as discovered
feeds, undated entries dropped by --since without a word)."""

import http.server
import json
import subprocess
import sys
import threading
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "feed.py"

RSS = b"""<?xml version="1.0"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/"><channel><title>Blog &amp; Co</title>
<item><title>New</title><link>https://b/new</link><pubDate>Mon, 12 Oct 2026 10:00:00 GMT</pubDate>
<description>&lt;p&gt;Hello &lt;b&gt;world&lt;/b&gt;&lt;/p&gt;</description><dc:creator>Ann</dc:creator></item>
<item><title>Old</title><link>https://b/old</link><pubDate>Tue, 01 Sep 2026 10:00:00 GMT</pubDate></item>
<item><title>Undated</title><link>https://b/undated</link></item>
</channel></rss>"""
ATOM = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><title>A</title>
<entry><title>E1</title><link rel="self" href="https://a/self"/><link rel="alternate" href="https://a/1"/>
<updated>2026-10-10T08:00:00Z</updated><author><name>Bo</name></author><summary>s1</summary></entry></feed>"""
RDF = b"""<?xml version="1.0"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
xmlns="http://purl.org/rss/1.0/"><channel><title>R</title></channel>
<item><title>R1</title><link>https://r/1</link></item></rdf:RDF>"""
JSONFEED = json.dumps(
    {
        "version": "https://jsonfeed.org/version/1.1",
        "title": "J",
        "items": [
            {
                "id": "1",
                "url": "https://j/1",
                "title": "J1",
                "date_published": "2026-10-01T00:00:00Z",
                "authors": [{"name": "Cy"}],
            }
        ],
    }
).encode()


@pytest.fixture
def site():
    pages = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in pages:
                self.send_error(404)
                return
            body, ctype = pages[self.path]
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield pages, f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


def feed(*args):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    return proc.returncode, proc.stdout, proc.stderr


def read_json(url, *extra):
    rc, out, err = feed("read", url, "--json", *extra)
    assert rc == 0, err
    return json.loads(out), err


@pytest.mark.parametrize(
    "body, ctype, fmt, first",
    [
        (RSS, "application/rss+xml", "rss", ("New", "https://b/new", "Ann")),
        (ATOM, "application/atom+xml", "atom", ("E1", "https://a/1", "Bo")),
        (RDF, "application/rdf+xml", "rss", ("R1", "https://r/1", "")),
        (JSONFEED, "application/feed+json", "jsonfeed", ("J1", "https://j/1", "Cy")),
    ],
)
def test_formats(site, body, ctype, fmt, first):
    pages, base = site
    pages["/f"] = (body, ctype)
    doc, _ = read_json(f"{base}/f")
    e = doc["entries"][0]
    assert doc["format"] == fmt and (e["title"], e["link"], e["author"] or "") == first


def test_html_is_stripped_and_dates_normalised(site):
    pages, base = site
    pages["/f"] = (RSS, "application/rss+xml")
    doc, _ = read_json(f"{base}/f")
    new = doc["entries"][0]
    assert doc["title"] == "Blog & Co"
    assert new["summary"] == "Hello world" and new["published"] == "2026-10-12T10:00:00+00:00"


def test_since_and_limit_announce_undated(site):
    pages, base = site
    pages["/f"] = (RSS, "application/rss+xml")
    doc, err = read_json(f"{base}/f", "--since", "2026-10-01")
    assert [e["title"] for e in doc["entries"]] == ["New"]
    assert "1 undated entr(y/ies) left out by --since" in err
    doc, _ = read_json(f"{base}/f", "--limit", "1")
    assert len(doc["entries"]) == 1


def test_read_discovers_the_advertised_feed(site):
    pages, base = site
    pages["/"] = (
        b'<html><head><link rel="alternate" type="application/atom+xml" href="/atom"></head></html>',
        "text/html",
    )
    pages["/atom"] = (ATOM, "application/atom+xml")
    doc, _ = read_json(f"{base}/")
    assert doc["url"] == f"{base}/atom" and doc["discovered_from"] == f"{base}/"


def test_read_falls_back_to_common_paths(site):
    pages, base = site
    pages["/"] = (b"<html><head></head></html>", "text/html")
    pages["/rss.xml"] = (RSS, "application/rss+xml")
    doc, _ = read_json(f"{base}/")
    assert doc["url"] == f"{base}/rss.xml"


def test_discover_lists_advertised_feeds_only(site):
    pages, base = site
    pages["/"] = (
        b'<link rel="alternate" type="application/rss+xml" href="/a.xml">'
        b'<link rel="stylesheet" type="text/css" href="/s.css">'
        b'<link rel="alternate" type="application/feed+json" href="https://x/f.json">',
        "text/html",
    )
    rc, out, _ = feed("discover", f"{base}/")
    assert rc == 0 and out.split() == [f"{base}/a.xml", "https://x/f.json"]


def test_discover_with_nothing_advertised_is_not_a_list_of_guesses(site):
    """Round-257: this printed nine guessed paths as if the page had advertised them."""
    pages, base = site
    pages["/"] = (b"<html></html>", "text/html")
    rc, out, err = feed("discover", f"{base}/")
    assert rc == 1 and out == "" and "no feed advertised" in err


def test_no_feed_anywhere_fails(site):
    pages, base = site
    pages["/"] = (b"<html></html>", "text/html")
    rc, _, err = feed("read", f"{base}/")
    assert rc == 1 and "no feed found" in err and "tried 9 candidates" in err


def test_http_error_and_bad_xml(site):
    pages, base = site
    rc, _, err = feed("read", f"{base}/missing")
    assert rc == 2 and "HTTP 404" in err
    pages["/bad"] = (b"<rss><channel><item>", "application/rss+xml")
    rc, _, err = feed("read", f"{base}/bad")
    assert rc == 2 and err.startswith("error:")
