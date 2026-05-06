"""Profile copy/clone utilities for envoy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from envoy.profile import load_profile, save_profile, profile_exists
from envoy.parser import merge_env


@dataclass
class CopyResult:
    source: str
    destination: str
    keys_copied: int
    overwritten: bool


def copy_profile(
    project: str,
    source: str,
    destination: str,
    overwrite: bool = False,
    keys: Optional[list[str]] = None,
) -> CopyResult:
    """Copy a profile (or a subset of its keys) to a new profile.

    Args:
        project:     Project name.
        source:      Name of the profile to copy from.
        destination: Name of the profile to copy to.
        overwrite:   If True, replace the destination profile entirely.
                     If False, merge source into destination (source wins).
        keys:        Optional list of specific keys to copy.  When None all
                     keys are copied.

    Returns:
        A CopyResult describing what happened.

    Raises:
        FileNotFoundError: If the source profile does not exist.
        FileExistsError:   If the destination profile already exists and
                           *overwrite* is False and the destination profile
                           is identical in path to the source.
    """
    if not profile_exists(project, source):
        raise FileNotFoundError(
            f"Source profile '{source}' not found in project '{project}'."
        )

    src_env = load_profile(project, source)

    if keys is not None:
        src_env = {k: v for k, v in src_env.items() if k in keys}

    dest_existed = profile_exists(project, destination)

    if dest_existed and not overwrite:
        dest_env = load_profile(project, destination)
        merged = merge_env(dest_env, src_env)  # src_env values win
    else:
        merged = dict(src_env)

    save_profile(project, destination, merged)

    return CopyResult(
        source=source,
        destination=destination,
        keys_copied=len(merged),
        overwritten=dest_existed and overwrite,
    )


def rename_profile(project: str, old_name: str, new_name: str) -> None:
    """Rename a profile by copying then deleting the original.

    Raises:
        FileNotFoundError: If *old_name* does not exist.
        FileExistsError:   If *new_name* already exists.
    """
    if not profile_exists(project, old_name):
        raise FileNotFoundError(
            f"Profile '{old_name}' not found in project '{project}'."
        )
    if profile_exists(project, new_name):
        raise FileExistsError(
            f"Profile '{new_name}' already exists in project '{project}'."
        )

    env = load_profile(project, old_name)
    save_profile(project, new_name, env)

    from envoy.profile import _profile_dir
    import os
    old_path = _profile_dir(project) / f"{old_name}.env"
    os.remove(old_path)
