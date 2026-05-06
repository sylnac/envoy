"""CLI commands for encrypting/decrypting profile secret values."""

from __future__ import annotations

import argparse
import sys

from envoy.encrypt import generate_key, encrypt_env, decrypt_env
from envoy.profile import load_profile, save_profile, profile_exists
from envoy.secrets import find_secret_keys


def cmd_encrypt(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envoy encrypt",
        description="Encrypt secret values in a profile.",
    )
    parser.add_argument("profile", help="Profile name to encrypt")
    parser.add_argument("--project", default=".", help="Project root directory")
    parser.add_argument(
        "--key", default=None, help="Fernet key (default: $ENVOY_SECRET_KEY)"
    )
    parser.add_argument(
        "--all", dest="all_keys", action="store_true",
        help="Encrypt all values, not just detected secrets",
    )
    parser.add_argument(
        "--generate-key", action="store_true",
        help="Generate and print a new key, then exit",
    )
    args = parser.parse_args(argv)

    if args.generate_key:
        print(generate_key())
        return 0

    if not profile_exists(args.project, args.profile):
        print(f"error: profile '{args.profile}' not found.", file=sys.stderr)
        return 1

    env = load_profile(args.project, args.profile)
    if args.all_keys:
        to_encrypt = env
    else:
        secret_keys = find_secret_keys(env)
        to_encrypt = {k: env[k] for k in secret_keys}
        non_secret = {k: env[k] for k in env if k not in secret_keys}

    try:
        encrypted_part = encrypt_env(to_encrypt, args.key)
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    merged = {**non_secret, **encrypted_part} if not args.all_keys else encrypted_part
    save_profile(args.project, args.profile, merged)
    print(f"Encrypted {len(encrypted_part)} key(s) in profile '{args.profile}'.")
    return 0


def cmd_decrypt(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envoy decrypt",
        description="Decrypt values in a profile.",
    )
    parser.add_argument("profile", help="Profile name to decrypt")
    parser.add_argument("--project", default=".", help="Project root directory")
    parser.add_argument(
        "--key", default=None, help="Fernet key (default: $ENVOY_SECRET_KEY)"
    )
    args = parser.parse_args(argv)

    if not profile_exists(args.project, args.profile):
        print(f"error: profile '{args.profile}' not found.", file=sys.stderr)
        return 1

    env = load_profile(args.project, args.profile)
    try:
        decrypted = decrypt_env(env, args.key)
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    save_profile(args.project, args.profile, decrypted)
    print(f"Decrypted {len(decrypted)} key(s) in profile '{args.profile}'.")
    return 0
