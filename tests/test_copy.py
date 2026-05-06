"""Tests for envoy.copy (profile copy/rename utilities)."""

from __future__ import annotations

import os
import pytest

from envoy.profile import save_profile, load_profile, profile_exists
from envoy.copy import copy_profile, rename_profile, CopyResult


@pytest.fixture()
def proj(tmp_path, monkeypatch):
    """Isolate profile storage to a temp directory."""
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "testproject"


def test_copy_creates_destination(proj):
    save_profile(proj, "base", {"A": "1", "B": "2"})
    result = copy_profile(proj, "base", "dev")
    assert profile_exists(proj, "dev")
    assert isinstance(result, CopyResult)
    assert result.keys_copied == 2
    assert result.source == "base"
    assert result.destination == "dev"
    assert result.overwritten is False


def test_copy_merges_by_default(proj):
    save_profile(proj, "base", {"A": "1", "B": "2"})
    save_profile(proj, "dev", {"B": "original", "C": "3"})
    copy_profile(proj, "base", "dev")  # merge; base wins on conflict
    merged = load_profile(proj, "dev")
    assert merged["A"] == "1"
    assert merged["B"] == "2"   # source wins
    assert merged["C"] == "3"   # dest-only key preserved


def test_copy_overwrite_replaces_destination(proj):
    save_profile(proj, "base", {"A": "1"})
    save_profile(proj, "dev", {"B": "2", "C": "3"})
    result = copy_profile(proj, "base", "dev", overwrite=True)
    dest_env = load_profile(proj, "dev")
    assert dest_env == {"A": "1"}
    assert result.overwritten is True


def test_copy_subset_of_keys(proj):
    save_profile(proj, "base", {"A": "1", "B": "2", "C": "3"})
    copy_profile(proj, "base", "partial", keys=["A", "C"])
    dest_env = load_profile(proj, "partial")
    assert "A" in dest_env
    assert "C" in dest_env
    assert "B" not in dest_env


def test_copy_missing_source_raises(proj):
    with pytest.raises(FileNotFoundError, match="Source profile"):
        copy_profile(proj, "nonexistent", "dev")


def test_rename_moves_profile(proj):
    save_profile(proj, "staging", {"X": "10"})
    rename_profile(proj, "staging", "production")
    assert profile_exists(proj, "production")
    assert not profile_exists(proj, "staging")
    assert load_profile(proj, "production") == {"X": "10"}


def test_rename_missing_source_raises(proj):
    with pytest.raises(FileNotFoundError):
        rename_profile(proj, "ghost", "new")


def test_rename_existing_destination_raises(proj):
    save_profile(proj, "a", {"K": "v"})
    save_profile(proj, "b", {"K": "v"})
    with pytest.raises(FileExistsError):
        rename_profile(proj, "a", "b")
