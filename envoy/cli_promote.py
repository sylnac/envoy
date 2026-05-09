"""CLI handler for the `envoy promote` sub-command."""
from __future__ import annotations

import argparse
import sys

from envoy.promote import promote_profile


def cmd_promote(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envoy promote",
        description="Promote env values from one profile to another.",
    )
    parser.add_argument("project", help="Project name")
    parser.add_argument("source", help="Source profile (e.g. staging)")
    parser.add_argument("destination", help="Destination profile (e.g. production)")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite existing keys in destination",
    )
    parser.add_argument(
        "--keys",
        metavar="KEY",
        nargs="+",
        default=None,
        help="Limit promotion to these keys",
    )
    parser.add_argument(
        "--no-history",
        dest="no_history",
        action="store_true",
        default=False,
        help="Skip recording a history snapshot before promoting",
    )

    args = parser.parse_args(argv)

    result = promote_profile(
        args.project,
        args.source,
        args.destination,
        overwrite=args.overwrite,
        keys=args.keys,
        record_history=not args.no_history,
    )

    if not result.ok:
        print(f"error: {result.error}", file=sys.stderr)
        return 1

    print(f"Promoted {args.source} → {args.destination}")
    print(f"  promoted : {len(result.keys_promoted)} key(s)")
    if result.overwritten:
        print(f"  overwritten: {', '.join(sorted(result.overwritten))}")
    if result.keys_skipped:
        print(f"  skipped  : {', '.join(sorted(result.keys_skipped))} (use --overwrite to replace)")

    return 0
