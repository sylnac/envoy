"""CLI surface for profile key expiry management."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone

from envoy.expire import check_stale, clear_expiry, get_expiry, set_expiry


def _parse_ttl(value: str) -> str:
    """Accept an ISO timestamp or a shorthand like '7d', '24h', '30m'."""
    units = {"d": "days", "h": "hours", "m": "minutes", "s": "seconds"}
    if value[-1] in units and value[:-1].isdigit():
        delta = timedelta(**{units[value[-1]]: int(value[:-1])})
        return (datetime.now(timezone.utc) + delta).isoformat()
    # Validate it parses as ISO
    datetime.fromisoformat(value)
    return value


def cmd_expire(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envoy expire",
        description="Manage per-key expiry timestamps in a profile.",
    )
    parser.add_argument("--root", default=".", help="Project root directory.")
    parser.add_argument("--json", dest="as_json", action="store_true")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_set = sub.add_parser("set", help="Set expiry for a key.")
    p_set.add_argument("profile")
    p_set.add_argument("key")
    p_set.add_argument("ttl", help="ISO timestamp or shorthand: 7d, 24h, 30m")

    p_clear = sub.add_parser("clear", help="Remove expiry for a key.")
    p_clear.add_argument("profile")
    p_clear.add_argument("key")

    p_get = sub.add_parser("get", help="Show expiry for a key.")
    p_get.add_argument("profile")
    p_get.add_argument("key")

    p_check = sub.add_parser("check", help="List stale keys in a profile.")
    p_check.add_argument("profile")

    args = parser.parse_args(argv)

    if args.cmd == "set":
        try:
            ts = _parse_ttl(args.ttl)
        except ValueError:
            print(f"error: invalid ttl/timestamp: {args.ttl}", file=sys.stderr)
            return 1
        result = set_expiry(args.root, args.profile, args.key, ts)
        if args.as_json:
            print(json.dumps({"profile": result.profile, "key": result.key, "expires_at": result.expires_at}))
        else:
            verb = "updated" if result.already_set else "set"
            print(f"{verb}: {args.key} expires at {result.expires_at}")
        return 0

    if args.cmd == "clear":
        existed = clear_expiry(args.root, args.profile, args.key)
        if args.as_json:
            print(json.dumps({"removed": existed, "key": args.key}))
        else:
            print(f"cleared: {args.key}" if existed else f"no expiry found for {args.key}")
        return 0

    if args.cmd == "get":
        ts = get_expiry(args.root, args.profile, args.key)
        if args.as_json:
            print(json.dumps({"key": args.key, "expires_at": ts}))
        else:
            print(ts if ts else f"no expiry set for {args.key}")
        return 0

    if args.cmd == "check":
        result = check_stale(args.root, args.profile)
        if args.as_json:
            print(json.dumps({"profile": result.profile, "stale": result.stale, "active": result.active}))
        else:
            if result.has_stale:
                print(f"stale keys in '{result.profile}': {', '.join(result.stale)}")
            else:
                print(f"no stale keys in '{result.profile}'")
        return 1 if result.has_stale else 0

    return 0
