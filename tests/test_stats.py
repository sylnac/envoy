"""Tests for envoy.stats module."""
from __future__ import annotations

import pytest

from envoy.profile import save_profile
from envoy.stats import profile_stats, project_stats, ProfileStats, ProjectStats


@pytest.fixture()
def proj(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "myproject"


def test_profile_stats_counts_keys(proj):
    save_profile(proj, "dev", {"HOST": "localhost", "PORT": "5432"})
    s = profile_stats(proj, "dev")
    assert s.total_keys == 2
    assert s.profile == "dev"


def test_profile_stats_counts_secrets(proj):
    save_profile(proj, "dev", {"API_KEY": "abc", "PASSWORD": "secret", "HOST": "localhost"})
    s = profile_stats(proj, "dev")
    assert s.secret_keys == 2
    assert s.plain_keys == 1


def test_profile_stats_empty_values(proj):
    save_profile(proj, "dev", {"HOST": "", "PORT": "5432", "TOKEN": ""})
    s = profile_stats(proj, "dev")
    assert s.empty_values == 2


def test_profile_stats_secret_ratio(proj):
    save_profile(proj, "dev", {"API_KEY": "x", "HOST": "y", "PORT": "z", "TOKEN": "t"})
    s = profile_stats(proj, "dev")
    assert s.secret_ratio == pytest.approx(0.5)


def test_profile_stats_empty_profile(proj):
    save_profile(proj, "empty", {})
    s = profile_stats(proj, "empty")
    assert s.total_keys == 0
    assert s.secret_ratio == 0.0


def test_profile_stats_keys_list(proj):
    save_profile(proj, "dev", {"A": "1", "B": "2"})
    s = profile_stats(proj, "dev")
    assert set(s.keys) == {"A", "B"}


def test_project_stats_aggregates_profiles(proj):
    save_profile(proj, "dev", {"HOST": "a", "PORT": "b"})
    save_profile(proj, "prod", {"HOST": "c", "SECRET_KEY": "d"})
    ps = project_stats(proj)
    assert ps.total_profiles == 2
    assert ps.total_keys == 4


def test_project_stats_unique_keys(proj):
    save_profile(proj, "dev", {"HOST": "a", "PORT": "b"})
    save_profile(proj, "prod", {"HOST": "c", "DEBUG": "false"})
    ps = project_stats(proj)
    # HOST appears in both but counts once
    assert ps.unique_keys == 3


def test_project_stats_by_profile_lookup(proj):
    save_profile(proj, "dev", {"X": "1"})
    save_profile(proj, "prod", {"Y": "2"})
    ps = project_stats(proj)
    mapping = ps.by_profile()
    assert "dev" in mapping
    assert "prod" in mapping
    assert isinstance(mapping["dev"], ProfileStats)


def test_project_stats_empty_project(proj):
    ps = project_stats(proj)
    assert ps.total_profiles == 0
    assert ps.total_keys == 0
    assert ps.unique_keys == 0
