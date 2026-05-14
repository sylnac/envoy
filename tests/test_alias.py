"""Tests for envoy.alias."""
import pytest

from envoy.alias import (
    aliases_for_profile,
    list_aliases,
    remove_alias,
    resolve_alias,
    set_alias,
)


@pytest.fixture()
def proj(tmp_path):
    return str(tmp_path)


def test_set_alias_returns_mapping(proj):
    result = set_alias(proj, "dev", "development")
    assert result["dev"] == "development"


def test_resolve_alias_returns_profile(proj):
    set_alias(proj, "prod", "production")
    assert resolve_alias(proj, "prod") == "production"


def test_resolve_alias_missing_returns_none(proj):
    assert resolve_alias(proj, "ghost") is None


def test_list_aliases_empty_when_none(proj):
    assert list_aliases(proj) == {}


def test_list_aliases_multiple(proj):
    set_alias(proj, "dev", "development")
    set_alias(proj, "stg", "staging")
    aliases = list_aliases(proj)
    assert aliases["dev"] == "development"
    assert aliases["stg"] == "staging"


def test_set_alias_overwrites_existing(proj):
    set_alias(proj, "dev", "development")
    set_alias(proj, "dev", "dev-new")
    assert resolve_alias(proj, "dev") == "dev-new"


def test_remove_alias_returns_true_when_existed(proj):
    set_alias(proj, "dev", "development")
    assert remove_alias(proj, "dev") is True
    assert resolve_alias(proj, "dev") is None


def test_remove_alias_returns_false_when_missing(proj):
    assert remove_alias(proj, "nope") is False


def test_aliases_for_profile_returns_list(proj):
    set_alias(proj, "dev", "development")
    set_alias(proj, "d", "development")
    set_alias(proj, "prod", "production")
    result = aliases_for_profile(proj, "development")
    assert sorted(result) == ["d", "dev"]


def test_aliases_for_profile_empty_when_none(proj):
    assert aliases_for_profile(proj, "missing") == []


def test_aliases_persist_across_calls(proj):
    set_alias(proj, "x", "xprofile")
    # Fresh call to list_aliases reads from disk
    assert list_aliases(proj)["x"] == "xprofile"
