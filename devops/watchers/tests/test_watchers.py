"""The watcher scripts and their shared watermark, offline.

watch_http_json and watch_rss run as real subprocesses against a local HTTP server, the way
cron runs them; watch_github is imported with urlopen stubbed (its API host is fixed). The
round-257 cases are the silent ones: a corrupt state file re-baselining (dropping every
item since the last good run), trimming that forgot random IDs, overflow past --max lost
without a word, a mistyped --id-field that can never fire, and a non-feed read as empty.
"""

import http.server
import importlib.util
import io
import json
import os
import subprocess
import sys
import threading
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load(name):
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path.remove(str(SCRIPTS))


@pytest.fixture
def state(tmp_path, monkeypatch):
    d = tmp_path / "state"
    monkeypatch.setenv("WATCHER_STATE_DIR", str(d))
    return d


@pytest.fixture
def server():
    """Serves whatever bytes the test puts in `pages[path]`."""
    pages = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in pages:
                self.send_error(404)
                return
            body = pages[self.path]
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    httpd = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield pages, f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()


def run(script, state_dir, *args):
    env = dict(os.environ, WATCHER_STATE_DIR=str(state_dir))
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=60,
    )
    return proc.returncode, proc.stdout, proc.stderr


# ------------------------------------------------------------------------- watermark
def test_first_run_baselines_then_emits_only_new(state):
    wm = load("_watermark")
    w = wm.Watermark.load("t")
    assert w.filter_new([{"id": 1}, {"id": 2}]) == [] and w.is_first_run is False
    w.save()
    w = wm.Watermark.load("t")
    assert w.filter_new([{"id": 2}, {"id": 3}]) == [{"id": 3}]


def test_corrupt_state_is_an_error_not_a_rebaseline(state):
    wm = load("_watermark")
    state.mkdir(parents=True)
    for content in ("{truncated", '["not", "an", "object"]', '{"seen_ids": "abc"}'):
        (state / "t.json").write_text(content, encoding="utf-8")
        with pytest.raises(wm.WatermarkError, match="unusable"):
            wm.Watermark.load("t")


def test_trim_keeps_the_current_batch_and_drops_the_oldest(state):
    """The trim went through a set: it dropped arbitrary IDs, even ones still in the feed."""
    wm = load("_watermark")
    w = wm.Watermark.load("t", max_seen=5)
    w.filter_new([{"id": i} for i in range(5)])  # baseline 0..4
    batch = [{"id": i} for i in (3, 4, 5, 6)]  # 3 and 4 still present
    assert [i["id"] for i in w.filter_new(batch)] == [5, 6]
    assert w.seen == ["2", "3", "4", "5", "6"]
    assert w.filter_new(batch) == []  # nothing in the live batch is ever forgotten


def test_trim_order_survives_save_and_load(state):
    wm = load("_watermark")
    w = wm.Watermark.load("t", max_seen=3)
    w.filter_new([{"id": "a"}, {"id": "b"}, {"id": "c"}])
    w.save()
    w = wm.Watermark.load("t", max_seen=3)
    w.filter_new([{"id": "d"}])
    assert w.seen == ["b", "c", "d"]


def test_missing_ids_are_counted(state):
    wm = load("_watermark")
    w = wm.Watermark.load("t")
    w.filter_new([{"id": 1}, {"x": 2}, {"x": 3}])
    assert w.missing_id == 2


def test_markdown_announces_overflow():
    wm = load("_watermark")
    out = wm.format_items_as_markdown([{"title": "A", "url": "u"}], not_shown=3)
    assert "## A\nu" in out and "_3 more new item(s) not shown" in out
    assert wm.format_items_as_markdown([]) == ""


def test_bad_watermark_name_is_rejected(state):
    with pytest.raises(ValueError):
        load("_watermark").Watermark("../escape")


# ------------------------------------------------------------------- watch_http_json
def put_json(pages, path, items):
    pages[path] = json.dumps({"data": {"events": items}}).encode()


