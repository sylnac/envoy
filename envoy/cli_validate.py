"""CLI command: envoy validate — check a profile against a schema or required keys."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envoy.profile import load_profile, profile_exists
from envoy.validate import validate_against_schema, validate_required_keys
from envoy.parser import parse_env_file


def _load_schema(schema_path: str) -> dict:
    """Load a schema .env file where values are rule names (required/optional)."""
    return parse_env_file(schema_path)


def cmd_validate(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envoy validate",
        description="Validate a profile against a schema or a list of required keys.",
    )
    parser.add_argument("profile", help="Profile name to validate")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--schema",
        metavar="FILE",
        help="Path to a schema .env file (values: required|optional|non-empty)",
    )
    group.add_argument(
        "--require",
        nargs="+",
        metavar="KEY",
        help="One or more keys that must be present and non-empty",
    )
    parser.add_argument(
        "--no-extra",
        action="store_true",
        help="Fail if the profile contains keys not listed in the schema",
    )
    args = parser.parse_args(argv)

    if not profile_exists(args.profile):
        print(f"error: profile '{args.profile}' does not exist", file=sys.stderr)
        return 2

    env = load_profile(args.profile)

    if args.schema:
        try:
            schema = _load_schema(args.schema)
        except FileNotFoundError:
            print(f"error: schema file '{args.schema}' not found", file=sys.stderr)
            return 2
        result = validate_against_schema(env, schema, allow_extra=not args.no_extra)
    else:
        result = validate_required_keys(env, args.require)

    print(result.summary())
    return 0 if result.valid else 1


if __name__ == "__main__":
    sys.exit(cmd_validate())
