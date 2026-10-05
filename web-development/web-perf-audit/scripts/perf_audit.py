#!/usr/bin/env python3
"""Zero-dependency static-site audit of the machine-checkable Front-End Performance Checklist items.

Scans built HTML files (and the local CSS/JS/fonts/images they reference) and prints one
``file:line: rule: message`` finding per problem. Exit code 1 when there are findings, 0 when clean.

Rules (checklist item in brackets):
  img-dimensions     <img> without width and height                       [Images dimensions]
  img-base64         data: URI image larger than --max-data-uri bytes      [Avoid Base64 images]
  img-lazy           more than 3 <img> and none has loading="lazy"         [Lazy loading]
  script-blocking    <script src> in <head> without defer/async/module     [Non-blocking JavaScript]
  css-after-js       stylesheet <link> after a blocking script             [CSS before JavaScript]
  style-in-body      <style> element inside <body>                         [Embedded or inline CSS]
  iframe-count       more than --max-iframes <iframe> elements             [Minimize iframes]
  font-format        @font-face src without woff2                          [Webfont formats]
  font-display       @font-face without font-display                       [Prevent invisible text]
  font-preconnect    Google Fonts used without a preconnect link           [preconnect for fonts]
  font-weight        local font files above --max-font-kb in total         [Webfont size]
  not-minified       local CSS/JS that looks unminified                    [Minification]
  page-weight        HTML + local assets above --max-page-kb               [Page weight]

Usage: perf_audit.py [--root DIR] [--max-page-kb N] [--max-font-kb N] [--max-iframes N]
                     [--max-data-uri N] PATH...   (PATH = HTML file or directory)
"""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

LOCAL_SKIP = ("http:", "https:", "//", "data:", "mailto:", "tel:", "#", "javascript:")
FONT_RE = re.compile(r"url\(\s*['\"]?([^'\")]+?)['\"]?\s*\)", re.I)
FACE_RE = re.compile(r"@font-face\s*\{(.*?)\}", re.I | re.S)


class Page(HTMLParser):
    """Collect the facts the rules need, with line numbers."""

    max_data_uri = 2048

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_head = False
        self.in_body = False
        self.blocking_script_seen = False
        self.findings: list[tuple[int, str, str]] = []
        self.assets: list[str] = []
        self.imgs = 0
        self.lazy_imgs = 0
        self.iframes: list[int] = []
        self.preconnect_hosts: set[str] = set()
        self.font_hosts: list[tuple[int, str]] = []

    def _add(self, rule: str, msg: str) -> None:
        self.findings.append((self.getpos()[0], rule, msg))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "head":
            self.in_head = True
        elif tag == "body":
            self.in_head, self.in_body = False, True
        elif tag == "img":
            self._img(a)
        elif tag == "iframe":
            self.iframes.append(self.getpos()[0])
        elif tag == "script" and a.get("src"):
            self._script(a)
        elif tag == "style" and self.in_body:
            self._add("style-in-body", "<style> inside <body> (move it to <head> or a file)")
        elif tag == "link":
            self._link(a)

    def handle_endtag(self, tag: str) -> None:
        if tag == "head":
            self.in_head = False

    def _img(self, a: dict[str, str]) -> None:
        self.imgs += 1
        if a.get("loading", "").lower() == "lazy":
            self.lazy_imgs += 1
        if not (a.get("width") and a.get("height")):
            self._add("img-dimensions", f"<img src={a.get('src', '?')!r}> lacks width and/or height (layout shift)")
        src = a.get("src", "")
        if src.startswith("data:") and len(src) > self.max_data_uri:
            self._add("img-base64", f"data: URI image of {len(src)} bytes (limit {self.max_data_uri})")
        elif src and not src.startswith(LOCAL_SKIP):
            self.assets.append(src)

    def _script(self, a: dict[str, str]) -> None:
        src = a["src"]
        deferred = "defer" in a or "async" in a or a.get("type", "").lower() == "module"
        if self.in_head and not deferred:
            self._add("script-blocking", f"<script src={src!r}> in <head> without defer/async/module")
            self.blocking_script_seen = True
        if not src.startswith(LOCAL_SKIP):
            self.assets.append(src)

    def _link(self, a: dict[str, str]) -> None:
        rel, href = a.get("rel", "").lower(), a.get("href", "")
        if "preconnect" in rel:
            self.preconnect_hosts.add(urlparse(href).netloc)
        if "stylesheet" in rel:
            if self.blocking_script_seen:
                self._add("css-after-js", f"stylesheet {href!r} comes after a blocking script")
            host = urlparse(href).netloc
            if host == "fonts.googleapis.com":
                self.font_hosts.append((self.getpos()[0], host))
            if href and not href.startswith(LOCAL_SKIP):
                self.assets.append(href)
        elif "preload" in rel and href and not href.startswith(LOCAL_SKIP):
            self.assets.append(href)


