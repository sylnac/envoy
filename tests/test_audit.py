"""Tests for envoy.audit and envoy.cli_audit."""

from __future__ import annotations

import pytest

from envoy.audit import (
    filter_log,
    format_entry,
    load_audit_log,
    record_action,
)
from envoy.cli_audit import cmd_audit


@pytest.fixture()
def proj(tmp_path):
    return str(tmp_path)


def test_record_action_returns_entry(proj):
    entry = record_action("save", "production", project_root=proj)
    assert entry["action"] == "save"
    assert entry["profile"] == "production"
    assert "timestamp" in entry
    assert entry["details"] == {}


def test_record_action_with_details(proj):
    entry = record_action("export", "staging", details={"format": "json"}, project_root=proj)
    assert entry["details"]["format"] == "json"


def test_load_audit_log_empty_when_no_file(proj):
    assert load_audit_log(project_root=proj) == []


def test_load_audit_log_returns_all_entries(proj):
    record_action("save", "dev", project_root=proj)
    record_action("delete", "dev", project_root=proj)
    entries = load_audit_log(project_root=proj)
    assert len(entries) == 2
    assert entries[0]["action"] == "save"
    assert entries[1]["action"] == "delete"


def test_filter_log_by_action(proj):
    record_action("save", "dev", project_root=proj)
    record_action("export", "dev", project_root=proj)
    entries = load_audit_log(project_root=proj)
    filtered = filter_log(entries, action="save")
    assert len(filtered) == 1
    assert filtered[0]["action"] == "save"


def test_filter_log_by_profile(proj):
    record_action("save", "dev", project_root=proj)
    record_action("save", "prod", project_root=proj)
    entries = load_audit_log(project_root=proj)
    filtered = filter_log(entries, profile="prod")
    assert len(filtered) == 1
    assert filtered[0]["profile"] == "prod"


def test_filter_log_combined(proj):
    record_action("save", "dev", project_root=proj)
    record_action("export", "dev", project_root=proj)
    record_action("save", "prod", project_root=proj)
    entries = load_audit_log(project_root=proj)
    filtered = filter_log(entries, action="save", profile="dev")
    assert len(filtered) == 1


def test_filter_log_no_match_returns_empty(proj):
    """Filtering with criteria that match no entries returns an empty list."""
    record_action("save", "dev", project_root=proj)
    entries = load_audit_log(project_root=proj)
    filtered = filter_log(entries, action="delete")
    assert filtered == []


def test_format_entry_no_details():
    entry = {"timestamp": "2024-01-01T00:00:00+00:00", "action": "save", "profile": "dev", "details": {}}
    line = format_entry(entry)
    assert "save" in line
    assert "dev" in line
    assert "(" not in line


def test_format_entry_with_details():
    entry = {"timestamp": "2024-01-01T00:00:00+00:00", "action": "export", "profile": "prod", "details": {"format": "json"}}
    line = format_entry(entry)
    assert "format=json" in line


def test_cmd_audit_no_entries(proj, capsys):
    result = cmd_audit(["--project-root", proj])
    assert result == 0
    out = capsys.readouterr().out
    assert "No audit log entries" in out


def test_cmd_audit_shows_entries(proj, capsys):
    record_action("save", "dev", project_root=proj)
    record_action("export", "dev", project_root=proj)
    result = cmd_audit(["--project-root", proj])
    assert result == 0
    out = capsys.readouterr().out
    assert "save" in out
    assert "export" in out
