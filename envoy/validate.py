"""Validation for .env profiles — check for missing keys, type hints, and required fields."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ValidationResult:
    missing: List[str] = field(default_factory=list)
    extra: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.missing and not self.errors

    def summary(self) -> str:
        parts = []
        if self.missing:
            parts.append(f"Missing keys ({len(self.missing)}): {', '.join(sorted(self.missing))}")
        if self.extra:
            parts.append(f"Extra keys ({len(self.extra)}): {', '.join(sorted(self.extra))}")
        if self.errors:
            parts.append(f"Errors: {'; '.join(self.errors)}")
        return "\n".join(parts) if parts else "OK"


def validate_against_schema(
    env: Dict[str, str],
    schema: Dict[str, str],
    allow_extra: bool = True,
) -> ValidationResult:
    """Validate env dict against a schema dict.

    Schema values may be:
      - "required"  — key must be present and non-empty
      - "optional"  — key may be absent
      - "non-empty" — key must be present and non-empty (alias for required)
    """
    result = ValidationResult()

    for key, rule in schema.items():
        rule = rule.strip().lower()
        if rule in ("required", "non-empty"):
            if key not in env:
                result.missing.append(key)
            elif not env[key].strip():
                result.errors.append(f"{key!r} is required but empty")
        elif rule == "optional":
            pass
        else:
            result.errors.append(f"Unknown rule {rule!r} for key {key!r}")

    if not allow_extra:
        for key in env:
            if key not in schema:
                result.extra.append(key)

    return result


def validate_no_empty_values(env: Dict[str, str]) -> ValidationResult:
    """Flag any keys whose values are empty strings."""
    result = ValidationResult()
    for key, value in env.items():
        if not value.strip():
            result.errors.append(f"{key!r} has an empty value")
    return result


def validate_required_keys(
    env: Dict[str, str], required: List[str]
) -> ValidationResult:
    """Ensure all keys in *required* are present and non-empty."""
    schema = {k: "required" for k in required}
    return validate_against_schema(env, schema, allow_extra=True)
