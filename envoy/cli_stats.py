"""CLI handler for the `envoy stats` command."""
from __future__ import annotations

import argparse
import json

from envoy.stats import profile_stats, project_stats
from envoy.profile import list_profiles


def cmd_stats(args: argparse.Namespace) -> int:
    project: str = args.project
    profile: str | None = getattr(args, "profile", None)
    as_json: bool = getattr(args, "json", False)

    if profile:
        profiles = [profile]
    else:
        profiles = list_profiles(project)
        if not profiles:
            print(f"No profiles found for project '{project}'.")
            return 1

    pstats = project_stats(project) if not profile else None

    rows = []
    for p in profiles:
        s = profile_stats(project, p)
        rows.append(s)

    if as_json:
        data = [
            {
                "profile": s.profile,
                "total_keys": s.total_keys,
                "secret_keys": s.secret_keys,
                "plain_keys": s.plain_keys,
                "empty_values": s.empty_values,
                "secret_ratio": round(s.secret_ratio, 4),
            }
            for s in rows
        ]
        print(json.dumps(data, indent=2))
        return 0

    col = "{:<20} {:>10} {:>10} {:>10} {:>10} {:>10}"
    print(col.format("PROFILE", "TOTAL", "SECRETS", "PLAIN", "EMPTY", "RATIO"))
    print("-" * 72)
    for s in rows:
        print(
            col.format(
                s.profile,
                s.total_keys,
                s.secret_keys,
                s.plain_keys,
                s.empty_values,
                f"{s.secret_ratio:.0%}",
            )
        )

    if pstats and len(rows) > 1:
        print("-" * 72)
        print(f"Profiles: {pstats.total_profiles}  "
              f"Total keys: {pstats.total_keys}  "
              f"Unique keys: {pstats.unique_keys}")

    return 0
