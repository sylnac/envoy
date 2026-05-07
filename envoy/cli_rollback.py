"""CLI command: envoy rollback — restore a profile from history."""

from __future__ import annotations

import argparse
import sys

from envoy.rollback import rollback_profile
from envoy.history import load_history


def cmd_rollback(argv: list[str] | None = None) -> int:
    """Entry point for the ``envoy rollback`` sub-command."""
    parser = argparse.ArgumentParser(
        prog="envoy rollback",
        description="Restore a profile to a previous snapshot.",
    )
    parser.add_argument("project", help="Project name")
    parser.add_argument("profile", help="Profile name (e.g. dev, prod)")
    parser.add_argument(
        "--index",
        type=int,
        default=-1,
        help="Snapshot index to restore (default: -1, most recent). "
             "Use --list to see available snapshots.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available snapshots and exit without rolling back.",
    )
    args = parser.parse_args(argv)

    if args.list:
        history = load_history(args.project, args.profile)
        if not history:
            print("No history found for this profile.")
            return 1
        for i, snap in enumerate(history):
            ts = snap.get("timestamp", "unknown")
            n = len(snap.get("env", {}))
            print(f"  [{i:>3}]  {ts}  ({n} keys)")
        return 0

    result = rollback_profile(
        project=args.project,
        profile=args.profile,
        snapshot_index=args.index,
    )

    if not result.success:
        print(f"error: {result.error}", file=sys.stderr)
        return 1

    print(
        f"Rolled back '{args.profile}' to snapshot from {result.timestamp} "
        f"({result.keys_restored} keys restored, was {result.previous_keys} keys)."
    )
    return 0
