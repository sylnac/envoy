"""Rollback a profile to a previous snapshot from history."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from envoy.history import get_snapshot, load_history
from envoy.profile import save_profile, load_profile, profile_exists


@dataclass
class RollbackResult:
    project: str
    profile: str
    snapshot_index: int
    timestamp: str
    keys_restored: int
    previous_keys: int
    success: bool
    error: Optional[str] = None


def rollback_profile(
    project: str,
    profile: str,
    snapshot_index: int = -1,
) -> RollbackResult:
    """Restore a profile to the state captured in a history snapshot.

    Parameters
    ----------
    project:
        Project identifier used to locate history and profiles.
    profile:
        Name of the profile to roll back.
    snapshot_index:
        Index into the history list (default -1 means the most recent
        snapshot *before* the current state, i.e. index -1 of all
        recorded snapshots).
    """
    history = load_history(project, profile)
    if not history:
        return RollbackResult(
            project=project,
            profile=profile,
            snapshot_index=snapshot_index,
            timestamp="",
            keys_restored=0,
            previous_keys=0,
            success=False,
            error="No history found for this profile.",
        )

    try:
        snapshot = history[snapshot_index]
    except IndexError:
        return RollbackResult(
            project=project,
            profile=profile,
            snapshot_index=snapshot_index,
            timestamp="",
            keys_restored=0,
            previous_keys=0,
            success=False,
            error=f"Snapshot index {snapshot_index} is out of range (history has {len(history)} entries).",
        )

    previous_env: dict[str, str] = {}
    if profile_exists(project, profile):
        previous_env = load_profile(project, profile)

    restored_env: dict[str, str] = snapshot.get("env", {})
    save_profile(project, profile, restored_env)

    return RollbackResult(
        project=project,
        profile=profile,
        snapshot_index=snapshot_index,
        timestamp=snapshot.get("timestamp", ""),
        keys_restored=len(restored_env),
        previous_keys=len(previous_env),
        success=True,
    )
