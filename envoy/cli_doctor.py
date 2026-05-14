"""CLI command: envoy doctor — diagnose project health."""
from __future__ import annotations

import argparse
import sys

from envoy.doctor import run_doctor


def cmd_doctor(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envoy doctor",
        description="Diagnose common issues in envoy profiles.",
    )
    parser.add_argument(
        "--project",
        default=".",
        help="Path to the project directory (default: current directory).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 on warnings as well as errors.",
    )
    args = parser.parse_args(argv)

    report = run_doctor(args.project)

    if args.json:
        import json

        data = [
            {"level": i.level, "profile": i.profile, "message": i.message}
            for i in report.issues
        ]
        print(json.dumps(data, indent=2))
    else:
        if not report.issues:
            print("envoy doctor: all checks passed.")
        else:
            for issue in report.issues:
                icon = "\u274c" if issue.level == "error" else "\u26a0\ufe0f"
                print(f"{icon}  [{issue.profile}] {issue.message}")

    if args.strict:
        return 0 if not report.issues else 1
    return 0 if report.ok else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(cmd_doctor())
