"""Tests for envoy.doctor."""
from __future__ import annotations

import os
import tempfile

import pytest

from envoy.doctor import DoctorReport, DoctorIssue, run_doctor
from envoy.profile import save_profile


@pytest.fixture()
def proj(tmp_path):
    return str(tmp_path)


def test_no_profiles_returns_warning(proj):
    report = run_doctor(proj)
    assert not report.ok or any(i.level == "warning" for i in report.issues)
    assert any("No profiles" in i.message for i in report.issues)


def test_clean_profile_no_issues(proj):
    save_profile(proj, "dev", {"APP_NAME": "myapp", "PORT": "8080"})
    report = run_doctor(proj)
    assert report.ok
    assert report.errors == []


def test_empty_secret_key_is_error(proj):
    save_profile(proj, "dev", {"API_KEY": "", "APP_NAME": "myapp"})
    report = run_doctor(proj)
    assert not report.ok
    errors = [i for i in report.errors if "API_KEY" in i.message]
    assert errors, "Expected error about empty API_KEY"


def test_lowercase_key_is_warning(proj):
    save_profile(proj, "dev", {"lowercase_key": "value"})
    report = run_doctor(proj)
    warnings = [i for i in report.warnings if "lowercase" in i.message.lower() or "convention" in i.message.lower()]
    assert warnings


def test_multiple_profiles_all_checked(proj):
    save_profile(proj, "dev", {"APP": "dev"})
    save_profile(proj, "prod", {"SECRET_KEY": ""})
    report = run_doctor(proj)
    profiles_with_issues = {i.profile for i in report.issues}
    assert "prod" in profiles_with_issues


def test_report_ok_property(proj):
    save_profile(proj, "dev", {"APP": "ok"})
    report = run_doctor(proj)
    assert report.ok is True


def test_report_summary_no_issues(proj):
    save_profile(proj, "dev", {"APP": "ok"})
    report = run_doctor(proj)
    assert "No issues" in report.summary()


def test_report_summary_with_issues(proj):
    save_profile(proj, "dev", {"TOKEN": ""})
    report = run_doctor(proj)
    summary = report.summary()
    assert "ERROR" in summary or "WARNING" in summary


def test_doctor_issue_dataclass():
    issue = DoctorIssue(level="error", profile="dev", message="bad thing")
    assert issue.level == "error"
    assert issue.profile == "dev"
    assert "bad" in issue.message
