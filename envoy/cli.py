"""Entry point for the envoy CLI."""
from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="envoy",
        description="Lightweight .env file manager with per-project profiles.",
    )
    sub = parser.add_subparsers(dest="command")

    # Register sub-commands (each module handles its own arg parsing)
    sub.add_parser("merge", add_help=False)
    sub.add_parser("validate", add_help=False)
    sub.add_parser("audit", add_help=False)
    sub.add_parser("snapshot-diff", add_help=False)
    sub.add_parser("template", add_help=False)
    sub.add_parser("encrypt", add_help=False)
    sub.add_parser("decrypt", add_help=False)
    sub.add_parser("copy", add_help=False)
    sub.add_parser("search", add_help=False)
    sub.add_parser("compare", add_help=False)
    sub.add_parser("import", add_help=False)
    sub.add_parser("rollback", add_help=False)
    sub.add_parser("tag", add_help=False)
    sub.add_parser("pin", add_help=False)
    sub.add_parser("archive", add_help=False)
    sub.add_parser("promote", add_help=False)
    sub.add_parser("sync", add_help=False)
    sub.add_parser("stats", add_help=False)
    sub.add_parser("doctor", add_help=False)

    args, remaining = parser.parse_known_args(argv)

    if args.command == "merge":
        from envoy.cli_merge import cmd_merge
        return cmd_merge(remaining)
    if args.command == "validate":
        from envoy.cli_validate import cmd_validate
        return cmd_validate(remaining)
    if args.command == "audit":
        from envoy.cli_audit import cmd_audit
        return cmd_audit(remaining)
    if args.command == "snapshot-diff":
        from envoy.cli_snapshot_diff import cmd_snapshot_diff
        return cmd_snapshot_diff(remaining)
    if args.command == "template":
        from envoy.cli_template import cmd_template
        return cmd_template(remaining)
    if args.command in ("encrypt", "decrypt"):
        from envoy.cli_encrypt import cmd_encrypt, cmd_decrypt
        fn = cmd_encrypt if args.command == "encrypt" else cmd_decrypt
        return fn(remaining)
    if args.command == "copy":
        from envoy.cli_copy import cmd_copy
        return cmd_copy(remaining)
    if args.command == "search":
        from envoy.cli_search import cmd_search
        return cmd_search(remaining)
    if args.command == "compare":
        from envoy.cli_compare import cmd_compare
        return cmd_compare(remaining)
    if args.command == "import":
        from envoy.cli_import import cmd_import
        return cmd_import(remaining)
    if args.command == "rollback":
        from envoy.cli_rollback import cmd_rollback
        return cmd_rollback(remaining)
    if args.command == "tag":
        from envoy.cli_tag import cmd_tag
        return cmd_tag(remaining)
    if args.command == "pin":
        from envoy.cli_pin import cmd_pin
        return cmd_pin(remaining)
    if args.command == "archive":
        from envoy.cli_archive import cmd_archive
        return cmd_archive(remaining)
    if args.command == "promote":
        from envoy.cli_promote import cmd_promote
        return cmd_promote(remaining)
    if args.command == "sync":
        from envoy.cli_sync import cmd_sync
        return cmd_sync(remaining)
    if args.command == "stats":
        from envoy.cli_stats import cmd_stats
        return cmd_stats(remaining)
    if args.command == "doctor":
        from envoy.cli_doctor import cmd_doctor
        return cmd_doctor(remaining)

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
