"""CLI handler for the `envoy group` sub-command."""
from __future__ import annotations

import json
import sys
from typing import List

from envoy.group import (
    add_to_group,
    delete_group,
    get_group,
    list_groups,
    remove_from_group,
)


def cmd_group(project: str, argv: List[str]) -> int:  # noqa: C901
    """
    Usage:
      envoy group add   <group> <profile> [--json]
      envoy group rm    <group> <profile> [--json]
      envoy group list  [<group>]         [--json]
      envoy group delete <group>          [--json]
    """
    as_json = "--json" in argv
    args = [a for a in argv if a != "--json"]

    if not args:
        print(cmd_group.__doc__, file=sys.stderr)
        return 2

    sub = args[0]

    if sub == "add":
        if len(args) < 3:
            print("Usage: envoy group add <group> <profile>", file=sys.stderr)
            return 2
        group, profile = args[1], args[2]
        try:
            result = add_to_group(project, group, profile)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if as_json:
            print(json.dumps({"group": result.group, "members": result.members, "added": result.added}))
        else:
            status = "added" if result.added else "already in group"
            print(f"{profile} {status} → {group} ({len(result.members)} members)")
        return 0

    if sub == "rm":
        if len(args) < 3:
            print("Usage: envoy group rm <group> <profile>", file=sys.stderr)
            return 2
        group, profile = args[1], args[2]
        result = remove_from_group(project, group, profile)
        if as_json:
            print(json.dumps({"group": result.group, "members": result.members, "removed": result.removed}))
        else:
            status = "removed" if result.removed else "was not in group"
            print(f"{profile} {status} ← {group} ({len(result.members)} members)")
        return 0

    if sub == "list":
        if len(args) >= 2:
            members = get_group(project, args[1])
            if as_json:
                print(json.dumps({"group": args[1], "members": members}))
            else:
                print(f"{args[1]}: {', '.join(members) if members else '(empty)'}")
        else:
            groups = list_groups(project)
            if as_json:
                print(json.dumps(groups))
            else:
                if not groups:
                    print("(no groups defined)")
                else:
                    for g, members in groups.items():
                        print(f"  {g}: {', '.join(members)}")
        return 0

    if sub == "delete":
        if len(args) < 2:
            print("Usage: envoy group delete <group>", file=sys.stderr)
            return 2
        existed = delete_group(project, args[1])
        if as_json:
            print(json.dumps({"group": args[1], "deleted": existed}))
        else:
            print(f"group '{args[1]}' {'deleted' if existed else 'did not exist'}")
        return 0 if existed else 1

    print(f"unknown sub-command: {sub}", file=sys.stderr)
    return 2
