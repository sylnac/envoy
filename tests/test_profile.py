"""Tests for envoy.profile module."""

import pytest

from envoy.profile import (
    delete_profile,
    list_profiles,
    load_profile,
    profile_exists,
    profile_path,
    save_profile,
)


def test_profile_path_structure(tmp_path):
    path = profile_path("production", base=str(tmp_path))
    assert path.name == "production.env"
    assert path.parent.name == ".envoy"


def test_save_and_load_profile(tmp_path):
    data = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    save_profile("dev", data, base=str(tmp_path))
    loaded = load_profile("dev", base=str(tmp_path))
    assert loaded == data


def test_list_profiles_empty(tmp_path):
    assert list_profiles(base=str(tmp_path)) == []


def test_list_profiles_multiple(tmp_path):
    save_profile("staging", {"X": "1"}, base=str(tmp_path))
    save_profile("production", {"X": "2"}, base=str(tmp_path))
    save_profile("dev", {"X": "3"}, base=str(tmp_path))
    assert list_profiles(base=str(tmp_path)) == ["dev", "production", "staging"]


def test_profile_exists_true(tmp_path):
    save_profile("test", {"KEY": "val"}, base=str(tmp_path))
    assert profile_exists("test", base=str(tmp_path)) is True


def test_profile_exists_false(tmp_path):
    assert profile_exists("ghost", base=str(tmp_path)) is False


def test_load_profile_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="Profile 'missing' not found"):
        load_profile("missing", base=str(tmp_path))


def test_delete_profile_existing(tmp_path):
    save_profile("temp", {"A": "1"}, base=str(tmp_path))
    assert delete_profile("temp", base=str(tmp_path)) is True
    assert not profile_exists("temp", base=str(tmp_path))


def test_delete_profile_nonexistent(tmp_path):
    assert delete_profile("nope", base=str(tmp_path)) is False


def test_save_creates_directory(tmp_path):
    nested_base = tmp_path / "project" / "subdir"
    save_profile("ci", {"CI": "true"}, base=str(nested_base))
    assert profile_exists("ci", base=str(nested_base))
