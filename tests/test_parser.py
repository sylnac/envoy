"""Tests for envoy.parser module."""

import pytest
from envoy.parser import parse_env_string, serialize_env


SAMPLE_ENV = """
# Database config
DB_HOST=localhost
DB_PORT=5432
DB_NAME="my_database"

# App secrets
SECRET_KEY='supersecret'
DEBUG=false
EMPTY_VAR=
SPACED_VALUE="hello world"
"""


def test_parse_basic_key_value():
    result = parse_env_string("FOO=bar")
    assert result == {"FOO": "bar"}


def test_parse_ignores_comments():
    result = parse_env_string("# this is a comment\nFOO=bar")
    assert "#" not in str(result)
    assert result == {"FOO": "bar"}


def test_parse_ignores_blank_lines():
    result = parse_env_string("\n\nFOO=bar\n\n")
    assert result == {"FOO": "bar"}


def test_parse_strips_double_quotes():
    result = parse_env_string('DB_NAME="my_database"')
    assert result["DB_NAME"] == "my_database"


def test_parse_strips_single_quotes():
    result = parse_env_string("SECRET_KEY='supersecret'")
    assert result["SECRET_KEY"] == "supersecret"


def test_parse_empty_value():
    result = parse_env_string("EMPTY_VAR=")
    assert result["EMPTY_VAR"] == ""


def test_parse_full_sample():
    result = parse_env_string(SAMPLE_ENV)
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"
    assert result["DB_NAME"] == "my_database"
    assert result["SECRET_KEY"] == "supersecret"
    assert result["DEBUG"] == "false"
    assert result["EMPTY_VAR"] == ""
    assert result["SPACED_VALUE"] == "hello world"


def test_serialize_plain_values():
    data = {"FOO": "bar", "BAZ": "qux"}
    output = serialize_env(data)
    assert "FOO=bar" in output
    assert "BAZ=qux" in output


def test_serialize_quotes_spaced_values():
    data = {"MSG": "hello world"}
    output = serialize_env(data)
    assert 'MSG="hello world"' in output


def test_serialize_quotes_empty_values():
    data = {"EMPTY": ""}
    output = serialize_env(data)
    assert 'EMPTY=""' in output


def test_roundtrip():
    original = {"HOST": "localhost", "NAME": "my db", "TOKEN": "abc123", "BLANK": ""}
    serialized = serialize_env(original)
    parsed = parse_env_string(serialized)
    assert parsed == original
