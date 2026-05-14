"""Tests for envoy.reorder"""
from __future__ import annotations

import pytest

from envoy.profile import save_profile
from envoy.reorder import reorder_profile, ok


@pytest.fixture()
def proj(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "myproject"


def _seed(proj: str, profile: str, data: dict) -> None:
    save_profile(proj, profile, data)


def test_reorder_basic(proj):
    _seed(proj, "dev", {"C": "3", "A": "1", "B": "2"})
    result = reorder_profile(proj, "dev", ["A", "B", "C"])
    assert ok(result)
    assert result.ordered_keys == ["A", "B", "C"]


def test_reorder_appends_unlisted_keys(proj):
    _seed(proj, "dev", {"A": "1", "B": "2", "Z": "26"})
    result = reorder_profile(proj, "dev", ["B", "A"])
    assert ok(result)
    assert result.ordered_keys == ["B", "A", "Z"]


def test_reorder_drop_remaining(proj):
    _seed(proj, "dev", {"A": "1", "B": "2", "Z": "26"})
    result = reorder_profile(proj, "dev", ["A"], append_remaining=False)
    assert ok(result)
    assert result.ordered_keys == ["A"]
    assert "Z" not in result.ordered_keys
    assert "B" not in result.ordered_keys


def test_reorder_ignores_unknown_keys_in_order(proj):
    _seed(proj, "dev", {"A": "1", "B": "2"})
    result = reorder_profile(proj, "dev", ["X", "A", "Y", "B"])
    assert ok(result)
    assert result.ordered_keys == ["A", "B"]


def test_reorder_missing_profile_returns_error(proj):
    result = reorder_profile(proj, "ghost", ["A"])
    assert not ok(result)
    assert result.error is not None
    assert "ghost" in result.error


def test_reorder_moved_count(proj):
    _seed(proj, "dev", {"A": "1", "B": "2", "C": "3"})
    result = reorder_profile(proj, "dev", ["C", "B", "A"])
    assert ok(result)
    assert result.moved + result.unchanged == len(result.ordered_keys)


def test_reorder_already_ordered(proj):
    _seed(proj, "dev", {"A": "1", "B": "2", "C": "3"})
    result = reorder_profile(proj, "dev", ["A", "B", "C"])
    assert ok(result)
    assert result.ordered_keys == ["A", "B", "C"]


def test_reorder_empty_profile(proj):
    _seed(proj, "dev", {})
    result = reorder_profile(proj, "dev", ["A", "B"])
    assert ok(result)
    assert result.ordered_keys == []
