"""CLI commands for profile alias management."""
from __future__ import annotations

import argparse
import json
import sys

from envoy.alias import (
    aliases_for_profile,
    list_aliases,
    remove_alias,
    resolve_alias,
    set_alias,
)


def cmd_alias(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envoy alias",
        description="Manage profile aliases.",
    )
    parser.add_argument("--project", default=".", help="Project directory")
    parser.add_argument("--json", dest="as_json", action="store_true")

    sub = parser.add_subparsers(dest="action")

    p_set = sub.add_parser("set", help="Create or update an alias")
    p_set.add_argument("alias")
    p_set.add_argument("profile")

    p_rm = sub.add_parser("remove", help="Delete an alias")
    p_rm.add_argument("alias")

    p_res = sub.add_parser("resolve", help="Print the profile for an alias")
    p_res.add_argument("alias")

    sub.add_parser("list", help="List all aliases")

    p_for = sub.add_parser("for", help="List aliases pointing to a profile")
    p_for.add_argument("profile")

    args = parser.parse_args(argv)

    if args.action == "set":
        mapping = set_alias(args.project, args.alias, args.profile)
        if args.as_json:
            print(json.dumps(mapping))
        else:
            print(f"Alias '{args.alias}' -> '{args.profile}' saved.")
        return 0

    if args.action == "remove":
        removed = remove_alias(args.project, args.alias)
        if args.as_json:
            print(json.dumps({"removed": removed, "alias": args.alias}))
        elif removed:
            print(f"Alias '{args.alias}' removed.")
        else:
            print(f"Alias '{args.alias}' not found.", file=sys.stderr)
            return 1
        return 0

    if args.action == "resolve":
        profile = resolve_alias(args.project, args.alias)
        if profile is None:
            print(f"No alias '{args.alias}' found.", file=sys.stderr)
            return 1
        print(json.dumps({"alias": args.alias, "profile": profile}) if args.as_json else profile)
        return 0

    if args.action == "list":
        aliases = list_aliases(args.project)
        if args.as_json:
            print(json.dumps(aliases))
        elif aliases:
            for alias, profile in sorted(aliases.items()):
                print(f"{alias:20s} -> {profile}")
        else:
            print("No aliases defined.")
        return 0

    if args.action == "for":
        names = aliases_for_profile(args.project, args.profile)
        if args.as_json:
            print(json.dumps(names))
        else:
            print("\n".join(names) if names else "No aliases for that profile.")
        return 0

    parser.print_help()
    return 1
