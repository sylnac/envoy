"""Tests for envoy.scaffold."""
import pytest

from envoy.profile import load_profile, profile_exists
from envoy.scaffold import ScaffoldResult, ok, scaffold_profile


@pytest.fixture()
def proj(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "myproject"


def test_scaffold_creates_profile(proj):
    result = scaffold_profile(proj, "dev", ["DB_HOST", "PORT"])
    assert ok(result)
    assert profile_exists(proj, "dev")


def test_scaffold_writes_all_keys(proj):
    result = scaffold_profile(proj, "dev", ["DB_HOST", "PORT", "CACHE"])
    assert result.keys_written == ["DB_HOST", "PORT", "CACHE"]


def test_scaffold_non_secret_gets_empty_placeholder(proj):
    scaffold_profile(proj, "dev", ["DB_HOST"])
    env = load_profile(proj, "dev")
    assert env["DB_HOST"] == ""


def test_scaffold_secret_key_gets_change_me(proj):
    scaffold_profile(proj, "dev", ["API_KEY", "DB_PASSWORD"])
    env = load_profile(proj, "dev")
    assert env["API_KEY"] == "CHANGE_ME"
    assert env["DB_PASSWORD"] == "CHANGE_ME"


def test_scaffold_custom_placeholder(proj):
    scaffold_profile(proj, "dev", ["APP_NAME"], placeholder="todo")
    env = load_profile(proj, "dev")
    assert env["APP_NAME"] == "todo"


def test_scaffold_custom_secret_placeholder(proj):
    scaffold_profile(proj, "dev", ["SECRET_TOKEN"], secret_placeholder="FILL_IN")
    env = load_profile(proj, "dev")
    assert env["SECRET_TOKEN"] == "FILL_IN"


def test_scaffold_uses_provided_defaults(proj):
    scaffold_profile(
        proj, "dev", ["DB_HOST", "PORT"], defaults={"DB_HOST": "localhost", "PORT": "5432"}
    )
    env = load_profile(proj, "dev")
    assert env["DB_HOST"] == "localhost"
    assert env["PORT"] == "5432"


def test_scaffold_does_not_overwrite_by_default(proj):
    scaffold_profile(proj, "dev", ["A"], defaults={"A": "original"})
    result = scaffold_profile(proj, "dev", ["A"], defaults={"A": "new"})
    assert not ok(result)
    assert result.skipped is True
    env = load_profile(proj, "dev")
    assert env["A"] == "original"


def test_scaffold_overwrite_replaces_profile(proj):
    scaffold_profile(proj, "dev", ["A"], defaults={"A": "original"})
    result = scaffold_profile(proj, "dev", ["B"], defaults={"B": "new"}, overwrite=True)
    assert ok(result)
    env = load_profile(proj, "dev")
    assert "A" not in env
    assert env["B"] == "new"


def test_scaffold_empty_keys_list(proj):
    result = scaffold_profile(proj, "dev", [])
    assert ok(result)
    assert result.keys_written == []
    env = load_profile(proj, "dev")
    assert env == {}


def test_scaffold_error_message_on_existing(proj):
    scaffold_profile(proj, "dev", ["X"])
    result = scaffold_profile(proj, "dev", ["X"])
    assert result.error is not None
    assert "overwrite" in result.error
