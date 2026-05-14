"""Diagnose common envoy project issues and misconfigurations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envoy.profile import list_profiles, load_profile, profile_path
from envoy.secrets import is_secret_key
from envoy.lint import lint_env


@dataclass
class DoctorIssue:
    level: str  # "error" | "warning" | "info"
    profile: str
    message: str


@dataclass
class DoctorReport:
    issues: List[DoctorIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.level == "error" for i in self.issues)

    @property
    def errors(self) -> List[DoctorIssue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> List[DoctorIssue]:
        return [i for i in self.issues if i.level == "warning"]

    def summary(self) -> str:
        if not self.issues:
            return "No issues found."
        lines = []
        for issue in self.issues:
            lines.append(f"[{issue.level.upper()}] {issue.profile}: {issue.message}")
        return "\n".join(lines)


def run_doctor(project_dir: str) -> DoctorReport:
    """Run all diagnostic checks for the given project directory."""
    report = DoctorReport()
    profiles = list_profiles(project_dir)

    if not profiles:
        report.issues.append(
            DoctorIssue(level="warning", profile="(none)", message="No profiles found.")
        )
        return report

    for name in profiles:
        path = profile_path(project_dir, name)
        try:
            env = load_profile(project_dir, name)
        except Exception as exc:  # noqa: BLE001
            report.issues.append(
                DoctorIssue(level="error", profile=name, message=f"Failed to load: {exc}")
            )
            continue

        # Lint checks
        lint = lint_env(env)
        for w in lint.warnings:
            report.issues.append(DoctorIssue(level="warning", profile=name, message=w))
        for e in lint.errors:
            report.issues.append(DoctorIssue(level="error", profile=name, message=e))

        # Secret keys with empty values
        for k, v in env.items():
            if is_secret_key(k) and not v:
                report.issues.append(
                    DoctorIssue(
                        level="error",
                        profile=name,
                        message=f"Secret key '{k}' has an empty value.",
                    )
                )

    return report
