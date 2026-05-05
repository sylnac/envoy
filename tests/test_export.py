"""Tests for envoy.export module."""

import json
import pytest
from envoy.export import to_shell_export, to_dotenv, to_json, export


SAMPLE_ENV = {
    "APP_NAME": "myapp",
    "DB_PASSWORD": "s3cr3t",
    "PORT": "8080",
}


# --- to_shell_export ---

def test_shell_export_format():
    result = to_shell_export({"FOO": "bar"})
    assert result.strip() == 'export FOO="bar"'

def test_shell_export_sorted():
    result = to_shell_export({"Z": "1", "A": "2"})
    lines = result.strip().splitlines()
    assert lines[0].startswith('export A=')
    assert lines[1].startswith('export Z=')

def test_shell_export_redact():
    result = to_shell_export(SAMPLE_ENV, redact=True)
    assert "s3cr3t" not in result
    assert "myapp" in result

def test_shell_export_empty():
    assert to_shell_export({}) == ""


# --- to_dotenv ---

def test_dotenv_format():
    result = to_dotenv({"KEY": "value"})
    assert result.strip() == 'KEY="value"'

def test_dotenv_redact():
    result = to_dotenv(SAMPLE_ENV, redact=True)
    assert "s3cr3t" not in result
    assert 'APP_NAME="myapp"' in result

def test_dotenv_empty():
    assert to_dotenv({}) == ""


# --- to_json ---

def test_json_is_valid_json():
    result = to_json(SAMPLE_ENV)
    parsed = json.loads(result)
    assert parsed["APP_NAME"] == "myapp"
    assert parsed["PORT"] == "8080"

def test_json_redact():
    result = to_json(SAMPLE_ENV, redact=True)
    parsed = json.loads(result)
    assert "s3cr3t" not in parsed["DB_PASSWORD"]
    assert parsed["APP_NAME"] == "myapp"

def test_json_sorted_keys():
    result = to_json({"Z": "1", "A": "2"})
    parsed = json.loads(result)
    assert list(parsed.keys()) == ["A", "Z"]


# --- export dispatcher ---

def test_export_dotenv_default():
    result = export({"X": "1"})
    assert 'X="1"' in result

def test_export_shell_format():
    result = export({"X": "1"}, fmt="shell")
    assert 'export X="1"' in result

def test_export_json_format():
    result = export({"X": "1"}, fmt="json")
    parsed = json.loads(result)
    assert parsed["X"] == "1"

def test_export_unknown_format_raises():
    with pytest.raises(ValueError, match="Unknown format"):
        export({"X": "1"}, fmt="xml")
