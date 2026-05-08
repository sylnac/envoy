"""Profile pinning — mark a profile as the active/default for a project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.profile import _profile_dir, profile_exists

_PIN_FILE = ".pinned"


def _pin_file(project: str) -> Path:
    return _profile_dir(project) / _PIN_FILE


def pin_profile(project: str, profile: str) -> str:
    """Pin *profile* as the active profile for *project*.

    Returns the profile name that was pinned.
    Raises ValueError if the profile does not exist.
    """
    if not profile_exists(project, profile):
        raise ValueError(f"Profile '{profile}' does not exist in project '{project}'")

    pf = _pin_file(project)
    pf.parent.mkdir(parents=True, exist_ok=True)
    pf.write_text(json.dumps({"pinned": profile}), encoding="utf-8")
    return profile


def unpin_profile(project: str) -> Optional[str]:
    """Remove the pinned profile for *project*.

    Returns the previously pinned profile name, or None if nothing was pinned.
    """
    pf = _pin_file(project)
    if not pf.exists():
        return None
    data = json.loads(pf.read_text(encoding="utf-8"))
    pf.unlink()
    return data.get("pinned")


def get_pinned(project: str) -> Optional[str]:
    """Return the currently pinned profile name, or None."""
    pf = _pin_file(project)
    if not pf.exists():
        return None
    try:
        data = json.loads(pf.read_text(encoding="utf-8"))
        return data.get("pinned")
    except (json.JSONDecodeError, OSError):
        return None


def is_pinned(project: str, profile: str) -> bool:
    """Return True if *profile* is the pinned profile for *project*."""
    return get_pinned(project) == profile
