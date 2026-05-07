"""Tests for envoy.cli_tag CLI commands."""
import pytest

from envoy.cli_tag import cmd_tag


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "proj"


def test_add_tag_exit_zero(isolated, capsys):
    rc = cmd_tag([isolated, "add", "dev", "local"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "local" in out


def test_add_tag_idempotent_output(isolated, capsys):
    cmd_tag([isolated, "add", "dev", "local"])
    rc = cmd_tag([isolated, "add", "dev", "local"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.count("local") == 1


def test_remove_tag(isolated, capsys):
    cmd_tag([isolated, "add", "dev", "local"])
    rc = cmd_tag([isolated, "remove", "dev", "local"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "local" not in out


def test_list_tags_none(isolated, capsys):
    rc = cmd_tag([isolated, "list", "dev"])
    assert rc == 0
    assert "No tags" in capsys.readouterr().out


def test_list_tags_shows_tags(isolated, capsys):
    cmd_tag([isolated, "add", "dev", "alpha"])
    cmd_tag([isolated, "add", "dev", "beta"])
    capsys.readouterr()
    rc = cmd_tag([isolated, "list", "dev"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_find_profiles_with_tag(isolated, capsys):
    cmd_tag([isolated, "add", "dev", "local"])
    cmd_tag([isolated, "add", "ci", "local"])
    capsys.readouterr()
    rc = cmd_tag([isolated, "find", "local"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "dev" in out
    assert "ci" in out


def test_find_no_match_returns_1(isolated, capsys):
    rc = cmd_tag([isolated, "find", "ghost"])
    assert rc == 1


def test_clear_tags(isolated, capsys):
    cmd_tag([isolated, "add", "dev", "local"])
    rc = cmd_tag([isolated, "clear", "dev"])
    assert rc == 0
    capsys.readouterr()
    cmd_tag([isolated, "list", "dev"])
    out = capsys.readouterr().out
    assert "No tags" in out
