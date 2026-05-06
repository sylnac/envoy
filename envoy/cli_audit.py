"""CLI command: envoy audit — display the audit log."""

from __future__ import annotations

import argparse
import sys
from typing import List

from envoy.audit import filter_log, format_entry, load_audit_log


def cmd_audit(argv: List[str] | None = None) -> int:
    """
    Usage:
        envoy audit [--profile NAME] [--action ACTION] [--last N]
    """
    parser = argparse.ArgumentParser(
        prog="envoy audit",
        description="Show the audit log of envoy actions.",
    )
    parser.add_argument(
        "--profile",
        metavar="NAME",
        help="Filter entries by profile name.",
    )
    parser.add_argument(
        "--action",
        metavar="ACTION",
        help="Filter entries by action (e.g. save, delete, export).",
    )
    parser.add_argument(
        "--last",
        metavar="N",
        type=int,
        default=None,
        help="Show only the last N entries.",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory).",
    )

    args = parser.parse_args(argv)

    entries = load_audit_log(project_root=args.project_root)
    entries = filter_log(entries, action=args.action, profile=args.profile)

    if args.last is not None:
        entries = entries[-args.last :]

    if not entries:
        print("No audit log entries found.")
        return 0

    for entry in entries:
        print(format_entry(entry))

    return 0


if __name__ == "__main__":
    sys.exit(cmd_audit())
