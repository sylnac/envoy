"""CLI commands for archiving and restoring profiles."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envoy.archive import archive_profiles, restore_profiles


def cmd_archive(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envoy archive",
        description="Archive or restore profiles as a zip bundle.",
    )
    sub = parser.add_subparsers(dest="subcmd", required=True)

    # -- save sub-command --
    save_p = sub.add_parser("save", help="Archive profiles to a zip file.")
    save_p.add_argument("project", help="Project name")
    save_p.add_argument("dest", help="Destination zip file path")
    save_p.add_argument(
        "--profiles", nargs="+", metavar="PROFILE",
        help="Profiles to include (default: all)",
    )

    # -- restore sub-command --
    rest_p = sub.add_parser("restore", help="Restore profiles from a zip file.")
    rest_p.add_argument("project", help="Project name")
    rest_p.add_argument("archive", help="Path to zip archive")
    rest_p.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing profiles",
    )

    args = parser.parse_args(argv)

    if args.subcmd == "save":
        result = archive_profiles(
            project=args.project,
            dest=args.dest,
            profiles=args.profiles,
        )
        if result.profiles:
            print(f"Archived {len(result.profiles)} profile(s) to {args.dest}:")
            for p in result.profiles:
                print(f"  + {p}")
        if result.errors:
            for e in result.errors:
                print(f"  ! {e}", file=sys.stderr)
        return 0 if result.ok else 1

    # restore
    if not Path(args.archive).exists():
        print(f"error: archive not found: {args.archive}", file=sys.stderr)
        return 2

    result = restore_profiles(
        project=args.project,
        archive_path=args.archive,
        overwrite=args.overwrite,
    )
    if result.profiles:
        print(f"Restored {len(result.profiles)} profile(s) from {args.archive}:")
        for p in result.profiles:
            print(f"  + {p}")
    if result.errors:
        for e in result.errors:
            print(f"  ! {e}", file=sys.stderr)
    return 0 if result.ok else 1
