"""Reorder keys within a profile according to a given key ordering."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envoy.profile import load_profile, save_profile, profile_exists


@dataclass
class ReorderResult:
    profile: str
    ordered_keys: List[str]
    moved: int
    unchanged: int
    error: Optional[str] = None


def ok(result: ReorderResult) -> bool:
    return result.error is None


def reorder_profile(
    project: str,
    profile: str,
    key_order: List[str],
    *,
    append_remaining: bool = True,
) -> ReorderResult:
    """Reorder keys in *profile* to match *key_order*.

    Keys not listed in *key_order* are appended at the end when
    *append_remaining* is True (default), or dropped when False.
    """
    if not profile_exists(project, profile):
        return ReorderResult(
            profile=profile,
            ordered_keys=[],
            moved=0,
            unchanged=0,
            error=f"Profile '{profile}' not found in project '{project}'",
        )

    env = load_profile(project, profile)

    seen: set[str] = set()
    new_env: dict[str, str] = {}

    for key in key_order:
        if key in env:
            new_env[key] = env[key]
            seen.add(key)

    if append_remaining:
        for key, value in env.items():
            if key not in seen:
                new_env[key] = value

    original_order = list(env.keys())
    new_order = list(new_env.keys())

    moved = sum(1 for i, k in enumerate(new_order) if i >= len(original_order) or original_order[i] != k)
    unchanged = len(new_order) - moved

    save_profile(project, profile, new_env)

    return ReorderResult(
        profile=profile,
        ordered_keys=new_order,
        moved=moved,
        unchanged=unchanged,
    )
