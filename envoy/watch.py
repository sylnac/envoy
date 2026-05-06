"""File watcher that detects changes to a .env profile on disk."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from envoy.profile import profile_path, load_profile
from envoy.diff import diff_profiles


@dataclass
class WatchEvent:
    """Emitted when a watched profile file changes."""

    project: str
    profile: str
    path: Path
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def _mtime(path: Path) -> float:
    """Return mtime for *path*, or 0.0 if it does not exist."""
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return 0.0


def watch_profile(
    project: str,
    profile: str,
    callback: Callable[[WatchEvent], None],
    *,
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll *profile* for the given *project* and invoke *callback* on changes.

    Parameters
    ----------
    project:        project name
    profile:        profile name (e.g. "development")
    callback:       called with a :class:`WatchEvent` whenever the file changes
    interval:       polling interval in seconds (default 1.0)
    max_iterations: stop after this many poll cycles (``None`` = run forever);
                    useful for testing.
    """
    path = profile_path(project, profile)
    last_mtime = _mtime(path)
    last_env: dict[str, str] = load_profile(project, profile) if path.exists() else {}

    iterations = 0
    while max_iterations is None or iterations < max_iterations:
        time.sleep(interval)
        current_mtime = _mtime(path)
        if current_mtime != last_mtime:
            current_env = load_profile(project, profile) if path.exists() else {}
            result = diff_profiles(last_env, current_env)
            event = WatchEvent(
                project=project,
                profile=profile,
                path=path,
                added=result.added,
                removed=result.removed,
                changed=result.changed,
            )
            callback(event)
            last_mtime = current_mtime
            last_env = current_env
        iterations += 1
