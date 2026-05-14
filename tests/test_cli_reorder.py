"""Tests for envoy.cli_reorder"""
from __future__ import annotations

import json
import pytest

from envoy.profile import save_profile, load_profile
from envoy.cli_reorder import cmd_reorder


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "proj"


def test_reorder_exit_zero_on_success(isolated):
    save_profile(isolated, "dev", {"B": "2", "A": "1"})
    rc = cmd_reorder([isolated, "dev", "A", "B"])
    assert rc == 0


def test_reorder_exit_one_on_missing_profile(isolated):
    rc = cmd_reorder([isolated, "ghost", "A"])
    assert rc == 1


def test_reorder_output_shows_counts(isolated, capsys):
    save_profile(isolated, "dev", {"B": "2", "A": "1"})
    cmd_reorder([isolated, "dev", "A", "B"])
    out = capsys.readouterr().out
    assert "reordered" in out


def test_reorder_json_output(isolated, capsys):
    save_profile(isolated, "dev", {"B": "2", "A": "1"})
    rc = cmd_reorder([isolated, "dev", "A", "B", "--json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert rc == 0
    assert data["ordered_keys"] == ["A", "B"]
    assert data["error"] is None


def test_reorder_json_error_on_missing_profile(isolated, capsys):
    rc = cmd_reorder([isolated, "ghost", "A", "--json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert rc == 1
    assert data["error"] is not None


def test_reorder_drop_remaining_flag(isolated):
    save_profile(isolated, "dev", {"A": "1", "B": "2", "C": "3"})
    cmd_reorder([isolated, "dev", "A", "--drop-remaining"])
    env = load_profile(isolated, "dev")
    assert list(env.keys()) == ["A"]
