"""Key/value transformation utilities for env profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from envoy.profile import load_profile, save_profile


@dataclass
class TransformResult:
    profile: str
    transformed: int = 0
    skipped: int = 0
    changes: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)


def ok(result: TransformResult) -> bool:
    return result.transformed >= 0


def _upper(value: str) -> str:
    return value.upper()


def _lower(value: str) -> str:
    return value.lower()


def _strip(value: str) -> str:
    return value.strip()


def _prefix(prefix: str) -> Callable[[str], str]:
    return lambda v: f"{prefix}{v}"


def _suffix(suffix: str) -> Callable[[str], str]:
    return lambda v: f"{v}{suffix}"


BUILTIN_TRANSFORMS: Dict[str, Callable[[str], str]] = {
    "upper": _upper,
    "lower": _lower,
    "strip": _strip,
}


def transform_profile(
    project: str,
    profile: str,
    transform: str | Callable[[str], str],
    keys: Optional[List[str]] = None,
    dry_run: bool = False,
) -> TransformResult:
    """Apply a transformation function to values in a profile.

    Args:
        project: Project root directory.
        profile: Profile name to transform.
        transform: Named transform ('upper', 'lower', 'strip') or a callable.
        keys: Optional list of keys to limit transformation to.
        dry_run: If True, compute changes but do not persist.

    Returns:
        TransformResult with counts and per-key change details.
    """
    env = load_profile(project, profile)
    if env is None:
        raise FileNotFoundError(f"Profile '{profile}' not found in project '{project}'")

    if callable(transform):
        fn = transform
    elif isinstance(transform, str):
        if transform not in BUILTIN_TRANSFORMS:
            raise ValueError(
                f"Unknown transform '{transform}'. "
                f"Available: {list(BUILTIN_TRANSFORMS)}"
            )
        fn = BUILTIN_TRANSFORMS[transform]
    else:
        raise TypeError("transform must be a string name or callable")

    result = TransformResult(profile=profile)
    updated: Dict[str, str] = {}

    for k, v in env.items():
        if keys is not None and k not in keys:
            updated[k] = v
            result.skipped += 1
            continue
        new_v = fn(v)
        updated[k] = new_v
        if new_v != v:
            result.transformed += 1
            result.changes[k] = (v, new_v)
        else:
            result.skipped += 1

    if not dry_run:
        save_profile(project, profile, updated)

    return result
