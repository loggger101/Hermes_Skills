#!/usr/bin/env python3
"""Watch any JSON endpoint that returns a list of objects; dedup by ID field.

Usage (via cron with --no-agent):

    hermes cron create api-events \\
      --schedule "*/1 * * * *" --no-agent \\
      --script "$HERMES_HOME/skills/devops/watchers/scripts/watch_http_json.py" \\
      --script-args "--name api --url https://api.example.com/events \\
                     --id-field event_id --items-path data.events"

The response can be:
  - a top-level JSON list (default), or
  - a JSON object with a dotted ``--items-path`` pointing to the list.

Each item is deduped by ``--id-field`` (default "id").

Optional ``--header KEY:VALUE`` flags pass HTTP headers (repeatable).
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _watermark import (  # type: ignore
    Watermark,
    WatermarkError,
    cap,
    checked_filter,
    format_items_as_markdown,
)


def _dig(obj, path: str):
    """Dotted-path lookup: _dig({'a':{'b':[1,2]}}, 'a.b') → [1,2]."""
    if not path:
        return obj
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def _parse_header(s: str):
    if ":" not in s:
        raise argparse.ArgumentTypeError(f"--header expects 'KEY: VALUE' (got {s!r})")
    k, v = s.split(":", 1)
    return (k.strip(), v.strip())


def main() -> int:
    p = argparse.ArgumentParser(description="Poll a JSON endpoint.")
    p.add_argument("--name", required=True, help="Watcher name (used for state file)")
    p.add_argument("--url", required=True, help="JSON endpoint URL")
    p.add_argument("--id-field", default="id", help="Field used to dedup items (default: 'id')")
    p.add_argument(
        "--items-path",
        default="",
        help="Dotted path to the list inside the JSON response (e.g. 'data.events')",
    )
    p.add_argument(
        "--title-field",
        default="title",
        help="Field used as the item title in the rendered output (default: 'title')",
    )
    p.add_argument(
        "--url-field",
        default="url",
        help="Field used as the item URL in the rendered output (default: 'url')",
    )
    p.add_argument(
        "--body-field",
        default="",
        help="Optional body field to include as a snippet under each item",
    )
    p.add_argument(
        "--max", type=int, default=20, help="Max new items to emit per tick (default: 20)"
    )
    p.add_argument(
        "--header",
        action="append",
        type=_parse_header,
        default=[],
        metavar="KEY: VALUE",
        help="HTTP header (repeatable)",
    )
    p.add_argument(
        "--timeout", type=float, default=20.0, help="HTTP timeout in seconds (default: 20)"
    )
    args = p.parse_args()

    req = urllib.request.Request(args.url, headers={"User-Agent": "Hermes-Watcher/1.0"})
    for k, v in args.header:
        req.add_header(k, v)

    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        print(f"watch_http_json: HTTP {e.code} from {args.url}", file=sys.stderr)
        return 2
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"watch_http_json: network error: {e}", file=sys.stderr)
        return 2

    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        print(f"watch_http_json: response is not valid JSON: {e}", file=sys.stderr)
        return 2

    items = _dig(data, args.items_path) if args.items_path else data
    if not isinstance(items, list):
        print(
            f"watch_http_json: items_path={args.items_path!r} did not resolve to a list "
            f"(got {type(items).__name__})",
            file=sys.stderr,
        )
        return 2

    # Keep only dicts — skip any bare strings / numbers so filter_new doesn't crash.
    dicts = [i for i in items if isinstance(i, dict)]
    if len(dicts) < len(items):
        print(
            f"watch_http_json: warning: {len(items) - len(dicts)} of {len(items)} item(s) "
            "are not objects and are skipped",
            file=sys.stderr,
        )
    if items and not dicts:
        print("watch_http_json: no item in the list is a JSON object", file=sys.stderr)
        return 2
    items = dicts

    try:
        wm = Watermark.load(args.name)
    except WatermarkError as e:
        print(f"watch_http_json: {e}", file=sys.stderr)
        return 2
    new_items, rc = checked_filter(wm, items, args.id_field, "watch_http_json")
    if rc is not None:
        return rc
    wm.save()

    new_items, not_shown = cap(new_items, args.max)

    body_key = args.body_field or None
    output = format_items_as_markdown(
        new_items,
        title_key=args.title_field,
        url_key=args.url_field,
        body_key=body_key,
        not_shown=not_shown,
    )
    if output:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
