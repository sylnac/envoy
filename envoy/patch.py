"""Apply a partial update (patch) to an existing profile.

A patch is a dict of key/value changes to merge into a profile.  Keys
with a value of ``None`` are *deleted* from the profile; all other keys
are inserted or overwritten.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy.profile import load_profile, save_profile, profile_exists
from envoy.history import record_snapshot


@dataclass
class PatchResult:
    profile: str
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    deleted: List[str] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.updated) + len(self.deleted)

    def summary(self) -> str:
        if not self.ok:
            return f"error: {self.error}"
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.updated:
            parts.append(f"{len(self.updated)} updated")
        if self.deleted:
            parts.append(f"{len(self.deleted)} deleted")
        return ", ".join(parts) if parts else "no changes"


def patch_profile(
    project: str,
    profile: str,
    patch: Dict[str, Optional[str]],
    *,
    record_history: bool = True,
) -> PatchResult:
    """Apply *patch* to *profile* within *project*.

    Parameters
    ----------
    project:
        Project identifier (directory name).
    profile:
        Profile name to patch.
    patch:
        Mapping of key -> value.  A ``None`` value means delete the key.
    record_history:
        When *True* (default) a history snapshot is recorded after the patch.
    """
    result = PatchResult(profile=profile)

    if not profile_exists(project, profile):
        result.error = f"profile '{profile}' not found in project '{project}'"
        return result

    env = load_profile(project, profile)

    for key, value in patch.items():
        if value is None:
            if key in env:
                del env[key]
                result.deleted.append(key)
        elif key in env:
            if env[key] != value:
                env[key] = value
                result.updated.append(key)
        else:
            env[key] = value
            result.added.append(key)

    save_profile(project, profile, env)

    if record_history and result.total_changes > 0:
        record_snapshot(project, profile, env)

    return result
