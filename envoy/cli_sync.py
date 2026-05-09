"""CLI surface for the sync feature."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envoy.sync import push_profile, pull_profile, sync_all


def cmd_sync(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envoy sync",
        description="Push or pull profiles to/from a shared directory.",
    )
    parser.add_argument("project", help="Project name")
    parser.add_argument(
        "direction",
        choices=["push", "pull"],
        help="Direction of sync",
    )
    parser.add_argument(
        "--remote",
        required=True,
        metavar="DIR",
        help="Path to the shared/remote directory",
    )
    parser.add_argument(
        "--profile",
        metavar="NAME",
        help="Sync a single profile (default: all profiles)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing profiles at the destination",
    )

    args = parser.parse_args(argv)
    remote_dir = Path(args.remote)

    if args.profile:
        if args.direction == "push":
            result = push_profile(args.project, args.profile, remote_dir, overwrite=args.overwrite)
        else:
            result = pull_profile(args.project, args.profile, remote_dir, overwrite=args.overwrite)
    else:
        result = sync_all(args.project, remote_dir, direction=args.direction, overwrite=args.overwrite)

    for p in result.pushed:
        print(f"  pushed  {p}")
    for p in result.pulled:
        print(f"  pulled  {p}")
    for p in result.skipped:
        print(f"  skipped {p} (already exists, use --overwrite)")
    for e in result.errors:
        print(f"  error   {e}", file=sys.stderr)

    total = len(result.pushed) + len(result.pulled)
    print(f"\nDone. {total} profile(s) synced, {len(result.skipped)} skipped.")
    return 0 if result.ok else 1
