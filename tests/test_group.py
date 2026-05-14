"""Tests for envoy.group and envoy.cli_group."""
from __future__ import annotations

import json
import pytest

from envoy.group import (
    add_to_group,
    delete_group,
    get_group,
    list_groups,
    remove_from_group,
)
from envoy.profile import save_profile
from envoy.cli_group import cmd_group


@pytest.fixture()
def proj(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    save_profile("myapp", "dev", {"KEY": "val"})
    save_profile("myapp", "staging", {"KEY": "val2"})
    save_profile("myapp", "prod", {"KEY": "val3"})
    return "myapp"


def test_add_to_group_returns_result(proj):
    result = add_to_group(proj, "backend", "dev")
    assert result.group == "backend"
    assert "dev" in result.members
    assert result.added == "dev"


def test_add_to_group_idempotent(proj):
    add_to_group(proj, "backend", "dev")
    result = add_to_group(proj, "backend", "dev")
    assert result.added is None
    assert result.members.count("dev") == 1


def test_add_missing_profile_raises(proj):
    with pytest.raises(FileNotFoundError):
        add_to_group(proj, "backend", "nonexistent")


def test_get_group_returns_members(proj):
    add_to_group(proj, "backend", "dev")
    add_to_group(proj, "backend", "staging")
    members = get_group(proj, "backend")
    assert set(members) == {"dev", "staging"}


def test_get_group_empty_when_none(proj):
    assert get_group(proj, "nope") == []


def test_remove_from_group(proj):
    add_to_group(proj, "backend", "dev")
    add_to_group(proj, "backend", "staging")
    result = remove_from_group(proj, "backend", "dev")
    assert result.removed == "dev"
    assert "dev" not in result.members


def test_remove_not_in_group(proj):
    result = remove_from_group(proj, "backend", "dev")
    assert result.removed is None


def test_list_groups_returns_all(proj):
    add_to_group(proj, "backend", "dev")
    add_to_group(proj, "frontend", "prod")
    groups = list_groups(proj)
    assert "backend" in groups
    assert "frontend" in groups


def test_delete_group_existing(proj):
    add_to_group(proj, "backend", "dev")
    existed = delete_group(proj, "backend")
    assert existed is True
    assert get_group(proj, "backend") == []


def test_delete_group_nonexistent(proj):
    assert delete_group(proj, "ghost") is False


# --- CLI tests ---

@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    save_profile("app", "dev", {"K": "v"})
    save_profile("app", "prod", {"K": "v"})
    return "app"


def test_cli_add_exit_zero(isolated):
    assert cmd_group(isolated, ["add", "g1", "dev"]) == 0


def test_cli_add_json_output(isolated, capsys):
    cmd_group(isolated, ["add", "g1", "dev", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert out["group"] == "g1"
    assert "dev" in out["members"]


def test_cli_list_all_groups(isolated, capsys):
    cmd_group(isolated, ["add", "g1", "dev"])
    cmd_group(isolated, ["add", "g2", "prod"])
    cmd_group(isolated, ["list", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert "g1" in out and "g2" in out


def test_cli_delete_returns_one_when_missing(isolated):
    assert cmd_group(isolated, ["delete", "ghost"]) == 1


def test_cli_unknown_sub_returns_two(isolated):
    assert cmd_group(isolated, ["bogus"]) == 2
