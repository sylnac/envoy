"""Tests for envoy.snapshot_diff."""

from __future__ import annotations

import pytest

from envoy.snapshot_diff import compare_snapshots, compare_to_current


@pytest.fixture()
def proj(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "myproject"


def _seed(project: str, *envs: dict) -> None:
    from envoy.history import record_snapshot

    for env in envs:
        record_snapshot(project, env)


def test_compare_two_snapshots(proj):
    _seed(proj, {"A": "1"}, {"A": "2", "B": "3"})
    cmp = compare_snapshots(proj, from_index=0, to_index=1)
    assert cmp.project == proj
    assert cmp.diff.changed == {"A": ("1", "2")}
    assert cmp.diff.added == {"B": "3"}
    assert cmp.diff.removed == {}


def test_compare_defaults_to_last_two(proj):
    _seed(proj, {"X": "old"}, {"X": "new"})
    cmp = compare_snapshots(proj)
    assert cmp.diff.changed == {"X": ("old", "new")}


def test_compare_no_changes(proj):
    _seed(proj, {"K": "v"}, {"K": "v"})
    cmp = compare_snapshots(proj)
    from envoy.diff import has_changes
    assert not has_changes(cmp.diff)


def test_compare_raises_on_empty_history(proj):
    with pytest.raises(ValueError, match="No history"):
        compare_snapshots(proj)


def test_compare_raises_on_insufficient_snapshots(proj):
    _seed(proj, {"A": "1"})
    with pytest.raises(ValueError, match="Not enough snapshots"):
        compare_snapshots(proj, from_index=0, to_index=1)


def test_compare_to_current_returns_diff(proj):
    _seed(proj, {"A": "1", "B": "old"})
    result = compare_to_current(proj, {"A": "1", "B": "new", "C": "added"})
    assert result is not None
    assert result.diff.changed == {"B": ("old", "new")}
    assert result.diff.added == {"C": "added"}
    assert result.to_timestamp == "(current)"


def test_compare_to_current_returns_none_when_no_history(proj):
    result = compare_to_current(proj, {"A": "1"})
    assert result is None
