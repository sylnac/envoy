"""Parser for .env files supporting comments, blank lines, and quoted values."""

import re
from typing import Dict, Optional


ENV_LINE_RE = re.compile(
    r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$"
)
COMMENT_RE = re.compile(r"^\s*#.*$")


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2:
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            return value[1:-1]
    return value


def parse_env_string(content: str) -> Dict[str, str]:
    """Parse a .env file string into a key-value dictionary.

    - Ignores blank lines and comment lines (starting with #).
    - Strips surrounding quotes from values.
    - Inline comments after unquoted values are NOT stripped (preserves raw value).
    """
    result: Dict[str, str] = {}
    for line in content.splitlines():
        if not line.strip() or COMMENT_RE.match(line):
            continue
        match = ENV_LINE_RE.match(line)
        if match:
            key = match.group("key")
            value = _strip_quotes(match.group("value").strip())
            result[key] = value
    return result


def parse_env_file(path: str) -> Dict[str, str]:
    """Read and parse a .env file from the given path."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return parse_env_string(fh.read())
    except FileNotFoundError:
        raise FileNotFoundError(f".env file not found: {path}")


def serialize_env(data: Dict[str, str]) -> str:
    """Serialize a key-value dictionary back to .env file format."""
    lines = []
    for key, value in data.items():
        # Quote values that contain spaces or are empty
        if not value or " " in value or "\t" in value:
            lines.append(f'{key}="{value}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")
