"""Tests for envoy.lint."""

import pytest
from envoy.lint import lint_env, LintResult


def test_clean_env_has_no_issues():
    env = {"DATABASE_URL": "postgres://localhost/db", "DEBUG": "true"}
    result = lint_env(env)
    assert result.ok
    assert result.warnings == []
    assert result.errors == []


def test_empty_value_produces_warning():
    result = lint_env({"API_KEY": ""})
    assert any("empty value" in w for w in result.warnings)


def test_lowercase_key_produces_warning():
    result = lint_env({"database_url": "value"})
    assert any("UPPER_SNAKE_CASE" in w for w in result.warnings)


def test_mixed_case_key_produces_warning():
    result = lint_env({"MyKey": "value"})
    assert any("UPPER_SNAKE_CASE" in w for w in result.warnings)


def test_upper_snake_key_no_convention_warning():
    result = lint_env({"MY_KEY_123": "value"})
    convention_warnings = [w for w in result.warnings if "UPPER_SNAKE_CASE" in w]
    assert convention_warnings == []


def test_unresolved_placeholder_warning():
    result = lint_env({"BASE_URL": "http://${HOST}:8080"})
    assert any("placeholder" in w for w in result.warnings)


def test_newline_in_value_warning():
    result = lint_env({"CERT": "-----BEGIN\nEND-----"})
    assert any("newline" in w for w in result.warnings)


def test_shadow_shell_var_warning():
    result = lint_env({"PATH": "/usr/local/bin"})
    assert any("PATH" in w and "shell" in w for w in result.warnings)


def test_shadow_home_warning():
    result = lint_env({"HOME": "/root"})
    assert any("HOME" in w for w in result.warnings)


def test_ok_property_false_when_errors():
    # Force an error by passing an empty key
    result = lint_env({"  ": "value"})
    assert not result.ok
    assert result.errors != []


def test_summary_no_issues():
    result = lint_env({"GOOD_KEY": "good_value"})
    assert result.summary() == "No issues found."


def test_summary_contains_warning_label():
    result = lint_env({"PATH": "/bin"})
    assert "[warning]" in result.summary()


def test_multiple_issues_all_reported():
    env = {
        "PATH": "",          # shadow + empty value
        "bad_key": "val",    # convention
    }
    result = lint_env(env)
    assert len(result.warnings) >= 3
