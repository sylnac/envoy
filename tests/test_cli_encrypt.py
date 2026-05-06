"""Tests for envoy.cli_encrypt."""

from __future__ import annotations

import pytest

pytest.importorskip("cryptography", reason="cryptography not installed")

from envoy.encrypt import generate_key, decrypt_env
from envoy.profile import save_profile, load_profile
from envoy.cli_encrypt import cmd_encrypt, cmd_decrypt


@pytest.fixture()
def isolated(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def key():
    return generate_key()


def test_generate_key_flag(isolated, capsys):
    rc = cmd_encrypt(["--generate-key", "ignored"], )
    # argparse sees --generate-key before positional; use argv directly
    rc = cmd_encrypt(["--generate-key", "someprofile"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert len(out) > 10


def test_encrypt_missing_profile(isolated, capsys):
    rc = cmd_encrypt(["nonexistent", "--project", isolated])
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_encrypt_secret_keys_only(isolated, key, capsys):
    env = {"DB_PASSWORD": "s3cret", "HOST": "localhost"}
    save_profile(isolated, "dev", env)

    rc = cmd_encrypt(["dev", "--project", isolated, "--key", key])
    assert rc == 0

    saved = load_profile(isolated, "dev")
    # HOST should be untouched
    assert saved["HOST"] == "localhost"
    # DB_PASSWORD should be encrypted (different from original)
    assert saved["DB_PASSWORD"] != "s3cret"


def test_encrypt_all_keys(isolated, key, capsys):
    env = {"HOST": "localhost", "PORT": "5432"}
    save_profile(isolated, "prod", env)

    rc = cmd_encrypt(["prod", "--project", isolated, "--key", key, "--all"])
    assert rc == 0

    saved = load_profile(isolated, "prod")
    assert saved["HOST"] != "localhost"
    assert saved["PORT"] != "5432"


def test_decrypt_round_trip(isolated, key, capsys):
    original = {"API_TOKEN": "tok_abc", "REGION": "us-east-1"}
    save_profile(isolated, "staging", original)

    cmd_encrypt(["staging", "--project", isolated, "--key", key, "--all"])
    rc = cmd_decrypt(["staging", "--project", isolated, "--key", key])
    assert rc == 0

    restored = load_profile(isolated, "staging")
    assert restored == original


def test_decrypt_missing_profile(isolated, capsys):
    rc = cmd_decrypt(["ghost", "--project", isolated])
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_decrypt_wrong_key_returns_error(isolated, key, capsys):
    env = {"SECRET": "value"}
    save_profile(isolated, "env", env)
    cmd_encrypt(["env", "--project", isolated, "--key", key, "--all"])

    wrong_key = generate_key()
    rc = cmd_decrypt(["env", "--project", isolated, "--key", wrong_key])
    assert rc == 1
    assert "error" in capsys.readouterr().err.lower()
