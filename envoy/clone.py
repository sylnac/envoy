"""Clone a profile from one project into another project's profile directory."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from envoy.profile import load_profile, save_profile, profile_path, profile_exists
from envoy.merge import merge_profiles


@dataclass
class CloneResult:
    source_project: str
    source_profile: str
    dest_project: str
    dest_profile: str
    keys_written: int
    already_existed: bool
    merged: bool


def clone_profile(
    source_project: str,
    source_profile: str,
    dest_project: str,
    dest_profile: Optional[str] = None,
    *,
    overwrite: bool = False,
    merge: bool = False,
) -> CloneResult:
    """Copy a profile from *source_project* into *dest_project*.

    Parameters
    ----------
    source_project:  project name (used as the first argument to profile helpers)
    source_profile:  profile name inside the source project
    dest_project:    target project name
    dest_profile:    target profile name; defaults to *source_profile*
    overwrite:       replace destination if it already exists
    merge:           merge source into destination instead of replacing
    """
    if dest_profile is None:
        dest_profile = source_profile

    source_data = load_profile(source_project, source_profile)
    already_existed = profile_exists(dest_project, dest_profile)

    if already_existed and not overwrite and not merge:
        raise FileExistsError(
            f"Profile '{dest_profile}' already exists in project '{dest_project}'. "
            "Use overwrite=True or merge=True."
        )

    if already_existed and merge:
        dest_data = load_profile(dest_project, dest_profile)
        merged_data = merge_profiles(dest_data, source_data, strategy="theirs")
        save_profile(dest_project, dest_profile, merged_data)
        return CloneResult(
            source_project=source_project,
            source_profile=source_profile,
            dest_project=dest_project,
            dest_profile=dest_profile,
            keys_written=len(merged_data),
            already_existed=True,
            merged=True,
        )

    save_profile(dest_project, dest_profile, source_data)
    return CloneResult(
        source_project=source_project,
        source_profile=source_profile,
        dest_project=dest_project,
        dest_profile=dest_profile,
        keys_written=len(source_data),
        already_existed=already_existed,
        merged=False,
    )
