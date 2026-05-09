"""Tests for envoy.sync."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envoy.sync import push_profile, pull_profile, sync_all
from envoy.profile import save_profile, load_profile


@pytest.fixture()
def proj(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path / "store"))
    return "myproject"


@pytest.fixture()
def remote(tmp_path):
    return tmp_path / "remote"


def test_push_creates_remote_file(proj, remote):
    save_profile(proj, "dev", {"KEY": "val"})
    result = push_profile(proj, "dev", remote)
    assert result.ok
    assert "dev" in result.pushed
    assert (remote / proj / "dev.json").exists()


def test_push_missing_local_profile_returns_error(proj, remote):
    result = push_profile(proj, "ghost", remote)
    assert not result.ok
    assert result.errors


def test_push_skips_existing_without_overwrite(proj, remote):
    save_profile(proj, "dev", {"A": "1"})
    push_profile(proj, "dev", remote)
    result = push_profile(proj, "dev", remote)
    assert "dev" in result.skipped
    assert result.pushed == []


def test_push_overwrite_replaces_remote(proj, remote):
    save_profile(proj, "dev", {"A": "1"})
    push_profile(proj, "dev", remote)
    save_profile(proj, "dev", {"A": "2"})
    result = push_profile(proj, "dev", remote, overwrite=True)
    assert "dev" in result.pushed
    data = json.loads((remote / proj / "dev.json").read_text())
    assert data["A"] == "2"


def test_pull_creates_local_profile(proj, remote):
    # Seed remote manually
    dest = remote / proj / "staging.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"DB": "prod"}))

    result = pull_profile(proj, "staging", remote)
    assert result.ok
    assert "staging" in result.pulled
    assert load_profile(proj, "staging") == {"DB": "prod"}


def test_pull_missing_remote_returns_error(proj, remote):
    result = pull_profile(proj, "nope", remote)
    assert not result.ok
    assert result.errors


def test_pull_skips_existing_without_overwrite(proj, remote):
    save_profile(proj, "dev", {"X": "1"})
    dest = remote / proj / "dev.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"X": "2"}))

    result = pull_profile(proj, "dev", remote)
    assert "dev" in result.skipped
    # Local should be unchanged
    assert load_profile(proj, "dev") == {"X": "1"}


def test_sync_all_push(proj, remote):
    save_profile(proj, "dev", {"A": "1"})
    save_profile(proj, "prod", {"B": "2"})
    result = sync_all(proj, remote, direction="push")
    assert result.ok
    assert set(result.pushed) == {"dev", "prod"}


def test_sync_all_pull(proj, remote):
    for name, data in [("alpha", {"K": "v1"}), ("beta", {"K": "v2"})]:
        dest = remote / proj / f"{name}.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(data))

    result = sync_all(proj, remote, direction="pull")
    assert result.ok
    assert set(result.pulled) == {"alpha", "beta"}


def test_sync_all_pull_missing_remote_dir(proj, remote):
    result = sync_all(proj, remote, direction="pull")
    assert not result.ok
    assert result.errors


def test_sync_all_invalid_direction(proj, remote):
    with pytest.raises(ValueError):
        sync_all(proj, remote, direction="sideways")
