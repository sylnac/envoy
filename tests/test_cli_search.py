"""Tests for envoy.cli_search."""
import os
import pytest

from envoy.profile import save_profile
from envoy.cli_search import cmd_search


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    save_profile(str(tmp_path), "dev", {"DB_HOST": "localhost", "SECRET_KEY": "s3cr3t", "PORT": "8000"})
    save_profile(str(tmp_path), "prod", {"DB_HOST": "prod.db", "SECRET_KEY": "pr0d", "PORT": "80"})
    return tmp_path


def test_search_finds_matches(isolated, capsys):
    rc = cmd_search(["DB_HOST", "--dir", str(isolated)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "dev" in out
    assert "prod" in out
    assert "2 match(es)" in out


def test_search_no_matches_returns_1(isolated, capsys):
    rc = cmd_search(["MISSING_KEY", "--dir", str(isolated)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "No matches" in out


def test_search_glob(isolated, capsys):
    rc = cmd_search(["DB_*", "--dir", str(isolated)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "DB_HOST" in out


def test_search_redact_secret(isolated, capsys):
    rc = cmd_search(["SECRET_KEY", "--redact", "--dir", str(isolated)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "s3cr3t" not in out
    assert "pr0d" not in out


def test_search_limit_profile(isolated, capsys):
    rc = cmd_search(["DB_HOST", "--profile", "dev", "--dir", str(isolated)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "dev" in out
    assert "1 match(es)" in out


def test_compare_flag(isolated, capsys):
    rc = cmd_search(["DB_HOST", "--compare", "--dir", str(isolated)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "localhost" in out
    assert "prod.db" in out


def test_compare_missing_key_shows_not_set(isolated, capsys):
    rc = cmd_search(["NONEXISTENT", "--compare", "--dir", str(isolated)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "(not set)" in out
