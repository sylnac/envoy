"""Tests for envoy.patch."""
from __future__ import annotations

import pytest

from envoy.profile import save_profile, load_profile
from envoy.patch import patch_profile, PatchResult


@pytest.fixture()
def proj(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "myproject"


def _seed(proj: str, profile: str, data: dict) -> None:
    save_profile(proj, profile, data)


# ---------------------------------------------------------------------------
# PatchResult helpers
# ---------------------------------------------------------------------------

def test_ok_when_no_error():
    r = PatchResult(profile="dev", added=["A"], updated=[], deleted=[])
    assert r.ok is True


def test_not_ok_when_error():
    r = PatchResult(profile="dev", error="boom")
    assert r.ok is False


def test_total_changes_counts_all_buckets():
    r = PatchResult(profile="dev", added=["A"], updated=["B", "C"], deleted=["D"])
    assert r.total_changes == 4


def test_summary_no_changes():
    r = PatchResult(profile="dev")
    assert r.summary() == "no changes"


def test_summary_with_changes():
    r = PatchResult(profile="dev", added=["X"], deleted=["Y"])
    assert "1 added" in r.summary()
    assert "1 deleted" in r.summary()


def test_summary_error():
    r = PatchResult(profile="dev", error="not found")
    assert "not found" in r.summary()


# ---------------------------------------------------------------------------
# patch_profile behaviour
# ---------------------------------------------------------------------------

def test_patch_missing_profile_returns_error(proj):
    result = patch_profile(proj, "ghost", {"KEY": "val"}, record_history=False)
    assert not result.ok
    assert "ghost" in result.error


def test_patch_adds_new_key(proj):
    _seed(proj, "dev", {"EXISTING": "yes"})
    result = patch_profile(proj, "dev", {"NEW_KEY": "hello"}, record_history=False)
    assert result.ok
    assert "NEW_KEY" in result.added
    env = load_profile(proj, "dev")
    assert env["NEW_KEY"] == "hello"


def test_patch_updates_existing_key(proj):
    _seed(proj, "dev", {"HOST": "localhost"})
    result = patch_profile(proj, "dev", {"HOST": "prod.example.com"}, record_history=False)
    assert "HOST" in result.updated
    assert load_profile(proj, "dev")["HOST"] == "prod.example.com"


def test_patch_same_value_not_counted_as_update(proj):
    _seed(proj, "dev", {"HOST": "localhost"})
    result = patch_profile(proj, "dev", {"HOST": "localhost"}, record_history=False)
    assert result.updated == []
    assert result.total_changes == 0


def test_patch_deletes_key_when_value_is_none(proj):
    _seed(proj, "dev", {"REMOVE_ME": "bye", "KEEP": "yes"})
    result = patch_profile(proj, "dev", {"REMOVE_ME": None}, record_history=False)
    assert "REMOVE_ME" in result.deleted
    env = load_profile(proj, "dev")
    assert "REMOVE_ME" not in env
    assert env["KEEP"] == "yes"


def test_patch_delete_missing_key_is_noop(proj):
    _seed(proj, "dev", {"KEEP": "yes"})
    result = patch_profile(proj, "dev", {"GHOST": None}, record_history=False)
    assert result.deleted == []
    assert result.total_changes == 0


def test_patch_mixed_operations(proj):
    _seed(proj, "dev", {"A": "1", "B": "2"})
    result = patch_profile(
        proj, "dev",
        {"A": "updated", "B": None, "C": "new"},
        record_history=False,
    )
    assert "A" in result.updated
    assert "B" in result.deleted
    assert "C" in result.added
    env = load_profile(proj, "dev")
    assert env == {"A": "updated", "C": "new"}
