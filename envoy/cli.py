"""Main CLI entry point for envoy."""

from __future__ import annotations

import sys
from typing import List, Optional

USAGE = """envoy — lightweight .env manager

Usage:
  envoy <command> [options]

Commands:
  merge     Merge two profiles into one
  validate  Validate a profile against a schema or required keys

Run `envoy <command> --help` for command-specific help.
"""


def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv or argv[0] in ("-h", "--help"):
        print(USAGE)
        return 0

    command, rest = argv[0], argv[1:]

    if command == "merge":
        from envoy.cli_merge import cmd_merge
        return cmd_merge(rest)

    if command == "validate":
        from envoy.cli_validate import cmd_validate
        return cmd_validate(rest)

    print(f"error: unknown command '{command}'", file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
