"""CLI command: envoy template — render a .env template against a profile."""
from __future__ import annotations

import argparse
import sys

from envoy.profile import load_profile, profile_exists
from envoy.template import find_placeholders, render_template_file


def cmd_template(argv: list[str] | None = None) -> int:
    """Entry-point for ``envoy template``.

    Usage::

        envoy template <template_file> [--profile NAME] [--check] [--out FILE]
    """
    parser = argparse.ArgumentParser(
        prog="envoy template",
        description="Render a .env template using values from a profile.",
    )
    parser.add_argument("template", help="Path to the template file")
    parser.add_argument(
        "--profile", default="default", help="Profile name to source values from (default: default)"
    )
    parser.add_argument(
        "--project", default=".", help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit with code 1 if any placeholders are unresolved instead of writing output",
    )
    parser.add_argument(
        "--out", default="-", help="Output file path; use '-' for stdout (default: -)"
    )
    args = parser.parse_args(argv)

    if not profile_exists(args.project, args.profile):
        print(f"error: profile '{args.profile}' not found in project '{args.project}'", file=sys.stderr)
        return 1

    env = load_profile(args.project, args.profile)

    try:
        rendered, missing = render_template_file(args.template, env)
    except FileNotFoundError:
        print(f"error: template file not found: {args.template}", file=sys.stderr)
        return 1

    if missing:
        print(f"warning: {len(missing)} unresolved placeholder(s): {', '.join(missing)}", file=sys.stderr)
        if args.check:
            return 1

    if args.out == "-":
        sys.stdout.write(rendered)
    else:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(rendered)
        print(f"written to {args.out}")

    return 0
