#!/usr/bin/env python3
"""Read-only, context-safe stats for a Claude Code session transcript (.jsonl).

Implements the "measure before reading" and "repeated work" steps of
references/session-diagnosis-protocol.md. Output is bounded: every quoted
field is cut to --cut characters and no record is ever printed whole.

    python transcript_stats.py SESSION.jsonl [--cut 120] [--repeat 3]

Prints: size and long lines, record-type counts, token totals counted once per
API message id (streamed records repeat the same usage), the five largest tool
results, gaps over ten minutes, and tool calls repeated at or over --repeat.
"""
import argparse
import collections
import json
import sys
from datetime import datetime

LONG_LINE = 100_000


def load(path):
    """Yield (line_no, raw_len, record_or_None) without holding the file in memory twice."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        for n, line in enumerate(fh, 1):
            try:
                yield n, len(line), json.loads(line)
            except ValueError:
                yield n, len(line), None


def cut(text, n):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 3] + "..."


def blocks(rec):
    content = (rec.get("message") or {}).get("content")
    return content if isinstance(content, list) else []


def block_size(b):
    c = b.get("content")
    if isinstance(c, str):
        return len(c)
    if isinstance(c, list):
        return sum(len(x.get("text", "")) for x in c if isinstance(x, dict))
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--cut", type=int, default=120)
    ap.add_argument("--repeat", type=int, default=3)
    a = ap.parse_args(argv)

    types = collections.Counter()
    long_lines, bad = [], 0
    usage_by_msg = {}
    usage_naive = collections.Counter()
    results = []
    stamps = []
    calls = collections.defaultdict(list)
    total_bytes = lines = 0

    for n, size, rec in load(a.path):
        lines, total_bytes = n, total_bytes + size
        if size > LONG_LINE:
            long_lines.append((n, size))
        if rec is None:
            bad += 1
            continue
        types[rec.get("type", "?")] += 1
        ts = rec.get("timestamp")
        if ts:
            try:
                stamps.append((datetime.fromisoformat(ts.replace("Z", "+00:00")), n))
            except ValueError:
                pass
        msg = rec.get("message") or {}
        u = msg.get("usage")
        if rec.get("type") == "assistant" and isinstance(u, dict):
            for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"):
                usage_naive[k] += u.get(k) or 0
            usage_by_msg[msg.get("id") or f"line{n}"] = u  # last record per message id wins
        for b in blocks(rec):
            if b.get("type") == "tool_result":
                results.append((block_size(b), n, b.get("tool_use_id", "")))
            elif b.get("type") == "tool_use":
                inp = b.get("input") or {}
                key = (inp.get("file_path") or inp.get("command") or inp.get("pattern")
                       or inp.get("description") or inp.get("query") or json.dumps(inp, sort_keys=True))
                calls[(b.get("name", "?"), cut(key, 200))].append(n)

    print(f"file: {a.path}\nlines: {lines}  bytes: {total_bytes}  unparsable: {bad}")
    print("lines over 100k chars:", ", ".join(f"{n}({s})" for n, s in long_lines) or "none")
    print("record types:", dict(types.most_common()))

    once = collections.Counter()
    for u in usage_by_msg.values():
        for k in usage_naive:
            once[k] += u.get(k) or 0
    print("\ntokens, once per message id  :", dict(once))
    print("tokens, naive sum of records :", dict(usage_naive))
    print(f"assistant records vs distinct message ids: {types.get('assistant', 0)} vs {len(usage_by_msg)}")

    print("\nlargest tool results (chars, line):")
    for size, n, tid in sorted(results, reverse=True)[:5]:
        print(f"  {size:>9}  line {n}  {tid[:14]}")

    stamps.sort()
    gaps = [(b[0] - a_[0], a_[1], b[1]) for a_, b in zip(stamps, stamps[1:])]
    big = [g for g in gaps if g[0].total_seconds() > 600]
    print(f"\ngaps over 10 min: {len(big)}")
    for g, l1, l2 in sorted(big, reverse=True)[:5]:
        print(f"  {g}  between lines {l1} and {l2}")

    print(f"\ntool calls repeated >= {a.repeat}:")
    shown = 0
    for (tool, key), at in sorted(calls.items(), key=lambda kv: -len(kv[1])):
        if len(at) >= a.repeat:
            print(f"  {len(at)}x {tool}: {cut(key, a.cut)}  (lines {at[0]}..{at[-1]})")
            shown += 1
            if shown == 15:
                break
    if not shown:
        print("  none")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