def test_http_json_flow(state, server):
    pages, base = server
    url = f"{base}/api"
    args = ["--name", "j", "--url", url, "--items-path", "data.events", "--max", "2"]
    put_json(pages, "/api", [{"id": 1, "title": "one", "url": "u1"}])
    assert run("watch_http_json.py", state, *args) == (0, "", "")  # baseline: silent
    put_json(pages, "/api", [{"id": i, "title": f"t{i}", "url": f"u{i}"} for i in range(1, 6)])
    rc, out, _ = run("watch_http_json.py", state, *args)
    assert rc == 0 and out.count("## t") == 2
    assert "_2 more new item(s) not shown (over --max); they are marked seen._" in out
    assert run("watch_http_json.py", state, *args)[1] == ""  # all seen now


def test_http_json_wrong_id_field_fails(state, server):
    pages, base = server
    put_json(pages, "/api", [{"id": 1}, {"id": 2}])
    args = [
        "--name",
        "j",
        "--url",
        f"{base}/api",
        "--items-path",
        "data.events",
        "--id-field",
        "uid",
    ]
    rc, _, err = run("watch_http_json.py", state, *args)
    assert rc == 2 and "none of the 2 item(s) has the id field 'uid'" in err
    assert not (state / "j.json").exists()  # nothing recorded on a failed tick


def test_http_json_partial_ids_and_non_objects_warn(state, server):
    pages, base = server
    put_json(pages, "/api", [{"id": 1}, {"other": 2}, "stray"])
    rc, _, err = run(
        "watch_http_json.py",
        state,
        "--name",
        "j",
        "--url",
        f"{base}/api",
        "--items-path",
        "data.events",
    )
    assert rc == 0
    assert "1 of 3 item(s) are not objects" in err and "1 of 2 item(s) lack 'id'" in err


@pytest.mark.parametrize(
    "path, body, needle",
    [
        ("/api", b"<html>", "not valid JSON"),
        ("/api", json.dumps({"data": {}}).encode(), "did not resolve to a list"),
        ("/missing", None, "HTTP 404"),
    ],
)
def test_http_json_bad_responses(state, server, path, body, needle):
    pages, base = server
    if body is not None:
        pages[path] = body
    rc, _, err = run(
        "watch_http_json.py",
        state,
        "--name",
        "j",
        "--url",
        f"{base}{path}",
        "--items-path",
        "data.events",
    )
    assert rc == 2 and needle in err


def test_corrupt_state_stops_the_watcher(state, server):
    pages, base = server
    put_json(pages, "/api", [{"id": 1}])
    state.mkdir(parents=True)
    (state / "j.json").write_text("{oops", encoding="utf-8")
    rc, out, err = run(
        "watch_http_json.py",
        state,
        "--name",
        "j",
        "--url",
        f"{base}/api",
        "--items-path",
        "data.events",
    )
    assert rc == 2 and out == "" and "is unusable" in err
    assert (state / "j.json").read_text(encoding="utf-8") == "{oops"  # left for inspection


# ------------------------------------------------------------------------- watch_rss
RSS = """<?xml version="1.0"?><rss version="2.0"><channel>{}</channel></rss>"""
ATOM = """<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">{}</feed>"""


def rss_items(n):
    return "".join(
        f"<item><guid>g{i}</guid><title>T{i}</title><link>https://x/{i}</link>"
        f"<description>d{i}</description></item>"
        for i in range(n)
    )


def test_rss_flow_with_summary(state, server):
    pages, base = server
    pages["/f"] = RSS.format(rss_items(1)).encode()
    args = ["--name", "r", "--url", f"{base}/f", "--with-summary"]
    assert run("watch_rss.py", state, *args)[0:2] == (0, "")
    pages["/f"] = RSS.format(rss_items(3)).encode()
    rc, out, _ = run("watch_rss.py", state, *args)
    assert rc == 0 and "## T1\nhttps://x/1\n\nd1" in out and "## T2" in out and "## T0" not in out


