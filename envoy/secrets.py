"""Secret masking and detection utilities for envoy."""

import re
from typing import Dict, List, Set

# Patterns that suggest a key holds a secret value
_SECRET_KEY_PATTERNS: List[re.Pattern] = [
    re.compile(r'(?i)(password|passwd|pwd)'),
    re.compile(r'(?i)(secret|token|api_key|apikey)'),
    re.compile(r'(?i)(private_key|privkey|auth)'),
    re.compile(r'(?i)(access_key|signing_key|encryption_key)'),
    re.compile(r'(?i)(database_url|db_url|dsn)'),
]

_MASK = "***"


def is_secret_key(key: str) -> bool:
    """Return True if the key name suggests it holds a secret."""
    return any(pattern.search(key) for pattern in _SECRET_KEY_PATTERNS)


def mask_value(value: str, visible_chars: int = 4) -> str:
    """Mask a secret value, optionally revealing the last N characters."""
    if len(value) <= visible_chars:
        return _MASK
    return _MASK + value[-visible_chars:]


def mask_secrets(
    env: Dict[str, str],
    visible_chars: int = 4,
) -> Dict[str, str]:
    """Return a copy of env with secret values masked."""
    return {
        key: mask_value(value, visible_chars) if is_secret_key(key) else value
        for key, value in env.items()
    }


def find_secret_keys(env: Dict[str, str]) -> Set[str]:
    """Return the set of keys in env that are considered secrets."""
    return {key for key in env if is_secret_key(key)}


def redact_for_display(
    env: Dict[str, str],
    reveal_keys: Set[str] | None = None,
) -> Dict[str, str]:
    """Mask all secret keys except those explicitly listed in reveal_keys."""
    reveal_keys = reveal_keys or set()
    result: Dict[str, str] = {}
    for key, value in env.items():
        if is_secret_key(key) and key not in reveal_keys:
            result[key] = mask_value(value)
        else:
            result[key] = value
    return result