def resolve(ref: str, page: Path, root: Path) -> Path:
    ref = ref.split("#")[0].split("?")[0]
    return (root / ref.lstrip("/")) if ref.startswith("/") else (page.parent / ref)


def looks_unminified(text: str) -> bool:
    if len(text) < 2000:
        return False
    return text.count("\n") > len(text) / 70


def audit_page(page: Path, root: Path, opts: argparse.Namespace) -> list[str]:
    html = page.read_text(encoding="utf-8", errors="replace")
    p = Page()
    p.max_data_uri = opts.max_data_uri
    p.feed(html)
    out = [(ln, r, m) for ln, r, m in p.findings]
    if p.imgs > 3 and p.lazy_imgs == 0:
        out.append((1, "img-lazy", f"{p.imgs} <img> elements and none uses loading=\"lazy\""))
    if len(p.iframes) > opts.max_iframes:
        out.append((p.iframes[opts.max_iframes], "iframe-count", f"{len(p.iframes)} <iframe> elements (limit {opts.max_iframes})"))
    if p.font_hosts and "fonts.gstatic.com" not in p.preconnect_hosts:
        out.append((p.font_hosts[0][0], "font-preconnect", "Google Fonts stylesheet without <link rel=preconnect href=https://fonts.gstatic.com>"))
    total = len(html.encode("utf-8"))
    font_bytes = 0
    seen: set[Path] = set()
    for ref in p.assets:
        f = resolve(ref, page, root)
        if f in seen or not f.is_file():
            continue
        seen.add(f)
        size = f.stat().st_size
        total += size
        if f.suffix == ".css":
            css = f.read_text(encoding="utf-8", errors="replace")
            if not f.name.endswith(".min.css") and looks_unminified(css):
                out.append((1, "not-minified", f"{ref} looks unminified ({size} bytes, many short lines)"))
            for face in FACE_RE.findall(css):
                if "font-display" not in face.lower():
                    out.append((1, "font-display", f"@font-face in {ref} has no font-display"))
                srcs = FONT_RE.findall(face)
                if srcs and not any(".woff2" in s.lower() for s in srcs):
                    out.append((1, "font-format", f"@font-face in {ref} has no woff2 source ({', '.join(srcs)})"))
                for s in srcs:
                    ff = resolve(s, f, root)
                    if ff.is_file() and ff not in seen:
                        seen.add(ff)
                        font_bytes += ff.stat().st_size
                        total += ff.stat().st_size
        elif f.suffix == ".js" and not f.name.endswith(".min.js") and looks_unminified(f.read_text(encoding="utf-8", errors="replace")):
            out.append((1, "not-minified", f"{ref} looks unminified ({size} bytes, many short lines)"))
    if font_bytes > opts.max_font_kb * 1024:
        out.append((1, "font-weight", f"local web fonts total {font_bytes // 1024} kB (limit {opts.max_font_kb} kB)"))
    if total > opts.max_page_kb * 1024:
        out.append((1, "page-weight", f"page plus local assets is {total // 1024} kB (limit {opts.max_page_kb} kB)"))
    rel = page.as_posix()
    return [f"{rel}:{ln}: {rule}: {msg}" for ln, rule, msg in sorted(out, key=lambda x: (x[0], x[1]))]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--root", default=".", help="site root for /-absolute references (default: cwd)")
    ap.add_argument("--max-page-kb", type=int, default=1500)
    ap.add_argument("--max-font-kb", type=int, default=300)
    ap.add_argument("--max-iframes", type=int, default=2)
    ap.add_argument("--max-data-uri", type=int, default=2048)
    opts = ap.parse_args(argv)
    root = Path(opts.root).resolve()
    pages: list[Path] = []
    for raw in opts.paths:
        p = Path(raw)
        pages += sorted(p.rglob("*.html")) if p.is_dir() else [p]
    if not pages:
        print("perf_audit: no HTML files found", file=sys.stderr)
        return 2
    findings: list[str] = []
    for page in pages:
        findings += audit_page(page, root, opts)
    print("\n".join(findings) if findings else f"perf_audit: {len(pages)} page(s) clean")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
