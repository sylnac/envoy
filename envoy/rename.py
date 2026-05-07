"""Profile renaming utilities for envoy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from envoy.profile import profile_path, load_profile, save_profile, profile_exists, delete_profile


@dataclass
class RenameResult:
    success: bool
    old_name: str
    new_name: str
    error: Optional[str] = None


def rename_profile(
    project: str,
    old_name: str,
    new_name: str,
    *,
    overwrite: bool = False,
) -> RenameResult:
    """Rename a profile from *old_name* to *new_name*.

    Parameters
    ----------
    project:   project identifier
    old_name:  existing profile name
    new_name:  desired profile name
    overwrite: if True, replace an existing destination profile
    """
    if not profile_exists(project, old_name):
        return RenameResult(
            success=False,
            old_name=old_name,
            new_name=new_name,
            error=f"Profile '{old_name}' does not exist.",
        )

    if old_name == new_name:
        return RenameResult(
            success=False,
            old_name=old_name,
            new_name=new_name,
            error="Source and destination profile names are identical.",
        )

    if profile_exists(project, new_name) and not overwrite:
        return RenameResult(
            success=False,
            old_name=old_name,
            new_name=new_name,
            error=(
                f"Profile '{new_name}' already exists. "
                "Use overwrite=True to replace it."
            ),
        )

    data = load_profile(project, old_name)
    save_profile(project, new_name, data)
    delete_profile(project, old_name)

    return RenameResult(success=True, old_name=old_name, new_name=new_name)
