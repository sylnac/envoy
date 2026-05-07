"""CLI handler for the `envoy import` command."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from envoy.import_env import import_from_env, import_from_file


def cmd_import(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envoy import",
        description="Import env vars from the shell or a .env file into a profile.",
    )
    parser.add_argument("project", help="Project name")
    parser.add_argument("profile", help="Target profile name")
    parser.add_argument(
        "--file", "-f", metavar="PATH",
        help="Import from a .env file instead of the current environment",
    )
    parser.add_argument(
        "--keys", "-k", metavar="KEY", nargs="+",
        help="Only import these specific keys (env import only)",
    )
    parser.add_argument(
        "--prefix", "-p", metavar="PREFIX",
        help="Only import keys with this prefix (env import only)",
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing keys in the profile",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="Suppress output",
    )

    args = parser.parse_args(argv)

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"error: file not found: {path}", file=sys.stderr)
            return 1
        result = import_from_file(
            args.project, args.profile, path, overwrite=args.overwrite
        )
    else:
        result = import_from_env(
            args.project,
            args.profile,
            keys=args.keys,
            overwrite=args.overwrite,
            prefix=args.prefix,
        )

    if not args.quiet:
        if result.imported:
            print(f"imported ({len(result.imported)}): {', '.join(sorted(result.imported))}")
        if result.overwritten:
            print(f"overwritten ({len(result.overwritten)}): {', '.join(sorted(result.overwritten))}")
        if result.skipped:
            print(f"skipped ({len(result.skipped)}): {', '.join(sorted(result.skipped))}")
        if result.total == 0 and not result.skipped:
            print("nothing to import")

    return 0
