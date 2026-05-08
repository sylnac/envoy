"""Tests for envoy.clone."""
from __future__ import annotations

import pytest

from envoy.clone import clone_profile, CloneResult
from envoy.profile import load_profile, save_profile, profile_exists


@pytest.fixture()
def proj(tmp_path, monkeypatch):
    """Redirect profile storage to a temp directory."""
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return tmp_path


def test_clone_creates_destination(proj):
    save_profile("src", "default", {"A": "1", "B": "2"})
    result = clone_profile("src", "default", "dst")
    assert isinstance(result, CloneResult)
    assert profile_exists("dst", "default")
    assert load_profile("dst", "default") == {"A": "1", "B": "2"}


def test_clone_custom_dest_profile_name(proj):
    save_profile("src", "staging", {"X": "10"})
    result = clone_profile("src", "staging", "dst", "production")
    assert result.dest_profile == "production"
    assert load_profile("dst", "production") == {"X": "10"}


def test_clone_keys_written_count(proj):
    save_profile("src", "default", {"A": "1", "B": "2", "C": "3"})
    result = clone_profile("src", "default", "dst")
    assert result.keys_written == 3


def test_clone_raises_if_dest_exists_no_flags(proj):
    save_profile("src", "default", {"A": "1"})
    save_profile("dst", "default", {"B": "2"})
    with pytest.raises(FileExistsError, match="already exists"):
        clone_profile("src", "default", "dst")


def test_clone_overwrite_replaces_destination(proj):
    save_profile("src", "default", {"NEW": "yes"})
    save_profile("dst", "default", {"OLD": "no"})
    result = clone_profile("src", "default", "dst", overwrite=True)
    assert load_profile("dst", "default") == {"NEW": "yes"}
    assert result.already_existed is True
    assert result.merged is False


def test_clone_merge_combines_keys(proj):
    save_profile("src", "default", {"A": "src_a", "B": "src_b"})
    save_profile("dst", "default", {"B": "dst_b", "C": "dst_c"})
    result = clone_profile("src", "default", "dst", merge=True)
    merged = load_profile("dst", "default")
    # 'theirs' strategy: source wins on conflict
    assert merged["A"] == "src_a"
    assert merged["B"] == "src_b"
    assert merged["C"] == "dst_c"
    assert result.merged is True


def test_clone_result_fields(proj):
    save_profile("alpha", "dev", {"K": "v"})
    result = clone_profile("alpha", "dev", "beta", "staging")
    assert result.source_project == "alpha"
    assert result.source_profile == "dev"
    assert result.dest_project == "beta"
    assert result.dest_profile == "staging"
    assert result.already_existed is False


def test_clone_already_existed_false_for_new_dest(proj):
    save_profile("src", "default", {"A": "1"})
    result = clone_profile("src", "default", "brand_new_project")
    assert result.already_existed is False
