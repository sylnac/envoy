"""Tests for envoy.cli_doctor."""
from __future__ import annotations

import json
import os
import sys

import pytest

from envoy.cli_doctor import cmd_doctor
from envoy.profile import save_profile


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_no_profiles_exits_zero(isolated):
    # No profiles → warning only, not an error → exit 0
    rc = cmd_doctor(["--project", str(isolated)])
    assert rc == 0


def test_clean_profile_exits_zero(isolated):
    save_profile(str(isolated), "dev", {"APP": "myapp"})
    rc = cmd_doctor(["--project", str(isolated)])
    assert rc == 0


def test_empty_secret_exits_one(isolated):
    save_profile(str(isolated), "dev", {"API_KEY": ""})
    rc = cmd_doctor(["--project", str(isolated)])
    assert rc == 1


def test_json_output_is_valid(isolated, capsys):
    save_profile(str(isolated), "dev", {"API_KEY": ""})
    cmd_doctor(["--project", str(isolated), "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert all("level" in item and "profile" in item and "message" in item for item in data)


def test_strict_mode_exits_one_on_warning(isolated):
    save_profile(str(isolated), "dev", {"lowercase_key": "val"})
    rc = cmd_doctor(["--project", str(isolated), "--strict"])
    assert rc == 1


def test_all_clear_message_printed(isolated, capsys):
    save_profile(str(isolated), "dev", {"APP": "ok"})
    cmd_doctor(["--project", str(isolated)])
    captured = capsys.readouterr()
    assert "passed" in captured.out
