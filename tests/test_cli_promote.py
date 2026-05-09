"""Tests for envoy.cli_promote."""
from __future__ import annotations

import pytest

from envoy.profile import save_profile, load_profile
from envoy.cli_promote import cmd_promote


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "testproject"


def test_promote_exit_zero_on_success(isolated):
    save_profile(isolated, "staging", {"KEY": "val"})
    rc = cmd_promote([isolated, "staging", "production", "--no-history"])
    assert rc == 0


def test_promote_exit_one_on_missing_source(isolated, capsys):
    rc = cmd_promote([isolated, "ghost", "production", "--no-history"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "ghost" in captured.err


def test_promote_output_shows_counts(isolated, capsys):
    save_profile(isolated, "staging", {"A": "1", "B": "2"})
    cmd_promote([isolated, "staging", "production", "--no-history"])
    out = capsys.readouterr().out
    assert "2 key(s)" in out


def test_promote_overwrite_flag(isolated):
    save_profile(isolated, "staging", {"A": "new"})
    save_profile(isolated, "production", {"A": "old"})
    cmd_promote([isolated, "staging", "production", "--overwrite", "--no-history"])
    assert load_profile(isolated, "production")["A"] == "new"


def test_promote_keys_flag_limits_promotion(isolated):
    save_profile(isolated, "staging", {"A": "1", "B": "2"})
    cmd_promote([isolated, "staging", "production", "--keys", "A", "--no-history"])
    prod = load_profile(isolated, "production")
    assert "A" in prod
    assert "B" not in prod


def test_promote_skipped_shown_in_output(isolated, capsys):
    save_profile(isolated, "staging", {"A": "new"})
    save_profile(isolated, "production", {"A": "old"})
    cmd_promote([isolated, "staging", "production", "--no-history"])
    out = capsys.readouterr().out
    assert "skipped" in out
    assert "--overwrite" in out
