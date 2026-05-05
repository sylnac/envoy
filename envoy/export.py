"""Export env profiles to various formats."""

from __future__ import annotations

import json
from typing import Dict

from envoy.secrets import redact_for_display


def to_shell_export(env: Dict[str, str], redact: bool = False) -> str:
    """Serialize env as shell export statements.

    Args:
        env: key/value pairs to export.
        redact: if True, mask secret values before exporting.

    Returns:
        A string of ``export KEY=VALUE`` lines.
    """
    if redact:
        env = redact_for_display(env)
    lines = [f'export {key}="{value}"' for key, value in sorted(env.items())]
    return "\n".join(lines) + ("\n" if lines else "")


def to_dotenv(env: Dict[str, str], redact: bool = False) -> str:
    """Serialize env as a .env file string.

    Args:
        env: key/value pairs.
        redact: if True, mask secret values.

    Returns:
        A .env-formatted string.
    """
    if redact:
        env = redact_for_display(env)
    lines = [f'{key}="{value}"' for key, value in sorted(env.items())]
    return "\n".join(lines) + ("\n" if lines else "")


def to_json(env: Dict[str, str], redact: bool = False, indent: int = 2) -> str:
    """Serialize env as a JSON string.

    Args:
        env: key/value pairs.
        redact: if True, mask secret values.
        indent: JSON indentation level.

    Returns:
        A JSON-formatted string.
    """
    if redact:
        env = redact_for_display(env)
    return json.dumps(dict(sorted(env.items())), indent=indent)


FORMATS = {
    "shell": to_shell_export,
    "dotenv": to_dotenv,
    "json": to_json,
}


def export(env: Dict[str, str], fmt: str = "dotenv", redact: bool = False) -> str:
    """Export env in the given format.

    Args:
        env: key/value pairs.
        fmt: one of 'shell', 'dotenv', 'json'.
        redact: mask secret values if True.

    Raises:
        ValueError: if fmt is not recognised.
    """
    if fmt not in FORMATS:
        raise ValueError(f"Unknown format '{fmt}'. Choose from: {list(FORMATS)}.")
    return FORMATS[fmt](env, redact=redact)
