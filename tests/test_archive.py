"""Tests for envoy.archive."""
from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from envoy.archive import archive_profiles, restore_profiles
from envoy.profile import load_profile, save_profile


@pytest.fixture()
def proj(tmp_path):
    return ("myproject", tmp_path)


def _seed(project, base, name, data):
    save_profile(project, name, data, base_dir=base)


def test_archive_creates_zip(proj, tmp_path):
    project, base = proj
    _seed(project, base, "dev", {"A": "1", "B": "2"})
    dest = str(tmp_path / "out.zip")
    result = archive_profiles(project, dest, base_dir=base)
    assert result.ok
    assert Path(dest).exists()
    assert "dev" in result.profiles


def test_archive_zip_contains_json_entries(proj, tmp_path):
    project, base = proj
    _seed(project, base, "dev", {"X": "y"})
    _seed(project, base, "prod", {"X": "z"})
    dest = str(tmp_path / "out.zip")
    archive_profiles(project, dest, base_dir=base)
    with zipfile.ZipFile(dest) as zf:
        names = zf.namelist()
    assert "dev.json" in names
    assert "prod.json" in names
    assert "_meta.json" in names


def test_archive_subset_of_profiles(proj, tmp_path):
    project, base = proj
    _seed(project, base, "dev", {"A": "1"})
    _seed(project, base, "prod", {"A": "2"})
    dest = str(tmp_path / "out.zip")
    result = archive_profiles(project, dest, profiles=["dev"], base_dir=base)
    assert result.profiles == ["dev"]
    with zipfile.ZipFile(dest) as zf:
        assert "prod.json" not in zf.namelist()


def test_archive_missing_profile_records_error(proj, tmp_path):
    project, base = proj
    dest = str(tmp_path / "out.zip")
    result = archive_profiles(project, dest, profiles=["ghost"], base_dir=base)
    assert not result.ok
    assert any("ghost" in e for e in result.errors)


def test_restore_creates_profiles(proj, tmp_path):
    project, base = proj
    _seed(project, base, "dev", {"KEY": "val"})
    dest = str(tmp_path / "bundle.zip")
    archive_profiles(project, dest, base_dir=base)

    # restore into a fresh base
    new_base = tmp_path / "fresh"
    new_base.mkdir()
    result = restore_profiles(project, dest, base_dir=new_base)
    assert result.ok
    assert "dev" in result.profiles
    data = load_profile(project, "dev", base_dir=new_base)
    assert data["KEY"] == "val"


def test_restore_skips_existing_without_overwrite(proj, tmp_path):
    project, base = proj
    _seed(project, base, "dev", {"K": "original"})
    dest = str(tmp_path / "bundle.zip")
    archive_profiles(project, dest, base_dir=base)

    # restore over itself without overwrite flag
    result = restore_profiles(project, dest, overwrite=False, base_dir=base)
    assert not result.ok
    assert any("already exists" in e for e in result.errors)


def test_restore_overwrites_when_flag_set(proj, tmp_path):
    project, base = proj
    _seed(project, base, "dev", {"K": "old"})
    dest = str(tmp_path / "bundle.zip")
    archive_profiles(project, dest, base_dir=base)
    _seed(project, base, "dev", {"K": "changed"})

    result = restore_profiles(project, dest, overwrite=True, base_dir=base)
    assert result.ok
    data = load_profile(project, "dev", base_dir=base)
    assert data["K"] == "old"  # restored from archive
