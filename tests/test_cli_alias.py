"""CLI tests for envoy alias commands."""
import json
import os
import pytest

from envoy.cli_alias import cmd_alias


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return str(tmp_path)


def test_set_alias_exit_zero(isolated):
    rc = cmd_alias(["--project", isolated, "set", "dev", "development"])
    assert rc == 0


def test_set_alias_json_output(isolated, capsys):
    cmd_alias(["--project", isolated, "--json", "set", "dev", "development"])
    out = json.loads(capsys.readouterr().out)
    assert out["dev"] == "development"


def test_remove_existing_alias(isolated):
    cmd_alias(["--project", isolated, "set", "dev", "development"])
    rc = cmd_alias(["--project", isolated, "remove", "dev"])
    assert rc == 0


def test_remove_missing_alias_exits_one(isolated):
    rc = cmd_alias(["--project", isolated, "remove", "ghost"])
    assert rc == 1


def test_resolve_returns_profile(isolated, capsys):
    cmd_alias(["--project", isolated, "set", "stg", "staging"])
    rc = cmd_alias(["--project", isolated, "resolve", "stg"])
    assert rc == 0
    assert capsys.readouterr().out.strip() == "staging"


def test_resolve_missing_exits_one(isolated):
    rc = cmd_alias(["--project", isolated, "resolve", "nope"])
    assert rc == 1


def test_list_aliases_output(isolated, capsys):
    cmd_alias(["--project", isolated, "set", "a", "alpha"])
    cmd_alias(["--project", isolated, "set", "b", "beta"])
    cmd_alias(["--project", isolated, "list"])
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_list_aliases_json(isolated, capsys):
    cmd_alias(["--project", isolated, "set", "p", "prod"])
    cmd_alias(["--project", isolated, "--json", "list"])
    data = json.loads(capsys.readouterr().out)
    assert data["p"] == "prod"


def test_for_profile(isolated, capsys):
    cmd_alias(["--project", isolated, "set", "dev", "development"])
    cmd_alias(["--project", isolated, "set", "d", "development"])
    cmd_alias(["--project", isolated, "--json", "for", "development"])
    names = json.loads(capsys.readouterr().out)
    assert sorted(names) == ["d", "dev"]


def test_no_action_exits_one(isolated):
    rc = cmd_alias(["--project", isolated])
    assert rc == 1
