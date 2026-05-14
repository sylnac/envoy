"""Tests for envoy.expire and envoy.cli_expire."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from envoy.expire import (
    check_stale,
    clear_expiry,
    get_expiry,
    set_expiry,
)
from envoy.cli_expire import cmd_expire


@pytest.fixture()
def proj(tmp_path):
    return str(tmp_path)


# ---------------------------------------------------------------------------
# set_expiry / get_expiry
# ---------------------------------------------------------------------------

def test_set_expiry_returns_result(proj):
    r = set_expiry(proj, "dev", "API_KEY", "2099-01-01T00:00:00+00:00")
    assert r.key == "API_KEY"
    assert r.expires_at == "2099-01-01T00:00:00+00:00"
    assert r.already_set is False


def test_set_expiry_already_set_flag(proj):
    set_expiry(proj, "dev", "API_KEY", "2099-01-01T00:00:00+00:00")
    r2 = set_expiry(proj, "dev", "API_KEY", "2099-06-01T00:00:00+00:00")
    assert r2.already_set is True


def test_get_expiry_returns_timestamp(proj):
    set_expiry(proj, "dev", "TOKEN", "2099-01-01T00:00:00+00:00")
    assert get_expiry(proj, "dev", "TOKEN") == "2099-01-01T00:00:00+00:00"


def test_get_expiry_returns_none_when_unset(proj):
    assert get_expiry(proj, "dev", "MISSING") is None


# ---------------------------------------------------------------------------
# clear_expiry
# ---------------------------------------------------------------------------

def test_clear_expiry_returns_true_when_existed(proj):
    set_expiry(proj, "dev", "X", "2099-01-01T00:00:00+00:00")
    assert clear_expiry(proj, "dev", "X") is True
    assert get_expiry(proj, "dev", "X") is None


def test_clear_expiry_returns_false_when_missing(proj):
    assert clear_expiry(proj, "dev", "NOPE") is False


# ---------------------------------------------------------------------------
# check_stale
# ---------------------------------------------------------------------------

def test_check_stale_detects_past_key(proj):
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    set_expiry(proj, "dev", "OLD_KEY", past)
    result = check_stale(proj, "dev")
    assert "OLD_KEY" in result.stale
    assert result.has_stale is True


def test_check_stale_active_key_not_stale(proj):
    future = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    set_expiry(proj, "dev", "FRESH", future)
    result = check_stale(proj, "dev")
    assert "FRESH" in result.active
    assert "FRESH" not in result.stale


def test_check_stale_empty_profile(proj):
    result = check_stale(proj, "empty")
    assert result.stale == []
    assert result.active == []
    assert result.has_stale is False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def test_cli_set_exit_zero(proj):
    assert cmd_expire(["--root", proj, "set", "dev", "API_KEY", "2099-01-01T00:00:00"]) == 0


def test_cli_set_shorthand_ttl(proj):
    assert cmd_expire(["--root", proj, "set", "dev", "API_KEY", "7d"]) == 0


def test_cli_get_json(proj, capsys):
    set_expiry(proj, "dev", "K", "2099-01-01T00:00:00+00:00")
    cmd_expire(["--root", proj, "--json", "get", "dev", "K"])
    out = json.loads(capsys.readouterr().out)
    assert out["expires_at"] == "2099-01-01T00:00:00+00:00"


def test_cli_check_returns_1_when_stale(proj):
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    set_expiry(proj, "dev", "EXPIRED", past)
    assert cmd_expire(["--root", proj, "check", "dev"]) == 1


def test_cli_check_returns_0_when_clean(proj):
    future = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    set_expiry(proj, "dev", "FRESH", future)
    assert cmd_expire(["--root", proj, "check", "dev"]) == 0


def test_cli_clear_removes_key(proj):
    set_expiry(proj, "dev", "K", "2099-01-01T00:00:00+00:00")
    cmd_expire(["--root", proj, "clear", "dev", "K"])
    assert get_expiry(proj, "dev", "K") is None
