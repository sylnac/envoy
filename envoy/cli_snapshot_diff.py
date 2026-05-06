"""CLI command: envoy snapshot-diff — show changes between history snapshots."""

from __future__ import annotations

import argparse
from typing import Optional

from envoy.diff import has_changes
from envoy.snapshot_diff import compare_snapshots


def _fmt_line(symbol: str, key: str, value: str) -> str:
    return f"  {symbol} {key}={value}"


def cmd_snapshot_diff(args: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envoy snapshot-diff",
        description="Compare two history snapshots for a project.",
    )
    parser.add_argument("project", help="Project name")
    parser.add_argument(
        "--from",
        dest="from_index",
        type=int,
        default=-2,
        metavar="N",
        help="Source snapshot index (default: second-to-last)",
    )
    parser.add_argument(
        "--to",
        dest="to_index",
        type=int,
        default=-1,
        metavar="N",
        help="Target snapshot index (default: latest)",
    )
    parser.add_argument(
        "--no-redact",
        action="store_true",
        help="Show secret values in plain text",
    )
    parsed = parser.parse_args(args)

    try:
        cmp = compare_snapshots(parsed.project, parsed.from_index, parsed.to_index)
    except ValueError as exc:
        print(f"error: {exc}")
        return 1

    print(
        f"snapshot-diff {parsed.project}  "
        f"{cmp.from_timestamp} (#{cmp.from_index}) → "
        f"{cmp.to_timestamp} (#{cmp.to_index})"
    )

    diff = cmp.diff
    if not has_changes(diff):
        print("  (no changes)")
        return 0

    from envoy.secrets import mask_value, is_secret_key

    def _val(key: str, value: str) -> str:
        if not parsed.no_redact and is_secret_key(key):
            return mask_value(value)
        return value

    for key in sorted(diff.added):
        print(_fmt_line("+", key, _val(key, diff.added[key])))
    for key in sorted(diff.removed):
        print(_fmt_line("-", key, _val(key, diff.removed[key])))
    for key in sorted(diff.changed):
        old, new = diff.changed[key]
        print(_fmt_line("~", key, f"{_val(key, old)} → {_val(key, new)}"))

    return 0
