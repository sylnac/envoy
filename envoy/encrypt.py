"""Simple symmetric encryption for secret values using Fernet."""

from __future__ import annotations

import base64
import os
from typing import Dict

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:  # pragma: no cover
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore

_ENV_KEY = "ENVOY_SECRET_KEY"


def _require_fernet() -> None:
    if Fernet is None:
        raise RuntimeError(
            "cryptography package is required for encryption. "
            "Install it with: pip install cryptography"
        )


def generate_key() -> str:
    """Generate a new Fernet key and return it as a string."""
    _require_fernet()
    return Fernet.generate_key().decode()


def _get_fernet(key: str | None = None) -> "Fernet":
    _require_fernet()
    resolved = key or os.environ.get(_ENV_KEY)
    if not resolved:
        raise ValueError(
            f"No encryption key provided. Set {_ENV_KEY} or pass key= explicitly."
        )
    return Fernet(resolved.encode() if isinstance(resolved, str) else resolved)


def encrypt_value(value: str, key: str | None = None) -> str:
    """Encrypt a plaintext value and return a base64-encoded ciphertext string."""
    f = _get_fernet(key)
    return f.encrypt(value.encode()).decode()


def decrypt_value(token: str, key: str | None = None) -> str:
    """Decrypt a ciphertext token and return the plaintext string."""
    f = _get_fernet(key)
    try:
        return f.decrypt(token.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Decryption failed: invalid token or wrong key.") from exc


def encrypt_env(env: Dict[str, str], key: str | None = None) -> Dict[str, str]:
    """Return a new dict with all values encrypted."""
    return {k: encrypt_value(v, key) for k, v in env.items()}


def decrypt_env(env: Dict[str, str], key: str | None = None) -> Dict[str, str]:
    """Return a new dict with all values decrypted."""
    return {k: decrypt_value(v, key) for k, v in env.items()}
