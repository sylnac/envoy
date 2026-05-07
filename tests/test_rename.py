"""Tests for envoy.rename."""

from __future__ import annotations

import pytest

from envoy.profile import save_profile, load_profile, profile_exists
from envoy.rename import rename_profile, RenameResult


@pytest.fixture()
def proj(tmp_path, monkeypatch):
    """Isolate profile storage to a temp directory."""
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "myproject"


def test_rename_success(proj):
    save_profile(proj, "dev", {"KEY": "val"})
    result = rename_profile(proj, "dev", "staging")
    assert result.success is True
    assert result.old_name == "dev"
    assert result.new_name == "staging"
    assert result.error is None


def test_rename_removes_old_profile(proj):
    save_profile(proj, "dev", {"KEY": "val"})
    rename_profile(proj, "dev", "staging")
    assert not profile_exists(proj, "dev")


def test_rename_creates_new_profile(proj):
    save_profile(proj, "dev", {"KEY": "val"})
    rename_profile(proj, "dev", "staging")
    assert profile_exists(proj, "staging")


def test_rename_preserves_data(proj):
    original = {"DB_HOST": "localhost", "PORT": "5432"}
    save_profile(proj, "dev", original)
    rename_profile(proj, "dev", "staging")
    assert load_profile(proj, "staging") == original


def test_rename_missing_source_fails(proj):
    result = rename_profile(proj, "ghost", "staging")
    assert result.success is False
    assert "ghost" in result.error


def test_rename_same_name_fails(proj):
    save_profile(proj, "dev", {"K": "v"})
    result = rename_profile(proj, "dev", "dev")
    assert result.success is False
    assert "identical" in result.error


def test_rename_destination_exists_no_overwrite(proj):
    save_profile(proj, "dev", {"K": "v"})
    save_profile(proj, "staging", {"K": "other"})
    result = rename_profile(proj, "dev", "staging")
    assert result.success is False
    assert "already exists" in result.error


def test_rename_destination_exists_with_overwrite(proj):
    save_profile(proj, "dev", {"K": "new_val"})
    save_profile(proj, "staging", {"K": "old_val"})
    result = rename_profile(proj, "dev", "staging", overwrite=True)
    assert result.success is True
    assert load_profile(proj, "staging") == {"K": "new_val"}
    assert not profile_exists(proj, "dev")
