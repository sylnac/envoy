"""Tests for envoy.search."""
import pytest

from envoy.profile import save_profile
from envoy.search import find_key_across_profiles, search_profiles


@pytest.fixture()
def proj(tmp_path):
    save_profile(str(tmp_path), "dev", {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET_KEY": "abc"})
    save_profile(str(tmp_path), "prod", {"DB_HOST": "prod.db", "DB_PORT": "5432", "API_TOKEN": "xyz"})
    save_profile(str(tmp_path), "test", {"DB_HOST": "testdb", "CACHE_URL": "redis://localhost"})
    return str(tmp_path)


def test_search_exact_key(proj):
    summary = search_profiles(proj, "DB_HOST")
    assert summary.total == 3
    assert all(r.key == "DB_HOST" for r in summary.results)


def test_search_glob_pattern(proj):
    summary = search_profiles(proj, "DB_*")
    keys = {r.key for r in summary.results}
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys
    assert "API_TOKEN" not in keys


def test_search_case_insensitive_by_default(proj):
    summary = search_profiles(proj, "db_host")
    assert summary.total == 3


def test_search_case_sensitive_no_match(proj):
    summary = search_profiles(proj, "db_host", case_sensitive=True)
    assert summary.total == 0


def test_search_value_pattern(proj):
    summary = search_profiles(proj, "DB_HOST", value_pattern="*localhost*")
    assert summary.total == 1
    assert summary.results[0].profile == "dev"


def test_search_specific_profiles(proj):
    summary = search_profiles(proj, "DB_PORT", profiles=["dev"])
    assert summary.total == 1
    assert summary.results[0].profile == "dev"
    assert summary.profiles_searched == 1


def test_search_no_match(proj):
    summary = search_profiles(proj, "NONEXISTENT_*")
    assert summary.total == 0


def test_by_profile_grouping(proj):
    summary = search_profiles(proj, "DB_*")
    grouped = summary.by_profile()
    assert "dev" in grouped
    assert "prod" in grouped


def test_find_key_across_profiles(proj):
    result = find_key_across_profiles(proj, "DB_HOST")
    assert result["dev"] == "localhost"
    assert result["prod"] == "prod.db"
    assert result["test"] == "testdb"


def test_find_key_missing_in_some_profiles(proj):
    result = find_key_across_profiles(proj, "API_TOKEN")
    assert result["prod"] == "xyz"
    assert result["dev"] is None
    assert result["test"] is None


def test_find_key_specific_profiles(proj):
    result = find_key_across_profiles(proj, "DB_HOST", profiles=["dev", "prod"])
    assert len(result) == 2
    assert "test" not in result
