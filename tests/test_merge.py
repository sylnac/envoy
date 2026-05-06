"""Tests for envoy.merge module."""

import pytest

from envoy.merge import merge_profiles, merge_with_conflicts


# --- merge_profiles ---

def test_merge_no_overlap():
    base = {"A": "1", "B": "2"}
    other = {"C": "3", "D": "4"}
    result = merge_profiles(base, other)
    assert result == {"A": "1", "B": "2", "C": "3", "D": "4"}


def test_merge_theirs_strategy():
    base = {"A": "1", "B": "2"}
    other = {"B": "overridden", "C": "3"}
    result = merge_profiles(base, other, strategy="theirs")
    assert result["B"] == "overridden"
    assert result["A"] == "1"
    assert result["C"] == "3"


def test_merge_ours_strategy():
    base = {"A": "1", "B": "original"}
    other = {"B": "overridden", "C": "3"}
    result = merge_profiles(base, other, strategy="ours")
    assert result["B"] == "original"
    assert result["C"] == "3"


def test_merge_error_strategy_raises_on_conflict():
    base = {"A": "1"}
    other = {"A": "2"}
    with pytest.raises(ValueError, match="Merge conflict on key 'A'"):
        merge_profiles(base, other, strategy="error")


def test_merge_error_strategy_no_conflict_ok():
    base = {"A": "1"}
    other = {"B": "2"}
    result = merge_profiles(base, other, strategy="error")
    assert result == {"A": "1", "B": "2"}


def test_merge_does_not_mutate_base():
    base = {"A": "1"}
    other = {"A": "2", "B": "3"}
    merge_profiles(base, other, strategy="theirs")
    assert base == {"A": "1"}


def test_merge_multiple_profiles():
    base = {"A": "1"}
    second = {"B": "2"}
    third = {"C": "3", "A": "overridden"}
    result = merge_profiles(base, second, third, strategy="theirs")
    assert result == {"A": "overridden", "B": "2", "C": "3"}


def test_merge_empty_base():
    result = merge_profiles({}, {"A": "1"})
    assert result == {"A": "1"}


def test_merge_empty_other():
    result = merge_profiles({"A": "1"}, {})
    assert result == {"A": "1"}


# --- merge_with_conflicts ---

def test_merge_with_conflicts_detects_conflicts():
    base = {"A": "1", "B": "2"}
    other = {"B": "changed", "C": "3"}
    merged, conflicts = merge_with_conflicts(base, other)
    assert "B" in conflicts
    assert "A" not in conflicts
    assert "C" not in conflicts


def test_merge_with_conflicts_same_value_no_conflict():
    base = {"A": "same"}
    other = {"A": "same"}
    _, conflicts = merge_with_conflicts(base, other)
    assert conflicts == []


def test_merge_with_conflicts_result_uses_theirs():
    base = {"A": "old"}
    other = {"A": "new"}
    merged, _ = merge_with_conflicts(base, other)
    assert merged["A"] == "new"


def test_merge_with_conflicts_no_changes():
    base = {"X": "1"}
    other = {"Y": "2"}
    merged, conflicts = merge_with_conflicts(base, other)
    assert conflicts == []
    assert merged == {"X": "1", "Y": "2"}
