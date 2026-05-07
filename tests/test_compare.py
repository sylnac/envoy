"""Tests for envoy.compare module."""
import pytest

from envoy.compare import compare_profiles, summary, CompareResult
from envoy.profile import save_profile


@pytest.fixture
def proj(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "myproject"


def test_compare_identical_profiles(proj):
    env = {"HOST": "localhost", "PORT": "5432"}
    save_profile(proj, "dev", env)
    save_profile(proj, "staging", env)
    result = compare_profiles(proj, "dev", "staging")
    assert not result.has_differences
    assert result.in_both_same == env
    assert result.only_in_a == {}
    assert result.only_in_b == {}
    assert result.in_both_different == {}


def test_compare_only_in_a(proj):
    save_profile(proj, "dev", {"HOST": "localhost", "DEBUG": "true"})
    save_profile(proj, "prod", {"HOST": "localhost"})
    result = compare_profiles(proj, "dev", "prod")
    assert result.only_in_a == {"DEBUG": "true"}
    assert result.only_in_b == {}
    assert result.has_differences


def test_compare_only_in_b(proj):
    save_profile(proj, "dev", {"HOST": "localhost"})
    save_profile(proj, "prod", {"HOST": "localhost", "LOG_LEVEL": "error"})
    result = compare_profiles(proj, "dev", "prod")
    assert result.only_in_b == {"LOG_LEVEL": "error"}
    assert result.only_in_a == {}


def test_compare_changed_values(proj):
    save_profile(proj, "dev", {"DB_URL": "localhost:5432"})
    save_profile(proj, "prod", {"DB_URL": "prod-db:5432"})
    result = compare_profiles(proj, "dev", "prod")
    assert "DB_URL" in result.in_both_different
    assert result.in_both_different["DB_URL"] == ("localhost:5432", "prod-db:5432")


def test_compare_missing_profile_treated_as_empty(proj):
    save_profile(proj, "dev", {"HOST": "localhost"})
    result = compare_profiles(proj, "dev", "nonexistent")
    assert result.only_in_a == {"HOST": "localhost"}
    assert result.only_in_b == {}


def test_compare_redact_secrets(proj):
    save_profile(proj, "dev", {"API_KEY": "secret123", "HOST": "localhost"})
    save_profile(proj, "prod", {"API_KEY": "othersecret", "HOST": "localhost"})
    result = compare_profiles(proj, "dev", "prod", redact=True)
    val_a, val_b = result.in_both_different["API_KEY"]
    assert "secret" not in val_a
    assert "secret" not in val_b
    assert "*" in val_a or val_a == "***"


def test_all_keys_aggregates_all(proj):
    save_profile(proj, "a", {"X": "1", "Y": "2"})
    save_profile(proj, "b", {"Y": "9", "Z": "3"})
    result = compare_profiles(proj, "a", "b")
    assert result.all_keys == {"X", "Y", "Z"}


def test_summary_no_differences(proj):
    save_profile(proj, "dev", {"HOST": "localhost"})
    save_profile(proj, "staging", {"HOST": "localhost"})
    result = compare_profiles(proj, "dev", "staging")
    out = summary(result)
    assert "No differences" in out


def test_summary_shows_changed_keys(proj):
    save_profile(proj, "dev", {"PORT": "3000"})
    save_profile(proj, "prod", {"PORT": "80"})
    result = compare_profiles(proj, "dev", "prod")
    out = summary(result)
    assert "PORT" in out
    assert "3000" in out
    assert "80" in out
