"""Tests for envoy.cli_sync."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envoy.profile import save_profile
from envoy.cli_sync import cmd_sync


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path / "store"))
    return tmp_path


def test_push_exit_zero_on_success(isolated):
    remote = isolated / "remote"
    save_profile("proj", "dev", {"KEY": "val"})
    rc = cmd_sync(["proj", "push", "--remote", str(remote), "--profile", "dev"])
    assert rc == 0
    assert (remote / "proj" / "dev.json").exists()


def test_pull_exit_zero_on_success(isolated):
    remote = isolated / "remote"
    dest = remote / "proj" / "qa.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"MODE": "qa"}))

    rc = cmd_sync(["proj", "pull", "--remote", str(remote), "--profile", "qa"])
    assert rc == 0


def test_push_missing_profile_exits_one(isolated):
    remote = isolated / "remote"
    rc = cmd_sync(["proj", "push", "--remote", str(remote), "--profile", "ghost"])
    assert rc == 1


def test_pull_missing_remote_exits_one(isolated):
    remote = isolated / "remote"
    rc = cmd_sync(["proj", "pull", "--remote", str(remote), "--profile", "nope"])
    assert rc == 1


def test_sync_all_push_multiple(isolated):
    remote = isolated / "remote"
    save_profile("proj", "dev", {"A": "1"})
    save_profile("proj", "prod", {"B": "2"})
    rc = cmd_sync(["proj", "push", "--remote", str(remote)])
    assert rc == 0
    assert (remote / "proj" / "dev.json").exists()
    assert (remote / "proj" / "prod.json").exists()


def test_overwrite_flag_passed_through(isolated, capsys):
    remote = isolated / "remote"
    save_profile("proj", "dev", {"V": "1"})
    cmd_sync(["proj", "push", "--remote", str(remote), "--profile", "dev"])
    save_profile("proj", "dev", {"V": "2"})
    rc = cmd_sync(["proj", "push", "--remote", str(remote), "--profile", "dev", "--overwrite"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "pushed" in out
