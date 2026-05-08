"""CLI commands for profile pinning."""

from __future__ import annotations

import argparse
import sys

from envoy.pin import get_pinned, is_pinned, pin_profile, unpin_profile


def cmd_pin(argv: list[str] | None = None) -> int:
    """Entry point for the ``envoy pin`` sub-command."""
    parser = argparse.ArgumentParser(
        prog="envoy pin",
        description="Pin, unpin, or query the active profile for a project.",
    )
    parser.add_argument("project", help="Project name")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("profile", nargs="?", default=None, help="Profile to pin")
    group.add_argument(
        "--unpin", action="store_true", help="Remove the current pin"
    )
    group.add_argument(
        "--status", action="store_true", help="Show currently pinned profile"
    )

    args = parser.parse_args(argv)

    if args.unpin:
        prev = unpin_profile(args.project)
        if prev:
            print(f"Unpinned '{prev}' from project '{args.project}'.")
        else:
            print(f"No profile was pinned for project '{args.project}'.")
        return 0

    if args.status or args.profile is None:
        pinned = get_pinned(args.project)
        if pinned:
            print(f"Pinned profile for '{args.project}': {pinned}")
            return 0
        else:
            print(f"No profile pinned for project '{args.project}'.")
            return 1

    # Pin the given profile
    try:
        pin_profile(args.project, args.profile)
        print(f"Pinned profile '{args.profile}' for project '{args.project}'.")
        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
