"""CLI command: envoy compare <profile_a> <profile_b>."""
from __future__ import annotations

import argparse
import sys

from envoy.compare import compare_profiles, summary


def cmd_compare(argv: list[str] | None = None) -> int:
    """Entry point for the compare subcommand."""
    parser = argparse.ArgumentParser(
        prog="envoy compare",
        description="Compare two profiles side by side.",
    )
    parser.add_argument("project", help="Project name")
    parser.add_argument("profile_a", help="First profile")
    parser.add_argument("profile_b", help="Second profile")
    parser.add_argument(
        "--redact",
        action="store_true",
        default=False,
        help="Mask secret values in output",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        default=False,
        help="Output result as JSON",
    )
    args = parser.parse_args(argv)

    result = compare_profiles(
        args.project,
        args.profile_a,
        args.profile_b,
        redact=args.redact,
    )

    if args.as_json:
        import json

        data = {
            "profile_a": result.profile_a,
            "profile_b": result.profile_b,
            "only_in_a": result.only_in_a,
            "only_in_b": result.only_in_b,
            "in_both_same": result.in_both_same,
            "in_both_different": {
                k: {"a": v[0], "b": v[1]}
                for k, v in result.in_both_different.items()
            },
        }
        print(json.dumps(data, indent=2))
    else:
        print(summary(result))

    return 1 if result.has_differences else 0


if __name__ == "__main__":
    sys.exit(cmd_compare())
