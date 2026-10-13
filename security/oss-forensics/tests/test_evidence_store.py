"""scripts/evidence-store.py: the CLI round trip, and `verify` catching every kind of
tampering a forensic store must detect (edited content, a deleted entry, a re-used id,
an entry with no custody record), plus a mistyped store path never verifying clean."""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "evidence-store.py"


def cli(store, *args):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--store", str(store), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    return proc.returncode, proc.stdout, proc.stderr


@pytest.fixture
def store(tmp_path):
    path = tmp_path / "evidence.json"
    for i, (typ, actor) in enumerate([("git", "mallory"), ("ioc", "mallory"), ("manual", None)]):
        args = ["add", "--source", f"src{i}", "--content", f"content {i}", "--type", typ]
        if actor:
            args += ["--actor", actor]
        rc, out, err = cli(path, *args)
        assert rc == 0 and f"EV-000{i + 1}" in out, err
    return path


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def test_round_trip(store):
    rc, out, _ = cli(store, "list", "--actor", "mallory")
    assert rc == 0 and out.count("[EV-") == 2
    rc, out, _ = cli(store, "query", "CONTENT 2")
    assert rc == 0 and "Found 1 result(s)" in out and "EV-0003" in out
    rc, out, _ = cli(store, "verify")
    assert rc == 0 and "All 3 evidence entries passed" in out
    rc, out, _ = cli(store, "export")
    assert rc == 0 and "| EV-0001 | git |" in out


def test_timestamps_are_valid_iso8601(store):
    """They used to end '+00:00Z', which fromisoformat (and strict parsers) reject."""
    data = load(store)
    stamps = [data["metadata"]["created_at"], data["evidence"][0]["collected_at"]]
    for ts in stamps:
        assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", ts), ts
        datetime.fromisoformat(ts.replace("Z", "+00:00"))


def test_edited_content_is_caught(store):
    data = load(store)
    data["evidence"][1]["content"] = "rewritten"
    save(store, data)
    rc, out, _ = cli(store, "verify")
    assert rc == 1 and "[EV-0002] sha256 mismatch" in out


def test_deleted_entry_is_caught(store):
    """Hash-only verify passed this: nothing remained to re-hash."""
    data = load(store)
    del data["evidence"][1]
    save(store, data)
    rc, out, _ = cli(store, "verify")
    assert rc == 1 and "[EV-0002] logged as added but the entry is gone" in out


def test_id_is_never_reissued_after_a_deletion(store):
    data = load(store)
    del data["evidence"][2]  # EV-0003 removed; len()+1 would hand out EV-0003 again
    save(store, data)
    rc, out, _ = cli(store, "add", "--source", "s", "--content", "c", "--type", "manual")
    assert rc == 0 and "EV-0004" in out


def test_duplicate_id_is_caught(store):
    data = load(store)
    data["evidence"][2]["id"] = "EV-0001"
    save(store, data)
    rc, out, _ = cli(store, "verify")
    assert rc == 1 and "[EV-0001] duplicate evidence id" in out


def test_entry_without_custody_record_is_caught(store):
    data = load(store)
    data["chain_of_custody"] = [
        c for c in data["chain_of_custody"] if c["evidence_id"] != "EV-0001"
    ]
    save(store, data)
    rc, out, _ = cli(store, "verify")
    assert rc == 1 and "[EV-0001] no 'add' record in chain_of_custody" in out


@pytest.mark.parametrize("command", ["verify", "list", "summary", "export"])
def test_missing_store_is_an_error(tmp_path, command):
    rc, out, err = cli(tmp_path / "typo.json", command)
    assert rc == 1 and "no evidence store" in err and "passed" not in out
    assert not (tmp_path / "typo.json").exists()


def test_corrupt_store_is_an_error(tmp_path):
    bad = tmp_path / "evidence.json"
    bad.write_text("{not json", encoding="utf-8")
    rc, _, err = cli(bad, "verify")
    assert rc == 1 and "Error loading evidence store" in err
