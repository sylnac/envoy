"""Tests for envoy.encrypt."""

from __future__ import annotations

import os
import pytest

pytest.importorskip("cryptography", reason="cryptography not installed")

from envoy.encrypt import (
    generate_key,
    encrypt_value,
    decrypt_value,
    encrypt_env,
    decrypt_env,
)


@pytest.fixture()
def key() -> str:
    return generate_key()


def test_generate_key_is_string(key):
    assert isinstance(key, str)
    assert len(key) > 0


def test_encrypt_returns_different_string(key):
    plaintext = "super_secret"
    ciphertext = encrypt_value(plaintext, key)
    assert ciphertext != plaintext


def test_round_trip(key):
    plaintext = "my_password_123"
    assert decrypt_value(encrypt_value(plaintext, key), key) == plaintext


def test_decrypt_wrong_key_raises(key):
    other_key = generate_key()
    token = encrypt_value("hello", key)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_value(token, other_key)


def test_decrypt_garbage_raises(key):
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_value("notavalidtoken", key)


def test_encrypt_env_encrypts_all_values(key):
    env = {"DB_PASS": "secret", "API_KEY": "abc123"}
    encrypted = encrypt_env(env, key)
    assert set(encrypted.keys()) == set(env.keys())
    for k, v in encrypted.items():
        assert v != env[k]


def test_decrypt_env_round_trip(key):
    env = {"DB_PASS": "secret", "API_KEY": "abc123", "HOST": "localhost"}
    assert decrypt_env(encrypt_env(env, key), key) == env


def test_uses_env_var_key(key, monkeypatch):
    monkeypatch.setenv("ENVOY_SECRET_KEY", key)
    plaintext = "from_env"
    token = encrypt_value(plaintext)  # no explicit key
    assert decrypt_value(token) == plaintext


def test_no_key_raises(monkeypatch):
    monkeypatch.delenv("ENVOY_SECRET_KEY", raising=False)
    with pytest.raises(ValueError, match="No encryption key"):
        encrypt_value("oops")
