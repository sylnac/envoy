"""Tests for envoy.rollback."""

from __future__ import annotations

import pytest

from envoy.history import record_snapshot
from envoy.profile import save_profile, load_profile
from envoy.rollback import rollback_profile


@pytest.fixture()
def proj(tmp_path, monkeypatch):
    """Redirect storage to a temp directory and return a project name."""
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "myproject"


def test_rollback_restores_snapshot(proj):
    env_v1 = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    env_v2 = {"DB_HOST": "prod.example.com", "DB_PORT": "5432", "DB_NAME": "app"}

    record_snapshot(proj, "production", env_v1)
    record_snapshot(proj, "production", env_v2)
    save_profile(proj, "production", env_v2)

    result = rollback_profile(proj, "production", snapshot_index=0)

    assert result.success is True
    assert result.keys_restored == len(env_v1)
    assert result.previous_keys == len(env_v2)
    restored = load_profile(proj, "production")
    assert restored == env_v1


def test_rollback_default_index_uses_last_snapshot(proj):
    env_a = {"FOO": "bar"}
    env_b = {"FOO": "baz", "EXTRA": "1"}

    record_snapshot(proj, "dev", env_a)
    record_snapshot(proj, "dev", env_b)
    save_profile(proj, "dev", env_b)

    result = rollback_profile(proj, "dev")  # default index=-1

    assert result.success is True
    restored = load_profile(proj, "dev")
    assert restored == env_b  # last snapshot == env_b


def test_rollback_no_history_returns_error(proj):
    result = rollback_profile(proj, "staging")

    assert result.success is False
    assert "No history" in result.error


def test_rollback_out_of_range_index_returns_error(proj):
    record_snapshot(proj, "dev", {"KEY": "val"})

    result = rollback_profile(proj, "dev", snapshot_index=99)

    assert result.success is False
    assert "out of range" in result.error


def test_rollback_result_contains_timestamp(proj):
    record_snapshot(proj, "dev", {"A": "1"})
    save_profile(proj, "dev", {"A": "1"})

    result = rollback_profile(proj, "dev", snapshot_index=0)

    assert result.success is True
    assert result.timestamp != ""


def test_rollback_works_when_profile_does_not_exist_yet(proj):
    """If there is no current profile file, previous_keys should be 0."""
    record_snapshot(proj, "fresh", {"INIT": "true"})

    result = rollback_profile(proj, "fresh", snapshot_index=0)

    assert result.success is True
    assert result.previous_keys == 0
    assert load_profile(proj, "fresh") == {"INIT": "true"}
