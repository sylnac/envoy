"""CLI command: envoy reorder"""
from __future__ import annotations

import argparse
import json
import sys

from envoy.reorder import reorder_profile, ok


def cmd_reorder(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envoy reorder",
        description="Reorder keys in a profile according to a given order.",
    )
    parser.add_argument("project", help="Project name")
    parser.add_argument("profile", help="Profile name")
    parser.add_argument(
        "keys",
        nargs="+",
        metavar="KEY",
        help="Keys in desired order (remaining keys appended unless --drop-remaining)",
    )
    parser.add_argument(
        "--drop-remaining",
        action="store_true",
        help="Drop keys not listed in KEY order instead of appending them",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Output result as JSON",
    )

    args = parser.parse_args(argv)

    result = reorder_profile(
        args.project,
        args.profile,
        args.keys,
        append_remaining=not args.drop_remaining,
    )

    if args.as_json:
        payload = {
            "profile": result.profile,
            "ordered_keys": result.ordered_keys,
            "moved": result.moved,
            "unchanged": result.unchanged,
            "error": result.error,
        }
        print(json.dumps(payload, indent=2))
        return 0 if ok(result) else 1

    if not ok(result):
        print(f"error: {result.error}", file=sys.stderr)
        return 1

    print(f"Profile '{result.profile}' reordered: {result.moved} key(s) moved, {result.unchanged} unchanged.")
    if result.ordered_keys:
        print("Key order: " + ", ".join(result.ordered_keys))
    return 0
