#!/usr/bin/env python3
"""Self-test for perf_audit.py: one clean site must pass, and each rule must fire on a planted defect.

Stdlib only. Exit code = number of failed checks (0 = all pass).
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE / "perf_audit.py"
FAILS: list[str] = []
COUNT = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global COUNT
    COUNT += 1
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + ("" if cond else f"  [{detail}]"))
    if not cond:
        FAILS.append(name)


def run(root: Path, *args: str) -> tuple[int, str]:
    p = subprocess.run(
        [sys.executable, str(AUDIT), "--root", str(root), *args, str(root)],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    return p.returncode, p.stdout + p.stderr


GOOD_HTML = """<!doctype html><html><head><meta charset=utf-8>
<link rel="preconnect" href="https://fonts.gstatic.com">
<link rel="stylesheet" href="css/site.min.css">
<script src="js/app.js" defer></script></head>
<body><img src="a.png" width="10" height="10" loading="lazy"><p>hi</p></body></html>"""

GOOD_CSS = "@font-face{font-family:F;src:url(../f.woff2) format('woff2');font-display:swap}body{margin:0}"

BAD_HTML = """<!doctype html><html><head><meta charset=utf-8>
<script src="js/blocking.js"></script>
<link rel="stylesheet" href="css/late.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=X">
</head><body>
<style>p{color:red}</style>
<img src="a.png"><img src="b.png" width="1" height="1"><img src="c.png" width="1" height="1"><img src="d.png" width="1" height="1">
<img src="data:image/png;base64,{b64}" width="1" height="1">
<iframe src="x.html"></iframe><iframe src="y.html"></iframe><iframe src="z.html"></iframe>
</body></html>"""

BAD_CSS = "@font-face{font-family:G;src:url(../big.ttf)}\n" + "a {\n  color: red;\n}\n" * 400
BAD_JS = "function f() {\n  return 1;\n}\n" * 400


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        good = Path(td) / "good"
        (good / "css").mkdir(parents=True)
        (good / "js").mkdir()
        (good / "index.html").write_text(GOOD_HTML, encoding="utf-8")
        (good / "css" / "site.min.css").write_text(GOOD_CSS, encoding="utf-8")
        (good / "js" / "app.js").write_text("console.log(1)", encoding="utf-8")
        (good / "a.png").write_bytes(b"x" * 100)
        (good / "f.woff2").write_bytes(b"w" * 100)
        rc, out = run(good)
        check("clean site -> exit 0", rc == 0, out)
        check("clean site -> 'clean' message", "clean" in out, out)

        bad = Path(td) / "bad"
        (bad / "css").mkdir(parents=True)
        (bad / "js").mkdir()
        (bad / "index.html").write_text(BAD_HTML.replace("{b64}", "A" * 3000), encoding="utf-8")
        (bad / "css" / "late.css").write_text(BAD_CSS, encoding="utf-8")
        (bad / "js" / "blocking.js").write_text(BAD_JS, encoding="utf-8")
        (bad / "big.ttf").write_bytes(b"t" * 400 * 1024)
        (bad / "a.png").write_bytes(b"p" * 1600 * 1024)
        rc, out = run(bad)
        check("planted-defect site -> exit 1", rc == 1, out)
        for rule in (
            "img-dimensions", "img-base64", "script-blocking", "css-after-js", "style-in-body",
            "iframe-count", "font-format", "font-display", "font-preconnect", "not-minified",
            "font-weight", "page-weight",
        ):
            check(f"rule fires: {rule}", f": {rule}:" in out, out)
        check("rule fires: img-lazy (5 imgs, none lazy)", ": img-lazy:" in out, out)
        check("output lines carry file:line", "index.html:" in out, out)

        # each rule is individually silenceable by fixing the defect (guards against always-on rules)
        fixed = Path(td) / "fixed"
        fixed.mkdir()
        (fixed / "index.html").write_text(
            '<!doctype html><html><head><script src="x.js" defer></script></head>'
            '<body><img src="a.png" width="2" height="2" loading="lazy"></body></html>',
            encoding="utf-8",
        )
        rc, out = run(fixed)
        check("defects fixed -> exit 0 again", rc == 0, out)

        # thresholds are honoured
        rc, out = run(good, "--max-page-kb", "0")
        check("--max-page-kb 0 makes the clean site fail page-weight", rc == 1 and ": page-weight:" in out, out)
        rc, _ = run(Path(td) / "does-not-exist")
        check("missing path -> non-zero", rc != 0)
    print(f"\n{COUNT - len(FAILS)}/{COUNT} checks passed")
    return len(FAILS)


if __name__ == "__main__":
    sys.exit(main())
