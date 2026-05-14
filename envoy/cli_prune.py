"""CLI handler for the *prune* sub-command."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from envoy.prune import prune_all_profiles, prune_empty_values, prune_keys_not_in_schema


def cmd_prune(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envoy prune",
        description="Remove stale or empty keys from profiles.",
    )
    parser.add_argument("project_dir", help="Project directory")
    parser.add_argument(
        "--profile", "-p", default=None,
        help="Target a single profile (default: all profiles)",
    )
    parser.add_argument(
        "--schema-keys", "-s", nargs="+", metavar="KEY",
        help="Keep only these keys; remove everything else",
    )
    parser.add_argument(
        "--dry-run", "-n", action="store_true",
        help="Show what would be removed without making changes",
    )
    parser.add_argument(
        "--json", dest="as_json", action="store_true",
        help="Output results as JSON",
    )
    args = parser.parse_args(argv)

    if args.profile:
        if args.schema_keys:
            result = prune_keys_not_in_schema(
                args.project_dir, args.profile,
                args.schema_keys, dry_run=args.dry_run,
            )
        else:
            result = prune_empty_values(
                args.project_dir, args.profile, dry_run=args.dry_run
            )
        results = {args.profile: result}
    else:
        results = prune_all_profiles(
            args.project_dir,
            schema_keys=args.schema_keys,
            dry_run=args.dry_run,
        )

    if args.as_json:
        payload = {
            name: {
                "removed": r.removed_keys,
                "count": r.count,
                "dry_run": r.dry_run,
            }
            for name, r in results.items()
        }
        print(json.dumps(payload, indent=2))
    else:
        for r in results.values():
            print(r.summary())

    total_removed = sum(r.count for r in results.values())
    return 0 if total_removed == 0 or args.dry_run else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(cmd_prune())
