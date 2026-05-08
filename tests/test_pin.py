"""Tests for envoy.pin and envoy.cli_pin."""

from __future__ import annotations

import pytest

from envoy.pin import get_pinned, is_pinned, pin_profile, unpin_profile
from envoy.profile import save_profile
from envoy.cli_pin import cmd_pin


@pytest.fixture()
def proj(tmp_path, monkeypatch):
    """Redirect profile storage to a temp directory."""
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "myproject"


def _make_profile(proj: str, name: str) -> None:
    save_profile(proj, name, {"KEY": "value"})


# --- unit tests for envoy.pin ---

def test_get_pinned_returns_none_when_no_pin(proj):
    assert get_pinned(proj) is None


def test_pin_profile_returns_profile_name(proj):
    _make_profile(proj, "dev")
    result = pin_profile(proj, "dev")
    assert result == "dev"


def test_get_pinned_after_pin(proj):
    _make_profile(proj, "staging")
    pin_profile(proj, "staging")
    assert get_pinned(proj) == "staging"


def test_pin_nonexistent_profile_raises(proj):
    with pytest.raises(ValueError, match="does not exist"):
        pin_profile(proj, "ghost")


def test_is_pinned_true(proj):
    _make_profile(proj, "prod")
    pin_profile(proj, "prod")
    assert is_pinned(proj, "prod") is True


def test_is_pinned_false_for_other_profile(proj):
    _make_profile(proj, "prod")
    _make_profile(proj, "dev")
    pin_profile(proj, "prod")
    assert is_pinned(proj, "dev") is False


def test_unpin_returns_previous_profile(proj):
    _make_profile(proj, "dev")
    pin_profile(proj, "dev")
    prev = unpin_profile(proj)
    assert prev == "dev"


def test_unpin_when_nothing_pinned_returns_none(proj):
    assert unpin_profile(proj) is None


def test_get_pinned_after_unpin_is_none(proj):
    _make_profile(proj, "dev")
    pin_profile(proj, "dev")
    unpin_profile(proj)
    assert get_pinned(proj) is None


# --- CLI tests ---

def test_cli_pin_sets_profile(proj, capsys):
    _make_profile(proj, "dev")
    rc = cmd_pin([proj, "dev"])
    assert rc == 0
    assert "dev" in capsys.readouterr().out


def test_cli_pin_missing_profile_exits_2(proj, capsys):
    rc = cmd_pin([proj, "ghost"])
    assert rc == 2


def test_cli_status_when_pinned(proj, capsys):
    _make_profile(proj, "dev")
    pin_profile(proj, "dev")
    rc = cmd_pin([proj, "--status"])
    assert rc == 0
    assert "dev" in capsys.readouterr().out


def test_cli_status_when_nothing_pinned_exits_1(proj, capsys):
    rc = cmd_pin([proj, "--status"])
    assert rc == 1


def test_cli_unpin(proj, capsys):
    _make_profile(proj, "dev")
    pin_profile(proj, "dev")
    rc = cmd_pin([proj, "--unpin"])
    assert rc == 0
    assert get_pinned(proj) is None
