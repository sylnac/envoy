"""Tests for envoy.cli_snapshot_diff."""

from __future__ import annotations

import pytest

from envoy.cli_snapshot_diff import cmd_snapshot_diff
from envoy.history import record_snapshot


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "testproj"


def test_no_history_returns_error(isolated, capsys):
    rc = cmd_snapshot_diff([isolated])
    assert rc == 1
    out = capsys.readouterr().out
    assert "error" in out


def test_no_changes_message(isolated, capsys):
    record_snapshot(isolated, {"K": "v"})
    record_snapshot(isolated, {"K": "v"})
    rc = cmd_snapshot_diff([isolated])
    assert rc == 0
    assert "(no changes)" in capsys.readouterr().out


def test_shows_added_key(isolated, capsys):
    record_snapshot(isolated, {})
    record_snapshot(isolated, {"NEW_KEY": "hello"})
    rc = cmd_snapshot_diff([isolated])
    assert rc == 0
    out = capsys.readouterr().out
    assert "+ NEW_KEY=hello" in out


def test_shows_removed_key(isolated, capsys):
    record_snapshot(isolated, {"GONE": "bye"})
    record_snapshot(isolated, {})
    rc = cmd_snapshot_diff([isolated])
    assert rc == 0
    assert "- GONE=bye" in capsys.readouterr().out


def test_shows_changed_key(isolated, capsys):
    record_snapshot(isolated, {"VAR": "old"})
    record_snapshot(isolated, {"VAR": "new"})
    rc = cmd_snapshot_diff([isolated])
    assert rc == 0
    assert "~ VAR=" in capsys.readouterr().out


def test_redacts_secrets_by_default(isolated, capsys):
    record_snapshot(isolated, {"API_KEY": "plain"})
    record_snapshot(isolated, {"API_KEY": "changed"})
    cmd_snapshot_diff([isolated])
    out = capsys.readouterr().out
    assert "plain" not in out
    assert "changed" not in out


def test_no_redact_flag_shows_values(isolated, capsys):
    record_snapshot(isolated, {"API_KEY": "plain"})
    record_snapshot(isolated, {"API_KEY": "changed"})
    cmd_snapshot_diff([isolated, "--no-redact"])
    out = capsys.readouterr().out
    assert "plain" in out
    assert "changed" in out