def test_atom_entries_use_id_and_href(state, server):
    pages, base = server
    entry = '<entry><id>urn:a{0}</id><title>A{0}</title><link href="https://a/{0}"/></entry>'
    pages["/a"] = ATOM.format(entry.format(0)).encode()
    run("watch_rss.py", state, "--name", "a", "--url", f"{base}/a")
    pages["/a"] = ATOM.format(entry.format(0) + entry.format(1)).encode()
    rc, out, _ = run("watch_rss.py", state, "--name", "a", "--url", f"{base}/a")
    assert rc == 0 and out.startswith("## A1\nhttps://a/1")


def test_html_page_is_not_an_empty_feed(state, server):
    pages, base = server
    pages["/f"] = b"<html><body><p>Please log in</p></body></html>"
    rc, _, err = run("watch_rss.py", state, "--name", "r", "--url", f"{base}/f")
    assert rc == 2 and "not an RSS/Atom feed" in err


def test_feed_without_guids_or_links_fails(state, server):
    pages, base = server
    pages["/f"] = RSS.format("<item><title>x</title></item>" * 2).encode()
    rc, _, err = run("watch_rss.py", state, "--name", "r", "--url", f"{base}/f")
    assert rc == 2 and "none of the 2 item(s) has the id field 'id'" in err


def test_invalid_xml_fails(state, server):
    pages, base = server
    pages["/f"] = b"<rss><channel>"
    rc, _, err = run("watch_rss.py", state, "--name", "r", "--url", f"{base}/f")
    assert rc == 2 and "invalid XML" in err


# ---------------------------------------------------------------------- watch_github
class FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def github(monkeypatch, state, payload, *args):
    mod = load("watch_github")
    seen = {}

    def urlopen(req, timeout):
        seen["url"], seen["auth"] = req.full_url, req.get_header("Authorization")
        return FakeResp(json.dumps(payload).encode())

    monkeypatch.setattr(mod.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(sys, "argv", ["watch_github.py", *args])
    return mod.main(), seen


def issues(*ids):
    return [
        {"id": i, "title": f"I{i}", "html_url": f"https://gh/{i}", "user": {"login": "u"}}
        for i in ids
    ]


def test_github_issues_flow(monkeypatch, state, capsys):
    monkeypatch.setenv("GITHUB_TOKEN", "t0k")
    rc, seen = github(monkeypatch, state, issues(1), "--name", "g", "--repo", "o/r")
    assert rc == 0 and seen["url"].startswith("https://api.github.com/repos/o/r/issues")
    assert seen["auth"] == "Bearer t0k"
    capsys.readouterr()
    rc, _ = github(
        monkeypatch, state, issues(1, 2, 3), "--name", "g", "--repo", "o/r", "--max", "1"
    )
    out = capsys.readouterr().out
    assert rc == 0 and out.count("## I") == 1 and "_1 more new item(s) not shown" in out


def test_github_commits_are_flattened(monkeypatch, state, capsys):
    def commit(sha):
        return {
            "sha": sha,
            "html_url": f"https://gh/c/{sha}",
            "commit": {"message": f"fix {sha}\n\nbody", "author": {"name": "n", "date": "d"}},
        }

    github(monkeypatch, state, [commit("a")], "--name", "c", "--repo", "o/r", "--scope", "commits")
    capsys.readouterr()
    rc, _ = github(
        monkeypatch,
        state,
        [commit("a"), commit("b")],
        "--name",
        "c",
        "--repo",
        "o/r",
        "--scope",
        "commits",
    )
    assert rc == 0 and "## fix b  (n)" in capsys.readouterr().out


@pytest.mark.parametrize(
    "payload, args, needle",
    [
        ({"message": "Not Found"}, ["--repo", "o/r"], "expected a list"),
        ([], ["--repo", "not a repo"], "must be owner/name"),
        ([], [], "one of --repo or --search is required"),
    ],
)
def test_github_bad_input(monkeypatch, state, capsys, payload, args, needle):
    rc, _ = github(monkeypatch, state, payload, "--name", "g", *args)
    assert rc == 2 and needle in capsys.readouterr().err
