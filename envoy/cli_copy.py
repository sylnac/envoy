"""CLI commands for copying and renaming profiles."""

from __future__ import annotations

import argparse
import sys

from envoy.copy import copy_profile, rename_profile


def cmd_copy(argv: list[str] | None = None) -> int:
    """Entry point for ``envoy copy`` and ``envoy rename`` sub-commands.

    Usage examples::

        envoy copy --project myapp staging production
        envoy copy --project myapp --keys DB_URL,SECRET_KEY base dev
        envoy copy --project myapp --overwrite staging production
        envoy copy --project myapp --rename staging old-staging
    """
    parser = argparse.ArgumentParser(
        prog="envoy copy",
        description="Copy or rename a profile within a project.",
    )
    parser.add_argument("--project", required=True, help="Project name.")
    parser.add_argument("source", help="Source profile name.")
    parser.add_argument("destination", help="Destination profile name.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite the destination profile entirely (default: merge).",
    )
    parser.add_argument(
        "--keys",
        default=None,
        help="Comma-separated list of keys to copy (default: all).",
    )
    parser.add_argument(
        "--rename",
        action="store_true",
        default=False,
        help="Rename source to destination instead of copying.",
    )

    args = parser.parse_args(argv)

    keys = [k.strip() for k in args.keys.split(",")] if args.keys else None

    try:
        if args.rename:
            rename_profile(args.project, args.source, args.destination)
            print(
                f"Renamed profile '{args.source}' → '{args.destination}' "
                f"in project '{args.project}'."
            )
        else:
            result = copy_profile(
                project=args.project,
                source=args.source,
                destination=args.destination,
                overwrite=args.overwrite,
                keys=keys,
            )
            action = "Overwrote" if result.overwritten else "Copied"
            print(
                f"{action} {result.keys_copied} key(s) from "
                f"'{result.source}' → '{result.destination}' "
                f"in project '{args.project}'."
            )
    except (FileNotFoundError, FileExistsError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0
