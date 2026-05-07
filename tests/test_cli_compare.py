"""Tests for envoy.cli_compare module."""
import json
import pytest

from envoy.cli_compare import cmd_compare
from envoy.profile import save_profile


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return tmp_path


def test_no_differences_returns_0(isolated, capsys):
    save_profile("proj", "dev", {"HOST": "localhost"})
    save_profile("proj", "prod", {"HOST": "localhost"})
    code = cmd_compare(["proj", "dev", "prod"])
    assert code == 0
    out = capsys.readouterr().out
    assert "No differences" in out


def test_differences_returns_1(isolated, capsys):
    save_profile("proj", "dev", {"PORT": "3000"})
    save_profile("proj", "prod", {"PORT": "80"})
    code = cmd_compare(["proj", "dev", "prod"])
    assert code == 1


def test_output_contains_key_and_values(isolated, capsys):
    save_profile("proj", "dev", {"PORT": "3000"})
    save_profile("proj", "prod", {"PORT": "80"})
    cmd_compare(["proj", "dev", "prod"])
    out = capsys.readouterr().out
    assert "PORT" in out
    assert "3000" in out
    assert "80" in out


def test_json_output(isolated, capsys):
    save_profile("proj", "dev", {"HOST": "a", "PORT": "1"})
    save_profile("proj", "prod", {"HOST": "b", "PORT": "1"})
    cmd_compare(["proj", "dev", "prod", "--json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["profile_a"] == "dev"
    assert data["profile_b"] == "prod"
    assert "HOST" in data["in_both_different"]
    assert data["in_both_different"]["HOST"]["a"] == "a"
    assert data["in_both_same"]["PORT"] == "1"


def test_redact_flag_masks_secrets(isolated, capsys):
    save_profile("proj", "dev", {"API_KEY": "supersecret"})
    save_profile("proj", "prod", {"API_KEY": "othersecret"})
    cmd_compare(["proj", "dev", "prod", "--redact"])
    out = capsys.readouterr().out
    assert "supersecret" not in out
    assert "othersecret" not in out


def test_missing_profile_treated_gracefully(isolated, capsys):
    save_profile("proj", "dev", {"X": "1"})
    code = cmd_compare(["proj", "dev", "ghost"])
    assert code == 1
    out = capsys.readouterr().out
    assert "X" in out
