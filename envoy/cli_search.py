"""CLI command for searching environment variables across profiles."""
from __future__ import annotations

import argparse
import os

from envoy.search import find_key_across_profiles, search_profiles
from envoy.secrets import mask_value, is_secret_key


def cmd_search(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envoy search",
        description="Search environment variables across profiles.",
    )
    parser.add_argument("pattern", help="Key glob pattern (e.g. DB_*, API_TOKEN)")
    parser.add_argument("--value", metavar="PATTERN", help="Also filter by value glob pattern")
    parser.add_argument("--profile", metavar="NAME", action="append", dest="profiles",
                        help="Limit to specific profiles (repeatable)")
    parser.add_argument("--redact", action="store_true", help="Mask secret values")
    parser.add_argument("--compare", action="store_true",
                        help="Show value per profile for an exact key")
    parser.add_argument("--dir", default=os.getcwd(), help="Project directory")
    args = parser.parse_args(argv)

    if args.compare:
        mapping = find_key_across_profiles(args.dir, args.pattern, profiles=args.profiles)
        if not mapping:
            print("No profiles found.")
            return 1
        print(f"Key: {args.pattern}")
        for prof, val in sorted(mapping.items()):
            display = "(not set)" if val is None else val
            if val is not None and args.redact and is_secret_key(args.pattern):
                display = mask_value(val)
            print(f"  {prof:<20} {display}")
        return 0

    summary = search_profiles(
        args.dir,
        args.pattern,
        value_pattern=args.value,
        profiles=args.profiles,
    )

    if summary.total == 0:
        print(f"No matches for '{args.pattern}' across {summary.profiles_searched} profile(s).")
        return 1

    grouped = summary.by_profile()
    for prof_name, results in sorted(grouped.items()):
        print(f"[{prof_name}]")
        for r in results:
            val = mask_value(r.value) if args.redact and is_secret_key(r.key) else r.value
            print(f"  {r.key}={val}")

    print(f"\n{summary.total} match(es) across {summary.profiles_searched} profile(s).")
    return 0
