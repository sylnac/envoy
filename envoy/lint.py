"""Lint .env profiles for common issues and style problems."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

# Keys that should never appear in .env files (security lint)
_FORBIDDEN_KEYS = {"AWS_SECRET_ACCESS_KEY", "GITHUB_TOKEN", "PRIVATE_KEY"}

# Recommended naming convention: UPPER_SNAKE_CASE
import re
_UPPER_SNAKE = re.compile(r'^[A-Z][A-Z0-9_]*$')


@dataclass
class LintResult:
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        lines = []
        for e in self.errors:
            lines.append(f"  [error]   {e}")
        for w in self.warnings:
            lines.append(f"  [warning] {w}")
        if not lines:
            return "No issues found."
        return "\n".join(lines)


def lint_env(env: Dict[str, str]) -> LintResult:
    """Run all lint checks against an env dict and return a LintResult."""
    result = LintResult()

    for key, value in env.items():
        # Error: empty key name
        if not key.strip():
            result.errors.append("Found a key with an empty name.")
            continue

        # Warning: key does not follow UPPER_SNAKE_CASE convention
        if not _UPPER_SNAKE.match(key):
            result.warnings.append(
                f"Key '{key}' does not follow UPPER_SNAKE_CASE naming convention."
            )

        # Warning: empty value
        if value == "":
            result.warnings.append(f"Key '{key}' has an empty value.")

        # Warning: value contains unresolved placeholder
        if "${" in value or "%{" in value:
            result.warnings.append(
                f"Key '{key}' may contain an unresolved placeholder: {value!r}."
            )

        # Warning: value looks like it contains a raw newline (multi-line leak)
        if "\n" in value:
            result.warnings.append(
                f"Key '{key}' contains a newline character — consider quoting or escaping."
            )

    # Error: duplicate detection is not possible on a dict, but warn on suspicious
    # keys that shadow common shell variables
    _SHELL_VARS = {"PATH", "HOME", "USER", "SHELL", "PWD", "LANG", "TERM"}
    for key in env:
        if key in _SHELL_VARS:
            result.warnings.append(
                f"Key '{key}' shadows a common shell environment variable."
            )

    return result
