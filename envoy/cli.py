"""envoy — Lightweight .env file manager CLI entry point."""
from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:  # noqa: C901
    args = argv if argv is not None else sys.argv[1:]

    if not args:
        _print_help()
        return 0

    command = args[0]
    rest = args[1:]

    if command in ("-h", "--help", "help"):
        _print_help()
        return 0

    if command == "merge":
        from envoy.cli_merge import cmd_merge
        return cmd_merge(rest)

    if command == "validate":
        from envoy.cli_validate import cmd_validate
        return cmd_validate(rest)

    if command == "audit":
        from envoy.cli_audit import cmd_audit
        return cmd_audit(rest)

    if command == "snapshot-diff":
        from envoy.cli_snapshot_diff import cmd_snapshot_diff
        return cmd_snapshot_diff(rest)

    if command == "template":
        from envoy.cli_template import cmd_template
        return cmd_template(rest)

    if command == "encrypt":
        from envoy.cli_encrypt import cmd_encrypt
        return cmd_encrypt(rest)

    if command == "decrypt":
        from envoy.cli_encrypt import cmd_decrypt
        return cmd_decrypt(rest)

    if command == "copy":
        from envoy.cli_copy import cmd_copy
        return cmd_copy(rest)

    if command == "search":
        from envoy.cli_search import cmd_search
        return cmd_search(rest)

    if command == "compare":
        from envoy.cli_compare import cmd_compare
        return cmd_compare(rest)

    if command == "import":
        from envoy.cli_import import cmd_import
        return cmd_import(rest)

    if command == "rollback":
        from envoy.cli_rollback import cmd_rollback
        return cmd_rollback(rest)

    if command == "tag":
        from envoy.cli_tag import cmd_tag
        return cmd_tag(rest)

    if command == "pin":
        from envoy.cli_pin import cmd_pin
        return cmd_pin(rest)

    if command == "archive":
        from envoy.cli_archive import cmd_archive
        return cmd_archive(rest)

    if command == "promote":
        from envoy.cli_promote import cmd_promote
        return cmd_promote(rest)

    if command == "sync":
        from envoy.cli_sync import cmd_sync
        return cmd_sync(rest)

    if command == "stats":
        from envoy.cli_stats import cmd_stats
        return cmd_stats(rest)

    if command == "doctor":
        from envoy.cli_doctor import cmd_doctor
        return cmd_doctor(rest)

    if command == "prune":
        from envoy.cli_prune import cmd_prune
        return cmd_prune(rest)

    if command == "reorder":
        from envoy.cli_reorder import cmd_reorder
        return cmd_reorder(rest)

    if command == "expire":
        from envoy.cli_expire import cmd_expire
        return cmd_expire(rest)

    if command == "alias":
        from envoy.cli_alias import cmd_alias
        return cmd_alias(rest)

    print(f"envoy: unknown command '{command}'", file=sys.stderr)
    return 1


def _print_help() -> None:
    print(
        "envoy — Lightweight .env file manager\n"
        "\nCommands:\n"
        "  merge            Merge two profiles\n"
        "  validate         Validate a profile against a schema\n"
        "  audit            Show audit log\n"
        "  snapshot-diff    Diff historical snapshots\n"
        "  template         Render a template with profile values\n"
        "  encrypt/decrypt  Encrypt or decrypt secret values\n"
        "  copy             Copy a profile\n"
        "  search           Search keys/values across profiles\n"
        "  compare          Compare two profiles side-by-side\n"
        "  import           Import variables from environment or file\n"
        "  rollback         Restore a previous snapshot\n"
        "  tag              Tag a profile\n"
        "  pin              Pin the active profile\n"
        "  archive          Archive/restore profiles to a zip\n"
        "  promote          Promote a profile to another\n"
        "  sync             Push/pull profiles to a remote directory\n"
        "  stats            Show project statistics\n"
        "  doctor           Health-check all profiles\n"
        "  prune            Remove empty or unknown keys\n"
        "  reorder          Reorder keys in a profile\n"
        "  expire           Set or check key expiry\n"
        "  alias            Manage profile aliases\n"
    )


if __name__ == "__main__":
    sys.exit(main())
