"""Profile sync — push/pull profiles to/from a shared directory (e.g. a mounted drive or shared folder)."""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envoy.profile import load_profile, save_profile, list_profiles, profile_path


@dataclass
class SyncResult:
    pushed: List[str] = field(default_factory=list)
    pulled: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _remote_path(remote_dir: Path, project: str, profile: str) -> Path:
    return remote_dir / project / f"{profile}.json"


def push_profile(
    project: str,
    profile: str,
    remote_dir: Path,
    overwrite: bool = False,
) -> SyncResult:
    """Copy a local profile to the remote directory."""
    result = SyncResult()
    local = profile_path(project, profile)
    if not local.exists():
        result.errors.append(f"Local profile '{profile}' not found for project '{project}'")
        return result

    dest = _remote_path(remote_dir, project, profile)
    if dest.exists() and not overwrite:
        result.skipped.append(profile)
        return result

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(local, dest)
    result.pushed.append(profile)
    return result


def pull_profile(
    project: str,
    profile: str,
    remote_dir: Path,
    overwrite: bool = False,
) -> SyncResult:
    """Copy a remote profile into the local store."""
    result = SyncResult()
    src = _remote_path(remote_dir, project, profile)
    if not src.exists():
        result.errors.append(f"Remote profile '{profile}' not found in '{remote_dir}'")
        return result

    local = profile_path(project, profile)
    if local.exists() and not overwrite:
        result.skipped.append(profile)
        return result

    data = json.loads(src.read_text())
    save_profile(project, profile, data)
    result.pulled.append(profile)
    return result


def sync_all(
    project: str,
    remote_dir: Path,
    direction: str = "push",
    overwrite: bool = False,
) -> SyncResult:
    """Sync all local profiles in *direction* ('push' or 'pull')."""
    if direction not in ("push", "pull"):
        raise ValueError("direction must be 'push' or 'pull'")

    combined = SyncResult()
    if direction == "push":
        profiles = list_profiles(project)
    else:
        remote_project_dir = remote_dir / project
        if not remote_project_dir.exists():
            combined.errors.append(f"No remote directory found for project '{project}'")
            return combined
        profiles = [p.stem for p in remote_project_dir.glob("*.json")]

    for prof in profiles:
        if direction == "push":
            r = push_profile(project, prof, remote_dir, overwrite=overwrite)
        else:
            r = pull_profile(project, prof, remote_dir, overwrite=overwrite)
        combined.pushed.extend(r.pushed)
        combined.pulled.extend(r.pulled)
        combined.skipped.extend(r.skipped)
        combined.errors.extend(r.errors)

    return combined
