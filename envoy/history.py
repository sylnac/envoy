"""Profile change history: snapshot and audit trail for .env profiles."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Optional

from envoy.profile import _profile_dir


def _history_dir(project_dir: Path) -> Path:
    return _profile_dir(project_dir) / ".history"


def _history_file(project_dir: Path, profile: str) -> Path:
    return _history_dir(project_dir) / f"{profile}.jsonl"


def record_snapshot(
    project_dir: Path,
    profile: str,
    env: dict,
    message: str = "",
) -> None:
    """Append a snapshot of *env* to the history log for *profile*."""
    hist_dir = _history_dir(project_dir)
    hist_dir.mkdir(parents=True, exist_ok=True)

    entry = {
        "ts": time.time(),
        "message": message,
        "env": env,
    }
    with _history_file(project_dir, profile).open("a") as fh:
        fh.write(json.dumps(entry) + "\n")


def load_history(project_dir: Path, profile: str) -> List[dict]:
    """Return all snapshots for *profile*, oldest first."""
    path = _history_file(project_dir, profile)
    if not path.exists():
        return []
    entries = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries


def get_snapshot(
    project_dir: Path, profile: str, index: int = -1
) -> Optional[dict]:
    """Return a single snapshot by *index* (default: latest)."""
    history = load_history(project_dir, profile)
    if not history:
        return None
    return history[index]


def clear_history(project_dir: Path, profile: str) -> None:
    """Delete all history for *profile*."""
    path = _history_file(project_dir, profile)
    if path.exists():
        path.unlink()
