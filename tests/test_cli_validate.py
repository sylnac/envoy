"""Tests for envoy.cli_validate."""

import pytest

from envoy.cli_validate import cmd_validate
from envoy.profile import save_profile


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_DIR", str(tmp_path))
    return tmp_path


def test_validate_required_keys_pass(isolated):
    save_profile("dev", {"DB_HOST": "localhost", "API_KEY": "secret"})
    rc = cmd_validate(["dev", "--require", "DB_HOST", "API_KEY"])
    assert rc == 0


def test_validate_required_keys_fail(isolated, capsys):
    save_profile("dev", {"DB_HOST": "localhost"})
    rc = cmd_validate(["dev", "--require", "DB_HOST", "API_KEY"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "API_KEY" in out


def test_validate_schema_pass(isolated, tmp_path):
    save_profile("prod", {"DB_HOST": "db.example.com", "PORT": "5432"})
    schema_file = tmp_path / "schema.env"
    schema_file.write_text("DB_HOST=required\nPORT=optional\n")
    rc = cmd_validate(["prod", "--schema", str(schema_file)])
    assert rc == 0


def test_validate_schema_missing_required(isolated, tmp_path, capsys):
    save_profile("prod", {"PORT": "5432"})
    schema_file = tmp_path / "schema.env"
    schema_file.write_text("DB_HOST=required\nPORT=optional\n")
    rc = cmd_validate(["prod", "--schema", str(schema_file)])
    assert rc == 1
    assert "DB_HOST" in capsys.readouterr().out


def test_validate_no_extra_fails(isolated, tmp_path, capsys):
    save_profile("dev", {"A": "1", "B": "2"})
    schema_file = tmp_path / "schema.env"
    schema_file.write_text("A=required\n")
    rc = cmd_validate(["dev", "--schema", str(schema_file), "--no-extra"])
    assert rc == 1
    assert "B" in capsys.readouterr().out


def test_validate_missing_profile(isolated, capsys):
    rc = cmd_validate(["ghost", "--require", "FOO"])
    assert rc == 2
    assert "ghost" in capsys.readouterr().err


def test_validate_missing_schema_file(isolated, capsys):
    save_profile("dev", {"A": "1"})
    rc = cmd_validate(["dev", "--schema", "/nonexistent/schema.env"])
    assert rc == 2
