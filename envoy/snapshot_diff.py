"""Compare environment snapshots across history entries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from envoy.diff import DiffResult, diff_profiles
from envoy.history import get_snapshot, load_history


@dataclass
class SnapshotComparison:
    project: str
    from_index: int
    to_index: int
    from_timestamp: str
    to_timestamp: str
    diff: DiffResult

    @property
    def has_changes(self) -> bool:
        """Return True if the diff contains any changes."""
        return bool(
            self.diff.added or self.diff.removed or self.diff.changed
        )


def compare_snapshots(
    project: str,
    from_index: int = -2,
    to_index: int = -1,
) -> SnapshotComparison:
    """Diff two history snapshots by index (negative = from end)."""
    history = load_history(project)
    if not history:
        raise ValueError(f"No history found for project '{project}'")

    try:
        snap_from = history[from_index]
        snap_to = history[to_index]
    except IndexError:
        raise ValueError(
            f"Not enough snapshots: have {len(history)}, "
            f"requested indices {from_index} and {to_index}"
        )

    diff = diff_profiles(snap_from["env"], snap_to["env"])

    return SnapshotComparison(
        project=project,
        from_index=from_index if from_index >= 0 else len(history) + from_index,
        to_index=to_index if to_index >= 0 else len(history) + to_index,
        from_timestamp=snap_from["timestamp"],
        to_timestamp=snap_to["timestamp"],
        diff=diff,
    )


def compare_to_current(
    project: str,
    current_env: dict[str, str],
    snapshot_index: int = -1,
) -> Optional[SnapshotComparison]:
    """Diff a snapshot against the currently active environment dict."""
    snap = get_snapshot(project, snapshot_index)
    if snap is None:
        return None

    diff = diff_profiles(snap["env"], current_env)
    history = load_history(project)

    resolved = snapshot_index if snapshot_index >= 0 else len(history) + snapshot_index

    return SnapshotComparison(
        project=project,
        from_index=resolved,
        to_index=-1,
        from_timestamp=snap["timestamp"],
        to_timestamp="(current)",
        diff=diff,
    )
