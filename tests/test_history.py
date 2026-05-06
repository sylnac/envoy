"""Tests for envoy.history."""

import time
from pathlib import Path

import pytest

from envoy.history import (
    clear_history,
    get_snapshot,
    load_history,
    record_snapshot,
)


@pytest.fixture()
def proj(tmp_path: Path) -> Path:
    return tmp_path


def test_record_and_load_single_snapshot(proj):
    env = {"KEY": "value", "PORT": "8080"}
    record_snapshot(proj, "dev", env, message="initial")

    history = load_history(proj, "dev")
    assert len(history) == 1
    assert history[0]["env"] == env
    assert history[0]["message"] == "initial"
    assert isinstance(history[0]["ts"], float)


def test_load_history_empty_when_no_file(proj):
    assert load_history(proj, "nonexistent") == []


def test_multiple_snapshots_appended_in_order(proj):
    record_snapshot(proj, "prod", {"A": "1"}, message="first")
    record_snapshot(proj, "prod", {"A": "2"}, message="second")
    record_snapshot(proj, "prod", {"A": "3"}, message="third")

    history = load_history(proj, "prod")
    assert len(history) == 3
    assert [h["message"] for h in history] == ["first", "second", "third"]


def test_get_snapshot_latest_by_default(proj):
    record_snapshot(proj, "dev", {"X": "old"})
    record_snapshot(proj, "dev", {"X": "new"})

    snap = get_snapshot(proj, "dev")
    assert snap is not None
    assert snap["env"] == {"X": "new"}


def test_get_snapshot_by_index(proj):
    record_snapshot(proj, "dev", {"X": "first"})
    record_snapshot(proj, "dev", {"X": "second"})

    snap = get_snapshot(proj, "dev", index=0)
    assert snap["env"] == {"X": "first"}


def test_get_snapshot_returns_none_when_empty(proj):
    assert get_snapshot(proj, "missing") is None


def test_clear_history_removes_file(proj):
    record_snapshot(proj, "staging", {"K": "v"})
    assert len(load_history(proj, "staging")) == 1

    clear_history(proj, "staging")
    assert load_history(proj, "staging") == []


def test_clear_history_noop_when_no_file(proj):
    # Should not raise even if file doesn't exist
    clear_history(proj, "ghost")


def test_profiles_are_isolated(proj):
    record_snapshot(proj, "dev", {"ENV": "dev"})
    record_snapshot(proj, "prod", {"ENV": "prod"})

    dev_history = load_history(proj, "dev")
    prod_history = load_history(proj, "prod")

    assert dev_history[0]["env"] == {"ENV": "dev"}
    assert prod_history[0]["env"] == {"ENV": "prod"}
