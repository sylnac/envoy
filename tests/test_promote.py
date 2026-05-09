"""Tests for envoy.promote."""
from __future__ import annotations

import pytest

from envoy.profile import save_profile, load_profile
from envoy.promote import promote_profile


@pytest.fixture()
def proj(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "myproject"


def test_promote_basic(proj):
    save_profile(proj, "staging", {"A": "1", "B": "2"})
    result = promote_profile(proj, "staging", "production", record_history=False)
    assert result.ok
    assert set(result.keys_promoted) == {"A", "B"}
    assert load_profile(proj, "production") == {"A": "1", "B": "2"}


def test_promote_skips_existing_by_default(proj):
    save_profile(proj, "staging", {"A": "new", "B": "2"})
    save_profile(proj, "production", {"A": "old"})
    result = promote_profile(proj, "staging", "production", record_history=False)
    assert "A" in result.keys_skipped
    assert "B" in result.keys_promoted
    assert load_profile(proj, "production")["A"] == "old"


def test_promote_overwrite_replaces_existing(proj):
    save_profile(proj, "staging", {"A": "new"})
    save_profile(proj, "production", {"A": "old"})
    result = promote_profile(proj, "staging", "production", overwrite=True, record_history=False)
    assert "A" in result.overwritten
    assert load_profile(proj, "production")["A"] == "new"


def test_promote_key_allowlist(proj):
    save_profile(proj, "staging", {"A": "1", "B": "2", "C": "3"})
    result = promote_profile(proj, "staging", "production", keys=["A", "C"], record_history=False)
    prod = load_profile(proj, "production")
    assert "A" in prod and "C" in prod
    assert "B" not in prod
    assert result.keys_promoted == sorted(["A", "C"], key=lambda x: x)


def test_promote_missing_source_returns_error(proj):
    result = promote_profile(proj, "nonexistent", "production", record_history=False)
    assert not result.ok
    assert "nonexistent" in result.error


def test_promote_creates_destination_if_absent(proj):
    save_profile(proj, "staging", {"X": "42"})
    result = promote_profile(proj, "staging", "prod-new", record_history=False)
    assert result.ok
    assert load_profile(proj, "prod-new") == {"X": "42"}


def test_promote_records_history(proj):
    from envoy.history import load_history
    save_profile(proj, "staging", {"A": "1"})
    save_profile(proj, "production", {"A": "old"})
    promote_profile(proj, "staging", "production", overwrite=True, record_history=True)
    history = load_history(proj, "production")
    assert len(history) >= 1
    assert history[0]["env"]["A"] == "old"
