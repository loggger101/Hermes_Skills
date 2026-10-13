"""scripts/transcript_stats.py on synthetic Claude Code transcripts: usage counted once per
message id, gaps, repeats, largest results, and inputs that must not look like a quiet
session."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "transcript_stats.py"


def run(path, *args):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(path), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    return proc.returncode, proc.stdout, proc.stderr


def write(tmp_path, records, extra_lines=()):
    p = tmp_path / "s.jsonl"
    lines = [json.dumps(r) for r in records] + list(extra_lines)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def assistant(msg_id, ts, out_tokens, blocks=()):
    return {
        "type": "assistant",
        "timestamp": ts,
        "message": {"id": msg_id, "usage": {"output_tokens": out_tokens}, "content": list(blocks)},
    }


def tool_use(cmd):
    return {"type": "tool_use", "name": "Bash", "input": {"command": cmd}}


def test_stats_on_a_small_session(tmp_path):
    big = {"type": "tool_result", "tool_use_id": "toolu_big", "content": "x" * 5000}
    records = [
        {"type": "user", "timestamp": "2026-10-13T10:00:00Z", "message": {"content": "go"}},
        # one API message streamed as two records repeating the same usage
        assistant("m1", "2026-10-13T10:00:05Z", 100, [tool_use("pytest -q")]),
        assistant("m1", "2026-10-13T10:00:06Z", 100, [tool_use("pytest -q")]),
        assistant("m2", "2026-10-13T10:30:00Z", 7, [tool_use("pytest -q")]),  # 30 min gap
        {"type": "user", "timestamp": "2026-10-13T10:30:01Z", "message": {"content": [big]}},
    ]
    rc, out, err = run(write(tmp_path, records))
    assert rc == 0, err
    assert "unparsable: 0" in out
    once = next(ln for ln in out.splitlines() if ln.startswith("tokens, once per message id"))
    naive = next(ln for ln in out.splitlines() if ln.startswith("tokens, naive sum"))
    assert "'output_tokens': 107" in once and "'output_tokens': 207" in naive
    assert "assistant records vs distinct message ids: 3 vs 2" in out
    assert "gaps over 10 min: 1  (unparsable timestamps, not measured: 0)" in out
    assert "3x Bash: pytest -q" in out
    assert "5000  line 5  toolu_big" in out


def test_bad_lines_and_timestamps_are_counted(tmp_path):
    records = [
        {"type": "user", "timestamp": "not-a-time", "message": {}},
        {"type": "user", "timestamp": 12345, "message": {}},  # not a string
        {"type": "user", "timestamp": "2026-10-13T10:00:00Z", "message": {}},
    ]
    rc, out, _ = run(write(tmp_path, records, extra_lines=["{truncated", "[1, 2]"]))
    assert rc == 0
    assert "unparsable: 2" in out  # the broken line AND the non-record JSON list
    assert "(unparsable timestamps, not measured: 2)" in out


def test_not_a_transcript_fails(tmp_path):
    p = tmp_path / "notes.txt"
    p.write_text("just some notes\nnot json at all\n", encoding="utf-8")
    rc, _, err = run(p)
    assert rc == 1 and "not a .jsonl transcript" in err


def test_empty_file_fails(tmp_path):
    p = tmp_path / "empty.jsonl"
    p.write_text("", encoding="utf-8")
    rc, _, err = run(p)
    assert rc == 1 and "no JSON record" in err


def test_output_is_bounded_by_cut(tmp_path):
    long_cmd = "echo " + "y" * 500
    records = [assistant(f"m{i}", "2026-10-13T10:00:00Z", 1, [tool_use(long_cmd)]) for i in range(3)]
    rc, out, _ = run(write(tmp_path, records), "--cut", "40")
    assert rc == 0
    line = next(ln for ln in out.splitlines() if "3x Bash:" in ln)
    assert "y" * 60 not in line and "..." in line
