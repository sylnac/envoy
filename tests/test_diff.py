"""Tests for envoy.diff module."""

from envoy.diff import DiffResult, diff_profiles


def test_diff_no_changes():
    base = {"KEY": "value", "PORT": "8080"}
    result = diff_profiles(base, base.copy())
    assert not result.has_changes
    assert result.unchanged == base


def test_diff_added_keys():
    base = {"A": "1"}
    target = {"A": "1", "B": "2"}
    result = diff_profiles(base, target)
    assert result.added == {"B": "2"}
    assert not result.removed
    assert not result.changed


def test_diff_removed_keys():
    base = {"A": "1", "B": "2"}
    target = {"A": "1"}
    result = diff_profiles(base, target)
    assert result.removed == {"B": "2"}
    assert not result.added
    assert not result.changed


def test_diff_changed_values():
    base = {"SECRET": "old_value"}
    target = {"SECRET": "new_value"}
    result = diff_profiles(base, target)
    assert result.changed == {"SECRET": ("old_value", "new_value")}
    assert not result.added
    assert not result.removed


def test_diff_mixed_changes():
    base = {"A": "1", "B": "2", "C": "3"}
    target = {"A": "1", "B": "changed", "D": "4"}
    result = diff_profiles(base, target)
    assert result.unchanged == {"A": "1"}
    assert result.changed == {"B": ("2", "changed")}
    assert result.removed == {"C": "3"}
    assert result.added == {"D": "4"}
    assert result.has_changes


def test_diff_empty_profiles():
    result = diff_profiles({}, {})
    assert not result.has_changes


def test_diff_base_empty():
    result = diff_profiles({}, {"NEW": "val"})
    assert result.added == {"NEW": "val"}


def test_diff_target_empty():
    result = diff_profiles({"OLD": "val"}, {})
    assert result.removed == {"OLD": "val"}


def test_summary_no_changes():
    result = DiffResult()
    assert result.summary() == "(no changes)"


def test_summary_with_changes():
    result = DiffResult(
        added={"NEW_KEY": "abc"},
        removed={"OLD_KEY": "xyz"},
        changed={"CHANGED": ("before", "after")},
    )
    summary = result.summary()
    assert "+ NEW_KEY=abc" in summary
    assert "- OLD_KEY=xyz" in summary
    assert "~ CHANGED: 'before' -> 'after'" in summary
