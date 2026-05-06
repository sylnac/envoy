"""Tests for envoy.validate."""

import pytest

from envoy.validate import (
    ValidationResult,
    validate_against_schema,
    validate_no_empty_values,
    validate_required_keys,
)


# ---------------------------------------------------------------------------
# ValidationResult helpers
# ---------------------------------------------------------------------------

def test_valid_when_no_issues():
    r = ValidationResult()
    assert r.valid is True


def test_invalid_when_missing():
    r = ValidationResult(missing=["FOO"])
    assert r.valid is False


def test_invalid_when_errors():
    r = ValidationResult(errors=["something wrong"])
    assert r.valid is False


def test_summary_ok():
    assert ValidationResult().summary() == "OK"


def test_summary_missing():
    r = ValidationResult(missing=["A", "B"])
    assert "Missing keys" in r.summary()
    assert "A" in r.summary()


def test_summary_extra():
    r = ValidationResult(extra=["X"])
    assert "Extra keys" in r.summary()


# ---------------------------------------------------------------------------
# validate_against_schema
# ---------------------------------------------------------------------------

def test_schema_all_present():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    schema = {"DB_HOST": "required", "DB_PORT": "required"}
    result = validate_against_schema(env, schema)
    assert result.valid


def test_schema_missing_required():
    env = {"DB_HOST": "localhost"}
    schema = {"DB_HOST": "required", "DB_PORT": "required"}
    result = validate_against_schema(env, schema)
    assert "DB_PORT" in result.missing
    assert not result.valid


def test_schema_empty_required_value():
    env = {"API_KEY": ""}
    schema = {"API_KEY": "required"}
    result = validate_against_schema(env, schema)
    assert not result.valid
    assert any("API_KEY" in e for e in result.errors)


def test_schema_optional_absent_is_ok():
    env = {}
    schema = {"DEBUG": "optional"}
    result = validate_against_schema(env, schema)
    assert result.valid


def test_schema_extra_keys_disallowed():
    env = {"A": "1", "B": "2"}
    schema = {"A": "required"}
    result = validate_against_schema(env, schema, allow_extra=False)
    assert "B" in result.extra


def test_schema_extra_keys_allowed_by_default():
    env = {"A": "1", "B": "2"}
    schema = {"A": "required"}
    result = validate_against_schema(env, schema)
    assert result.extra == []


def test_schema_unknown_rule():
    env = {"A": "1"}
    schema = {"A": "mandatory"}
    result = validate_against_schema(env, schema)
    assert result.errors


# ---------------------------------------------------------------------------
# validate_no_empty_values
# ---------------------------------------------------------------------------

def test_no_empty_values_all_good():
    env = {"A": "1", "B": "hello"}
    assert validate_no_empty_values(env).valid


def test_no_empty_values_detects_empty():
    env = {"A": "", "B": "ok"}
    result = validate_no_empty_values(env)
    assert not result.valid
    assert any("A" in e for e in result.errors)


# ---------------------------------------------------------------------------
# validate_required_keys
# ---------------------------------------------------------------------------

def test_required_keys_all_present():
    env = {"X": "a", "Y": "b"}
    assert validate_required_keys(env, ["X", "Y"]).valid


def test_required_keys_missing():
    env = {"X": "a"}
    result = validate_required_keys(env, ["X", "Y"])
    assert "Y" in result.missing
