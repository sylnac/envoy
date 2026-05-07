"""Tests for envoy.import_env."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from envoy.import_env import import_from_env, import_from_file
from envoy.profile import load_profile


@pytest.fixture()
def proj(tmp_path, monkeypatch):
    import envoy.profile as _p
    monkeypatch.setattr(_p, "_profile_dir", lambda name: tmp_path / name)
    return "testproject"


def test_import_from_env_basic(proj, monkeypatch):
    monkeypatch.setenv("MY_VAR", "hello")
    monkeypatch.setenv("OTHER", "world")
    result = import_from_env(proj, "dev", keys=["MY_VAR"])
    assert "MY_VAR" in result.imported
    assert "OTHER" not in result.imported
    data = load_profile(proj, "dev")
    assert data["MY_VAR"] == "hello"


def test_import_from_env_prefix(proj, monkeypatch):
    monkeypatch.setenv("APP_HOST", "localhost")
    monkeypatch.setenv("APP_PORT", "8080")
    monkeypatch.setenv("UNRELATED", "nope")
    result = import_from_env(proj, "dev", prefix="APP_")
    assert set(result.imported) >= {"APP_HOST", "APP_PORT"}
    assert "UNRELATED" not in result.imported


def test_import_skips_existing_by_default(proj, monkeypatch):
    from envoy.profile import save_profile
    save_profile(proj, "dev", {"EXISTING": "old"})
    monkeypatch.setenv("EXISTING", "new")
    result = import_from_env(proj, "dev", keys=["EXISTING"])
    assert "EXISTING" in result.skipped
    assert load_profile(proj, "dev")["EXISTING"] == "old"


def test_import_overwrites_when_flag_set(proj, monkeypatch):
    from envoy.profile import save_profile
    save_profile(proj, "dev", {"EXISTING": "old"})
    monkeypatch.setenv("EXISTING", "new")
    result = import_from_env(proj, "dev", keys=["EXISTING"], overwrite=True)
    assert "EXISTING" in result.overwritten
    assert load_profile(proj, "dev")["EXISTING"] == "new"


def test_import_from_file(proj, tmp_path):
    env_file = tmp_path / ".env.foreign"
    env_file.write_text("DB_HOST=db.example.com\nDB_PORT=5432\n")
    result = import_from_file(proj, "prod", env_file)
    assert set(result.imported) == {"DB_HOST", "DB_PORT"}
    data = load_profile(proj, "prod")
    assert data["DB_HOST"] == "db.example.com"
    assert data["DB_PORT"] == "5432"


def test_import_from_file_skip_existing(proj, tmp_path):
    from envoy.profile import save_profile
    save_profile(proj, "prod", {"DB_HOST": "original"})
    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=new_host\nDB_PORT=5432\n")
    result = import_from_file(proj, "prod", env_file, overwrite=False)
    assert "DB_HOST" in result.skipped
    assert "DB_PORT" in result.imported
    assert load_profile(proj, "prod")["DB_HOST"] == "original"


def test_import_result_total(proj, monkeypatch):
    monkeypatch.setenv("K1", "v1")
    monkeypatch.setenv("K2", "v2")
    result = import_from_env(proj, "dev", keys=["K1", "K2"])
    assert result.total == 2
