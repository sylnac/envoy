"""Scaffold a new .env profile from a schema or list of keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envoy.profile import profile_exists, save_profile
from envoy.secrets import is_secret_key


@dataclass
class ScaffoldResult:
    profile: str
    keys_written: list[str] = field(default_factory=list)
    skipped: bool = False
    error: Optional[str] = None


def ok(result: ScaffoldResult) -> bool:
    return result.error is None


def scaffold_profile(
    project: str,
    profile: str,
    keys: list[str],
    *,
    defaults: Optional[dict[str, str]] = None,
    placeholder: str = "",
    secret_placeholder: str = "CHANGE_ME",
    overwrite: bool = False,
) -> ScaffoldResult:
    """Create a new profile pre-populated with the given keys.

    Args:
        project: Project identifier.
        profile: Profile name to create.
        keys: Ordered list of keys to include.
        defaults: Optional mapping of key -> default value.
        placeholder: Value to use for non-secret keys without a default.
        secret_placeholder: Value to use for secret keys without a default.
        overwrite: Replace the profile if it already exists.

    Returns:
        ScaffoldResult describing what was written.
    """
    if profile_exists(project, profile) and not overwrite:
        return ScaffoldResult(
            profile=profile,
            skipped=True,
            error=f"Profile '{profile}' already exists (use overwrite=True to replace)",
        )

    resolved_defaults: dict[str, str] = defaults or {}
    env: dict[str, str] = {}

    for key in keys:
        if key in resolved_defaults:
            env[key] = resolved_defaults[key]
        elif is_secret_key(key):
            env[key] = secret_placeholder
        else:
            env[key] = placeholder

    save_profile(project, profile, env)

    return ScaffoldResult(
        profile=profile,
        keys_written=list(env.keys()),
    )
