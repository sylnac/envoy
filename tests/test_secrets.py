"""Tests for envoy.secrets module."""

import pytest
from envoy.secrets import (
    is_secret_key,
    mask_value,
    mask_secrets,
    find_secret_keys,
    redact_for_display,
)


# --- is_secret_key ---

def test_is_secret_key_password():
    assert is_secret_key("DB_PASSWORD") is True

def test_is_secret_key_token():
    assert is_secret_key("GITHUB_TOKEN") is True

def test_is_secret_key_api_key():
    assert is_secret_key("STRIPE_API_KEY") is True

def test_is_secret_key_safe_key():
    assert is_secret_key("APP_NAME") is False

def test_is_secret_key_case_insensitive():
    assert is_secret_key("db_password") is True


# --- mask_value ---

def test_mask_value_long_string():
    result = mask_value("supersecretvalue", visible_chars=4)
    assert result == "***alue"

def test_mask_value_short_string():
    result = mask_value("abc", visible_chars=4)
    assert result == "***"

def test_mask_value_exact_length():
    result = mask_value("abcd", visible_chars=4)
    assert result == "***"

def test_mask_value_no_visible_chars():
    result = mask_value("mysecret", visible_chars=0)
    assert result == "***"


# --- mask_secrets ---

def test_mask_secrets_masks_secret_keys():
    env = {"DB_PASSWORD": "hunter2", "APP_NAME": "myapp"}
    result = mask_secrets(env)
    assert result["APP_NAME"] == "myapp"
    assert "hunter2" not in result["DB_PASSWORD"]

def test_mask_secrets_leaves_non_secrets_intact():
    env = {"PORT": "8080", "DEBUG": "true"}
    result = mask_secrets(env)
    assert result == env

def test_mask_secrets_empty_env():
    assert mask_secrets({}) == {}


# --- find_secret_keys ---

def test_find_secret_keys_returns_secrets():
    env = {"API_KEY": "abc", "HOST": "localhost", "SECRET": "xyz"}
    secrets = find_secret_keys(env)
    assert secrets == {"API_KEY", "SECRET"}

def test_find_secret_keys_no_secrets():
    env = {"HOST": "localhost", "PORT": "5432"}
    assert find_secret_keys(env) == set()


# --- redact_for_display ---

def test_redact_for_display_masks_by_default():
    env = {"DB_PASSWORD": "secret123", "APP_ENV": "production"}
    result = redact_for_display(env)
    assert result["APP_ENV"] == "production"
    assert "secret123" not in result["DB_PASSWORD"]

def test_redact_for_display_reveal_key():
    env = {"DB_PASSWORD": "secret123"}
    result = redact_for_display(env, reveal_keys={"DB_PASSWORD"})
    assert result["DB_PASSWORD"] == "secret123"

def test_redact_for_display_empty_reveal():
    env = {"GITHUB_TOKEN": "ghp_abc123"}
    result = redact_for_display(env, reveal_keys=set())
    assert "ghp_abc123" not in result["GITHUB_TOKEN"]
