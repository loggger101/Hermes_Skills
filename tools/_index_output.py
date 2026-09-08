#!/usr/bin/env python3
"""Shared write-guard for the index generators (gen-*.py, regen-dependency-map.py).

Two failure modes this closes:

1. **Overwriting a good index with an empty one.** Every generator ends in
   `out.write_text(...)`. If the scan underneath it returns nothing (wrong cwd,
   moved tree, a rename that breaks a glob), the generator cheerfully truncates a
   correct index to a header and exits 0. `emit()` refuses to write below a floor.

2. **Silent index drift.** Nothing detected that SKILLS-INDEX/CODE-INDEX/
   REFERENCES-INDEX/DEPENDENCY had fallen behind the files they describe -- that is
   how the repo carried "166 skills" while 167 were on disk. `--check` renders the
   index in memory and compares, without writing, so CI/verify-all can gate on it.

Stdlib only. Import from a sibling tool: `from _index_output import emit, wants_check`.
"""
import sys
from pathlib import Path


def wants_check(argv=None) -> bool:
    """True when the caller was run with --check (compare, do not write)."""
    return "--check" in (argv if argv is not None else sys.argv[1:])


def emit(path, content: str, *, count: int, floor: int, label: str, check: bool) -> None:
    """Write `content` to `path`, or compare against it when `check` is set.

    Raises SystemExit(1) on drift in check mode, or SystemExit(2) if `count` is
    below `floor` -- a scan that thin means the scan failed, not that the repo
    shrank, and writing it would destroy a working index.
    """
    path = Path(path)
    if count < floor:
        raise SystemExit(
            "[FATAL] " + label + ": scan produced only " + str(count) + " entries "
            "(floor " + str(floor) + "). Refusing to overwrite " + path.name + " -- "
            "this is a failed scan, not an empty repo. Check the working directory "
            "and that the tree is intact."
        )
    if check:
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current != content:
            if not path.exists():
                print("[DRIFT] " + path.name + " does not exist (would be created)")
            else:
                cur_lines, new_lines = current.splitlines(), content.splitlines()
                print("[DRIFT] " + path.name + " is stale: "
                      + str(len(cur_lines)) + " lines on disk vs "
                      + str(len(new_lines)) + " generated")
                for i, (a, b) in enumerate(zip(cur_lines, new_lines)):
                    if a != b:
                        print("        first difference at line " + str(i + 1) + ":")
                        print("          on disk   : " + a[:120])
                        print("          generated : " + b[:120])
                        break
            raise SystemExit(1)
        print("[OK] " + path.name + " is up to date (" + str(count) + " entries)")
        return
    path.write_text(content, encoding="utf-8")
