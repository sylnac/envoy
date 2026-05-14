"""Tests for envoy.prune."""
from __future__ import annotations

import pytest

from envoy.profile import save_profile, load_profile
from envoy.prune import (
    prune_empty_values,
    prune_keys_not_in_schema,
    prune_all_profiles,
)


@pytest.fixture()
def proj(tmp_path):
    return str(tmp_path)


def test_prune_empty_removes_blank_values(proj):
    save_profile(proj, "dev", {"A": "1", "B": "", "C": "3"})
    result = prune_empty_values(proj, "dev")
    assert result.removed_keys == ["B"]
    assert result.count == 1
    assert load_profile(proj, "dev") == {"A": "1", "C": "3"}


def test_prune_empty_no_blanks(proj):
    save_profile(proj, "dev", {"A": "1", "B": "2"})
    result = prune_empty_values(proj, "dev")
    assert result.removed_keys == []
    assert "nothing to prune" in result.summary()


def test_prune_empty_dry_run_does_not_mutate(proj):
    save_profile(proj, "dev", {"A": "", "B": "ok"})
    result = prune_empty_values(proj, "dev", dry_run=True)
    assert result.removed_keys == ["A"]
    assert load_profile(proj, "dev") == {"A": "", "B": "ok"}
    assert "Would remove" in result.summary()


def test_prune_schema_removes_unknown_keys(proj):
    save_profile(proj, "prod", {"A": "1", "B": "2", "C": "3"})
    result = prune_keys_not_in_schema(proj, "prod", ["A", "C"])
    assert "B" in result.removed_keys
    assert load_profile(proj, "prod") == {"A": "1", "C": "3"}


def test_prune_schema_dry_run(proj):
    save_profile(proj, "prod", {"X": "1", "Y": "2"})
    result = prune_keys_not_in_schema(proj, "prod", ["X"], dry_run=True)
    assert result.removed_keys == ["Y"]
    assert load_profile(proj, "prod") == {"X": "1", "Y": "2"}


def test_prune_schema_all_allowed(proj):
    save_profile(proj, "staging", {"A": "1"})
    result = prune_keys_not_in_schema(proj, "staging", ["A", "B"])
    assert result.removed_keys == []
    assert result.ok is True


def test_prune_all_profiles_empty_values(proj):
    save_profile(proj, "dev", {"A": "", "B": "ok"})
    save_profile(proj, "prod", {"C": "val", "D": ""})
    results = prune_all_profiles(proj)
    assert "A" in results["dev"].removed_keys
    assert "D" in results["prod"].removed_keys


def test_prune_all_profiles_with_schema(proj):
    save_profile(proj, "dev", {"KEEP": "1", "DROP": "2"})
    results = prune_all_profiles(proj, schema_keys=["KEEP"])
    assert "DROP" in results["dev"].removed_keys
    assert load_profile(proj, "dev") == {"KEEP": "1"}


def test_prune_result_summary_removed(proj):
    save_profile(proj, "dev", {"OLD": ""})
    result = prune_empty_values(proj, "dev")
    summary = result.summary()
    assert "Removed" in summary
    assert "OLD" in summary
