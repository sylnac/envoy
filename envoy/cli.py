"""Main CLI entry-point for envoy."""
from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:  # pragma: no cover
    import argparse

    from envoy.cli_merge import cmd_merge
    from envoy.cli_validate import cmd_validate
    from envoy.cli_audit import cmd_audit
    from envoy.cli_snapshot_diff import cmd_snapshot_diff
    from envoy.cli_template import cmd_template
    from envoy.cli_encrypt import cmd_encrypt, cmd_decrypt
    from envoy.cli_copy import cmd_copy
    from envoy.cli_search import cmd_search
    from envoy.cli_compare import cmd_compare
    from envoy.cli_import import cmd_import
    from envoy.cli_rollback import cmd_rollback
    from envoy.cli_tag import cmd_tag

    parser = argparse.ArgumentParser(
        prog="envoy",
        description="Lightweight .env file manager with per-project profiles.",
    )
    sub = parser.add_subparsers(dest="command")

    commands = {
        "merge": cmd_merge,
        "validate": cmd_validate,
        "audit": cmd_audit,
        "snapshot-diff": cmd_snapshot_diff,
        "template": cmd_template,
        "encrypt": cmd_encrypt,
        "decrypt": cmd_decrypt,
        "copy": cmd_copy,
        "search": cmd_search,
        "compare": cmd_compare,
        "import": cmd_import,
        "rollback": cmd_rollback,
        "tag": cmd_tag,
    }

    for name in commands:
        sub.add_parser(name)

    args, rest = parser.parse_known_args(argv)

    if args.command in commands:
        return commands[args.command](rest)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
