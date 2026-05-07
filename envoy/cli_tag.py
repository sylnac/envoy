"""CLI commands for profile tagging."""
from __future__ import annotations

import argparse
import sys

from envoy.tag import add_tag, remove_tag, get_tags, profiles_with_tag, clear_tags


def cmd_tag(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envoy tag",
        description="Manage tags on profiles.",
    )
    parser.add_argument("project", help="Project name")
    sub = parser.add_subparsers(dest="action", required=True)

    p_add = sub.add_parser("add", help="Add a tag to a profile")
    p_add.add_argument("profile")
    p_add.add_argument("tag")

    p_rm = sub.add_parser("remove", help="Remove a tag from a profile")
    p_rm.add_argument("profile")
    p_rm.add_argument("tag")

    p_list = sub.add_parser("list", help="List tags for a profile")
    p_list.add_argument("profile")

    p_find = sub.add_parser("find", help="Find profiles with a given tag")
    p_find.add_argument("tag")

    p_clear = sub.add_parser("clear", help="Clear all tags from a profile")
    p_clear.add_argument("profile")

    args = parser.parse_args(argv)

    if args.action == "add":
        tags = add_tag(args.project, args.profile, args.tag)
        print(f"Tags for '{args.profile}': {', '.join(tags) or '(none)'}")
        return 0

    if args.action == "remove":
        tags = remove_tag(args.project, args.profile, args.tag)
        print(f"Tags for '{args.profile}': {', '.join(tags) or '(none)'}")
        return 0

    if args.action == "list":
        tags = get_tags(args.project, args.profile)
        if tags:
            for t in tags:
                print(t)
        else:
            print(f"No tags for profile '{args.profile}'.")
        return 0

    if args.action == "find":
        profiles = profiles_with_tag(args.project, args.tag)
        if profiles:
            for p in profiles:
                print(p)
        else:
            print(f"No profiles tagged '{args.tag}'.")
            return 1
        return 0

    if args.action == "clear":
        clear_tags(args.project, args.profile)
        print(f"Cleared all tags from '{args.profile}'.")
        return 0

    return 1
