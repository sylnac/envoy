"""Additional tests for value-pattern filtering in cli_search."""
import pytest

from envoy.profile import save_profile
from envoy.cli_search import cmd_search
from envoy.search import search_profiles


@pytest.fixture()
def proj(tmp_path):
    save_profile(str(tmp_path), "local", {
        "REDIS_URL": "redis://localhost:6379",
        "DATABASE_URL": "postgres://localhost/mydb",
        "SENTRY_DSN": "https://sentry.io/123",
    })
    save_profile(str(tmp_path), "staging", {
        "REDIS_URL": "redis://staging.cache:6379",
        "DATABASE_URL": "postgres://staging.db/mydb",
        "SENTRY_DSN": "https://sentry.io/456",
    })
    return str(tmp_path)


def test_value_filter_localhost_only(proj):
    summary = search_profiles(proj, "*_URL", value_pattern="*localhost*")
    assert summary.total == 2
    assert all("localhost" in r.value for r in summary.results)


def test_value_filter_no_match(proj):
    summary = search_profiles(proj, "*_URL", value_pattern="*nonexistent*")
    assert summary.total == 0


def test_cli_value_filter(proj, capsys):
    rc = cmd_search(["*_URL", "--value", "*localhost*", "--dir", proj])
    assert rc == 0
    out = capsys.readouterr().out
    assert "localhost" in out
    assert "staging" not in out


def test_cli_value_filter_no_match(proj, capsys):
    rc = cmd_search(["*_URL", "--value", "*nothing*", "--dir", proj])
    assert rc == 1
    out = capsys.readouterr().out
    assert "No matches" in out


def test_search_profiles_searched_count(proj):
    summary = search_profiles(proj, "REDIS_URL")
    assert summary.profiles_searched == 2
    assert summary.total == 2
