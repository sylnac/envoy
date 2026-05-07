"""Tests for envoy.tag module."""
import pytest

from envoy.tag import (
    add_tag,
    remove_tag,
    get_tags,
    profiles_with_tag,
    clear_tags,
)


@pytest.fixture()
def proj(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "myproject"


def test_add_tag_returns_tag_list(proj):
    tags = add_tag(proj, "dev", "local")
    assert "local" in tags


def test_add_tag_idempotent(proj):
    add_tag(proj, "dev", "local")
    tags = add_tag(proj, "dev", "local")
    assert tags.count("local") == 1


def test_get_tags_empty_when_none(proj):
    assert get_tags(proj, "dev") == []


def test_get_tags_after_add(proj):
    add_tag(proj, "staging", "cloud")
    add_tag(proj, "staging", "prod-like")
    tags = get_tags(proj, "staging")
    assert "cloud" in tags
    assert "prod-like" in tags


def test_remove_tag(proj):
    add_tag(proj, "dev", "local")
    add_tag(proj, "dev", "debug")
    tags = remove_tag(proj, "dev", "local")
    assert "local" not in tags
    assert "debug" in tags


def test_remove_nonexistent_tag_is_safe(proj):
    tags = remove_tag(proj, "dev", "ghost")
    assert tags == []


def test_profiles_with_tag(proj):
    add_tag(proj, "dev", "local")
    add_tag(proj, "ci", "local")
    add_tag(proj, "prod", "remote")
    profiles = profiles_with_tag(proj, "local")
    assert "dev" in profiles
    assert "ci" in profiles
    assert "prod" not in profiles


def test_profiles_with_tag_empty(proj):
    assert profiles_with_tag(proj, "nonexistent") == []


def test_clear_tags(proj):
    add_tag(proj, "dev", "local")
    add_tag(proj, "dev", "debug")
    clear_tags(proj, "dev")
    assert get_tags(proj, "dev") == []


def test_clear_tags_nonexistent_profile_is_safe(proj):
    clear_tags(proj, "ghost")  # should not raise


def test_tags_isolated_per_profile(proj):
    add_tag(proj, "dev", "local")
    assert get_tags(proj, "prod") == []
