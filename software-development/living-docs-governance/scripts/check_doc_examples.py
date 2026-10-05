#!/usr/bin/env python3
"""Run the JavaScript examples in Markdown docs and compare printed output to the comments.

For every fenced ```js / ```javascript block that has `console.log(...)  // expected`
lines, run the block under Node, capture each console.log call (formatted with
util.inspect), and compare, in order, with the trailing `// expected` comments.

    python check_doc_examples.py docs/*.md          # exit 1 on any mismatch or crash
    python check_doc_examples.py --verbose page.md  # also print passing blocks

Rules (kept deliberately small):
  * Only console.log lines carrying a trailing `// ...` comment are checked, in order.
  * A block with no such lines is skipped. A block that throws is a FAIL unless its
    first line is `// throws`.
  * Comparison is whitespace-insensitive and treats 'x' and "x" as the same string.
  * A block marked `// no-run` on its first line is skipped (browser-only, pseudo-code).
Requires `node` on PATH. Stdlib only. Exit codes: 0 all good, 1 mismatches, 2 usage/runtime problem.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FENCE = re.compile(r"^```(?:js|javascript)\s*$")
LOG_LINE = re.compile(r"console\.log\(.*\)\s*;?\s*//\s*(.+?)\s*$")

PREAMBLE = r"""
const __util = require('util');
const __out = [];
console.log = (...a) => { __out.push(a.map(x => typeof x === 'string' ? x : __util.inspect(x, {depth: 4, breakLength: Infinity})).join(' ')); };
process.on('exit', () => { process.stdout.write('\n@@RESULT@@' + JSON.stringify(__out)); });
"""


def norm(s):
    s = s.strip().strip(";")
    s = re.sub(r"\s+", " ", s)
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"`":
        s = s[1:-1]
    return s.replace('"', "'")


def blocks(text):
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if FENCE.match(lines[i]):
            start = i + 1
            j = start
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            yield start + 1, lines[start:j]
            i = j
        i += 1


def run_block(code_lines, node):
    code = PREAMBLE + "\n".join(code_lines)
    with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False, encoding="utf-8") as f:
        f.write(code)
        path = f.name
    try:
        p = subprocess.run([node, path], capture_output=True, text=True, timeout=20, encoding="utf-8")
    finally:
        Path(path).unlink(missing_ok=True)
    out = None
    if "@@RESULT@@" in p.stdout:
        out = json.loads(p.stdout.split("@@RESULT@@", 1)[1])
    return p.returncode, out, p.stderr.strip().splitlines()[-1:] if p.stderr.strip() else []


def main(argv):
    verbose = "--verbose" in argv
    files = [a for a in argv if not a.startswith("--")]
    node = shutil.which("node")
    if not files or not node:
        print("usage: check_doc_examples.py [--verbose] FILE.md ...   (needs node on PATH)")
        return 2
    bad = checked = 0
    for fn in files:
        for lineno, code in blocks(Path(fn).read_text(encoding="utf-8")):
            first = code[0].strip() if code else ""
            if first.startswith("// no-run"):
                continue
            expected = []
            for ln in code:
                m = LOG_LINE.search(ln)
                if m:
                    expected.append(m.group(1))
            if not expected:
                continue
            checked += 1
            rc, out, err = run_block(code, node)
            if rc != 0 and not first.startswith("// throws"):
                bad += 1
                print(f"FAIL {fn}:{lineno}: block crashed (rc {rc}) {err}")
                continue
            got = out or []
            if len(got) != len(expected):
                bad += 1
                print(f"FAIL {fn}:{lineno}: {len(expected)} expected console.log value(s), program printed {len(got)}: {got}")
                continue
            diffs = [(i + 1, e, g) for i, (e, g) in enumerate(zip(expected, got)) if norm(e) != norm(g)]
            if diffs:
                bad += 1
                for i, e, g in diffs:
                    print(f"FAIL {fn}:{lineno}: console.log #{i} comment says {e!r} but printed {g!r}")
            elif verbose:
                print(f"ok   {fn}:{lineno}: {len(expected)} value(s)")
    print(f"{checked} block(s) checked, {bad} failing")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
